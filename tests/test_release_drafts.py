import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import hikari.cli as cli
from hikari.cli import _release_notes_preview
from hikari.git import GitRepo
from hikari.release import load_release_draft, release_draft_path, save_release_draft


class ReleaseDraftStorageTests(unittest.TestCase):
    def test_draft_persists_by_project_and_version_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project_a = base / "project-a"
            project_b = base / "project-b"
            project_a.mkdir()
            project_b.mkdir()
            home = base / "hikari-home"

            path = save_release_draft(project_a, "v1.2.3", "## Changes\n\n- First item", home)

            self.assertEqual(load_release_draft(project_a, "1.2.3", home), "## Changes\n\n- First item\n")
            self.assertIsNone(load_release_draft(project_b, "v1.2.3", home))
            self.assertIsNone(load_release_draft(project_a, "v1.2.4", home))
            self.assertNotIn(project_a.resolve(), path.parents)

    def test_empty_draft_is_rejected_without_overwriting_existing_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            home = Path(directory) / "home"
            save_release_draft(root, "v1.0.0", "Existing notes", home)

            with self.assertRaisesRegex(ValueError, "cannot be empty"):
                save_release_draft(root, "v1.0.0", "  \n", home)

            self.assertEqual(load_release_draft(root, "v1.0.0", home), "Existing notes\n")

    def test_invalid_version_cannot_escape_draft_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                release_draft_path(directory, "../../secrets")

    def test_interactive_flow_edits_saves_and_reuses_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / "project"
            project.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            repo = GitRepo(project)
            home = base / "hikari-home"
            answers = iter(["2", "## Edited", "", "- Saved item", ".", "4", "1"])
            with patch.dict(os.environ, {"HIKARI_HOME": str(home)}), patch("builtins.input", side_effect=lambda *_: next(answers)):
                chosen = _release_notes_preview(repo, "v2.0.0", "## Generated\n\n- Original")

            self.assertEqual(chosen, "## Edited\n\n- Saved item")
            self.assertEqual(load_release_draft(project, "v2.0.0", home), chosen + "\n")
            self.assertEqual(repo.status_porcelain(), "")

    def test_interactive_flow_can_load_a_saved_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / "project"
            project.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            repo = GitRepo(project)
            home = base / "hikari-home"
            save_release_draft(project, "v2.1.0", "## Saved\n\n- Keep this", home)
            answers = iter(["3", "1"])
            with patch.dict(os.environ, {"HIKARI_HOME": str(home)}), patch("builtins.input", side_effect=lambda *_: next(answers)):
                chosen = _release_notes_preview(repo, "v2.1.0", "## Generated\n\n- New")
            self.assertEqual(chosen, "## Saved\n\n- Keep this\n")


    def test_yes_mode_skips_interactive_draft_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=project, check=True)
            subprocess.run(["git", "config", "user.name", "HIKARI Test"], cwd=project, check=True)
            (project / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            (project / "CHANGELOG.md").write_text("## 1.0.1\n\n- Test release\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=project, check=True)
            subprocess.run(["git", "commit", "-m", "feat: prepare release"], cwd=project, check=True, capture_output=True)
            repo = GitRepo(project)
            with patch.object(cli, "_release_notes_preview", side_effect=AssertionError("unexpected interactive prompt")), patch.object(cli, "spinner", return_value=__import__("contextlib").nullcontext()), patch.object(cli, "success"), patch.object(cli, "warning"):
                cli.release_interactive(repo, yes=True)
            self.assertTrue(repo.tag_exists("v1.0.1"))

    def test_cancel_returns_none_without_creating_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / "project"
            project.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            repo = GitRepo(project)
            home = base / "hikari-home"
            with patch.dict(os.environ, {"HIKARI_HOME": str(home)}), patch("builtins.input", return_value="0"):
                chosen = _release_notes_preview(repo, "v2.2.0", "Generated notes")
            self.assertIsNone(chosen)
            self.assertIsNone(load_release_draft(project, "v2.2.0", home))
