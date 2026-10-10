from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import hashlib

from ._version import get_version
from .action_tracking import _ACTIVE_ACTION_RESULT, error, set_action_outcome as _set_action_outcome, success, warning, warning_outcome as _warning_outcome
from .git import GitError, GitRepo, LocalProject, recommended_gitignore, auto_commit_message
from .release import build_changelog_notes, load_release_draft, next_version, save_release_draft
from .misc import miscellaneous
from .profile import generate_repository_profile
from .ui import BOLD, CYAN, DIM, MAGENTA, WHITE, banner, clear_screen, footer, menu, section, spinner, color

HIKARI_VERSION = get_version()
VERSION = HIKARI_VERSION  # backwards-compatible alias for integrations

def _action_log_path(repo: GitRepo | LocalProject) -> Path:
    """Return a per-project action-history file outside the target repository."""
    identity = hashlib.sha256(str(repo.root).encode("utf-8")).hexdigest()[:16]
    base = Path(os.environ.get("HIKARI_HOME", Path.home() / ".hikari"))
    return base / "action-status" / f"{identity}.json"


_warned_about_history = False


def record_action(repo: GitRepo | LocalProject, action: str, status: str, detail: str = "") -> None:
    """Persist minimal action metadata; never store command output or credentials."""
    global _warned_about_history
    path = _action_log_path(repo)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(records, list):
                records = []
        except (OSError, ValueError):
            records = []
        records.append({
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "action": action[:48],
            "status": status[:24],
            "detail": detail[:180],
        })
        path.write_text(json.dumps(records[-30:], indent=2), encoding="utf-8")
    except OSError as exc:
        # Logging must not block the operation, but disabled history must be visible.
        if not _warned_about_history:
            print(f"  (action history disabled: {exc.strerror or exc})", file=sys.stderr)
            _warned_about_history = True

