"""Tests for config-sync CLI."""

import tempfile
from pathlib import Path

from config_sync.cli import read_source, strip_frontmatter, init_rules


def test_strip_frontmatter():
    input_text = "---\nname: test\n---\nContent here"
    result = strip_frontmatter(input_text)
    assert result == "Content here"
    assert "---" not in result


def test_strip_frontmatter_none():
    input_text = "No frontmatter here"
    result = strip_frontmatter(input_text)
    assert result == input_text


def test_read_source_from_rules():
    with tempfile.TemporaryDirectory() as tmp:
        rules = Path(tmp) / ".claude" / "rules"
        rules.mkdir(parents=True)
        (rules / "style.md").write_text("# Style\nUse 2 spaces")
        result = read_source(Path(tmp))
        assert "Use 2 spaces" in result


def test_read_source_fallback_claude_md():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "CLAUDE.md").write_text("# Rules\nBe careful")
        result = read_source(Path(tmp))
        assert "Be careful" in result


def test_init_splits_claude_md():
    with tempfile.TemporaryDirectory() as tmp:
        claude_md = Path(tmp) / "CLAUDE.md"
        claude_md.write_text("## Style\nUse 2 spaces\n\n## Testing\nWrite tests first")
        init_rules(Path(tmp))
        rules_dir = Path(tmp) / ".claude" / "rules"
        assert rules_dir.exists()
        files = list(rules_dir.glob("*.md"))
        assert len(files) >= 2
