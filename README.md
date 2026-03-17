# readme

A Claude Code skill that creates and improves README documents for GitHub projects.

Give it a project with no README and it writes one from scratch — grounded in real analysis of the source code, not boilerplate templates. Give it a project with an existing README and it audits quality, catches inaccuracies, and makes targeted improvements.

## Install

```sh
claude skill add --url https://github.com/AdePhil/good-readme
```

## What It Does

**Create mode** — For projects without a README:
- Reads your source code, config files, and package metadata to understand what the project actually does
- Asks who the audience is, then drafts a README tailored to them
- Produces real, tested code examples — not pseudocode

**Improve mode** — For projects with an existing README:
- Audits the current README against a 22-criterion quality checklist (scored out of 100)
- Checks code examples against the actual codebase for accuracy
- Identifies gaps, outdated content, and unnecessary sections
- Presents specific recommendations before making changes

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

The skill automatically activates when you ask about READMEs, documentation quality, or writing project documentation.

## What's Included

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition — philosophy, modes, and workflow checklists |
| `references/anatomy.md` | Section-by-section guide for every part of a README |
| `references/examples.md` | Patterns from well-regarded open-source projects |
| `references/quality-checklist.md` | 22-criterion scoring rubric (100-point scale) |
| `references/anti-patterns.md` | 15 common README mistakes and how to fix them |

## Key Principles

1. **Lead with value** — the first 3 lines determine if someone keeps reading
2. **Show, don't tell** — code examples over prose descriptions
3. **Be honest about scope** — state what the project does AND doesn't do
4. **Respect ecosystem conventions** — npm projects look different from Rust crates
5. **Test your examples** — broken code examples destroy trust instantly

## License

MIT — see [LICENSE](LICENSE)
