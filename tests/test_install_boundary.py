"""Self-tests for scripts/check_install_boundary.py: the clean tree passes, planted repo-only files fail.

The script finds the repo root from its own location, so each case copies the
script (and, where named, this repo's real declarations: package.json,
.claude-plugin/, skills/) into a fresh temporary root and runs it as CI does:
a subprocess, judged by exit code.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_install_boundary.py"
SKILL = "skills/good-readme"

# The boundary contract: none of these may ship inside an installed skill.
REPO_ONLY_PATHS = [
    "evals/shared-benchmark.json",
    "tests/test_x.py",
    "references/tests/test_x.py",
    "eval-runs/latest/output.md",
    "research/notes.md",
    "skill-development/plan.md",
    "node_modules/pkg/index.js",
    ".git/HEAD",
    ".github/workflows/ci.yml",
    "__pycache__/x.cpython-311.pyc",
    "scripts/helper.pyc",
    "scripts/helper.pyo",
    ".DS_Store",
]


class InstallBoundaryTest(unittest.TestCase):
    def new_root(self, with_repo_declarations: bool = False) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "scripts").mkdir()
        shutil.copy2(SCRIPT, root / "scripts")
        if with_repo_declarations:
            shutil.copy2(ROOT / "package.json", root)
            shutil.copytree(ROOT / ".claude-plugin", root / ".claude-plugin")
            shutil.copytree(ROOT / "skills", root / "skills")
        return root

    @staticmethod
    def write(root: Path, rel: str, text: str = "x") -> None:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    @staticmethod
    def run_gate(root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(root / "scripts" / SCRIPT.name)],
                              capture_output=True, text=True, check=False)

    def assert_passes(self, root: Path, *dirs: str) -> None:
        result = self.run_gate(root)
        self.assertEqual(result.returncode, 0, result.stderr)
        for rel in dirs:
            self.assertIn(rel, result.stdout)

    def assert_fails_naming(self, root: Path, text: str) -> None:
        result = self.run_gate(root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(text, result.stderr)

    def test_this_repo_passes(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(SKILL, result.stdout)

    def test_copy_of_this_repo_passes(self) -> None:
        self.assert_passes(self.new_root(with_repo_declarations=True), SKILL)

    def test_each_repo_only_path_fails(self) -> None:
        for rel in REPO_ONLY_PATHS:
            with self.subTest(rel=rel):
                root = self.new_root(with_repo_declarations=True)
                self.write(root, f"{SKILL}/{rel}")
                self.assert_fails_naming(root, f"{SKILL}/{rel}")

    def test_ordinary_skill_files_pass(self) -> None:
        # Near misses for the banned names: these belong in an installed skill.
        root = self.new_root(with_repo_declarations=True)
        for rel in ["references/evaluation.md", "scripts/helper.py", "assets/tests.png", "DS_Store.md"]:
            self.write(root, f"{SKILL}/{rel}")
        self.assert_passes(root, SKILL)

    def test_each_declaration_source_is_checked(self) -> None:
        # Outside skills/*/ so the script's undeclared fallback glob cannot find it.
        skill = "lib/skills/readme"
        declarations = {
            "package.json skill.entry": {"package.json": {"skill": {"entry": f"{skill}/SKILL.md"}}},
            "package.json pi.skills": {"package.json": {"pi": {"skills": ["./lib/skills"]}}},
            "marketplace plugin skills": {".claude-plugin/marketplace.json":
                                          {"plugins": [{"skills": [f"./{skill}"]}]}},
        }
        for label, files in declarations.items():
            with self.subTest(label):
                root = self.new_root()
                for rel, data in files.items():
                    self.write(root, rel, json.dumps(data))
                self.write(root, f"{skill}/SKILL.md", "# skill")
                self.assert_passes(root, skill)
                self.write(root, f"{skill}/evals/case.json")
                self.assert_fails_naming(root, f"{skill}/evals/case.json")

    def test_every_declared_skill_is_checked(self) -> None:
        # Two different skills from two sources; only one of them is dirty.
        for dirty in ["lib/a", "lib/b"]:
            with self.subTest(dirty=dirty):
                root = self.new_root()
                self.write(root, "package.json", json.dumps({"skill": {"entry": "lib/a/SKILL.md"}}))
                self.write(root, ".claude-plugin/marketplace.json", json.dumps({"plugins": [{"skills": ["./lib/b"]}]}))
                self.write(root, "lib/a/SKILL.md")
                self.write(root, "lib/b/SKILL.md")
                self.assert_passes(root, "lib/a", "lib/b")
                self.write(root, f"{dirty}/tests/t.py")
                self.assert_fails_naming(root, f"{dirty}/tests/t.py")

    def test_pi_skills_dir_only_expands_to_folders_with_skill_md(self) -> None:
        root = self.new_root()
        self.write(root, "package.json", json.dumps({"pi": {"skills": ["./lib/skills"]}}))
        self.write(root, "lib/skills/real/SKILL.md")
        self.write(root, "lib/skills/notaskill/tests/t.py")
        self.assert_passes(root, "lib/skills/real")
        self.assertNotIn("notaskill", self.run_gate(root).stdout)

    def test_undeclared_skill_is_found_by_fallback(self) -> None:
        root = self.new_root()
        self.write(root, "package.json", json.dumps({"name": "x"}))
        self.write(root, "skills/found/SKILL.md")
        self.assert_passes(root, "skills/found")
        self.write(root, "skills/found/evals/case.json")
        self.assert_fails_naming(root, "skills/found/evals/case.json")

    def test_declared_dir_without_skill_md_fails(self) -> None:
        root = self.new_root()
        self.write(root, "package.json", json.dumps({"skill": {"entry": f"{SKILL}/SKILL.md"}}))
        self.write(root, f"{SKILL}/README.md")
        self.assert_fails_naming(root, "missing SKILL.md")

    def test_declared_dir_that_does_not_exist_fails(self) -> None:
        root = self.new_root()
        self.write(root, ".claude-plugin/marketplace.json", json.dumps({"plugins": [{"skills": ["./skills/gone"]}]}))
        self.assert_fails_naming(root, "directory does not exist")

    def test_no_skill_declared_or_discovered_fails(self) -> None:
        root = self.new_root()
        self.write(root, "package.json", json.dumps({"name": "x"}))
        self.assert_fails_naming(root, "no installable skill directory")

    def test_invalid_json_is_an_error_not_a_pass(self) -> None:
        root = self.new_root()
        self.write(root, "package.json", "{not json")
        result = self.run_gate(root)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("package.json is not valid JSON", result.stderr)


if __name__ == "__main__":
    unittest.main()
