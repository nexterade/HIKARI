import subprocess
from unittest.mock import patch
import tempfile
import unittest
from pathlib import Path

from hikari.cli import parser
from hikari.git import GitError, GitRepo


class ReleaseModeTests(unittest.TestCase):
    def _git(self, path: Path, *args: str) -> None:
        subprocess.run(["git", *args], cwd=path, check=True, capture_output=True, text=True)

    def test_cli_exposes_release_manager_command(self):
        args = parser().parse_args(["release-manager"])
        self.assertEqual(args.command, "release-manager")

    def test_cli_exposes_action_status_command(self):
        args = parser().parse_args(["action-status"])
        self.assertEqual(args.command, "action-status")

    def test_cli_exposes_current_and_custom_release_modes(self):
        args = parser().parse_args(["release", "--current"])
        self.assertTrue(args.current)
        args = parser().parse_args(["release", "--custom"])
        self.assertTrue(args.custom)
        args = parser().parse_args(["release", "--version", "v2.4.1"])
        self.assertEqual(args.version, "v2.4.1")


    def test_release_list_requests_only_supported_json_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=path, check=True)
            repo = GitRepo(path)
            with patch.object(repo, "run_gh", return_value="[]") as run_gh:
                self.assertEqual(repo.github_releases(), [])
            args = run_gh.call_args.args
            self.assertNotIn("url", args[-1].split(","))
            self.assertIn("tagName", args[-1])

    def test_existing_local_tag_is_detected_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            self._git(path, "init", "-q")
            self._git(path, "config", "user.email", "test@example.invalid")
            self._git(path, "config", "user.name", "HIKARI Test")
            (path / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            self._git(path, "add", "VERSION")
            self._git(path, "commit", "-m", "test snapshot", "-q")
            repo = GitRepo(path)
            repo.tag("v1.2.3")
            self.assertTrue(repo.tag_exists("v1.2.3"))
            with self.assertRaisesRegex(GitError, "already exists"):
                repo.tag("v1.2.3")


class ReleaseManagerMethodTests(unittest.TestCase):
    def test_local_tags_can_be_listed_and_deleted_without_touching_release_api(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=path, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=path, check=True)
            subprocess.run(["git", "config", "user.name", "HIKARI Test"], cwd=path, check=True)
            (path / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            subprocess.run(["git", "add", "VERSION"], cwd=path, check=True)
            subprocess.run(["git", "commit", "-m", "test snapshot", "-q"], cwd=path, check=True)
            repo = GitRepo(path)
            repo.tag("v1.2.3")
            self.assertIn("v1.2.3", repo.local_tags())
            repo.delete_local_tag("v1.2.3")
            self.assertNotIn("v1.2.3", repo.local_tags())
            with self.assertRaisesRegex(GitError, "does not exist"):
                repo.delete_local_tag("v1.2.3")



def test_release_tag_inventory_merges_local_remote_and_release_tags():
    from unittest.mock import patch
    from hikari.cli import _release_tag_inventory

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=path, check=True)
        repo = GitRepo(path)
        from contextlib import ExitStack
        with ExitStack() as stack:
            stack.enter_context(patch.object(repo, "has_remote", return_value=True))
            stack.enter_context(patch.object(repo, "local_tags", return_value=["v1.0.0", "v0.9.0"]))
            stack.enter_context(patch.object(repo, "run", return_value="abc123 refs/tags/v1.0.0\ndef456 refs/tags/v0.8.0"))
            stack.enter_context(patch.object(repo, "github_releases", return_value=[
                {"tagName": "v1.0.0", "name": "Stable"},
                {"tagName": "v0.7.0", "name": "Legacy"},
            ]))
            tags, issues = _release_tag_inventory(repo)

    by_name = {item["tag"]: item for item in tags}
    assert set(by_name) == {"v1.0.0", "v0.9.0", "v0.8.0", "v0.7.0"}
    assert by_name["v1.0.0"]["local"] is True
    assert by_name["v1.0.0"]["remote"] is True
    assert by_name["v1.0.0"]["release"]["name"] == "Stable"
    assert by_name["v0.9.0"]["local"] is True
    assert by_name["v0.8.0"]["remote"] is True
    assert by_name["v0.7.0"]["release"]["name"] == "Legacy"
    assert issues == []

class ReleaseManagerSafetyRegressionTests(unittest.TestCase):
    def test_refresh_reloads_inventory_without_recursive_reentry(self):
        from unittest.mock import call
        from hikari.cli import release_manager

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=path, check=True)
            repo = GitRepo(path)
            inventory = ([{"tag": "v1.0.0", "local": True, "remote": False, "release": None}], [])
            with patch("hikari.cli._release_tag_inventory", side_effect=[inventory, ([], [])]) as load:
                with patch("builtins.input", side_effect=["r", "0"]):
                    release_manager(repo)
            self.assertEqual(load.call_count, 2)

    def test_cancel_remote_tag_deletion_never_calls_delete(self):
        from hikari.cli import _release_tag_details

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=path, check=True)
            repo = GitRepo(path)
            item = {"tag": "v1.2.3", "local": False, "remote": True, "release": None}
            with patch("builtins.input", return_value="5"), patch("hikari.cli.confirm", return_value=False):
                with patch.object(repo, "delete_remote_tag") as delete_remote:
                    _release_tag_details(repo, item)
            delete_remote.assert_not_called()


