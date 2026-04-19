"""Tests for config-sync detectors."""

import tempfile
from pathlib import Path

from config_sync.detectors import detect_tools


def test_detect_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        result = detect_tools(Path(tmp))
        assert result == []


def test_detect_cursor():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / ".cursor").mkdir()
        result = detect_tools(Path(tmp))
        assert "cursor" in result


def test_detect_copilot():
    with tempfile.TemporaryDirectory() as tmp:
        github = Path(tmp) / ".github"
        github.mkdir()
        (github / "copilot-instructions.md").write_text("test")
        result = detect_tools(Path(tmp))
        assert "copilot" in result


def test_detect_codex():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "AGENTS.md").write_text("test")
        result = detect_tools(Path(tmp))
        assert "codex" in result


def test_detect_multiple():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / ".cursor").mkdir()
        (Path(tmp) / "AGENTS.md").write_text("test")
        (Path(tmp) / "GEMINI.md").write_text("test")
        result = detect_tools(Path(tmp))
        assert "cursor" in result
        assert "codex" in result
        assert "gemini" in result
        assert len(result) == 3


def test_sorted_output():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / ".zed").mkdir()  # zed comes last alphabetically
        (Path(tmp) / "AGENTS.md").write_text("test")  # codex
        result = detect_tools(Path(tmp))
        assert result == sorted(result)
