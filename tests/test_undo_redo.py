import subprocess
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hikari.git import GitError, GitRepo


def git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr)
    return proc.stdout.strip()


class UndoRedoTests(unittest.TestCase):
    def make_repo(self, path: Path) -> GitRepo:
        git(path, "init")
        git(path, "config", "user.email", "hikari@example.invalid")
        git(path, "config", "user.name", "HIKARI Tests")
        (path / "note.txt").write_text("before\n", encoding="utf-8")
        git(path, "add", "note.txt")
        git(path, "commit", "-m", "initial")
        (path / "note.txt").write_text("after\n", encoding="utf-8")
        git(path, "add", "note.txt")
        git(path, "commit", "-m", "feat: change note")
        return GitRepo(path)

    def test_undo_and_redo_preserve_history(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_repo(root)
            original_head = repo.run("rev-parse", "HEAD")
            self.assertEqual(repo.undo_last_commit(), "feat: change note")
            self.assertTrue(repo.run("log", "-1", "--pretty=%s").startswith('Revert "feat: change note"'))
            self.assertEqual((root / "note.txt").read_text(encoding="utf-8"), "before\n")
            self.assertTrue(repo.redo_last_undo().startswith('Revert "feat: change note"'))
            self.assertEqual((root / "note.txt").read_text(encoding="utf-8"), "after\n")
            self.assertEqual(repo.run("rev-list", "--count", "HEAD"), "4")
            self.assertNotEqual(repo.run("rev-parse", "HEAD"), original_head)

    def test_undo_refuses_dirty_tree(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            root = Path(tmp); repo = self.make_repo(root)
            (root / "note.txt").write_text("unsaved\n", encoding="utf-8")
            with self.assertRaisesRegex(GitError, "clean working tree"):
                repo.undo_last_commit()
            self.assertEqual((root / "note.txt").read_text(encoding="utf-8"), "unsaved\n")

    def test_redo_refuses_non_revert_head(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            repo = self.make_repo(Path(tmp))
            with self.assertRaisesRegex(GitError, "No immediately preceding undo/revert"):
                repo.redo_last_undo()

    def test_restore_only_unstaged_tracked_file(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            root = Path(tmp); repo = self.make_repo(root)
            (root / "note.txt").write_text("unstaged\n", encoding="utf-8")
            (root / "new.txt").write_text("untracked\n", encoding="utf-8")
            self.assertEqual(repo.tracked_worktree_changes(), ["note.txt"])
            repo.restore_tracked_worktree_file("note.txt")
            self.assertEqual((root / "note.txt").read_text(encoding="utf-8"), "after\n")
            self.assertTrue((root / "new.txt").exists())
            with self.assertRaisesRegex(GitError, "unsafe file path"):
                repo.restore_tracked_worktree_file("../outside.txt")

    def test_restore_refuses_staged_only_file(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            root = Path(tmp); repo = self.make_repo(root)
            (root / "note.txt").write_text("staged\n", encoding="utf-8")
            git(root, "add", "note.txt")
            with self.assertRaisesRegex(GitError, "no unstaged tracked changes"):
                repo.restore_tracked_worktree_file("note.txt")


if __name__ == "__main__":
    unittest.main()
