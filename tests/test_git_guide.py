import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hikari.cli import git_guide_text
from hikari.ui import menu


class GitGuideTests(unittest.TestCase):
    def test_git_guide_explains_beginner_terms(self):
        guide = git_guide_text().lower()
        for term in ("commit", "push", "pull", "pull request", "release", "tag", "branch", "remote"):
            self.assertIn(term, guide)
        self.assertIn("does not upload", guide)
        self.assertIn("different from", guide)

    def test_menu_has_git_guide_and_plain_language_actions(self):
        output = StringIO()
        with patch("builtins.input", side_effect=["10"]), patch("sys.stdout", output):
            self.assertEqual(menu(is_git=True, has_remote=True), "10")
        rendered = output.getvalue().lower()
        self.assertIn("git guide", rendered)
        self.assertIn("hybrid mode", rendered)

    def test_menu_keeps_guide_available_in_local_mode(self):
        output = StringIO()
        with patch("builtins.input", side_effect=["10"]), patch("sys.stdout", output):
            self.assertEqual(menu(is_git=False, has_remote=False), "10")
        self.assertIn("git guide", output.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
