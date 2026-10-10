## 0.6.8 — Editable Release Notes Drafts

- Add an interactive release-notes preview flow with options to edit multiline Markdown, load a saved draft, save the current draft, use the current notes, or cancel.
- Persist drafts per project path and target version under HIKARI home (or `HIKARI_HOME`), outside the target repository.
- Keep draft editing/saving separate from Git mutations; existing release confirmation, dirty-tree, duplicate-tag, and remote-state guards remain active.
- Preserve non-interactive `--yes` behavior by using generated notes without opening draft prompts.
- Add regression tests for persistence, project/version isolation, empty drafts, interactive edit/load/cancel flows, and repository cleanliness.

## 0.6.7 — Operation-specific outcome summaries

- Record concrete summaries for read-only STATUS, Git Guide, and Troubleshoot actions instead of generic completion details.
- Route local utility success/warning/error feedback through the active action-history tracker so the selected utility's result is recorded.
- Replace generic fallback details with truthful summaries when a submenu returns without making a change or reporting a result.
- Preserve partial success and skipped remote-publication context while keeping history bounded and free of command output/credentials.
- Add regression tests for utility-result propagation and read-only STATUS summaries.

## 0.6.6 — Outcome-accurate action history

- Replace generic `FINISHED` results for new interactive dashboard actions with `SUCCESS`, `FAILED`, `CANCELLED`, or `BLOCKED` based on terminal operation feedback.
- Record concise per-action summaries, including explicit cancellation/back navigation and Git-readiness blocks in Local Mode.
- Share outcome tracking with local utilities while preserving bounded, privacy-conscious history outside the target repository.
- Add regression tests for outcome classification, summary length, Local Mode blocking, and submenu cancellation.
- Exact-artifact validation is required after packaging; authenticated GitHub smoke testing remains environment-dependent because `gh` is not installed here.

## 0.6.5 — Real Git integration and artifact lineage checks

- Add integration coverage against real temporary Git repositories and a local bare remote for remote tag lookup, confirmed absence, deletion, and unreachable remote failure.
- Strengthen exact ZIP preflight to validate version and artifact lineage in continuation snapshots, release manifest, and current changelog entry.
- Validation runs against the exact extracted artifact; authenticated GitHub smoke testing remains unavailable when `gh` is not installed.

## 0.6.4 — Fail-closed remote tag verification

- Make remote tag existence checks distinguish a successful empty result (tag absent) from a failed remote query (state unknown).
- Raise an explicit GitError when no origin is configured or remote tag state cannot be verified; remote-tag deletion does not proceed after verification errors.
- Add regression tests for remote lookup failures, guarded deletion, and confirmed tag absence.
- Canonical standard-library unittest suite: 94 tests passed locally; exact packaged artifact gate is recorded in the release manifest.

## 0.6.3 — Release Manager refresh safety and continuity repair

- Replace recursive tag-list refresh with an iterative loop so repeated refreshes do not grow the Python call stack.
- Correct stale dashboard references and README anchors to the current 12-operation layout.
- Reclassify implemented 0.6.2 capabilities as implemented instead of leaving them marked Unreleased.
- Add regression coverage for refresh behavior and cancellation of destructive tag actions.
- Runtime change is limited to Release Manager refresh navigation; Git/GitHub operations and deletion semantics are unchanged.

## 0.6.2 — Release State and Documentation Synchronization

- Synchronize the current project state, boot snapshots, tutorial, and release manifest with the implemented 12-operation dashboard.
- Record the Release Manager as nested under RELEASE and keep repository profile generation and backup restore represented in current-state documentation.
- Correct stale validation metadata: the canonical standard-library unittest suite contains 89 tests; no pytest run or authenticated live GitHub smoke test is claimed.
- Documentation/metadata-only patch; no runtime behavior changed.

## 0.6.2 — Hybrid Dashboard polish

- Reworked Release Manager to browse merged local and remote tags, inspect selected tag details, and run tag-specific management actions.
- Change the main operation list to the compact `OPERATIONS / 12 MODULES` layout with aligned labels and one-line descriptions.
- Shorten dashboard descriptions; detailed explanations remain in the corresponding operation/submenu and Git Guide.
- Rename the visible menu-12 label to `MISC` while preserving the existing operation ID and behavior.
- Correct the numeric prompt to `Choose operation [0–12]` and update dashboard rendering tests.

