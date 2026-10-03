"""Self-tests for scripts/check_install_boundary.py: the clean tree passes, planted repo-only files fail.

The script finds the repo root from its own location, so each test copies the
script and this repo's real declarations (package.json, .claude-plugin/,
skills/) into a temporary root and runs it as CI does: a subprocess, judged by
exit code.
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


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(root / "scripts" / SCRIPT.name)],
                          capture_output=True, text=True, check=False)


class InstallBoundaryTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "scripts").mkdir()
        shutil.copy2(SCRIPT, self.root / "scripts")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def copy_repo_declarations(self) -> None:
        shutil.copy2(ROOT / "package.json", self.root)
        shutil.copytree(ROOT / ".claude-plugin", self.root / ".claude-plugin", dirs_exist_ok=True)
        shutil.copytree(ROOT / "skills", self.root / "skills")

    def write(self, rel: str, text: str = "x") -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def assert_fails_naming(self, rel: str) -> None:
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(rel, result.stderr)

    def test_this_repo_passes(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(SKILL, result.stdout)

    def test_copy_of_this_repo_passes(self) -> None:
        self.copy_repo_declarations()
        self.assertEqual(run(self.root).returncode, 0)

    def test_planted_repo_only_paths_fail(self) -> None:
        for rel in [f"{SKILL}/evals/shared-benchmark.json",
                    f"{SKILL}/references/tests/test_x.py",
                    f"{SKILL}/__pycache__/x.cpython-311.pyc",
                    f"{SKILL}/scripts/helper.pyc",
                    f"{SKILL}/.DS_Store",
                    f"{SKILL}/eval-runs/latest/output.md"]:
            with self.subTest(rel=rel):
                self.copy_repo_declarations()
                self.write(rel)
                self.assert_fails_naming(rel)
                shutil.rmtree(self.root / "skills")

    def test_ordinary_skill_files_pass(self) -> None:
        # Near misses for the banned names: these belong in an installed skill.
        self.copy_repo_declarations()
        for rel in ["references/evaluation.md", "scripts/helper.py", "assets/tests.png", "DS_Store.md"]:
            self.write(f"{SKILL}/{rel}")
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_each_declaration_source_is_checked(self) -> None:
        declarations = {
            "package.json skill.entry": {"package.json": {"skill": {"entry": f"{SKILL}/SKILL.md"}}},
            "package.json pi.skills": {"package.json": {"pi": {"skills": ["./skills"]}}},
            "marketplace plugin skills": {".claude-plugin/marketplace.json":
                                          {"plugins": [{"skills": [f"./{SKILL}"]}]}},
        }
        for label, files in declarations.items():
            with self.subTest(label):
                for rel, data in files.items():
                    self.write(rel, json.dumps(data))
                self.write(f"{SKILL}/SKILL.md", "# skill")
                self.assertEqual(run(self.root).returncode, 0)
                self.write(f"{SKILL}/evals/case.json")
                self.assert_fails_naming(f"{SKILL}/evals/case.json")
                for rel in [*files, "skills"]:
                    path = self.root / rel
                    shutil.rmtree(path) if path.is_dir() else path.unlink()

    def test_declared_dir_without_skill_md_fails(self) -> None:
        self.write("package.json", json.dumps({"skill": {"entry": f"{SKILL}/SKILL.md"}}))
        self.write(f"{SKILL}/README.md")
        self.assert_fails_naming("missing SKILL.md")

    def test_declared_dir_that_does_not_exist_fails(self) -> None:
        self.write(".claude-plugin/marketplace.json", json.dumps({"plugins": [{"skills": ["./skills/gone"]}]}))
        self.assert_fails_naming("directory does not exist")

    def test_no_skill_declared_or_discovered_fails(self) -> None:
        self.write("package.json", json.dumps({"name": "x"}))
        self.assert_fails_naming("no installable skill directory")

    def test_invalid_json_is_an_error_not_a_pass(self) -> None:
        self.write("package.json", "{not json")
        result = run(self.root)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("package.json is not valid JSON", result.stderr)


if __name__ == "__main__":
    unittest.main()
