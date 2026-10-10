from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def release_draft_path(root, target: str, home=None) -> Path:
    """Return an isolated per-project, per-version release-draft path.

    Drafts live in HIKARI's home directory, never inside the target repository.
    """
    match = SEMVER.fullmatch(str(target).strip())
    if not match:
        raise ValueError(f"invalid semantic version: {target}")
    version = ".".join(match.groups())
    project_root = Path(root).expanduser().resolve()
    identity = hashlib.sha256(str(project_root).encode("utf-8")).hexdigest()[:16]
    base = Path(home) if home is not None else Path(
        os.environ.get("HIKARI_HOME", Path.home() / ".hikari")
    )
    return base / "release-drafts" / identity / f"{version}.md"


def load_release_draft(root, target: str, home=None) -> str | None:
    """Load a saved Markdown draft, returning None when no draft exists."""
    path = release_draft_path(root, target, home)
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    return content if content.strip() else None


def save_release_draft(root, target: str, content: str, home=None) -> Path:
    """Persist non-empty Markdown outside the target project/repository."""
    if not isinstance(content, str) or not content.strip():
        raise ValueError("release-note draft cannot be empty")
    path = release_draft_path(root, target, home)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text(content.rstrip() + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
    return path


def next_version(current: str, kind: str) -> str:
    match = SEMVER.match(current.strip())
    if not match:
        raise ValueError(f"invalid semantic version: {current}")
    major, minor, patch = map(int, match.groups())
    if kind == "major":
        major, minor, patch = major + 1, 0, 0
    elif kind == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    return f"v{major}.{minor}.{patch}"


def build_release_notes(commits: list[str]) -> str:
    """Build legacy commit-derived notes.

    Kept for callers/tests that still want commit grouping. Release publishing
    uses :func:`build_changelog_notes` instead so GitHub notes come from the
    project's CHANGELOG rather than an arbitrary sync commit.
    """
    if not commits:
        return ""
    groups: dict[str, list[str]] = {"Features": [], "Fixes": [], "Other": []}
    for commit in commits:
        clean = commit.strip()
        lower = clean.lower()
        if lower.startswith(("feat", "feature")):
            groups["Features"].append(clean)
        elif lower.startswith(("fix", "bugfix", "hotfix")):
            groups["Fixes"].append(clean)
        else:
            groups["Other"].append(clean)
    sections = []
    for title, items in groups.items():
        if items:
            sections.append("## " + title + "\n\n" + "\n".join(f"- {item}" for item in items))
    return "\n\n".join(sections)


def build_changelog_notes(root, target: str) -> str:
    """Find release notes in changelog files anywhere in the project."""
    from pathlib import Path
    from .git import find_changelogs

    root = Path(root)
    candidates = find_changelogs(root)
    version = target.lstrip("vV")
    heading = re.compile(r"^##\s+(?:\[?v?" + re.escape(version) + r"\]?)(?:[ \t]+[-—:].*)?$", re.I | re.M)
    unreleased = re.compile(r"^##\s+\[?unreleased\]?(?:[ \t]+[-—:].*)?$", re.I | re.M)
    parsed = []
    for index, changelog in enumerate(candidates):
        try:
            text = changelog.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for pattern, kind in ((heading, 0), (unreleased, 1)):
            match = pattern.search(text)
            if not match:
                continue
            body_start = match.end()
            next_heading = re.search(r"^##\s+", text[body_start:], re.M)
            body_end = body_start + next_heading.start() if next_heading else len(text)
            body = text[body_start:body_end].strip()
            if body:
                parsed.append((kind, index, body))
            break
    if not parsed:
        return ""
    return min(parsed, key=lambda item: (item[0], item[1]))[2]