## 0.6.2 — Unified Release Hub and GitHub CLI compatibility
- Fold Release Manager actions into dashboard menu 6, RELEASE & MANAGER; remove its separate top-level entry.
- This was an intermediate mapping; the later 12-operation dashboard nests Undo/Redo and History/Log under MANAGE.
- Stop requesting unsupported `url` from `gh release list --json`; display available release metadata without assuming that field.
- Preserve the direct `release-manager` CLI command as a compatibility alias and keep destructive confirmations default-N.

## 0.6.1 — Backup restore workflow

- Add an explicit Restore Backup action to Backup Rotator.
- List available project ZIP backups, choose an archive and destination, preview overwrite count, and require typed confirmation.
- Validate archive paths before extracting to prevent path traversal.

# Changelog

## 0.6.2 — Repository Profile Generator
- Add an opt-in, deterministic profile generator to menu 11 GITHUB REPO creation flow.
- Preview and optionally edit About text and review suggested Topics before repository creation.
- Apply About during `gh repo create`, then add Topics through GitHub CLI; report topic-application failures without hiding successful repository creation.
- Keep generation and repository creation behind separate `[y/N]` confirmations; no implicit push and no external AI/network analysis.
- Add regression tests for metadata extraction, fallback behavior, and description length.


## 0.6.0 — Runtime version precedence fix
### Fixed
- Source checkouts now resolve the displayed HIKARI version from the root `VERSION` file before consulting installed package metadata.
- Prevented stale globally installed `hikari-lab` metadata from overriding the hybrid dashboard checkout version.
- Added regression coverage for source-first version resolution and installed-metadata fallback.


## 0.6.0 — Hybrid Dashboard + Full Operations
### Added
- Combine the live project-health dashboard and explicit TARGET project/path in one persistent screen.
- Show all 15 operation IDs together, with consistent separators around Target, Dashboard, and Operations layouts.
- Pass the active target path and read-only status snapshot into the menu after screen redraw, preventing target context from being cleared before display.
### Changed
- Restore the complete numbered operations console while retaining beginner-friendly descriptions and local/Git safety guidance.
- Bump the project version to 0.6.0 across runtime metadata and documentation.


## 0.6.2 — Dashboard Information Density
- Replace the configuration-only snapshot with live Git health: branch, working-tree state, categorized changes, upstream divergence, last commit, and next-step guidance.
- Make Local Mode dashboard explain version detection and the local-only boundary.
- Add regression coverage for rendering the live health snapshot while preserving existing menu operation IDs.

## 0.5.10 — Consistency & Safety Remediation
- Resolve package, CLI, and banner versions through one shared version resolver with a source-tree `VERSION` fallback.
- Align tests and documentation with the simple/advanced dashboard (`M` toggles advanced tools; `0` exits).
- Centralize scan exclusions, skip symlinks during inventory/changelog discovery, and unify local version detection.
- Report action-history persistence failures once per process without blocking Git operations.
- Validate GitHub repository names, add confirmed origin URL replacement, fix rclone command argument types, and consolidate SQLite identifier quoting.
- Add Python 3.10–3.12 GitHub Actions test workflow.

0.5.8 — Hybrid Numeric/Letter Navigation

- Dashboard categories use 1–5 and 0 exits; submenus show stable numeric operation IDs.
- B consistently returns one level and X exits HIKARI, avoiding shortcut collisions such as B being both an operation and Back.
- Keep the banner, auto-clear behavior, and internal operation IDs intact.

## 0.5.8 — Persistent Banner, Exit & Letter Navigation

- Restore HIKARI banner after each screen clear so identity remains visible.
- Add explicit X/Q exit controls and B back navigation.
- Replace numeric category/submenu selection with hybrid numeric/letter navigation while preserving stable internal operation IDs.

## 0.5.6 — Auto-clear Dashboard History

- Clear stale terminal output before repainting the dashboard and category submenu, preventing navigation logs from piling up on mobile terminals.
- Keep the active category visible with a compact HIKARI header after clearing.
- Add regression coverage for screen clearing across category/submenu navigation.

## 0.5.5 — Category Dashboard & Git Readiness

- Reorganized the main console into five categories with contextual submenus while preserving internal operation IDs.
- Added a Git Readiness prompt when users choose Git-dependent actions from Local Mode; it routes to local INIT REPO only after explicit selection and explains that initialization does not upload files.
- Added clearer guidance when remote-dependent operations are selected without a configured remote.
- Kept diagnosis read-only and destructive Git actions behind existing confirmation flows.

