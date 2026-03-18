# good-readme

A Claude Code skill for writing and improving GitHub README documents.

Give it a project with no README and it writes one from scratch — grounded in real analysis of the source code, not boilerplate templates. Give it a project with an existing README and it audits quality against a 100-point rubric, catches inaccuracies, and makes targeted improvements.

## Install

> Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

```sh
claude skill add --url https://github.com/adewale/good-readme
```

## Usage

Open Claude Code in any project directory and ask:

```
Write a README for this project
```

```
Audit this project's README and suggest improvements
```

```
Score this README and tell me what to fix first
```

The skill activates automatically when you ask about READMEs, documentation quality, or writing project docs.

### Example: Audit output

The improve mode scores your README across six categories and returns a structured report:

```
## README Quality Audit

**Project:** my-project
**Score:** 62 / 100
**Rating:** Adequate

| Category                    | Score | Max |
|-----------------------------|-------|-----|
| First Impressions           | 14    | 20  |
| Getting Started             | 12    | 20  |
| Usage & Examples            | 10    | 20  |
| Structure & Scannability    | 11    | 15  |
| Accuracy & Maintenance      | 10    | 15  |
| Completeness                |  5    | 10  |

### Priority Improvements

1. Quick-start — no working example after install steps — add a 3-step quick-start
2. Code examples — imports are missing — make examples copy-pasteable
3. Value proposition — description says what, not why — add one sentence on the problem it solves
```

## What It Does

**Create mode** — for projects without a README:
- Reads source code, config files, and package metadata to understand what the project does
- Asks who the audience is, then drafts a README tailored to them
- Produces real, tested code examples — not pseudocode
- Follows ecosystem conventions (npm vs Rust vs Python vs Go)

**Improve mode** — for projects with an existing README:
- Audits against a 22-criterion quality checklist scored out of 100
- Checks code examples against the actual codebase for accuracy
- Identifies gaps, outdated content, and unnecessary sections
- Presents specific recommendations before making changes

## What's Included

| File | Purpose |
|------|---------|
| `skills/good-readme/SKILL.md` | Skill definition — philosophy, modes, and workflow checklists |
| `skills/good-readme/references/anatomy.md` | Section-by-section guide for every part of a README |
| `skills/good-readme/references/examples.md` | Patterns extracted from well-regarded open-source projects |
| `skills/good-readme/references/quality-checklist.md` | 22-criterion scoring rubric (100-point scale) |
| `skills/good-readme/references/anti-patterns.md` | 15 common README mistakes and how to fix them |

## Contributing

Contributions welcome. If you'd like to improve the skill's reference materials or add new patterns:

```sh
git clone https://github.com/adewale/good-readme.git
cd good-readme
```

Open a PR with your changes. For larger additions (new reference files, changes to the scoring rubric), please open an issue first to discuss.

## License

MIT — see [LICENSE](LICENSE)
