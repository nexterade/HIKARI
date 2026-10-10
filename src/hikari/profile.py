"""Deterministic repository profile suggestions derived from local project files."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

_TOPIC_RULES = (
    ("python", ("python", "pyproject.toml")),
    ("cli", ("cli", "command-line", "command line")),
    ("dashboard", ("dashboard", "web dashboard")),
    ("git", ("git", "git workflow", "repository")),
    ("github", ("github", "github actions", "github api")),
    ("automation", ("automation", "automate", "workflow automation")),
    ("backup", ("backup", "backup rotator", "restore backup")),
    ("release-management", ("release manager", "release management", "github release")),
    ("developer-tools", ("developer tools", "developer automation", "development tool")),
    ("terminal", ("terminal", "console", "tui")),
    ("security", ("safety-first", "security", "safe workflow")),
)


def generate_repository_profile(root: Path) -> dict[str, object]:
    """Return conservative About/Topics suggestions without network or AI access."""
    root = Path(root)
    readme = ""
    for name in ("README.md", "README.rst", "README.txt"):
        path = root / name
        if path.is_file():
            try:
                readme = path.read_text(encoding="utf-8")
                break
            except (OSError, UnicodeError):
                pass
    project: dict = {}
    try:
        project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8")).get("project", {})
    except (OSError, UnicodeError, ValueError):
        pass
    name = str(project.get("name") or root.name).strip()
    description = str(project.get("description") or "").strip()
    if not description:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", readme) if p.strip()]
        for paragraph in paragraphs:
            cleaned = re.sub(r"[`*_>#]", "", paragraph).strip()
            if cleaned and not cleaned.startswith(("[", "http://", "https://")):
                description = re.sub(r"\s+", " ", cleaned)
                break
    if not description:
        description = f"Tools and workflow utilities for {name}."
    description = re.sub(r"\s+", " ", description).strip()
    if len(description) > 300:
        description = description[:297].rstrip() + "..."

    corpus = (readme + "\n" + str(project.get("description", "")) + "\n" + " ".join(p.name for p in root.iterdir() if p.is_dir())).lower()
    topics = [topic for topic, needles in _TOPIC_RULES if any(needle in corpus for needle in needles)]
    if not topics:
        topics = ["developer-tools"]
    return {"name": name, "description": description, "topics": topics[:20], "source": "local project metadata and README; deterministic, no network/AI"}
