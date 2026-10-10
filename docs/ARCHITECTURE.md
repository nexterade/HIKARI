# HIKARI/.LAB — Architecture

## Identity

- Project: `hikari-lab`
- Runtime: Python 3.10+
- Interface: interactive CLI wizard + command mode
- Git provider: Git via subprocess
- GitHub integration: GitHub CLI (`gh`) via subprocess
- Storage: no application database; target project files and Git remain authoritative

## Architecture decision

HIKARI is a thin orchestration layer that can operate before Git is initialized. It has two runtime states:

```text
LocalProject
    |
    +-- local version detection
    +-- local file/project scan
    +-- project-aware .gitignore
    +-- offline utilities
    |
    +-- init_repo() --> GitRepo
                         |
                         +-- status / scan
                         +-- pull / push / sync
                         +-- guarded force-sync
                         +-- SemVer release
                         +-- GitHub Release via gh
```

Git remains authoritative once initialized. A missing `origin` is valid Git state, not an application error; operations that require a remote explicitly guard against it.

## Boundaries

### Core/domain

- command routing
- Local Mode vs Git Mode detection
- confirmation policy
- semantic terminal presentation
- local version detection
- release version calculation
- changelog-based release-note extraction
- project-aware `.gitignore` generation

### Integration

`src/hikari/git.py` is the boundary for Git process execution and project filesystem inspection relevant to repository workflows.

`gh` is invoked only for GitHub-specific release operations. HIKARI does not store GitHub credentials.

## Source of truth

1. Target project files and `.git` state — authoritative local project/repository state.
2. GitHub remote — authoritative remote/release state when configured.
3. `CHANGELOG.md` — authoritative project release-note source for HIKARI releases.
4. HIKARI output — derived operational view.
5. `docs/STATE.md`, `PROJECT_STATE.json`, and boot/continuation files — operational documentation aids; they must reflect the implementation but do not outrank the implementation or CHECKPOINT governance.

## Remote-aware operation contract

- `PULL`, `PUSH`, and `FORCE SYNC` require both Git and `origin`.
- `SYNC` may operate locally when `origin` is absent and must never blindly push to a missing remote.
- `PUSH` detects uncommitted changes and offers an explicit commit+push path; it does not silently create commits.
- `RELEASE` can produce a local commit/tag without a remote. GitHub publication is skipped when no remote exists.

## Release strategy

SemVer is used for application releases. Project version detection is local-first and prefers structured manifests (`pyproject.toml`, `package.json`, `VERSION`, `version.txt`, `PROJECT_STATE.json`) before narrative files.

Release notes come from the target project's `CHANGELOG.md` or `docs/CHANGELOG.md`. Exact target-version headings win over `Unreleased`.

## .gitignore strategy

The `.GITIGNORE` menu generates recommendations from the detected project stack. Existing `.gitignore` files are preserved by default; replacement is an explicit user action. `INIT REPO` skips generation when an existing project `.gitignore` is present.

## UI strategy

Semantic color helpers keep presentation rules centralized. Color falls back to plain text for non-TTY, `NO_COLOR`, or `TERM=dumb`. The identity signature `✦` is contextual rather than a suffix on every line. Operation output is cleared before returning to the main wizard.

## Security/trust boundary

`git` and `gh` remain external trusted executables. HIKARI never persists credentials. Confirmation is required for destructive operations. Secret material must not enter source, logs, documentation, fixtures, or release artifacts.

## Change policy

Behavior changes require regression tests. Changes to Git/GitHub operation semantics are MEDIUM impact at minimum because they affect external state. Destructive behavior is HIGH impact and requires explicit tests and documentation review.


## Undo / Redo boundary (0.4.9)

Undo/Redo is intentionally history-preserving: commit undo creates a revert commit; redo is allowed only when HEAD is itself a revert commit and reverses that revert with another commit. Both require a clean working tree. File restoration is limited to a listed tracked path with unstaged changes and does not discard staged or untracked files. All destructive choices are explicitly confirmed by the interactive UI.


## Category dashboard and readiness routing (0.5.5)

The UI presents five top-level categories and returns existing operation IDs to the dispatcher, minimizing risk to operation implementations. Readiness checks are contextual UI gates: Local Mode users are informed before a Git-dependent action and can route to the explicit local initialization flow; missing remotes are explained before remote-dependent actions proceed. No remote is created and no file is uploaded by readiness routing.


## Automatic navigation screen clearing (0.5.6)

`ui.menu()` clears the visible terminal before drawing the main category dashboard and each category submenu, avoiding accumulated prompts/logs on mobile terminal sessions. Clearing is guarded by TTY detection in `clear_screen()`.
