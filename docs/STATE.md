# 0.6.8 — Editable Release Notes Drafts

- Interactive RELEASE supports previewing, editing, loading, and saving multiline Markdown notes for a target version.
- Drafts are stored per resolved project and version under HIKARI home (or `HIKARI_HOME`), outside the target repository.
- Draft editing/saving does not commit, tag, push, or publish; the existing release confirmation and clean-working-tree/duplicate-tag guards remain in force.
- `--yes` retains the generated-notes path without interactive draft prompts.
- Regression coverage verifies draft persistence, project/version isolation, empty-draft rejection, edit/load/cancel flows, and clean target repository state.
- Authenticated GitHub smoke testing remains environment-dependent and is not claimed unless performed.

## Identity

- Project name: `hikari-lab`
- Display identity: `HIKARI/.LAB`
- Version: `0.6.8`
- Status: hybrid target + live-status dashboard with full 12-operation interactive CLI, outcome-accurate action history, beginner Git guide, Git history/log, and read-only auto troubleshooting
- Runtime: Python 3.10+
- Milestone: workflow polish / hybrid local-Git mode

## Current implementation

Implemented a standalone Python CLI that can manage both plain local project folders and Git repositories. The wizard supports status/scan, pull, smart push, sync, guarded force-sync, SemVer release, changelog-derived release notes with editable/persisted per-project drafts outside the target repository, GitHub Release creation and Release Manager nested under menu 6 RELEASE (list/view/delete GitHub Releases; list/delete local tags; delete remote tags with confirmation and fail-closed remote-state verification), Undo/Redo utility (revert-based commit undo, constrained redo, and per-file unstaged tracked-file restore), and unified STATUS (project inventory, Git state, and per-project recent-action history stored outside the target repository) through `gh`/Git, project-aware `.gitignore` management, GitHub Repo configuration (create a repository or connect an existing GitHub URL without implicit push), opt-in deterministic Repository Profile Generator for About/Topics during new repo creation, offline/local utilities, semantic terminal colors, contextual `✦` branding, automatic dashboard/submenu output clearing, persistent banner redraw, explicit exit/back controls, and hybrid dashboard navigation with the complete 1–12 operation list.

New dashboard action records carry a terminal outcome (`SUCCESS`, `FAILED`, `CANCELLED`, or `BLOCKED`) and a concise operation result. Legacy `FINISHED` entries already present in a user's existing history are not rewritten retroactively.

Git is optional at first launch. A local project can be initialized into Git without being uploaded. Git operations that require `origin` explicitly guard against a missing remote. The GitHub Repo menu requires local Git initialization before creating a remote, asks for visibility and confirmation, and never pushes project files as part of repository creation.

## Documentation invariants

- Existing project `.gitignore` is preserved automatically.
- Release notes discover changelog/history files by filename semantics across the entire project tree, without assuming a fixed folder; commit-message `auto` summarizes working-tree changes and consults project documentation.
- Version display is sourced from local project metadata.
- `PUSH` never silently commits; dirty-tree PUSH offers an explicit commit+push choice.
- `SYNC` and `RELEASE` remain safe when no remote is configured.
- Action history remains bounded, stored outside the target repository, and excludes command output and credentials.

## Current next gate

Run the canonical suite and executable Artifact Compliance Gate against the exact packaged ZIP. Authenticated GitHub smoke testing remains environment-dependent until `gh` and a disposable authenticated GitHub repository are available. History/log and troubleshooting are read-only; recovery actions remain user-confirmed.

## Source of truth

1. `docs/CHECKPOINT.md` — universal governance.
2. Source/configuration + target project state — implementation reality.
3. `docs/STATE.md` — current implementation state.
4. `docs/BACKLOG.md` — planned work.
5. `docs/ARCHITECTURE.md` — architecture and boundaries.
6. `README.md` / `docs/TUTORIAL.md` — user-facing behavior.
7. `docs/SECURITY.md` — security/privacy baseline.
8. `docs/CHANGELOG.md` — historical changes.

## 0.6.1 — Backup Restore Workflow (historical)

- Added restore workflow to Miscellaneous → Backup Rotator.
- Restore validates ZIP paths, previews overwrite count, and requires typing RESTORE.

# 0.6.0 — Hybrid Dashboard + Full Operations

The hybrid dashboard now keeps an explicit TARGET panel (project name and absolute path) and a read-only live snapshot in Git Mode: active branch, working-tree cleanliness, categorized changed-path counts, remote, upstream ahead/behind counts, last commit, and a context-aware suggested next step. Local Mode explains version detection and keeps the local-only safety boundary visible. All 12 operation IDs are visible at once, and each major layout (TARGET, DASHBOARD, OPERATIONS) is separated by a horizontal rule. Target context is rendered inside the screen that owns the dashboard, so it is not erased by screen clearing. The snapshot is derived from local Git state at menu entry; it does not fetch or mutate remote state. Operation IDs 1–12 are contiguous; all are visible in the main dashboard.

## Historical 0.5.10 — Simple/Advanced Dashboard

The v0.5.10 dashboard used `M` to toggle advanced tools. That navigation was replaced in v0.6.0 by a full operation list; the current implementation consolidates those historical operations into 12 top-level entries with nested submenus.

## 0.5.3 — Beginner-friendly Git Guide

Menu 13 explains core Git/GitHub concepts in plain language. Main-menu descriptions and operation preambles distinguish commit/push/pull/Pull Request/tag/release and warn about destructive FORCE SYNC.

## 0.5.2 — Informative Status & Scan

STATUS and SCAN now expose project location, local timestamp, inventory size/counts, latest modified file/time, extension mix, and largest files; Git SCAN adds branch, remote, version, last commit, change totals, and changed paths. Main-menu target context remains shared across all operations.

## 0.5.1 — Unified Status

Menu 1 STATUS now combines live project/repository health with recent HIKARI action history. The separate ACTION STATUS menu entry was removed to keep the console compact. The `action-status` CLI alias remains for compatibility.