## 0.5.4 — Git History & Auto Troubleshoot

- Added HISTORY / LOG menu with recent commits, authors, dates, tags, upstream and ahead/behind context.
- Added read-only AUTO TROUBLESHOOT for dirty trees, missing remotes/upstreams, divergence, behind/ahead states, and potentially unrelated histories.
- Troubleshooting gives safe next steps and explicitly avoids automatic merge/reset/rebase/force-push.

## 0.5.3 — Beginner-friendly Git Guide

### Added
- Added menu 14 — GIT GUIDE, a plain-language reference for commit, push, pull, Pull Request, branch, remote, tag, release, clone, merge, and .gitignore.
- Added clearer operation descriptions to the main menu and explanations before PULL, PUSH, SYNC, RELEASE, and high-risk FORCE SYNC.
- Clarified that commit saves locally, push publishes saved commits, Pull Request proposes a review/merge, and a Git tag differs from a GitHub Release.
- Updated onboarding docs and release metadata for v0.5.3.

## 0.5.2 — Informative Status & Scan

### Changed
- Expanded STATUS context with location, scan timestamp, inventory counts/size, latest file modification, detected version, Git state, and recent action history.
- Expanded SCAN in both Local and Git modes with scan time, location, directory/file counts, total size, latest modified file/time, file-type distribution, largest files, Git branch/remote/version/last commit, change counts, and changed paths.
- Added shared project inventory helpers that skip common dependency and VCS directories.
- Audited top-level operations for context; target panel already supplies project/path/branch/remote/version, while operation-specific confirmations and requirements remain in each flow.

## 0.5.1 — Unified Status

### Changed
- Integrated recent HIKARI action history into menu 1 — STATUS; removed the separate ACTION STATUS menu entry.
- STATUS now presents repository/project health together with recent action records in one place.
- Kept the `action-status` CLI command as a backward-compatible alias; the interactive menu uses STATUS as the single entry point.

## 0.5.0 — Action Status visibility

- Added menu option 14 / `hikari action-status` for live branch, remote, upstream, working-tree, ahead/behind, version, and last-commit status.
- Added a bounded per-project action history outside the target repository; records timestamps, action labels, coarse status, and short safe details only (no command output or credentials).
- Kept the status log best-effort so logging failures cannot block Git workflows.

# Changelog

## 0.6.2 — Dashboard Information Density
- Replace the configuration-only snapshot with live Git health: branch, working-tree state, categorized changes, upstream divergence, last commit, and next-step guidance.
- Make Local Mode dashboard explain version detection and the local-only boundary.
- Add regression coverage for rendering the live health snapshot while preserving existing menu operation IDs.

## 0.4.4 — GitHub repository configuration

- Add a dedicated GITHUB REPO menu to create a new GitHub repository or connect an existing GitHub URL.
- Require explicit visibility and confirmation for repository creation.
- Keep repository creation separate from pushing project files.
- Update project state and tutorial documentation.


## 0.4.3 — Artifact validation and continuity repair

- Fixed release preflight to recognize required `src/` and `tests/` contents in ZIP archives that omit explicit directory entries.
- Repaired the release manifest and Creation Chronicle so release lineage reflects HIKARI/.LAB rather than the unrelated starter artifact.
- Bumped the project patch version consistently across package metadata and continuity snapshots.

## 0.4.2 — Hybrid project workflow

- Added Local Mode so HIKARI can manage a project before Git initialization.
- Added local-first version detection from project metadata and documentation.
- Added remote guards for PUSH, SYNC, and RELEASE when `origin` is absent.
- Added smart PUSH with explicit `Commit changes + push` or `Push existing commits only` choices.
- Added changelog-derived release notes from the target project's `CHANGELOG.md` or `docs/CHANGELOG.md`.
- Added project-aware `.gitignore` management with preview and safe replacement confirmation.
- Existing project `.gitignore` files are preserved and automatically skipped during repository initialization.
- Added semantic terminal colors with non-color fallback and contextual `✦` branding.
- Added operation-log clearing before returning to the main wizard.
- Kept HIKARI standalone: the tool operates on an external target project.


## 0.4.0 — HIKARI Utility Hybrid

