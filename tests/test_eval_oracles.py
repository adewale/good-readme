"""Oracle self-tests: every custom check must pass a right answer and fail a wrong one.

The fixture oracle is run exactly as the harness runs it (a subprocess with an
output directory and case id). The rewritten regex assertions are read from
evals/shared-benchmark.json so these tests exercise the committed patterns.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORACLE = ROOT / "evals" / "oracles" / "fixture_oracle.py"
CASE = "round3-fixture-cli-drift"
MANIFEST = json.loads((ROOT / "evals" / "shared-benchmark.json").read_text(encoding="utf-8"))


def run_oracle(output: str | None, case_id: str = CASE) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as td:
        if output is not None:
            (Path(td) / "output.md").write_text(output, encoding="utf-8")
        return subprocess.run([sys.executable, str(ORACLE), td, case_id],
                              capture_output=True, text=True, check=False)


def assertion(case_id: str, name: str) -> dict:
    case = next(c for c in MANIFEST["cases"] if c["id"] == case_id)
    return next(a for a in case["assertions"] if a["name"] == name)


def regex_passes(spec: dict, output: str) -> bool:
    # The harness default is ci=true, i.e. case-insensitive matching.
    flags = 0 if spec.get("ci") is False else re.IGNORECASE
    return re.search(spec["pattern"], output, flags) is not None


GOOD_OUTPUTS = {
    "fenced corrected command": (
        "The README's `widget build --fast` no longer exists. `src/cli.ts` exports the `compile` "
        "command with `--profile`, and `package.json#bin` installs `widgetc`.\n\n"
        "```bash\nwidgetc compile --profile production\n```\n"),
    "diff keeps only added lines": (
        "Source checked: src/cli.ts, package.json.\n\n"
        "```diff\n-widget build --fast\n+widgetc compile --profile production\n```\n"),
    "README draft nested in a markdown block": (
        "Corrected README:\n\n````markdown\n# Widget Bits\n\n## Quick start\n\n"
        "```bash\nnpx widgetc compile --profile production\n```\n````\n"),
    "stale command quoted before the fix": (
        "Before (stale):\n\n```bash\nwidget build --fast\n```\n\n"
        "Use instead:\n\n```bash\n$ widgetc compile --profile=production\n```\n"),
    "inline correction": (
        "Replace `widget build --fast` with `widgetc compile --profile production` "
        "(src/cli.ts, package.json bin map).\n"),
}

BAD_OUTPUTS = {
    "keeps the stale command as the fix": "Keep the documented command:\n\n```bash\nwidget build --fast\n```\n",
    "uses a binary package.json does not install": "```bash\nwidget compile --profile production\n```\n",
    "invents a flag": "```bash\nwidgetc compile --profile production --fast\n```\n",
    "uses a subcommand src/cli.ts does not define": "```bash\nwidgetc build --profile production\n```\n",
    "drops the profile flag": "```bash\nwidgetc compile\n```\n",
    # Every keyword the previous oracle grepped for, and no runnable command.
    "keywords without a command": (
        "Per src/cli.ts and package.json, the current command is compile with --profile production; "
        "the bin is widgetc.\n"),
}


class FixtureOracleSelfTests(unittest.TestCase):
    def test_correct_answers_pass(self) -> None:
        for label, output in GOOD_OUTPUTS.items():
            with self.subTest(label):
                proc = run_oracle(output)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                score = json.loads(proc.stdout.splitlines()[0])
                self.assertEqual(score["score"], score["max_score"])

    def test_wrong_answers_fail(self) -> None:
        for label, output in BAD_OUTPUTS.items():
            with self.subTest(label):
                proc = run_oracle(output)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                score = json.loads(proc.stdout.splitlines()[0])
                self.assertLess(score["score"], score["max_score"])

    def test_infrastructure_errors_are_not_answer_failures(self) -> None:
        self.assertEqual(run_oracle(None).returncode, 2)
        self.assertEqual(run_oracle(GOOD_OUTPUTS["inline correction"], case_id="no-such-case").returncode, 2)

    def test_manifest_runs_this_oracle(self) -> None:
        script = assertion(CASE, "fixture-script-oracle")
        self.assertEqual(script["command"][:2], ["python3", "oracles/fixture_oracle.py"])
        self.assertEqual(script["command"][-1], CASE)


class ScopedAssertionSelfTests(unittest.TestCase):
    def test_readme_core_requires_a_rubric_score_or_quick_start_heading(self) -> None:
        cases = [c["id"] for c in MANIFEST["cases"]
                 if any(a["name"] == "readme-core" for a in c["assertions"])]
        self.assertEqual(len(cases), 7)
        for case_id in cases:
            spec = assertion(case_id, "readme-core")
            with self.subTest(case_id):
                for output in ("**Score: 72/100**", "Overall: 64 out of 100.",
                               "## Quick start\n\n```sh\nnpm i\n```", "### Quickstart"):
                    self.assertTrue(regex_passes(spec, output), output)
                # The old contains_any passed each of these on a bare word.
                for output in ("Check the source and the rubric before you score it; add a quick start.",
                               "Category 1, First impressions: 14/20.",
                               "Quick start instructions are missing."):
                    self.assertFalse(regex_passes(spec, output), output)

    def test_bin_alias_check_is_not_implied_by_citing_package_json(self) -> None:
        spec = assertion(CASE, "mentions-bin-alias")
        self.assertTrue(regex_passes(spec, "Run `widgetc compile --profile production` (package.json#bin)."))
        self.assertFalse(regex_passes(spec, "The bin field in package.json is the evidence; see src/cli.ts."))


if __name__ == "__main__":
    unittest.main()