class RemoteTagFailureSafetyTests(unittest.TestCase):
    def test_remote_tag_lookup_raises_when_remote_state_cannot_be_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=path, check=True)
            repo = GitRepo(path)
            with patch.object(repo, "has_remote", return_value=True), patch.object(
                repo, "run", side_effect=GitError("Could not resolve host: example.invalid")
            ) as run:
                with self.assertRaisesRegex(GitError, "Could not resolve host"):
                    repo.remote_tag_exists("v1.2.3")
            run.assert_called_once_with("ls-remote", "--tags", "--refs", "origin", "refs/tags/v1.2.3")

    def test_remote_tag_delete_does_not_push_when_remote_state_is_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=path, check=True)
            repo = GitRepo(path)
            with patch.object(repo, "has_remote", return_value=True), patch.object(
                repo, "run", side_effect=GitError("remote unavailable")
            ) as run:
                with self.assertRaisesRegex(GitError, "remote unavailable"):
                    repo.delete_remote_tag("v1.2.3")
            run.assert_called_once_with("ls-remote", "--tags", "--refs", "origin", "refs/tags/v1.2.3")

    def test_remote_tag_absence_is_only_reported_after_successful_lookup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=path, check=True)
            repo = GitRepo(path)
            with patch.object(repo, "has_remote", return_value=True), patch.object(repo, "run", return_value="") as run:
                self.assertFalse(repo.remote_tag_exists("v1.2.3"))
            run.assert_called_once_with("ls-remote", "--tags", "--refs", "origin", "refs/tags/v1.2.3")


class RemoteTagRealGitIntegrationTests(unittest.TestCase):
    """Exercise remote tag checks against disposable real Git repositories."""

    def _run(self, cwd: Path, *args: str) -> str:
        proc = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
        if proc.returncode:
            raise AssertionError(proc.stderr or proc.stdout or f"git {' '.join(args)} failed")
        return proc.stdout.strip()

    def test_real_bare_remote_tag_lookup_and_delete(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            remote = base / "remote.git"
            project = base / "project"
            project.mkdir()
            self._run(base, "init", "--bare", str(remote))
            self._run(project, "init", "-b", "main")
            self._run(project, "config", "user.email", "hikari-test@example.invalid")
            self._run(project, "config", "user.name", "HIKARI Integration Test")
            (project / "README.md").write_text("disposable integration fixture\n", encoding="utf-8")
            self._run(project, "add", "README.md")
            self._run(project, "commit", "-m", "initial fixture")
            self._run(project, "remote", "add", "origin", str(remote))
            self._run(project, "tag", "v9.8.7")
            self._run(project, "push", "origin", "main", "v9.8.7")

            repo = GitRepo(project)
            self.assertTrue(repo.remote_tag_exists("v9.8.7"))
            self.assertFalse(repo.remote_tag_exists("v9.8.6"))
            repo.delete_remote_tag("v9.8.7")
            self.assertFalse(repo.remote_tag_exists("v9.8.7"))
            refs = subprocess.run(
                ["git", "--git-dir", str(remote), "show-ref", "--tags"],
                text=True, capture_output=True,
            )
            self.assertEqual(refs.returncode, 1)

    def test_real_git_remote_failure_is_not_reported_as_tag_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / "project"
            project.mkdir()
            self._run(project, "init", "-b", "main")
            self._run(project, "remote", "add", "origin", str(base / "missing-remote.git"))
            repo = GitRepo(project)
            with self.assertRaises(GitError):
                repo.remote_tag_exists("v9.8.7")
            with self.assertRaises(GitError):
                repo.delete_remote_tag("v9.8.7")
