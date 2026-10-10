import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hikari.release import build_changelog_notes, build_release_notes, next_version


class ReleaseTests(unittest.TestCase):
    def test_next_version(self):
        self.assertEqual(next_version("v1.2.3", "patch"), "v1.2.4")
        self.assertEqual(next_version("v1.2.3", "minor"), "v1.3.0")
        self.assertEqual(next_version("v1.2.3", "major"), "v2.0.0")


    def test_release_notes_from_changelog(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.4.2\n- Fixed release metadata.\n- Improved terminal flow.\n\n## 0.4.1\n- Older change.\n",
                encoding="utf-8",
            )
            notes = build_changelog_notes(root, "v0.4.2")
            self.assertEqual(notes, "- Fixed release metadata.\n- Improved terminal flow.")

    def test_release_notes_from_unreleased_changelog(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## Unreleased\n- Pending release note.\n\n## 0.4.1\n- Older change.\n",
                encoding="utf-8",
            )
            self.assertEqual(build_changelog_notes(root, "v0.4.2"), "- Pending release note.")

    def test_release_notes_group_commits(self):
        notes = build_release_notes(["feat: add scan", "fix: handle empty repo", "docs: update guide"])
        self.assertIn("## Features", notes)
        self.assertIn("## Fixes", notes)
        self.assertIn("## Other", notes)


if __name__ == "__main__":
    unittest.main()



class RebrandAndReleaseTests(unittest.TestCase):
    def test_empty_release_notes_do_not_claim_maintenance_release(self):
        self.assertEqual(build_release_notes([]), "")

    def test_cli_is_rebranded(self):
        import hikari.cli as cli
        self.assertEqual(cli.parser().prog, "hikari")
        version_file = Path(__file__).resolve().parents[1] / "VERSION"
        expected = version_file.read_text(encoding="utf-8").strip()
        self.assertEqual(cli.VERSION.lstrip("v"), expected.lstrip("v"))
        import hikari
        self.assertEqual(hikari.__version__.lstrip("v"), expected.lstrip("v"))

    def test_cli_accepts_standalone_project_path(self):
        from unittest.mock import patch
        import hikari.cli as cli
        captured = {}
        with patch.object(cli, "run_wizard", side_effect=lambda repo: captured.update(root=repo.root)) as _wizard:
            with patch.object(cli, "GitRepo", side_effect=lambda path: type("R", (), {"root": path})()):
                cli.main(["/tmp/example-project"])
        self.assertEqual(str(captured["root"]), "/tmp/example-project")

    def test_terminal_identity_marker(self):
        from hikari.ui import IDENTITY, terminal_text
        self.assertEqual(IDENTITY, "◈")
        self.assertEqual(terminal_text("hello"), "hello")
        self.assertEqual(terminal_text(""), "")

    def test_misc_module_imports(self):
        from hikari.misc import miscellaneous, tree_printer, ghost_grep, file_hasher, backup_rotator, sync_helper, sync_remote, color_note_exporter
        self.assertTrue(callable(miscellaneous))
        self.assertTrue(all(callable(fn) for fn in (tree_printer, ghost_grep, file_hasher, backup_rotator, sync_helper, sync_remote, color_note_exporter)))
