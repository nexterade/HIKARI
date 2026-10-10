from pathlib import Path
import json

from hikari.git import GitRepo


def _repo(path: Path) -> GitRepo:
    repo = GitRepo.__new__(GitRepo)
    repo.root = path
    return repo


def test_local_version_prefers_project_manifest(tmp_path):
    (tmp_path / "PROJECT_STATE.json").write_text(json.dumps({"version": "0.9.1"}))
    (tmp_path / "pyproject.toml").write_text("[project]\nversion = \"1.0.0\"\n")
    assert _repo(tmp_path).local_version() == ("v1.0.0", "pyproject.toml")


def test_local_version_supports_project_state(tmp_path):
    (tmp_path / "PROJECT_STATE.json").write_text(json.dumps({"version": "0.9.1"}))
    assert _repo(tmp_path).local_version() == ("v0.9.1", "PROJECT_STATE.json")


def test_local_version_falls_back_to_changelog(tmp_path):
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## v2.4.0\n")
    assert _repo(tmp_path).local_version() == ("v2.4.0", "CHANGELOG.md")


def test_local_version_never_uses_git_tags(tmp_path):
    (tmp_path / "README.md").write_text("# Project\nCurrent version: v3.2.1\n")
    assert _repo(tmp_path).local_version() == ("v3.2.1", "README.md")
