from pathlib import Path

from hikari.git import LocalProject
from hikari.ui import menu


def test_local_project_does_not_require_git(tmp_path):
    (tmp_path / "VERSION").write_text("0.9.1\n", encoding="utf-8")
    project = LocalProject(tmp_path)
    assert project.name == tmp_path.name
    assert project.local_version() == ("v0.9.1", "VERSION")
    assert project.branch() == "(local only)"
    assert project.remote() == "(none)"
    assert "not initialized" in project.status_text()


def test_local_project_can_initialize_git(tmp_path):
    project = LocalProject(tmp_path)
    project.init_repo()
    assert (tmp_path / ".git").exists()


def test_local_project_transition_to_git_repo(monkeypatch, tmp_path):
    import hikari.cli as cli
    (tmp_path / "VERSION").write_text("1.2.3\n", encoding="utf-8")
    choices = iter(["1", "9", "y", "0", ""])
    monkeypatch.setattr("builtins.input", lambda *args: next(choices))
    monkeypatch.setattr(cli, "banner", lambda *args: None)
    monkeypatch.setattr(cli, "footer", lambda *args: None)
    monkeypatch.setattr(cli, "menu", lambda is_git=True: next(choices))
    # Exercise the LocalProject-to-GitRepo transition directly; wizard I/O is not the subject of this test.
    project = LocalProject(tmp_path)
    assert project.local_version() == ("v1.2.3", "VERSION")
    project.init_repo()
    from hikari.git import GitRepo
    repo = GitRepo(tmp_path)
    assert repo.root == tmp_path.resolve()


def test_sync_commits_local_repo_without_origin(monkeypatch, tmp_path):
    import subprocess
    import hikari.cli as cli
    from hikari.git import GitRepo

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "hikari@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "HIKARI Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("before\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("after\n", encoding="utf-8")

    monkeypatch.setattr(cli, "confirm", lambda *args: True)
    monkeypatch.setattr("builtins.input", lambda *args: "local sync")

    repo = GitRepo(tmp_path)
    assert repo.has_remote() is False
    cli.sync(repo)
    assert repo.run("log", "-1", "--pretty=%s") == "local sync"


def test_release_creates_local_commit_and_tag_without_origin(monkeypatch, tmp_path):
    import subprocess
    import hikari.cli as cli
    from hikari.git import GitRepo

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "hikari@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "HIKARI Test"], cwd=tmp_path, check=True)
    (tmp_path / "VERSION").write_text("0.4.1\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("initial\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## 0.4.2\n- Release test notes.\n\n## 0.4.1\n- Initial release.\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True, text=True)

    monkeypatch.setattr(cli, "confirm", lambda *args: True)
    monkeypatch.setattr("builtins.input", lambda *args: "1")
    monkeypatch.setattr(cli, "spinner", lambda *args: __import__("contextlib").nullcontext())
    monkeypatch.setattr(cli, "success", lambda *args: None)
    monkeypatch.setattr(cli, "warning", lambda *args: None)

    repo = GitRepo(tmp_path)
    cli.release_interactive(repo, version="v0.4.2")

    assert repo.has_remote() is False
    assert repo.run("tag", "--list") == "v0.4.2"
    assert repo.run("log", "-1", "--pretty=%s") == "initial"


def test_push_dirty_tree_can_commit_and_push(monkeypatch, tmp_path):
    import subprocess
    import hikari.cli as cli
    from hikari.git import GitRepo

    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True, text=True)
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "hikari@example.invalid"], cwd=project, check=True)
    subprocess.run(["git", "config", "user.name", "HIKARI Test"], cwd=project, check=True)
    (project / "README.md").write_text("before\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=project, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=project, check=True, capture_output=True, text=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=project, check=True)
    subprocess.run(["git", "push", "-u", "origin", "master"], cwd=project, check=True, capture_output=True, text=True)
    (project / "README.md").write_text("after\n", encoding="utf-8")

    answers = iter(["1", "feat: update readme", "y"])
    monkeypatch.setattr("builtins.input", lambda *args: next(answers))
    monkeypatch.setattr(cli, "spinner", lambda *args: __import__("contextlib").nullcontext())
    monkeypatch.setattr(cli, "success", lambda *args: None)
    monkeypatch.setattr(cli, "warning", lambda *args: None)

    repo = GitRepo(project)
    cli.push_interactive(repo)

    assert repo.status_porcelain() == ""
    assert repo.run("log", "-1", "--pretty=%s") == "feat: update readme"


def test_push_without_remote_is_safe(tmp_path):
    import subprocess
    from hikari.git import GitRepo, GitError

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "hikari@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "HIKARI Test"], cwd=tmp_path, check=True)
    repo = GitRepo(tmp_path)
    try:
        repo.push()
    except GitError as exc:
        assert "No origin remote configured" in str(exc)
    else:
        raise AssertionError("push should reject repositories without a remote")

def test_init_repo_offers_project_gitignore_when_missing(monkeypatch, tmp_path):
    import hikari.cli as cli
    project = LocalProject(tmp_path)
    project.init_repo()
    answers = iter(["1"])
    monkeypatch.setattr("builtins.input", lambda *args: next(answers))
    monkeypatch.setattr(cli, "success", lambda *args: None)
    monkeypatch.setattr(cli, "warning", lambda *args: None)
    cli._offer_project_gitignore(tmp_path, tmp_path.name)
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "# Python" not in text
    assert ".env" in text
    assert ".vscode/" in text


def test_existing_gitignore_is_never_overwritten(monkeypatch, tmp_path):
    import hikari.cli as cli
    existing = "# Project-owned\ncustom-cache/\n"
    (tmp_path / ".gitignore").write_text(existing, encoding="utf-8")
    monkeypatch.setattr(cli, "success", lambda *args: None)
    cli._offer_project_gitignore(tmp_path, tmp_path.name)
    assert (tmp_path / ".gitignore").read_text(encoding="utf-8") == existing


def test_project_gitignore_detects_python_and_node(monkeypatch, tmp_path):
    import hikari.cli as cli
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (tmp_path / "package.json").write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr("builtins.input", lambda *args: "1")
    monkeypatch.setattr(cli, "success", lambda *args: None)
    cli._offer_project_gitignore(tmp_path, "demo")
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "__pycache__/" in text
    assert "node_modules/" in text
