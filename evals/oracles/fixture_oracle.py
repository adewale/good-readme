#!/usr/bin/env python3
"""Fixture-backed output oracle for shared Skill Eval Harness script assertions.

Instead of re-grepping the manifest's own keywords, this oracle checks the
commands an answer proposes against the fixture's sources of truth:

- the executables the fixture's ``package.json`` ``bin`` map actually installs;
- the subcommand and flags ``src/cli.ts`` defines;
- the executables the fixture's stale ``README.md`` documents.

A proposed command is a line in a shell/diff code block (``+`` lines only in a
diff; Markdown blocks are searched recursively), or an inline code span that
starts with an installed executable and has arguments. A code block introduced
as the "before" or "stale" text is quoted evidence, not a proposal. The answer
passes when it proposes at least one command for the fixture CLI and every such
command uses an installed executable, the source subcommand, and only
source-defined flags (including ``--profile``).

Exit status: 0 pass, 1 fail, 2 usage/infrastructure error. The first stdout
line is the harness score line ``{"score", "max_score", "case_id"}``.
"""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = {
    "round3-fixture-cli-drift": HERE.parent / "fixtures" / "round3-cli-drift",
}
SHELL_INFO = {"", "bash", "sh", "shell", "console", "zsh", "terminal"}
MARKDOWN_INFO = {"markdown", "md"}
RUNNERS = {"npx", "pnpx", "bunx"}
QUOTED_CONTEXT = re.compile(
    r"\b(before|stale|old|outdated|current readme|existing readme|incorrect|wrong|replace|remove|was)\b",
    re.IGNORECASE,
)
FENCE_OPEN = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})[ \t]*(?P<info>[^\s`]*)")
INLINE_CODE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")


def closes(line: str, fence: str) -> bool:
    return re.match(rf"^[ \t]*{re.escape(fence[0])}{{{len(fence)},}}[ \t]*$", line) is not None


def code_blocks(markdown: str) -> list[tuple[str, str, str]]:
    """(info, body, lead-in line) for every fenced block, recursing into Markdown blocks."""
    blocks: list[tuple[str, str, str]] = []
    lines = markdown.splitlines()
    i = 0
    last_text = ""
    while i < len(lines):
        match = FENCE_OPEN.match(lines[i])
        if not match:
            if lines[i].strip():
                last_text = lines[i]
            i += 1
            continue
        fence = match.group("fence")
        info = match.group("info").lower()
        body: list[str] = []
        i += 1
        while i < len(lines) and not closes(lines[i], fence):
            body.append(lines[i])
            i += 1
        i += 1  # closing fence (or end of text)
        text = "\n".join(body)
        blocks.append((info, text, last_text))
        if info in MARKDOWN_INFO:
            blocks.extend(code_blocks(text))
        last_text = ""
    return blocks


def command_tokens(line: str) -> list[str] | None:
    line = line.strip()
    if line.startswith("$ "):
        line = line[2:].strip()
    if not line or line.startswith("#"):
        return None
    try:
        tokens = shlex.split(line, comments=True)
    except ValueError:
        return None
    while tokens and tokens[0] in RUNNERS:
        tokens = tokens[1:]
    return tokens or None


def fenced_proposals(markdown: str) -> list[list[str]]:
    proposals: list[list[str]] = []
    for info, body, lead_in in code_blocks(markdown):
        if info not in SHELL_INFO and info != "diff":
            continue
        if QUOTED_CONTEXT.search(lead_in):
            continue
        for raw in body.splitlines():
            line = raw
            if info == "diff":
                if not line.startswith("+") or line.startswith("+++"):
                    continue
                line = line[1:]
            tokens = command_tokens(line)
            if tokens:
                proposals.append(tokens)
    return proposals


def prose_without_fences(markdown: str) -> str:
    kept: list[str] = []
    fence: str | None = None
    for line in markdown.splitlines():
        match = FENCE_OPEN.match(line)
        if fence is None and match:
            fence = match.group("fence")
        elif fence is not None and closes(line, fence):
            fence = None
        elif fence is None:
            kept.append(line)
    return "\n".join(kept)


def fixture_facts(root: Path) -> tuple[set[str], str, set[str], set[str]]:
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    bin_field = package.get("bin") or {}
    installed = set(bin_field) if isinstance(bin_field, dict) else {str(package["name"])}
    source = (root / "src" / "cli.ts").read_text(encoding="utf-8")
    command_match = re.search(r"export const command = ['\"]([^'\"]+)['\"]", source)
    flags_match = re.search(r"export const flags = \[([^\]]*)\]", source)
    if not command_match or not flags_match:
        raise ValueError(f"{root / 'src' / 'cli.ts'} does not export command and flags")
    flags = set(re.findall(r"['\"](--[\w-]+)['\"]", flags_match.group(1)))
    stale = {tokens[0] for tokens in fenced_proposals((root / "README.md").read_text(encoding="utf-8"))}
    return installed, command_match.group(1), flags, stale


def evaluate(text: str, root: Path) -> list[tuple[str, bool, str]]:
    installed, subcommand, flags, stale = fixture_facts(root)
    cli_names = installed | stale
    fenced = [tokens for tokens in fenced_proposals(text) if tokens[0] in cli_names]
    inline: list[list[str]] = []
    for span in INLINE_CODE.findall(prose_without_fences(text)):
        tokens = command_tokens(span)
        # A bare `widgetc` names the executable; only a span with arguments is a command.
        if tokens and len(tokens) > 1 and tokens[0] in installed:
            inline.append(tokens)
    commands = fenced + inline
    uninstalled = [" ".join(t) for t in fenced if t[0] not in installed]
    wrong_subcommand = [
        " ".join(t) for t in commands
        if t[0] in installed and next((a for a in t[1:] if not a.startswith("-")), None) != subcommand
    ]
    used_flags = {arg.split("=", 1)[0] for t in commands for arg in t[1:] if arg.startswith("--")}
    invented = sorted(used_flags - flags)
    with_profile = [t for t in commands
                    if t[0] in installed and "--profile" in {a.split("=", 1)[0] for a in t}]
    return [
        ("proposes-installed-command", any(t[0] in installed for t in commands),
         f"no proposed command runs an executable package.json installs {sorted(installed)}"),
        ("no-uninstalled-executable", not uninstalled,
         f"a code block proposes executables package.json does not install: {uninstalled}"),
        ("uses-source-subcommand", bool(commands) and not wrong_subcommand,
         f"commands must use the src/cli.ts subcommand {subcommand!r}: {wrong_subcommand or 'none proposed'}"),
        ("uses-source-flags-only", bool(with_profile) and not invented,
         f"flags must come from src/cli.ts {sorted(flags)} and include --profile; invented: {invented}"),
    ]


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: fixture_oracle.py OUTPUT_DIR CASE_ID", file=sys.stderr)
        return 2
    output_dir = Path(sys.argv[1])
    case_id = sys.argv[2]
    root = FIXTURES.get(case_id)
    if root is None:
        print(f"unknown case id: {case_id}", file=sys.stderr)
        return 2
    out = output_dir / "output.md"
    if not out.exists():
        print(f"missing output: {out}", file=sys.stderr)
        return 2
    try:
        results = evaluate(out.read_text(encoding="utf-8", errors="replace"), root)
    except (OSError, ValueError, KeyError) as exc:
        print(f"fixture error: {exc}", file=sys.stderr)
        return 2
    passed = sum(1 for _, ok, _ in results if ok)
    print(json.dumps({"score": passed, "max_score": len(results), "case_id": case_id}))
    failures = [(name, why) for name, ok, why in results if not ok]
    if failures:
        print("FAIL fixture oracle")
        for name, why in failures:
            print(f"- {name}: {why}")
        return 1
    print("OK fixture oracle: " + case_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
