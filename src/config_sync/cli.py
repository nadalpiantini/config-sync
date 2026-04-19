"""CLI entry point for config-sync."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from .detectors import detect_tools
from .generators import TOOLS


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter (--- ... ---) from content."""
    return re.sub(r"^---\n.*?\n---\n?", "", content, count=1, flags=re.DOTALL).strip()


def read_source(repo: Path) -> str:
    """Read canonical source: .claude/rules/*.md or CLAUDE.md fallback."""
    rules_dir = repo / ".claude" / "rules"
    parts: list[str] = []

    if rules_dir.is_dir():
        md_files = sorted(rules_dir.glob("*.md"))
        if md_files:
            for f in md_files:
                raw = f.read_text(encoding="utf-8")
                clean = strip_frontmatter(raw)
                if clean:
                    parts.append(f"## {f.stem}\n\n{clean}")
            return "\n\n".join(parts)

    claude_md = repo / "CLAUDE.md"
    if claude_md.exists():
        raw = claude_md.read_text(encoding="utf-8")
        clean = strip_frontmatter(raw)
        if clean:
            return clean

    print("ERROR: No .claude/rules/*.md or CLAUDE.md found.", file=sys.stderr)
    sys.exit(1)


def init_rules(repo: Path) -> None:
    """Create .claude/rules/ from existing CLAUDE.md."""
    claude_md = repo / "CLAUDE.md"
    if not claude_md.exists():
        print("ERROR: No CLAUDE.md to init from.", file=sys.stderr)
        sys.exit(1)

    rules_dir = repo / ".claude" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    content = claude_md.read_text(encoding="utf-8")
    content = strip_frontmatter(content)

    sections = re.split(r"(?=^## )", content, flags=re.MULTILINE)

    if len(sections) <= 1:
        (rules_dir / "project-rules.md").write_text(content, encoding="utf-8")
        print("  Created .claude/rules/project-rules.md")
    else:
        for section in sections:
            section = section.strip()
            if not section:
                continue
            match = re.match(r"^## (.+)", section)
            if match:
                name = re.sub(r"[^a-z0-9]+", "-", match.group(1).lower()).strip("-")
                filename = f"{name}.md"
            else:
                filename = "general.md"
            (rules_dir / filename).write_text(section, encoding="utf-8")
            print(f"  Created .claude/rules/{filename}")

    count = len(list(rules_dir.glob("*.md")))
    print(f"  Init complete. {count} rule file{'s' if count != 1 else ''} created.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="config-sync",
        description="Generate AI coding assistant config files from a single source.",
    )
    parser.add_argument("repo", help="Path to project repository")
    parser.add_argument("--tools", help="Comma-separated tool list (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--init", action="store_true", help="Create .claude/rules/ from CLAUDE.md")
    parser.add_argument("--list-tools", action="store_true", help="List supported tools and exit")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args()

    if args.list_tools:
        print("Supported tools:\n")
        for tool_id, (file, desc, _) in TOOLS.items():
            print(f"  {tool_id:12s}  {file:40s}  {desc}")
        print(f"\n  {len(TOOLS)} tools total")
        return

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: {repo} is not a directory", file=sys.stderr)
        sys.exit(1)

    if args.init:
        print("Initializing .claude/rules/ from CLAUDE.md...")
        init_rules(repo)
        return

    source = read_source(repo)
    if not source:
        print("ERROR: Source is empty.", file=sys.stderr)
        sys.exit(1)

    if args.tools:
        requested = {t.strip() for t in args.tools.split(",")}
        selected = [t for t in TOOLS if t in requested]
        unknown = requested - set(TOOLS)
        if unknown:
            print(f"WARNING: Unknown tools ignored: {', '.join(sorted(unknown))}", file=sys.stderr)
    else:
        selected = list(TOOLS)

    if not selected:
        print("ERROR: No valid tools selected.", file=sys.stderr)
        sys.exit(1)

    detected = detect_tools(repo)
    print(f"Source: {len(source)} chars")
    if detected:
        print(f"Detected: {', '.join(detected)}")
    print(f"Generating: {', '.join(selected)}")
    print()

    for tool_id in selected:
        filename, desc, formatter = TOOLS[tool_id]
        output = formatter(source)
        outpath = repo / filename

        if args.dry_run:
            print(f"  [{desc:25s}] {filename} ({len(output):,d} chars)")
        else:
            outpath.parent.mkdir(parents=True, exist_ok=True)
            outpath.write_text(output, encoding="utf-8")
            print(f"  + {filename} ({len(output):,d} chars)")

    if not args.dry_run:
        print(f"\nDone. {len(selected)} config file{'s' if len(selected) != 1 else ''} generated.")
        print("Edit source at .claude/rules/")


if __name__ == "__main__":
    main()
