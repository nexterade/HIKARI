import json
import tempfile
import subprocess
import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hikari.cli import _ACTIVE_ACTION_RESULT, _action_log_path, _action_status_text, _set_action_outcome, _warning_outcome, record_action, run_wizard, success as tracked_success, warning as tracked_warning
from hikari.git import GitRepo, LocalProject


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)
    return result.stdout.strip()


class ActionStatusTests(unittest.TestCase):

    def test_warning_outcomes_distinguish_cancelled_failed_and_blocked(self):
        self.assertEqual(_warning_outcome("Push cancelled. No changes were made.")[0], "CANCELLED")
        self.assertEqual(_warning_outcome("GitHub Release deletion failed: unavailable")[0], "FAILED")
        self.assertEqual(_warning_outcome("This operation requires a Git repository.")[0], "BLOCKED")
        self.assertEqual(_warning_outcome("Unknown choice. No changes were made.")[0], "FAILED")
        self.assertIsNone(_warning_outcome("No origin remote configured; showing local tags only."))
        self.assertIsNone(_warning_outcome("Uncommitted changes detected."))


    def test_terminal_messages_update_active_action_and_preserve_partial_success(self):
        from io import StringIO
        from contextlib import redirect_stdout

        result = {"status": "SUCCESS", "detail": "Completed; see operation output for details"}
        token = _ACTIVE_ACTION_RESULT.set(result)
        try:
            with redirect_stdout(StringIO()):
                tracked_warning("Backup operation cancelled.")
            self.assertEqual(result["status"], "CANCELLED")
            with redirect_stdout(StringIO()):
                tracked_success("Backup created successfully.")
                tracked_warning("Remote publication skipped: no remote configured.")
            self.assertEqual(result["status"], "SUCCESS")
            self.assertIn("Backup created successfully", result["detail"])
            self.assertIn("skipped", result["detail"])
        finally:
            _ACTIVE_ACTION_RESULT.reset(token)

    def test_active_action_result_keeps_concise_terminal_detail(self):
        result = {"status": "SUCCESS", "detail": "Completed; see operation output for details"}
        token = _ACTIVE_ACTION_RESULT.set(result)
        try:
            _set_action_outcome("CANCELLED", "Release cancelled. No changes were made.")
            self.assertEqual(result["status"], "CANCELLED")
            self.assertEqual(result["detail"], "Release cancelled. No changes were made.")
            _set_action_outcome("FAILED", "x" * 220)
            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(len(result["detail"]), 180)
        finally:
            _ACTIVE_ACTION_RESULT.reset(token)

    def test_local_mode_git_action_is_recorded_as_blocked(self):
        from io import StringIO
        from contextlib import redirect_stdout
        from unittest.mock import patch

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            os.environ["HIKARI_HOME"] = str(base / "hikari-home")
            repo = LocalProject(project)
            with patch("hikari.cli.clear_screen"), patch("hikari.cli.banner"), patch("hikari.cli.footer"), patch("hikari.cli.menu", side_effect=["3", "0"]), patch("builtins.input", return_value=""):
                with redirect_stdout(StringIO()):
                    run_wizard(repo)
            records = json.loads(_action_log_path(repo).read_text(encoding="utf-8"))
            terminal = [record for record in records if record["status"] != "STARTED"]
            self.assertEqual(terminal[-1]["status"], "BLOCKED")
            self.assertIn("Requires Git", terminal[-1]["detail"])

    def test_sync_hub_back_is_recorded_as_cancelled(self):
        from unittest.mock import patch
        from io import StringIO
        from contextlib import redirect_stdout
        from hikari.cli import sync_hub

        result = {"status": "SUCCESS", "detail": "Completed; see operation output for details"}
        token = _ACTIVE_ACTION_RESULT.set(result)
        try:
            with patch("builtins.input", return_value="0"):
                with redirect_stdout(StringIO()):
                    sync_hub(LocalProject(Path.cwd()))
            self.assertEqual(result["status"], "CANCELLED")
            self.assertIn("no sync performed", result["detail"])
        finally:
            _ACTIVE_ACTION_RESULT.reset(token)

    def test_misc_utility_result_is_recorded_in_dashboard_history(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from unittest.mock import patch
        from hikari.misc import success as misc_success

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            os.environ["HIKARI_HOME"] = str(base / "hikari-home")
            repo = LocalProject(project)

            def fake_tree(_root):
                misc_success("Tree Printer inspected 2 files.")

            with patch("hikari.cli.clear_screen"), patch("hikari.cli.banner"), patch("hikari.cli.footer"), \
                 patch("hikari.cli.menu", side_effect=["12", "0"]), patch("hikari.misc.tree_printer", side_effect=fake_tree), \
                 patch("hikari.misc._pause"), patch("builtins.input", side_effect=["1", "q", ""]):
                with redirect_stdout(StringIO()):
                    run_wizard(repo)

            records = json.loads(_action_log_path(repo).read_text(encoding="utf-8"))
            terminal = [record for record in records if record["status"] != "STARTED"]
            self.assertEqual(terminal[-1]["status"], "SUCCESS")
            self.assertEqual(terminal[-1]["detail"], "Tree Printer inspected 2 files.")

    def test_misc_utility_warning_and_error_update_active_outcome(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from hikari.misc import error as misc_error, warning as misc_warning

        for reporter, message, expected in (
            (misc_warning, "Remote publication skipped: no remote configured.", "BLOCKED"),
            (misc_error, "Utility failed to write output.", "FAILED"),
        ):
            with self.subTest(expected=expected):
                result = {"status": "SUCCESS", "detail": "Completed; see operation output for details"}
                token = _ACTIVE_ACTION_RESULT.set(result)
                try:
                    with redirect_stdout(StringIO()):
                        reporter(message)
                    self.assertEqual(result["status"], expected)
                    self.assertIn(message, result["detail"])
                finally:
                    _ACTIVE_ACTION_RESULT.reset(token)

    def test_status_action_records_read_only_result_summary(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from unittest.mock import patch

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            os.environ["HIKARI_HOME"] = str(base / "hikari-home")
            repo = LocalProject(project)
            with patch("hikari.cli.clear_screen"), patch("hikari.cli.banner"), patch("hikari.cli.footer"), \
                 patch("hikari.cli.menu", side_effect=["1", "0"]), patch("builtins.input", return_value=""):
                with redirect_stdout(StringIO()):
                    run_wizard(repo)
            records = json.loads(_action_log_path(repo).read_text(encoding="utf-8"))
            terminal = [record for record in records if record["status"] != "STARTED"]
            self.assertEqual(terminal[-1]["status"], "SUCCESS")
            self.assertEqual(terminal[-1]["detail"], "Read-only project status and recent action history displayed")

    def test_action_history_is_bounded_and_stored_outside_target_repo(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            home = base / "hikari-home"
            os.environ["HIKARI_HOME"] = str(home)
            repo = LocalProject(project)
            for number in range(35):
                record_action(repo, f"ACTION-{number}", "FINISHED", "safe summary")
            log_path = _action_log_path(repo)
            records = json.loads(log_path.read_text(encoding="utf-8"))
            assert len(records) == 30
            assert records[0]["action"] == "ACTION-5"
            assert log_path.is_relative_to(home)
            assert not log_path.is_relative_to(project)
            assert "command output" not in log_path.read_text(encoding="utf-8").lower()


    def test_action_status_shows_local_mode_and_recent_actions(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            (project / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            os.environ["HIKARI_HOME"] = str(base / "hikari-home")
            repo = LocalProject(project)
            record_action(repo, "SCAN", "FINISHED", "Scan complete")
            report = _action_status_text(repo)
            assert "ACTION STATUS" in report
            assert "v1.2.3" in report
            assert "local only" in report
            assert "SCAN" in report
            assert "Scan complete" in report


    def test_action_status_shows_git_worktree_and_branch(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            _git(project, "init", "-b", "main")
            _git(project, "config", "user.email", "hikari-test@example.invalid")
            _git(project, "config", "user.name", "HIKARI Test")
            (project / "README.md").write_text("hello\n", encoding="utf-8")
            _git(project, "add", "README.md")
            _git(project, "commit", "-m", "initial")
            os.environ["HIKARI_HOME"] = str(base / "hikari-home")
            report = _action_status_text(GitRepo(project))
            assert "Branch        main" in report
            assert "Working tree  CLEAN" in report
            assert "Last commit   " in report
            assert "Upstream      (not configured)" in report


    def test_menu_integrates_action_history_into_status_without_extra_menu(self):
        from io import StringIO
        from contextlib import redirect_stdout
        from hikari.ui import menu
        output = StringIO()
        import builtins
        original_input = builtins.input
        try:
            builtins.input = lambda _prompt="": "0"
            with redirect_stdout(output):
                menu(is_git=True, has_remote=True)
        finally:
            builtins.input = original_input
        rendered = output.getvalue()
        assert "HYBRID MODE" in rendered
        assert "ACTION STATUS" not in rendered


    def test_hybrid_dashboard_shows_target_full_operations_and_separators(self):
        from io import StringIO
        from contextlib import redirect_stdout
        import builtins
        from hikari.ui import menu

        output = StringIO()
        original_input = builtins.input
        try:
            builtins.input = lambda _prompt="": "0"
            with redirect_stdout(output):
                menu(
                    is_git=True,
                    has_remote=True,
                    snapshot={
                        "working_tree": "DIRTY",
                        "changes": "2 path(s) · 2 modified · 0 added · 0 deleted · 0 untracked",
                        "sync": "no upstream configured",
                        "last_commit": "abc123 example commit",
                        "next_step": "Review local changes before committing",
                    },
                    target_context={
                        "name": "DemoProject",
                        "root": "/tmp/DemoProject",
                        "branch": "main",
                        "remote": "(none)",
                        "version": "v1.2.3",
                        "version_source": "VERSION",
                    },
                )
        finally:
            builtins.input = original_input

        rendered = output.getvalue()
        for expected in (
            "TARGET PROJECT", "DemoProject", "/tmp/DemoProject", "LIVE PROJECT STATUS",
            "Working tree", "DIRTY", "OPERATIONS / 12 MODULES", "11 TROUBLESHOOT",
            "7 REPOSITORY", "└─", "HYBRID MODE",
        ):
            assert expected in rendered
        for key in range(1, 13):
            assert f"{key:>2} " in rendered

    def test_local_scan_reports_inventory_metadata(self):
        from hikari.git import LocalProject
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "hello.py").write_text("print('hi')\n", encoding="utf-8")
            (root / "notes.md").write_text("notes\n", encoding="utf-8")
            report = LocalProject(root).scan_text()
            for expected in ("Location", "Scanned at", "Directories", "Files", "Total size", "Latest file", "Modified at", "FILE TYPES", "Largest files", ".py", ".md"):
                self.assertIn(expected, report)

    def test_git_scan_reports_change_paths_and_inventory(self):
        from hikari.git import GitRepo
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "tracked.txt").write_text("before\n", encoding="utf-8")
            subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=root, check=True, capture_output=True)
            (root / "tracked.txt").write_text("after\n", encoding="utf-8")
            (root / "new.txt").write_text("new\n", encoding="utf-8")
            report = GitRepo(root).scan_text()
            for expected in ("Location", "Scanned at", "Total size", "Git branch", "Last commit", "Changed paths", "tracked.txt", "new.txt"):
                self.assertIn(expected.lower(), report.lower())


if __name__ == "__main__":
    unittest.main()