- Added native **Miscellaneous** utility lab to the HIKARI console.
- Hybridized the useful YookAI/Semut utilities without coupling HIKARI to the YookAI runtime:
  - Tree Printer
  - Ghost Grep
  - File Hasher
  - Backup Rotator
  - Sync Helper
  - Sync Remote (rclone)
  - ColorNote Exporter (SQLite → Markdown + HTML)
- Utility output is stored outside the working project by default (`~/.hikari`).
- Main Git/GitHub wizard remains standalone and keeps its single identity banner.

HIKARI/.LAB — Changelog

## 0.3.0 — HIKARI/.LAB rebrand
- Rebranded the project to **HIKARI/.LAB** (`光`, light).
- Renamed the standalone command from `hikari` to `hikari`.
- Established the public brand as a developer automation laboratory.
- Kept the cyberpunk repository-control console direction.

## 0.2.0 — Cyberpunk console
- Added interactive cyberpunk terminal presentation.
- Added operation spinners and clearer repository target information.
- Added safer force-sync confirmation.
- Added release notes derived from commit history.

## 0.1.0 — MVP
- Defined the safety-first GitHub workflow automation CLI.
- Added status, scan, pull, push, sync, force-sync, and release operations.

## 0.4.5

### Added
- Auto commit messages summarize actual changed paths and scan project documentation for context.
- RELEASE discovers changelog files in root, `docs/`, and nested folders; exact version entries take precedence over `Unreleased`.

### Fixed
- Release notes no longer depend on changelog being at project root or only in `docs/`.

## 0.4.6

### Fixed
- Changelog discovery no longer assumes root or `docs/` placement; it scans project-specific changelog/history/release-note filenames recursively and selects notes by version content.


## 0.4.6 — Guided release recovery and version consistency

### Added
- RELEASE falls back to a visible, commit-derived notes draft when no matching changelog entry exists.
- RELEASE identifies the draft source so users can review notes before confirming publication.

### Fixed
- Synchronize package metadata, CLI identity, and continuity metadata to VERSION 0.4.6.
- Ensure canonical unittest discovery can import the src-layout package in auto-commit tests.


## 0.4.7 — Hybrid release controls

### Added
- Interactive RELEASE choices: Quick Release, Force Release Current, and Custom Version.
- CLI flags `--current` and `--custom`; explicit `--version` remains available.

### Fixed
- RELEASE no longer stages or commits unrelated working-tree changes; dirty trees stop safely.
- Refuse existing local/remote tags and duplicate GitHub Releases.
- Fail closed when GitHub release state cannot be verified, and report success only after tag push and GitHub Release creation succeed.


## 0.4.8 — Release Manager

- Added a dedicated RELEASE MANAGER menu and `release-manager` CLI command.
- List and inspect GitHub Releases, delete a GitHub Release without implicitly deleting its tag, list local tags, and delete local/remote tags as separate confirmed actions.
- Added regression coverage for the command and local-tag deletion.


## 0.4.9 — Undo / Redo utility

- Added `UNDO / REDO` main-menu utility and `hikari undo-redo` command.
- Undo uses a new revert commit rather than rewriting branch history.
- Redo reverses only an immediately preceding revert commit and also preserves history.
- Added per-file restore for unstaged tracked changes, with candidate listing, path validation, and explicit confirmation; staged and untracked files are not touched.
- Commit undo/redo refuses to run with a dirty working tree.


## 0.6.2 — Dashboard navigation consolidation

- Consolidated the dashboard from 15 entries to 12: SYNC now contains guided sync and FORCE SYNC; RELEASE contains release creation and release/tag management; REPOSITORY contains local Git initialization and GitHub repository setup; MANAGE contains Undo/Redo and History/Log.
- Reordered GIT GUIDE, TROUBLESHOOT, and MISCELLANEOUS to match the requested dashboard layout.
- Updated menu selection ranges, action history labels, README menu reference, and menu-related regression tests.
- Preserved high-risk confirmation defaults (`N`) and kept force sync separate from guided sync.


## 0.6.2 — Landscape and terminal-width resilience
- Make the HIKARI identity banner adapt to narrow terminal widths instead of overflowing fixed box art.
- Keep the dashboard in one predictable column in portrait and landscape; cap content width and wrap long project paths, change summaries, and commit subjects.
- Add regression coverage for narrow/wide terminal width and long dashboard fields.
