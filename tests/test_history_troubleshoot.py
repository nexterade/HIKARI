import sys
import tempfile
import unittest
from pathlib import Path
from io import StringIO
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hikari.cli import history_log, troubleshoot
from hikari.ui import menu

class HistoryTroubleshootTests(unittest.TestCase):
    def test_menu_exposes_history_and_troubleshoot(self):
        out = StringIO()
        with patch("builtins.input", side_effect=["9"]), patch("sys.stdout", out):
            self.assertEqual(menu(is_git=True, has_remote=True), "9")
        self.assertIn("MANAGE", out.getvalue())
        self.assertIn("OPERATIONS / 12 MODULES", out.getvalue())

    def test_local_mode_git_operation_offers_readiness_path(self):
        out = StringIO()
        with patch("builtins.input", side_effect=["2"]), patch("sys.stdout", out):
            self.assertEqual(menu(is_git=False, has_remote=False), "2")
        self.assertIn("HYBRID MODE", out.getvalue())
        self.assertIn("LOCAL MODE", out.getvalue())

    def test_dashboard_has_simple_and_advanced_modes(self):
        out = StringIO()
        with patch("builtins.input", side_effect=["0"]), patch("sys.stdout", out):
            self.assertEqual(menu(is_git=True, has_remote=True), "0")
        self.assertIn("HYBRID MODE", out.getvalue())
        self.assertIn("OPERATIONS / 12 MODULES", out.getvalue())

    def test_history_log_lists_commits_and_tags(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            from types import SimpleNamespace
            repo = SimpleNamespace()
            repo.root = root
            repo.name = "demo"
            repo.branch = lambda: "main"
            repo.run = lambda *args, check=True: {
                ("log", "-15", "--date=short", "--pretty=format:%h | %ad | %an | %s"): "abc123 | 2026-01-02 | Tester | initial commit",
                ("tag", "--sort=-creatordate", "--format=%(refname:short) | %(creatordate:short) | %(subject)"): "v1.0.0 | 2026-01-02 | release",
                ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"): "origin/main",
                ("rev-list", "--left-right", "--count", "HEAD...origin/main"): "2 1",
            }.get(args, "")
            out = StringIO()
            with patch("sys.stdout", out): history_log(repo)
            self.assertIn("abc123", out.getvalue())
            self.assertIn("v1.0.0", out.getvalue())
            self.assertIn("Local-only commits: 2 | Remote-only commits: 1", out.getvalue())

    def test_troubleshoot_reports_missing_upstream_without_mutating(self):
        with tempfile.TemporaryDirectory() as td:
            from types import SimpleNamespace
            repo = SimpleNamespace()
            repo.root = Path(td)
            repo.name = "demo"
            repo.branch = lambda: "master"
            repo.remote = lambda: "https://example.invalid/demo.git"
            repo.status_porcelain = lambda: "?? new.txt"
            repo.run = lambda *args, check=True: "" if args[0] in {"rev-parse", "merge-base"} else ""
            out = StringIO()
            with patch("sys.stdout", out): troubleshoot(repo)
            report = out.getvalue()
            self.assertIn("Working tree has uncommitted changes", report)
            self.assertIn("Branch has no upstream", report)
            self.assertIn("read-only", report.lower())

if __name__ == "__main__":
    unittest.main()
