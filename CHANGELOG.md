# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- `evals/oracles/fixture_oracle.py` now checks the commands an answer proposes against the `round3-cli-drift` fixture itself: the `package.json` `bin` map, the subcommand and flags `src/cli.ts` defines, and the stale README command. Before, it re-grepped the manifest's own keywords, so an answer with no runnable command passed.
- `readme-core` (7 cases) is a scoped regex, requiring a score out of 100 or a real Quick start heading, instead of `contains_any ["score", "rubric", "quick start", "source"]`. `mentions-bin-alias` requires `widgetc` instead of accepting `package.json`, which `cites-source-files` already required.
- Trigger cases declare `should_trigger` and the judge-only holdout/holdback judges are `"gate": true`, so the manifest validates on Skill Eval Harness `main` as well as 0.6.0.
- Pinned the harness to `skill-eval-harness==0.6.0` in `evals/shared-harness.md` and the manifest; CI runs the oracle self-tests, `validate --strict-leakage --check-ablations` and `audit-manifest --fail-on-blockers`.

## [0.1.0] - 2026-03-17

### Added

- Skill definition with two modes: create (new README) and improve (audit existing)
- 22-criterion quality scoring rubric (100-point scale)
- Section-by-section anatomy guide for README writing
- Patterns catalog from well-regarded open-source projects
- 15 documented anti-patterns with fixes
- Ecosystem-specific conventions (npm, Python, Rust, Go, CLI, web apps, ML)
- `.claude-plugin/plugin.json` for marketplace discovery

[0.1.0]: https://github.com/adewale/good-readme/releases/tag/v0.1.0
