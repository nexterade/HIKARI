# hikari — Continuation

## Current

HIKARI/.LAB 0.6.8 implements a standalone interactive wizard for both plain local projects and Git repositories.

## What works

- Local Mode and Git Mode
- local-first version detection
- status/scan
- pull/push with remote guards
- smart PUSH with explicit commit+push choice
- sync with safe no-remote behavior
- guarded force sync
- SemVer release with interactive release-note preview/edit/load/save; drafts persist per project/version outside the target repository
- CHANGELOG-derived release notes
- local release without remote
- GitHub Release through `gh` when a remote is configured
- RELEASE MANAGER to list/view/delete GitHub Releases and manage local/remote tags with explicit confirmation
- project-aware `.gitignore` menu and init-time skip for existing `.gitignore`
- semantic terminal colors and contextual `✦` identity
- conservative UNDO / REDO: revert commit, redo revert, confirmed single-file restore for unstaged tracked edits
- operation-log clearing
- STATUS action history with live repository state and bounded per-project action history stored outside target repo; new interactive records classify SUCCESS, FAILED, CANCELLED, or BLOCKED and include operation-specific result summaries, including utility results and read-only reports

## Next

1. Canonical tests and exact packaged artifact preflight are required for each release.
2. Perform a real Git/GitHub smoke test in a disposable repository with authenticated `gh` when the environment is available.
3. Consider configurable default branch/remote and dry-run support.

- GIT GUIDE explains Git/GitHub concepts in plain language and distinguishes commit/push/pull/Pull Request/tag/release.


Current navigation: HISTORY / LOG is nested under MANAGE (menu 9); read-only AUTO TROUBLESHOOT is menu 11. Troubleshooting must not mutate repository state automatically.


Latest UI update (0.5.6): five category dashboard with focused submenus; Local Mode Git-dependent selections route through explicit Git readiness guidance before INIT REPO.


Latest UI fix (0.5.6): automatically clear stale terminal output before dashboard and category submenu redraws to keep navigation clean on mobile terminals.


Implemented capability (0.6.2): menu 7 REPOSITORY offers an opt-in deterministic Repository Profile Generator for About/Topics when creating a new GitHub repository. It previews metadata derived from local README/pyproject, allows About editing, and retains separate default-N confirmations. No push is performed.


## Current dashboard mapping (2026-10)

The authoritative main dashboard now has 12 entries: 1 STATUS, 2 SCAN, 3 PULL, 4 PUSH, 5 SYNC (submenu: guided sync / FORCE SYNC), 6 RELEASE (submenu: create release / manage releases and tags), 7 REPOSITORY (submenu: initialize local Git / GitHub repo configuration), 8 .GITIGNORE, 9 MANAGE (submenu: UNDO/REDO / HISTORY/LOG), 10 GIT GUIDE, 11 TROUBLESHOOT, 12 MISCELLANEOUS. Older menu-number references elsewhere in this continuity file describe prior snapshots; use this mapping for the current implementation. High-risk operations retain explicit confirmation with default N.


## 0.6.8 artifact gate

Current package is `hikari-lab-v0.6.8.zip`. Canonical test command: `python3 -m unittest discover -s tests -v`; exact artifact must pass `python3 tests/release_preflight.py PATH_TO_ZIP`. Action history uses terminal outcomes SUCCESS, FAILED, CANCELLED, and BLOCKED, with concrete summaries for read-only and utility flows plus partial/skipped outcomes. Real Git integration tests use disposable local/bare repositories. Live authenticated GitHub smoke testing remains environment-dependent because `gh` is not installed in the current validation environment.


## 0.6.8 release-note draft flow
Interactive release preparation can use generated notes, edit multiline Markdown, load a saved project/version draft, or save the current draft under HIKARI home (`HIKARI_HOME` override). Draft operations do not mutate the target repository. `--yes` uses generated notes without interactive prompts.
