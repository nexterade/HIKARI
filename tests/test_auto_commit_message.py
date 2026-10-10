from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hikari.git import auto_commit_message


class FakeRepo:
    def __init__(self, root, status):
        self.root = Path(root)
        self._status = status

    def run(self, *args, **kwargs):
        return self._status


def test_auto_commit_message_summarizes_changed_areas(tmp_path):
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    message = auto_commit_message(FakeRepo(tmp_path, " M src/app.py\n M docs/guide.md"))
    assert message.startswith(("chore:", "docs:", "fix:", "feat:"))
    assert message != "update: project changes"
    assert len(message) <= 72


def test_auto_commit_message_handles_test_only_changes(tmp_path):
    message = auto_commit_message(FakeRepo(tmp_path, " M tests/test_app.py"))
    assert message.startswith("test:")
