import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hikari import ui


class DashboardClearTests(unittest.TestCase):
    def test_dashboard_clears_and_exits(self):
        clears = []
        with patch("builtins.input", return_value="0"), patch.object(ui, "clear_screen", side_effect=lambda: clears.append(True)):
            self.assertEqual(ui.menu(is_git=True, has_remote=True), "0")
        self.assertEqual(len(clears), 1)

    def test_full_operations_redraw_banner_and_has_exit(self):
        choices = iter(["0"])
        output = []
        with patch("builtins.input", side_effect=lambda _prompt="": next(choices)), patch.object(ui, "clear_screen"), patch("builtins.print", side_effect=lambda *a, **k: output.append(" ".join(map(str, a)))):
            self.assertEqual(ui.menu(is_git=True, has_remote=True), "0")
        rendered = "\\n".join(output)
        self.assertGreaterEqual(rendered.count("H I K A R I"), 1)
        self.assertIn("OPERATIONS / 12 MODULES", rendered)
        self.assertIn("6 RELEASE", rendered)
        self.assertIn("9 MANAGE", rendered)
        self.assertIn("0  EXIT HIKARI", rendered)


    def test_dashboard_renders_live_health_snapshot(self):
        choices = iter(["0"])
        output = []
        snapshot = {
            "branch": "main",
            "working_tree": "DIRTY",
            "changes": "2 path(s) · 1 modified · 0 added · 0 deleted · 1 untracked",
            "remote": "origin configured",
            "sync": "1 ahead / 2 behind",
            "last_commit": "abc123 fix: example",
            "next_step": "Review local changes before committing",
        }
        with patch("builtins.input", side_effect=lambda _prompt="": next(choices)), patch.object(ui, "clear_screen"), patch("builtins.print", side_effect=lambda *a, **k: output.append(" ".join(map(str, a)))):
            self.assertEqual(ui.menu(is_git=True, has_remote=True, snapshot=snapshot), "0")
        rendered = "\\n".join(output)
        for expected in ("LIVE PROJECT STATUS", "Working tree", "DIRTY", "1 ahead / 2 behind", "Review local changes before committing", "OPERATIONS / 12 MODULES"):
            self.assertIn(expected, rendered)

    def test_dashboard_has_12_contiguous_operations_and_groups_are_nested(self):
        choices = iter(["0"])
        output = []
        with patch("builtins.input", side_effect=lambda _prompt="": next(choices)), patch.object(ui, "clear_screen"), patch("builtins.print", side_effect=lambda *a, **k: output.append(" ".join(map(str, a)))):
            self.assertEqual(ui.menu(is_git=True, has_remote=True), "0")
        rendered = "\n".join(output)
        self.assertIn("11 TROUBLESHOOT", rendered)
        self.assertIn("12 MISC", rendered)

    def test_advanced_menu_preserves_operation_ids(self):
        choices = iter(["10"])
        with patch("builtins.input", side_effect=lambda _prompt="": next(choices)), patch.object(ui, "clear_screen"):
            self.assertEqual(ui.menu(is_git=True, has_remote=True), "10")


if __name__ == "__main__":
    unittest.main()
    def test_dashboard_wraps_long_fields_and_uses_compact_banner_on_narrow_terminal(self):
        choices = iter(["0"])
        output = []
        snapshot = {
            "working_tree": "DIRTY",
            "changes": "19 path(s) · " + "modified " * 12,
            "sync": "no upstream configured",
            "last_commit": "abc123 " + "a very long commit subject " * 5,
            "next_step": "Review local changes before committing",
        }
        context = {
            "name": "HIKARI",
            "root": "/storage/emulated/0/Project/" + "nested/" * 8 + "HIKARI",
            "branch": "master",
            "remote": "https://github.com/nexterade/HIKARI.git",
            "version": "v0.6.1",
        }
        with patch("builtins.input", side_effect=lambda *_: next(choices)), \
             patch.object(ui, "clear_screen"), \
             patch.object(ui, "shutil_terminal_width", return_value=48), \
             patch("builtins.print", side_effect=lambda *a, **k: output.append(" ".join(map(str, a)))):
            self.assertEqual(ui.menu(is_git=True, has_remote=True, snapshot=snapshot, target_context=context), "0")
        rendered = "\\n".join(output)
        self.assertIn("HIKARI /.LAB // LOCAL WORKSPACE", rendered)
        self.assertIn("OPERATIONS / 12 MODULES", rendered)
        self.assertIn("Choose operation [0–12]", rendered)
        self.assertIn("nested/", rendered)
