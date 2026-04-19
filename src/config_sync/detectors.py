"""Auto-detect which AI tools are configured in a repo."""

from pathlib import Path


# tool_id → list of paths that indicate the tool is in use
DETECTORS: dict[str, list[str]] = {
    "cursor": [".cursor"],
    "copilot": [".github/copilot-instructions.md"],
    "windsurf": [".windsurf"],
    "cline": [".clinerules"],
    "kiro": [".kiro"],
    "amazonq": [".amazonq"],
    "trae": [".trae"],
    "codex": ["AGENTS.md"],
    "gemini": ["GEMINI.md"],
    "aider": ["CONVENTIONS.md"],
    "goose": [".goosehints"],
    "zed": [".rules"],
}


def detect_tools(repo: Path) -> list[str]:
    """Return list of tool IDs already configured in the repo."""
    detected = []
    for tool_id, paths in DETECTORS.items():
        for p in paths:
            if (repo / p).exists():
                detected.append(tool_id)
                break
    return sorted(detected)
