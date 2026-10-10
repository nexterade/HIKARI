import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hikari import __version__
from hikari._version import get_version
from hikari.git import GitRepo, detect_local_version, find_changelogs, project_inventory
from hikari.constants import SKIP_DIRS


class RemediationTests(unittest.TestCase):
    def test_version_resolver_matches_version_file_in_source_tree(self):
        expected = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(get_version(), expected)
        self.assertEqual(__version__, expected)

    def test_nested_project_state_version_is_shared_by_git_and_local_detection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "PROJECT_STATE.json").write_text(json.dumps({"project": {"version": "1.2.3"}}), encoding="utf-8")
            self.assertEqual(detect_local_version(root), ("v1.2.3", "PROJECT_STATE.json"))
            repo = GitRepo.__new__(GitRepo)
            repo.root = root
            self.assertEqual(repo.local_version(), ("v1.2.3", "PROJECT_STATE.json"))

    def test_shared_skip_dirs_include_python_tool_caches(self):
        self.assertTrue({".ruff_cache", ".mypy_cache", "target", "env"}.issubset(SKIP_DIRS))

    def test_inventory_and_changelog_discovery_skip_symlinks(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            root, external = Path(td), Path(outside)
            (root / "CHANGELOG.md").write_text("## v1.0.0\n- local\n", encoding="utf-8")
            (external / "CHANGELOG.md").write_text("## v9.9.9\n- outside\n", encoding="utf-8")
            (root / "linked-changelog.md").symlink_to(external / "CHANGELOG.md")
            (root / "linked-file.txt").symlink_to(external / "CHANGELOG.md")
            self.assertEqual([p.name for p in find_changelogs(root)], ["CHANGELOG.md"])
            inventory = project_inventory(root)
            self.assertEqual(inventory["files"], 1)

    def test_git_repo_constructor_does_not_call_tool_check(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            repo = GitRepo(root)
            self.assertEqual(repo.root, root.resolve())


if __name__ == "__main__":
    unittest.main()