def _action_status_text(repo: GitRepo | LocalProject) -> str:
    """Show live project state and a small, privacy-conscious action history."""
    lines = ["\nACTION STATUS", "=" * 48, f"  Project       {repo.name}", f"  Path          {repo.root}", f"  Git mode      {'enabled' if isinstance(repo, GitRepo) else 'local only'}"]
    version, source = repo.local_version()
    lines.append(f"  Version       {version or '(not detected)'}{f' ({source})' if source else ''}")
    if isinstance(repo, GitRepo):
        branch = repo.branch()
        remote = repo.remote()
        lines.extend([f"  Branch        {branch}", f"  Remote        {remote or '(not configured)'}"])
        dirty = repo.status_porcelain()
        lines.append(f"  Working tree  {'DIRTY — changes detected' if dirty else 'CLEAN'}")
        upstream = repo.run("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False)
        lines.append(f"  Upstream      {upstream or '(not configured)'}")
        if upstream:
            counts = repo.run("rev-list", "--left-right", "--count", f"HEAD...{upstream}", check=False).split()
            if len(counts) == 2 and all(item.isdigit() for item in counts):
                lines.append(f"  Ahead/behind  {counts[0]} ahead / {counts[1]} behind")
        head = repo.run("log", "-1", "--format=%h %s", check=False)
        lines.append(f"  Last commit   {head or '(no commits yet)'}")
    else:
        lines.extend(["  Branch        (not initialized)", "  Remote        (none)", "  Working tree  Local files; no Git diff available"])
    lines.extend(["", "RECENT ACTIONS", "-" * 48])
    try:
        records = json.loads(_action_log_path(repo).read_text(encoding="utf-8"))
        if not isinstance(records, list):
            records = []
    except (OSError, ValueError):
        records = []
    if not records:
        lines.append("  No HIKARI actions recorded for this project yet.")
    else:
        for item in reversed(records[-10:]):
            stamp = str(item.get("time", ""))
            if stamp.endswith("+00:00"):
                stamp = stamp[:-6] + "Z"
            lines.append(f"  {stamp} | {item.get('status', 'UNKNOWN'):<9} | {item.get('action', 'Action')}")
            if item.get("detail"):
                lines.append(f"      {item['detail']}")
    lines.extend(["", "Note: history stores action labels/status only, not terminal output or credentials."])
    return "\n".join(lines)

def action_status(repo: GitRepo | LocalProject) -> None:
    section("Action status")
    with spinner("Collecting live project and action state"):
        report = _action_status_text(repo)
    print(report, end="")




def git_guide_text() -> str:
    """Return beginner-friendly explanations of common Git/GitHub concepts."""
    return "\n".join([
        "\nGIT GUIDE — PLAIN LANGUAGE", "=" * 64,
        "Git is a history/snapshot tool for your project. GitHub is a website that can host that history.",
        "You can use HIKARI in Local Mode before initializing Git; local files stay on this device.",
        "",
        "CORE IDEAS",
        "  Repository (repo)  A project folder whose changes Git tracks.",
        "  Working tree        The files as they look right now on your device.",
        "  Stage               Choose which changes should go into the next commit.",
        "  Commit              Save a named snapshot in local Git history. A commit does not upload files.",
        "  Branch              A separate line of work, useful for trying changes safely.",
        "  Remote / origin     A named link to another copy of the repository, often on GitHub.",
        "  Pull                Bring remote commits into your local branch; it can change local files.",
        "  Push                Send already-saved local commits to the remote. It does not mean 'save'.",
        "  Sync                HIKARI workflow to reconcile remote/local state and optionally commit/push.",
        "  Tag                 A named pointer to a particular commit, often used for a version.",
        "  Release             A published version announcement/package, often built around a tag and notes.",
        "  Pull Request (PR)   A proposal to merge one branch into another for review. A Pull Request is different from PULL, which brings remote commits into your local branch.",
        "  Merge               Combine changes from branches.",
        "  Clone               Download a repository to create a local copy for the first time.",
        "  .gitignore          Rules telling Git which untracked files it should usually ignore.",
        "",
        "WHAT HIKARI'S BUTTONS DO",
        "  STATUS              Explain current project/repository health and recent HIKARI actions.",
        "  SCAN                Inspect file inventory and report detected changes/metadata.",
        "  PULL                Get changes from the configured remote; requires Git + remote.",
        "  PUSH                Publish local commits; dirty files require an explicit choice to commit first.",
        "  SYNC                Guided local/remote synchronization; review the summary before confirming.",
        "  RELEASE             Mark a version with a tag and, when possible, publish a GitHub Release.",
        "  FORCE SYNC          Reset local state to origin and may delete local/untracked work. High risk.",
        "  .GITIGNORE          Preview/create ignore rules; existing files are preserved.",
        "  INIT REPO           Start Git tracking locally. This does not upload anything.",
        "  GITHUB REPO         Create/connect a GitHub repository; this alone does not push project files.",
        "  RELEASE & MANAGER   Create releases or manage GitHub Releases and local/remote tags.",
        "  UNDO / REDO         Undo a commit by adding a revert commit; file restore can discard edits.",
        "",
        "BEGINNER SAFETY TIPS",
        "  • Commit is a local save point; push is the step that sends commits to a remote.",
        "  • Pull Request is a review/merge proposal; PULL downloads changes into your local branch.",
        "  • A tag is a Git label; a GitHub Release is a release page that can use that tag.",
        "  • Read paths and confirmation prompts. Cancel if you do not understand the impact.",
        "  • FORCE SYNC can discard work. Make a backup or commit important changes first.",
        "  • HIKARI does not store GitHub credentials; GitHub actions use the installed gh tool.",
        "=" * 64,
    ])


def git_guide() -> None:
    section("Git guide for beginners")
    print(git_guide_text())


def history_log(repo: GitRepo) -> None:
    """Display readable local history and, when available, remote divergence."""
    section("Git history & log")
    branch = repo.branch()
    print(f"Project: {repo.name} | Branch: {branch} | Path: {repo.root}")
    print("Recent commits (newest first):")
    commits = repo.run("log", "-15", "--date=short", "--pretty=format:%h | %ad | %an | %s", check=False)
    print(commits or "  No commits yet.")
    tags = repo.run("tag", "--sort=-creatordate", "--format=%(refname:short) | %(creatordate:short) | %(subject)", check=False)
    print("\nRecent tags:")
    print("\n".join(tags.splitlines()[:10]) if tags else "  No tags found.")
    upstream = repo.run("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False)
    if upstream:
        counts = repo.run("rev-list", "--left-right", "--count", f"HEAD...{upstream}", check=False)
        print(f"\nUpstream: {upstream}")
        if counts:
            ahead, behind = counts.split()[:2]
            print(f"Local-only commits: {ahead} | Remote-only commits: {behind}")
            if int(ahead) and int(behind):
                print("Interpretation: branches diverged; inspect the log before pulling/pushing.")
    else:
        print("\nUpstream: not configured for this branch.")
    print("\nTip: commit = saved local snapshot; push = publish commits; pull = integrate remote commits.")


def troubleshoot(repo: GitRepo) -> None:
    """Run read-only checks and explain common Git states without mutating history."""
    section("Auto troubleshoot — read-only diagnosis")
    findings = []
    branch = repo.branch()
    remote = repo.remote()
    status = repo.status_porcelain()
    upstream = repo.run("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False)
    print(f"Project: {repo.name} | Branch: {branch} | Remote: {remote or '(none)'}")
    if status:
        findings.append(("Working tree has uncommitted changes", "Review STATUS/SCAN; commit or stash important edits before integrating remote changes."))
    else:
        findings.append(("Working tree is clean", "No tracked/untracked changes reported by Git status."))
    if not remote:
        findings.append(("No remote configured", "Use GITHUB REPO to connect a remote. This does not upload files by itself."))
    elif not upstream:
        findings.append(("Branch has no upstream", f"Verify remote branch first. If correct, set it with: git branch --set-upstream-to=origin/{branch} {branch}"))
    else:
        counts = repo.run("rev-list", "--left-right", "--count", f"HEAD...{upstream}", check=False).split()
        if len(counts) == 2 and all(x.isdigit() for x in counts):
            ahead, behind = map(int, counts)
            if ahead and behind:
                findings.append((f"Branches diverged ({ahead} local-only / {behind} remote-only commits)", "Inspect HISTORY / LOG, then choose merge or rebase intentionally. Avoid force-push."))
            elif behind:
                findings.append((f"Local branch is behind by {behind} commit(s)", "Fetch and inspect remote commits before integrating; use PULL after confirming strategy."))
            elif ahead:
                findings.append((f"Local branch is ahead by {ahead} commit(s)", "PUSH can publish saved commits if remote history accepts a fast-forward."))
    if remote:
        head = repo.run("rev-parse", "--verify", "HEAD", check=False)
        remote_head = repo.run("rev-parse", "--verify", f"{upstream}" if upstream else f"refs/remotes/origin/{branch}", check=False)
        if head and remote_head:
            common = repo.run("merge-base", "HEAD", remote_head, check=False)
            if not common:
                findings.append(("Local and remote histories may be unrelated", "Do not force-push. Verify both histories matter, create a backup branch, then consider a deliberate merge with --allow-unrelated-histories."))
    for index, (title, advice) in enumerate(findings, 1):
        print(f"\n[{index}] {title}\n    Next: {advice}")
    print("\nSafety: diagnosis is read-only. HIKARI has not merged, reset, rebased, deleted, or pushed anything.")


def _dashboard_snapshot(repo: GitRepo | LocalProject) -> dict[str, str]:
    """Build a concise, read-only dashboard summary from live project state."""
    version, _source = repo.local_version()
    if not isinstance(repo, GitRepo):
        return {
            "version": version or "not detected",
            "files": "use SCAN FILES for inventory",
            "next_step": "Initialize Git only if you want local commit history",
        }
    dirty = repo.status_porcelain()
    changed = len(dirty.splitlines())
    counts = {"modified": 0, "added": 0, "deleted": 0, "untracked": 0}
    for line in dirty.splitlines():
        code = line[:2]
        if "?" in code:
            counts["untracked"] += 1
        elif "D" in code:
            counts["deleted"] += 1
        elif "A" in code:
            counts["added"] += 1
        else:
            counts["modified"] += 1
    upstream = repo.run("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False)
    sync = "no upstream configured"
    if upstream:
        raw = repo.run("rev-list", "--left-right", "--count", f"HEAD...{upstream}", check=False).split()
        if len(raw) == 2 and all(value.isdigit() for value in raw):
            ahead, behind = map(int, raw)
            sync = f"{ahead} ahead / {behind} behind"
        else:
            sync = "upstream status unavailable"
    behind_count = 0
    if upstream:
        raw_counts = repo.run("rev-list", "--left-right", "--count", f"HEAD...{upstream}", check=False).split()
        if len(raw_counts) == 2 and all(value.isdigit() for value in raw_counts):
            behind_count = int(raw_counts[1])
    next_step = (
        "Review local changes before committing" if dirty
        else "Review incoming commits before pulling" if behind_count
        else "Push saved commits if ready" if upstream and sync.split(" / ")[0] not in {"0 ahead", "0"}
        else "Inspect status or scan files"
    )
    return {
        "branch": repo.branch(),
        "working_tree": "DIRTY" if dirty else "CLEAN",
        "changes": f"{changed} path(s) · {counts['modified']} modified · {counts['added']} added · {counts['deleted']} deleted · {counts['untracked']} untracked",
        "remote": repo.remote() or "not configured",
        "sync": sync,
        "last_commit": repo.run("log", "-1", "--format=%h %s", check=False) or "no commits yet",
        "next_step": next_step,
    }


def run_wizard(repo: GitRepo | LocalProject) -> None:
    # The identity banner is intentionally rendered once. Repainting it on
    # every loop makes terminal scrollback look like the console duplicated
    # itself, especially on mobile terminals.
    clear_screen()
    banner(HIKARI_VERSION)
    while True:
        local_version, version_source = repo.local_version()
        choice = menu(
            is_git=isinstance(repo, GitRepo),
            has_remote=repo.has_remote() if isinstance(repo, GitRepo) else False,
            snapshot=_dashboard_snapshot(repo),
            target_context={
                "name": repo.name,
                "root": str(repo.root),
                "branch": repo.branch(),
                "remote": repo.remote(),
                "version": local_version,
                "version_source": version_source,
            },
        )
        tracked_action = {"1": "STATUS", "2": "SCAN", "3": "PULL", "4": "PUSH", "5": "SYNC", "6": "RELEASE", "7": "REPOSITORY", "8": ".GITIGNORE", "9": "MANAGE", "10": "GIT GUIDE", "11": "TROUBLESHOOT", "12": "MISCELLANEOUS"}.get(choice)
        action_repo = repo
        if tracked_action:
            record_action(action_repo, tracked_action, "STARTED", "Action flow started")
        action_result = {"status": "SUCCESS", "detail": "Completed; see operation output for details"}
        action_token = _ACTIVE_ACTION_RESULT.set(action_result) if tracked_action else None
        try:
            if choice == "1":
                section("Repository status")
                with spinner("Reading project health and recent actions"):
                    text = repo.status_text()
                    action_report = _action_status_text(repo)
                    marker = "RECENT ACTIONS"
                    history = action_report[action_report.find(marker):] if marker in action_report else marker + "\\nNo action history yet."
                print(text)
                print("\\n" + history)
                _set_action_outcome("SUCCESS", "Read-only project status and recent action history displayed")
            elif choice == "2":
                section("Change scanner")
                with spinner("Scanning working tree"):
                    text = repo.scan_text()
                print(text)
                _set_action_outcome("SUCCESS", "Project inventory and change scan completed")
            elif choice in {"3", "4", "5", "6", "9", "11"} and not isinstance(repo, GitRepo):
                warning("This operation requires a Git repository. Use [7] REPOSITORY to initialize Git first.")
                _set_action_outcome("BLOCKED", "Requires Git; initialize the target repository first")
            elif choice == "3":
                section("Pull")
                print("  Pull brings remote commits into your current local branch. Review your changes first; this is different from a Pull Request (a proposal for review).")
                with spinner("Pulling latest remote state"):
                    result = repo.pull()
                success(result or "Repository is up to date.")
            elif choice == "4":
                section("Push")
                print("  Push sends saved local commits to the configured remote. Uncommitted file edits are not included unless you explicitly choose commit + push.")
                push_interactive(repo)
            elif choice == "5":
                sync_hub(repo)
            elif choice == "6":
                section("Release")
                release_hub(repo)
            elif choice == "7":
                repo = repository_hub(repo)
            elif choice == "8":
                section(".gitignore")
                gitignore_menu(repo.root, repo.name)
            elif choice == "9":
                manage_hub(repo)
            elif choice == "10":
                git_guide()
                _set_action_outcome("SUCCESS", "Read-only Git Guide displayed")
            elif choice == "11":
                troubleshoot(repo)
                _set_action_outcome("SUCCESS", "Read-only Git diagnosis displayed; no repository changes made")
            elif choice == "12":
                section("Miscellaneous")
                miscellaneous(repo.root)
            elif choice == "0":
                footer()
                return
            else:
                warning("Unknown operation. Choose one of the listed options.")
            if tracked_action and action_result["detail"] == "Completed; see operation output for details":
                summaries = {
                    "PUSH": "Push flow ended without a reported publish result",
                    "SYNC": "Sync flow ended without a reported reconciliation result",
                    "RELEASE": "Release hub viewed; no tag or publication change reported",
                    "REPOSITORY": "Repository hub returned; no configuration change reported",
                    ".GITIGNORE": ".gitignore reviewed; no file change reported",
                    "MANAGE": "Management hub returned; no recovery change reported",
                    "GIT GUIDE": "Read-only Git Guide displayed",
                    "TROUBLESHOOT": "Read-only Git diagnosis displayed; no repository changes made",
                    "MISCELLANEOUS": "Utility menu returned; no terminal result was reported",
                }
                _set_action_outcome("SUCCESS", summaries.get(tracked_action, f"{tracked_action} flow completed"))
        except (GitError, ValueError) as exc:
            _set_action_outcome("FAILED", str(exc))
            error(str(exc))
        except Exception as exc:
            _set_action_outcome("FAILED", f"Unexpected {type(exc).__name__}: {exc}")
            raise
        finally:
            if tracked_action:
                record_action(action_repo, tracked_action, action_result["status"], action_result["detail"])
            if action_token is not None:
                _ACTIVE_ACTION_RESULT.reset(action_token)
        footer()
        input(color("\n  Press ENTER to return to operations... ", DIM))
        # Keep the interactive console clean: the previous operation log is
        # cleared before the next operations screen is rendered.
        clear_screen()
        banner(HIKARI_VERSION)




def sync_hub(repo: GitRepo | LocalProject) -> None:
    """Combine guided sync and the explicitly high-risk force-sync workflow."""
    print("  [1] Guided SYNC (review, reconcile, optional commit/push)")
    print("  [2] FORCE SYNC (HIGH RISK: replace local state with origin)")
    print("  [0] Back")
    choice = input(color("\n  ❯ ", MAGENTA)).strip()
    if choice in {"", "0"}:
        _set_action_outcome("CANCELLED", "Returned to dashboard; no sync performed")
        return
    if choice == "1":
        print("  Sync guides local/remote reconciliation. HIKARI asks before creating a commit and pushing it.")
        sync(repo)
    elif choice == "2":
        print("  HIGH RISK: this resets the local branch to origin and may delete untracked files.")
        print("  Back up or commit anything important first.")
        force_sync(repo)
    else:
        warning("Unknown choice. No changes were made.")


def repository_hub(repo: GitRepo | LocalProject) -> GitRepo | LocalProject:
    """Combine local Git initialization and GitHub repository configuration."""
    print("  [1] Initialize local Git history (does not upload files)")
    print("  [2] Create/connect/change GitHub repository")
    print("  [0] Back")
    choice = input(color("\n  ❯ ", MAGENTA)).strip()
    if choice in {"", "0"}:
        _set_action_outcome("CANCELLED", "Returned to dashboard; repository unchanged")
        return repo
    if choice == "1":
        if isinstance(repo, GitRepo):
            warning("Git is already initialized for this project.")
            return repo
        if not confirm("Initialize Git in this project? This does not delete or upload files."):
            warning("Initialization cancelled. No changes were made.")
            return repo
        with spinner("Initializing local Git repository"):
            new_repo = repo.init_repo()
        success("Git repository initialized locally.")
        _offer_project_gitignore(new_repo.root, new_repo.name)
        return new_repo
    if choice == "2":
        github_repo_menu(repo)
        return repo
    warning("Unknown choice. No changes were made.")
    return repo


def manage_hub(repo: GitRepo | LocalProject) -> None:
    """Combine recovery controls and history/log inspection."""
    print("  [1] UNDO / REDO — review safe recovery options")
    print("  [2] HISTORY / LOG — inspect commits, tags, and branch divergence")
    print("  [0] Back")
    choice = input(color("\n  ❯ ", MAGENTA)).strip()
    if choice in {"", "0"}:
        _set_action_outcome("CANCELLED", "Returned to dashboard; no management action performed")
        return
    if not isinstance(repo, GitRepo):
        warning("MANAGE actions require Git. Use [7] REPOSITORY to initialize Git first.")
        return
    if choice == "1":
        section("Undo / Redo")
        undo_redo_manager(repo)
    elif choice == "2":
        history_log(repo)
    else:
        warning("Unknown choice. No changes were made.")


def github_repo_menu(repo: GitRepo | LocalProject) -> None:
    """Configure a GitHub repository without publishing project files implicitly."""
    print("  [1] Create a new GitHub repository")
    print("  [2] Connect an existing GitHub repository URL")
    print("  [3] Change existing origin URL")
    print("  [0] Back")
    choice = input(color("\n  ❯ ", MAGENTA)).strip()
    if choice == "0" or not choice:
        _set_action_outcome("CANCELLED", "Returned to dashboard; GitHub repository configuration unchanged")
        return
    if choice not in {"1", "2", "3"}:
        warning("Unknown choice. No changes were made.")
        return

    if not isinstance(repo, GitRepo):
        warning("Initialize Git locally first with [10] INIT REPO. No upload has occurred.")
        return

    if repo.has_remote():
        if choice != "3":
            warning(f"An origin remote is already configured: {repo.remote()}")
            warning("Choose [3] to change it explicitly.")
            return
        new_url = input("  New origin URL: ").strip()
        if not new_url or new_url.startswith("-"):
            warning("Invalid remote URL. No changes were made.")
            return
        if input(f"  Change origin from {repo.remote()} to {new_url}? [y/N]: ").strip().lower() not in {"y", "yes"}:
            warning("Cancelled. Origin was not changed.")
            return
        repo.run("remote", "set-url", "origin", new_url)
        success("Origin URL updated. No project files were pushed.")
        return
    elif choice == "3":
        warning("No origin is configured to change.")
        return

    if choice == "1":
        name = input(f"  Repository name [{repo.name}]: ").strip() or repo.name
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", name) or name in {".", ".."}:
            warning("Invalid repository name: use letters, digits, dot, dash, underscore (max 100 chars).")
            return
        print("  Visibility: [1] Private (recommended)  [2] Public")
        visibility = input("  ❯ ").strip()
        if visibility not in {"1", "2"}:
            warning("Cancelled. Choose visibility explicitly; no changes were made.")
            return
        public_flag = "--public" if visibility == "2" else "--private"
        profile = None
        if confirm("Generate About description and Topics from local project files?"):
            profile = generate_repository_profile(repo.root)
            section("Repository Profile Generator — preview")
            print(f"  Source: {profile['source']}")
            print(f"  About:  {profile['description']}")
            print(f"  Topics: {', '.join(profile['topics'])}")
            print("  These suggestions are deterministic; no AI service or network lookup is used.")
            if confirm("Use this profile? You can edit the About text now."):
                edited = input("  About description [ENTER keeps suggestion]: ").strip()
                if edited:
                    profile["description"] = edited[:300]
            else:
                profile = None
        print("\n  Plan: create GitHub repository and configure origin.")
        if profile:
            print("  Repository About will be set during creation; Topics will be applied afterward.")
        print("  Project files will NOT be pushed by this operation.")
        if not confirm("Continue? This creates a repository on GitHub."):
            warning("Cancelled. No remote was created.")
            return
        try:
            args = ["repo", "create", name, public_flag, "--source", str(repo.root), "--remote", "origin"]
            if profile:
                args.extend(["--description", str(profile["description"])])
            with spinner("Creating GitHub repository"):
                result = repo.run_gh(*args)
            success(result or "GitHub repository created and origin configured.")
            if profile:
                try:
                    for topic in profile["topics"]:
                        repo.run_gh("repo", "edit", "--add-topic", str(topic))
                    success("Repository About and Topics applied to GitHub.")
                except GitError as exc:
                    warning(f"Repository created, but some Topics could not be applied: {exc}")
                    warning("You can add them later in GitHub repository Settings.")
            success("No project commits or files were pushed by HIKARI.")
        except GitError as exc:
            error(f"GitHub repository creation failed: {exc}")
        return

    url = input("  Existing GitHub repository URL (HTTPS or SSH): ").strip()
    if not (url.startswith("https://github.com/") or url.startswith("git@github.com:")):
        warning("Only a GitHub HTTPS or SSH URL is accepted. No changes were made.")
        return
    if url.endswith(".git"):
        url = url[:-4]
    if not confirm(f"Configure origin as {url}? This does not push files."):
        warning("Cancelled. No changes were made.")
        return
    repo.run("remote", "add", "origin", url)
    success("Origin configured. Use PUSH or SYNC separately when ready to publish.")


def _offer_project_gitignore(root: Path, project_name: str) -> None:
    """Offer a project-aware .gitignore only when the project has none."""
    path = root / ".gitignore"
    if path.exists():
        success("Project .gitignore detected; keeping the existing file.")
        return

    content = recommended_gitignore(root)
    print()
    print(f'No .gitignore detected.')
    print()
    print(f'Generate "{project_name}" recommended .gitignore?')
    print()
    print("  [1] Yes")
    print("  [2] Show preview")
    print("  [0] Skip")
    choice = input("  ❯ ").strip()

    if choice == "1":
        path.write_text(content, encoding="utf-8")
        success(f'Generated "{project_name}" recommended .gitignore.')
    elif choice == "2":
        section(".gitignore preview")
        print(content, end="")
        if confirm("Create this .gitignore?"):
            path.write_text(content, encoding="utf-8")
            success(f'Generated "{project_name}" recommended .gitignore.')
        else:
            warning(".gitignore generation skipped. No changes were made.")
    else:
        warning(".gitignore generation skipped.")

def gitignore_menu(root: Path, project_name: str) -> None:
    """Manage the target project's .gitignore without overwriting it silently."""
    path = root / ".gitignore"
    if path.exists():
        print("  ✓ Existing .gitignore detected.")
        print()
        print("  [1] View")
        print("  [2] Scan / validate")
        print("  [3] Replace with recommended")
        print("  [0] Back")
        choice = input(color("\n  ❯ ", MAGENTA)).strip()
        if choice == "1":
            section(".gitignore")
            try:
                print(path.read_text(encoding="utf-8"), end="")
            except (OSError, UnicodeError) as exc:
                error(f"Unable to read .gitignore: {exc}")
        elif choice == "2":
            try:
                text = path.read_text(encoding="utf-8")
                lines = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
                success(f".gitignore readable — {len(lines)} active rule(s).")
            except (OSError, UnicodeError) as exc:
                error(f"Invalid .gitignore encoding or unreadable file: {exc}")
        elif choice == "3":
            content = recommended_gitignore(root)
            section("Recommended .gitignore preview")
            print(content, end="")
            if confirm("Replace the existing .gitignore? This will overwrite project rules."):
                path.write_text(content, encoding="utf-8")
                success(f'Replaced "{project_name}" .gitignore with the recommended template.')
            else:
                warning("Replacement cancelled. Existing .gitignore was preserved.")
        return

    print("  No .gitignore detected.")
    print()
    print(f'  Generate "{project_name}" recommended .gitignore?')
    print()
    print("  [1] Yes")
    print("  [2] Show preview")
    print("  [0] Skip")
    choice = input(color("\n  ❯ ", MAGENTA)).strip()
    content = recommended_gitignore(root)
    if choice == "1":
        path.write_text(content, encoding="utf-8")
        success(f'Generated "{project_name}" recommended .gitignore.')
    elif choice == "2":
        section(".gitignore preview")
        print(content, end="")
        if confirm("Create this .gitignore?"):
            path.write_text(content, encoding="utf-8")
            success(f'Generated "{project_name}" recommended .gitignore.')
        else:
            warning(".gitignore generation skipped. No changes were made.")
    else:
        warning(".gitignore generation skipped.")


def push_interactive(repo: GitRepo) -> None:
    """Publish commits, offering an explicit commit+push path for dirty trees."""
    if not repo.has_remote():
        warning("No remote configured. PUSH requires an origin remote.")
        return

    status = repo.status_porcelain()
    if not status:
        with spinner("Publishing local commits"):
            repo.push()
        success("Local commits pushed to remote. Working tree is clean.")
        return

    print(repo.scan_text())
    warning("Uncommitted changes detected.")
    print("  PUSH normally publishes existing commits only.")
    print()
    print("  [1] Commit changes + push")
    print("  [2] Push existing commits only")
    print("  [0] Cancel")
    choice = input("  ❯ ").strip()

    if choice == "0" or not choice:
        warning("Push cancelled. No changes were made.")
        return

    if choice == "2":
        with spinner("Publishing local commits"):
            repo.push()
        success("Existing commits pushed to remote. Uncommitted changes remain local.")
        return

    if choice != "1":
        warning("Unknown choice. Push cancelled.")
        return

    raw_message = input("  Commit message [auto: scan project changes]: ").strip()
    message = auto_commit_message(repo) if not raw_message or raw_message.lower() == "auto" else raw_message
    print(f"  Commit message: {message}")
    warning("This will stage all detected changes, create a local commit, and push it to the configured remote.")
    confirm = input("  Commit + push? [y/N] ").strip().lower()
    if confirm not in {"y", "yes"}:
        warning("Commit + push cancelled. No changes were committed or uploaded.")
        return
    with spinner("Staging changes"):
        repo.add_all()
    with spinner("Creating commit"):
        repo.commit(message)
    with spinner("Publishing local commits"):
        repo.push()

    if repo.status_porcelain():
        warning("Push completed, but the working tree still has changes.")
    else:
        success("Changes committed and pushed. Working tree is clean.")


def sync(repo: GitRepo, yes: bool = False) -> None:
    """Synchronize a Git repository, with or without an origin remote.

    A local repository is still a valid synchronization target. When no
    origin exists, SYNC commits local changes but deliberately does not try
    to push to a nonexistent remote. When an origin exists, the normal
    pull/commit/push workflow is used.
    """
    has_remote = repo.has_remote()
    with spinner("Scanning local and remote state" if has_remote else "Scanning local repository state"):
        status = repo.status_porcelain()
    print(repo.scan_text())

    if not status:
        if has_remote:
            with spinner("Pulling latest changes"):
                repo.pull()
            success("Repository synchronized. Working tree is clean.")
        else:
            success("Local repository is synchronized. No changes to commit.")
        return

    if not yes and not confirm(
        "Commit and push these changes?" if has_remote else
        "Commit these local changes? (no remote configured)"
    ):
        warning("Sync cancelled. No changes were made.")
        return

    raw_message = input("  Commit message [auto: scan project changes]: ").strip()
    message = auto_commit_message(repo) if not raw_message or raw_message.lower() == "auto" else raw_message
    print(f"  Commit message: {message}")
    with spinner("Staging changes"):
        repo.add_all()
    with spinner("Creating commit"):
        repo.commit(message)

    if has_remote:
        with spinner("Pushing to remote"):
            repo.push()
        success("Repository synchronized and changes published.")
    else:
        success("Local repository synchronized. Commit created; no remote configured.")


def _edit_release_notes(initial: str) -> str:
    """Collect a multiline Markdown replacement; a single dot ends editing."""
    print("  Enter release notes one line at a time. A single '.' on its own line finishes.")
    if initial:
        print("  Existing notes are shown above; enter the replacement from scratch.")
    lines: list[str] = []
    while True:
        try:
            line = input("  | ")
        except EOFError:
            break
        if line == ".":
            break
        lines.append(line)
    edited = "\n".join(lines).strip()
    if not edited:
        warning("Edited release notes are empty; keeping the previous draft.")
        return initial
    return edited


def _release_notes_preview(repo: GitRepo, target_version: str, notes: str) -> str | None:
    """Interactive preview/edit/load/save flow; returns None when cancelled."""
    while True:
        saved = None
        try:
            saved = load_release_draft(repo.root, target_version)
        except (OSError, UnicodeError, ValueError) as exc:
            warning(f"Could not read saved release-note draft: {exc}")
        print(f"\n  RELEASE NOTES PREVIEW — {target_version}\n")
        print(f"{notes}\n")
        print("  [1] Use these notes")
        print("  [2] Edit notes")
        print(f"  [3] Load saved draft {'(available)' if saved else '(none saved)'}")
        print("  [4] Save current notes as draft")
        print("  [0] Cancel release")
        choice = input(color("\n  ❯ ", MAGENTA)).strip()
        if choice == "1":
            return notes
        if choice == "2":
            notes = _edit_release_notes(notes)
            continue
        if choice == "3":
            if not saved:
                warning("No saved draft exists for this project and version.")
                continue
            notes = saved
            continue
        if choice == "4":
            try:
                path = save_release_draft(repo.root, target_version, notes)
            except (OSError, UnicodeError, ValueError) as exc:
                warning(f"Could not save release-note draft: {exc}")
            else:
                success(f"Release-note draft saved outside the repository: {path}")
            continue
        if choice == "0" or not choice:
            warning("Release cancelled. No changes were made.")
            return None
        warning("Unknown choice. Select 1, 2, 3, 4, or 0.")


def release_interactive(
    repo: GitRepo, version: str | None = None, yes: bool = False,
    current: bool = False, custom: bool = False,
) -> None:
    if repo.status_porcelain():
        warning("Working tree has uncommitted changes. Commit or stash them first; release cancelled safely.")
        return
    local_current, local_source = repo.local_version()
    if not local_current:
        warning("No local project version found. Set a version in project metadata before releasing.")
        return
    current_version = local_current
    print(f"  {color('CURRENT VERSION', DIM)}  {current_version}  {color(f'[{local_source}]', DIM)}")

    if version:
        target_version = version if version.startswith("v") else f"v{version}"
    elif current:
        target_version = current_version
    elif custom:
        typed = input("  Custom target version (e.g. v1.2.3): ").strip()
        from .release import SEMVER
        if not SEMVER.fullmatch(typed):
            raise ValueError(f"invalid semantic version: {typed}")
        target_version = typed if typed.startswith("v") else f"v{typed}"
    elif yes:
        target_version = next_version(current_version, "patch")
    else:
        suggested = next_version(current_version, "patch")
        print("\n  [1] Quick release — use suggested next version")
        print("  [2] Force release current version")
        print("  [3] Custom version")
        print("  [0] Cancel")
        choice = input(color("\n  ❯ ", MAGENTA)).strip()
        if choice == "0" or not choice:
            warning("Release cancelled. No changes were made.")
            return
        if choice == "1":
            target_version = suggested
        elif choice == "2":
            target_version = current_version
        elif choice == "3":
            typed = input("  Custom target version (e.g. v1.2.3): ").strip()
            from .release import SEMVER
            if not SEMVER.fullmatch(typed):
                raise ValueError(f"invalid semantic version: {typed}")
            target_version = typed if typed.startswith("v") else f"v{typed}"
        else:
            warning("Unknown choice. Release cancelled.")
            return

    from .release import SEMVER
    if not SEMVER.fullmatch(target_version):
        raise ValueError(f"invalid semantic version: {target_version}")
    if repo.tag_exists(target_version):
        warning(f"Tag {target_version} already exists locally. Refusing duplicate/overwrite release.")
        return
    has_remote = repo.has_remote()
    if has_remote and repo.remote_tag_exists(target_version):
        warning(f"Remote tag {target_version} already exists. Refusing to overwrite remote history.")
        return
    if has_remote and repo.github_release_exists(target_version):
        warning(f"GitHub Release {target_version} already exists. Refusing to create a duplicate.")
        return

    latest_tag = repo.latest_tag()
    commits = repo.commits_since(latest_tag) if latest_tag else repo.run("log", "--pretty=format:%s", check=False).splitlines()
    if not commits:
        warning(f"No commits available for release {target_version}. Nothing to release.")
        return
    notes = build_changelog_notes(repo.root, target_version)
    notes_source = "project changelog"
    if not notes:
        from .release import build_release_notes
        notes = build_release_notes(commits)
        if not notes:
            warning(f"No release notes found for {target_version}, and no commits are available to draft notes from.")
            return
        notes_source = "commit-derived draft (not found in changelog)"
        warning(f"No changelog entry for {target_version}; using a visible draft from {len(commits)} commit(s).")

    print(f"\n  {color('CURRENT', DIM)}  {current_version}")
    print(f"  {color('TARGET', CYAN)}   {color(target_version, BOLD + WHITE)}")
    print(f"  {color('COMMITS', DIM)}  {len(commits)}")
    print(f"  {color('NOTES SOURCE', DIM)}  {notes_source}")
    if not yes:
        selected_notes = _release_notes_preview(repo, target_version, notes)
        if selected_notes is None:
            return
        notes = selected_notes
    else:
        print(f"\n{notes}\n")
    if has_remote:
        prompt = f"Publish {target_version} from current HEAD (tag + push + GitHub Release)?"
    else:
        prompt = f"Create local tag {target_version} at current HEAD? (no remote configured)"
    if not yes and not confirm(prompt):
        warning("Release cancelled. No changes were made.")
        return

    # A release labels the current source snapshot; it must not silently stage/commit
    # unrelated working-tree edits or bump the project's version files.
    if repo.status_porcelain():
        warning("Working tree changed during release preparation. Commit or stash changes; release cancelled safely.")
        return
    if repo.tag_exists(target_version):
        warning(f"Tag {target_version} was created concurrently. No release tag was changed.")
        return
    try:
        with spinner(f"Creating tag {target_version}"):
            repo.tag(target_version)
    except GitError as exc:
        warning(f"Could not create release tag {target_version}: {exc}")
        return
    if not has_remote:
        success(f"Local release tag created: {target_version}")
        warning("No remote configured; GitHub publication skipped.")
        return
    with spinner(f"Pushing tag {target_version}"):
        repo.push_tag(target_version)
    with spinner("Publishing GitHub release"):
        repo.github_release(target_version, notes)
    success(f"Release published and verified by gh: {target_version}")


def release_hub(repo: GitRepo | LocalProject) -> None:
    """Combine release creation and release/tag maintenance under dashboard menu 6."""
    print("  [1] Create a release (version tag + optional GitHub Release)")
    print("  [2] Manage GitHub Releases and Git tags")
    print("  [0] Back")
    choice = input(color("\n  ❯ ", MAGENTA)).strip()
    if choice in {"", "0"}:
        _set_action_outcome("CANCELLED", "Returned to dashboard; no release action performed")
        return
    if choice == "1":
        print("  A release marks a version with a Git tag and may publish release notes to GitHub.")
        release_interactive(repo)
    elif choice == "2":
        if not isinstance(repo, GitRepo):
            warning("Release management requires a Git repository. Initialize Git first.")
            return
        release_manager(repo)
    else:
        warning("Unknown choice. No changes were made.")


def _release_tag_inventory(repo: GitRepo) -> tuple[list[dict[str, object]], list[str]]:
    """Merge local tags, origin tags, and GitHub Release tags without hiding partial failures."""
    inventory: dict[str, dict[str, object]] = {}
    issues: list[str] = []

    try:
        for tag in repo.local_tags():
            if tag:
                inventory.setdefault(tag, {"tag": tag, "local": False, "remote": False, "release": None})
                inventory[tag]["local"] = True
    except GitError as exc:
        issues.append(f"Local tags unavailable: {exc}")

    if repo.has_remote():
        try:
            raw = repo.run("ls-remote", "--tags", "--refs", "origin")
            for line in raw.splitlines():
                parts = line.split(None, 1)
                if len(parts) != 2:
                    continue
                tag_ref = parts[1].strip()
                if tag_ref.startswith("refs/tags/"):
                    tag = tag_ref[len("refs/tags/"):]
                    inventory.setdefault(tag, {"tag": tag, "local": False, "remote": False, "release": None})
                    inventory[tag]["remote"] = True
        except GitError as exc:
            issues.append(f"Remote tags unavailable: {exc}")
        try:
            releases = repo.github_releases()
            for release in releases:
                tag = str(release.get("tagName") or "").strip()
                if not tag:
                    continue
                inventory.setdefault(tag, {"tag": tag, "local": False, "remote": False, "release": None})
                inventory[tag]["release"] = release
        except GitError as exc:
            issues.append(f"GitHub Releases unavailable: {exc}")
    else:
        issues.append("No origin remote configured; showing local tags only.")

    return [inventory[tag] for tag in sorted(inventory, key=str.casefold)], issues


def _release_tag_details(repo: GitRepo, item: dict[str, object]) -> None:
    tag = str(item["tag"])
    release = item.get("release")
    print("\n  TAG DETAILS")
    print(f"  Tag             : {tag}")
    print(f"  Local           : {'yes' if item.get('local') else 'no'}")
    print(f"  Remote origin   : {'yes' if item.get('remote') else 'no'}")
    print(f"  GitHub Release  : {'yes' if release else 'no'}")
    if item.get("local"):
        try:
            sha = repo.run("rev-parse", f"refs/tags/{tag}^{{}}")
            subject = repo.run("log", "-1", "--format=%s", f"refs/tags/{tag}^{{}}")
            date = repo.run("log", "-1", "--format=%cI", f"refs/tags/{tag}^{{}}")
            print(f"  Commit          : {sha[:12]}")
            print(f"  Commit date     : {date}")
            print(f"  Commit subject  : {subject}")
            annotation = repo.run("for-each-ref", "--format=%(contents:subject)", f"refs/tags/{tag}", check=False)
            if annotation:
                print(f"  Tag annotation  : {annotation}")
        except GitError as exc:
            warning(f"Could not read local tag details: {exc}")
    if isinstance(release, dict):
        status = "draft" if release.get("isDraft") else ("prerelease" if release.get("isPrerelease") else "published")
        print(f"  Release name    : {release.get('name') or tag}")
        print(f"  Release status  : {status}")
        print(f"  Published       : {release.get('publishedAt') or 'unknown'}")
    print("\\n  [1] Refresh details")
    print("  [2] View GitHub Release")
    print("  [3] Delete GitHub Release")
    print("  [4] Delete local Git tag")
    print("  [5] Delete remote Git tag")
    print("  [6] Compare local and remote")
    print("  [0] Back")
    action = input(color("\\n  ❯ ", MAGENTA)).strip()
    if action in {"", "0"}:
        _set_action_outcome("CANCELLED", "Returned to tag list; no tag action performed")
        return
    if action == "1":
        refreshed, issues = _release_tag_inventory(repo)
        match = next((candidate for candidate in refreshed if candidate["tag"] == tag), None)
        if match:
            _release_tag_details(repo, match)
        else:
            warning(f"Tag {tag} is no longer present in the available sources.")
        for issue in issues:
            warning(issue)
    elif action == "2":
        if not release:
            warning(f"No GitHub Release exists for tag {tag}.")
        else:
            try:
                print(repo.github_release_details(tag))
            except GitError as exc:
                warning(f"Could not load GitHub Release details: {exc}")
    elif action == "3":
        if not release:
            warning(f"No GitHub Release exists for tag {tag}; nothing to delete.")
        else:
            warning(f"This deletes the GitHub Release object for {tag}; Git tags remain untouched.")
            if confirm(f"Permanently delete GitHub Release {tag}?"):
                try:
                    repo.delete_github_release(tag)
                    success(f"GitHub Release deleted: {tag}. Git tags were not changed.")
                except GitError as exc:
                    warning(f"GitHub Release deletion failed: {exc}")
            else:
                warning("Delete cancelled. No changes were made.")
    elif action in {"4", "5"}:
        scope = "local" if action == "4" else "remote origin"
        exists = bool(item.get("local")) if action == "4" else bool(item.get("remote"))
        if not exists:
            warning(f"Tag {tag} does not exist in {scope}.")
        else:
            warning(f"This permanently deletes the {scope} Git tag {tag}; it does not delete release assets/notes.")
            if confirm(f"Delete {scope} tag {tag}?"):
                try:
                    (repo.delete_local_tag if action == "4" else repo.delete_remote_tag)(tag)
                    success(f"Deleted {scope} tag: {tag}")
                except GitError as exc:
                    warning(f"Could not delete {scope} tag {tag}: {exc}")
            else:
                warning("Delete cancelled. No changes were made.")
    elif action == "6":
        print(f"  Local tag : {'present' if item.get('local') else 'absent'}")
        print(f"  Remote tag: {'present' if item.get('remote') else 'absent'}")
        print(f"  Release   : {'present' if release else 'absent'}")
    else:
        warning("Unknown choice. No changes were made.")


def release_manager(repo: GitRepo) -> None:
    """Browse a merged local/remote tag inventory and manage each selected tag."""
    while True:
        tags, issues = _release_tag_inventory(repo)
        print("  ◆ RELEASE & TAG MANAGER ◆")
        if not tags:
            warning("No tags found in the available sources.")
        else:
            for index, item in enumerate(tags, 1):
                sources = []
                if item.get("local"):
                    sources.append("LOCAL")
                if item.get("remote"):
                    sources.append("REMOTE")
                if item.get("release"):
                    sources.append("GITHUB RELEASE")
                print(f"  [{index}] {item['tag']}  •  {' + '.join(sources) if sources else 'SOURCE UNKNOWN'}")
        for issue in issues:
            warning(issue)
        print("  [R] Refresh tag list")
        print("  [0] Back")
        choice = input(color("\n  ❯ Choose tag: ", MAGENTA)).strip()
        if choice in {"", "0"}:
            return
        if choice.lower() == "r":
            continue
        if not choice.isdigit() or not (1 <= int(choice) <= len(tags)):
            warning("Invalid selection. No changes were made.")
            return
        _release_tag_details(repo, tags[int(choice) - 1])
        return


def undo_redo_manager(repo: GitRepo) -> None:
    """Interactive, conservative undo/redo utilities."""
    print("  [1] Undo last commit (creates a revert commit; safe for shared history)")
    print("  [2] Redo last undo (only when HEAD is a Revert commit)")
    print("  [3] Restore one file's unstaged tracked changes")
    print("  [0] Back")
    choice = input(color("\n  ❯ ", MAGENTA)).strip()
    if choice == "0" or not choice:
        _set_action_outcome("CANCELLED", "Returned to management menu; no recovery action performed")
        return
    if choice == "1":
        subject = repo.run("log", "-1", "--pretty=%s", check=False)
        if not subject:
            warning("No commit available to undo.")
            return
        print(f"  Latest commit: {subject}")
        warning("Undo creates a new revert commit; it does not erase history.")
        if confirm("Revert the latest commit?"):
            original = repo.undo_last_commit()
            success(f"Undo completed with a new revert commit. Reverted: {original}")
        else:
            warning("Undo cancelled. No changes were made.")
    elif choice == "2":
        subject = repo.run("log", "-1", "--pretty=%s", check=False)
        if not subject.lower().startswith("revert "):
            warning("Redo is available only when HEAD is the undo/revert commit.")
            return
        print(f"  Undo commit to reverse: {subject}")
        warning("Redo creates another commit; it does not rewrite history.")
        if confirm("Redo the last undo?"):
            reverted = repo.redo_last_undo()
            success(f"Redo completed by reverting: {reverted}")
        else:
            warning("Redo cancelled. No changes were made.")
    elif choice == "3":
        paths = repo.tracked_worktree_changes()
        if not paths:
            warning("No unstaged tracked file changes to restore. Staged and untracked files are left untouched.")
            return
        print("  Unstaged tracked changes:")
        for path in paths:
            print(f"    • {path}")
        selected = input("  Exact file path to restore (blank cancels): ").strip()
        if not selected:
            warning("Restore cancelled. No changes were made.")
            return
        if selected not in paths:
            warning("That file is not in the listed restore candidates. No changes were made.")
            return
        warning("This discards unstaged edits in the selected file. Staged and untracked files are untouched.")
        if confirm(f"Restore unstaged changes in {selected}?"):
            repo.restore_tracked_worktree_file(selected)
            success(f"Restored unstaged changes in {selected}")
        else:
            warning("Restore cancelled. No changes were made.")
    else:
        warning("Unknown choice. No changes were made.")


def force_sync(repo: GitRepo, yes: bool = False) -> None:
    warning("FORCE SYNC can discard local changes and untracked files.")
    if not yes and not confirm("Reset local branch to origin and delete untracked files?"):
        warning("Force sync cancelled. No changes were made.")
        return
    with spinner("Fetching origin"):
        repo.fetch()
    with spinner("Resetting local branch to origin"):
        repo.force_sync()
    success("Local branch synchronized with origin.")


def confirm(prompt: str) -> bool:
    return input(f"  {prompt} {color('[y/N]', DIM)} ").strip().lower() in {"y", "yes"}


COMMANDS = {"status", "scan", "pull", "push", "sync", "force-sync", "release", "release-manager", "undo-redo", "action-status"}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hikari", description="HIKARI/.LAB cyberpunk Git/GitHub workflow console.")
    p.add_argument("--path", type=Path, default=Path.cwd(), help="Project path (default: current directory)")
    sub = p.add_subparsers(dest="command")
    sub.add_parser("status")
    sub.add_parser("action-status", help="show live repository state and recent HIKARI actions")
    sub.add_parser("scan")
    sub.add_parser("pull")
    sub.add_parser("push")
    for name in ("sync", "force-sync"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--yes", action="store_true", help="Skip confirmation")
    sub.add_parser("release-manager", help="view and manage GitHub Releases and Git tags")
    sub.add_parser("undo-redo", help="safely undo commits, redo a revert, or restore unstaged file edits")
    rel = sub.add_parser("release")
    rel.add_argument("kind", nargs="?", choices=("patch", "minor", "major"), default="patch")
    rel.add_argument("--version", help="Explicit version, e.g. v1.2.3")
    rel.add_argument("--current", action="store_true", help="Release the version already declared by the project")
    rel.add_argument("--custom", action="store_true", help="Prompt for a custom target version")
    rel.add_argument("--yes", action="store_true", help="Skip confirmation")
    return p


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and not argv[0].startswith("-") and argv[0] not in COMMANDS:
        argv = ["--path", argv[0], *argv[1:]]
    args = parser().parse_args(argv)
    try:
        path = args.path.expanduser().resolve()
        try:
            repo: GitRepo | LocalProject = GitRepo(path)
        except GitError as exc:
            if not str(exc).startswith("not a Git repository"):
                raise
            repo = LocalProject(path)
            if args.command in {"pull", "push", "sync", "force-sync", "release", "release-manager", "undo-redo"}:
                raise GitError("this project is not a Git repository; initialize Git first")
        if not args.command:
            run_wizard(repo)
            return
        if args.command == "status":
            print(repo.status_text())
        elif args.command == "action-status":
            action_status(repo)
        elif args.command == "scan":
            print(repo.scan_text())
        elif args.command == "pull":
            repo.pull(); success("Changes pulled from remote.")
        elif args.command == "push":
            push_interactive(repo)
        elif args.command == "sync":
            sync(repo, args.yes)
        elif args.command == "force-sync":
            force_sync(repo, args.yes)
        elif args.command == "release-manager":
            release_manager(repo)
        elif args.command == "undo-redo":
            undo_redo_manager(repo)
        elif args.command == "release":
            version = args.version
            if version is None and not args.current and not args.custom:
                local_current, _ = repo.local_version()
                version = next_version(local_current or "v0.0.0", args.kind)
            release_interactive(repo, version=version, yes=args.yes, current=args.current, custom=args.custom)
    except (GitError, ValueError) as exc:
        error(str(exc))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
