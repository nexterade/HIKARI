# HIKARI/.LAB — Release Manifest

## Current artifact

- Project: `hikari-lab`
- Display identity: `HIKARI/.LAB`
- Version: `0.6.8`
- Artifact: `hikari-lab-v0.6.8.zip`
- Canonical test command: `python3 -m unittest discover -s tests -v`
- Canonical test result: **111 unittest tests passed** against the exact extracted artifact.
- Exact ZIP preflight: **PASS** against `hikari-lab-v0.6.8.zip`.
- Hosted GitHub Actions execution and real GitHub publication remain environment-dependent.

## 0.6.8 change note

- Interactive RELEASE supports preview, multiline editing, loading saved notes, and saving a draft for the target project/version.
- Drafts are stored under HIKARI home (`HIKARI_HOME` override) outside the target repository; draft operations alone do not mutate Git state.
- Non-interactive `--yes` uses generated notes without opening draft prompts; existing release safety checks remain active.
- Regression tests cover persistence, project/version isolation, empty draft rejection, and interactive edit/load/cancel flows.
- Canonical suite and exact-artifact preflight are required on the exact packaged ZIP; authenticated GitHub smoke testing remains environment-dependent.

## 0.6.7 change note

- Read-only STATUS, Git Guide, and Troubleshoot flows record specific result summaries.
- Local utility success/warning/error feedback is captured by the same action tracker used by Git workflows.
- Generic fallback summaries are replaced with truthful no-change/no-result details; partial success and skipped remote publication remain visible.
- Regression tests cover utility success/warning/error propagation and read-only STATUS history.
- Canonical tests and exact-artifact preflight were finalized after packaging; authenticated GitHub smoke testing remained environment-dependent because `gh` was unavailable.

## 0.6.6 change note

- New interactive action-history records use `SUCCESS`, `FAILED`, `CANCELLED`, or `BLOCKED`, based on operation feedback rather than generic `FINISHED`.
- Concise action details summarize results or explain why an operation was skipped/blocked/cancelled.
- Outcome tracking spans interactive CLI flows and local utilities while keeping bounded history outside the target repository and excluding command output/credentials.
- Regression tests cover status classification, detail bounds, Local Mode blocking, and submenu cancellation.
- The final packaged ZIP was validated by the executable Artifact Compliance Gate after extraction; canonical suite: **101 tests passed**.
- Authenticated GitHub smoke test was not run: `gh` is not installed in this environment.

## 0.6.4 change note

- Remote tag lookup now uses checked `git ls-remote --tags --refs`; command failures surface as errors rather than being misreported as a missing tag.
- Remote tag deletion stops before the destructive push if remote state cannot be verified.
- Regression coverage includes unknown remote state, no destructive push on verification failure, and confirmed absence after a successful lookup.
- Canonical suite: 94 unittest tests passed. Exact-artifact preflight and test results are run again after packaging.
- Authenticated GitHub smoke testing was not performed; this release validates failure handling with local mocks and repository fixtures.

## 0.6.3 change note

- Release Manager refresh is iterative rather than recursive.
- Documentation/continuity snapshots now consistently describe the 12-operation dashboard and implemented 0.6.2 features.
- Regression tests cover refresh and default-N cancellation of destructive tag actions.

## Dashboard refactor note

The hybrid dashboard presents the target project path, live local Git health, context-aware next-step guidance, and all 12 contiguous operation IDs. The values are read from local state; no implicit fetch or mutation occurs during dashboard rendering.

## Origin and scope

HIKARI/.LAB is a standalone Python 3.10+ CLI for safety-first local-project and Git/GitHub workflow automation. It operates on a user-selected target project and does not persist GitHub credentials.

## Included implementation

- Interactive Local Mode and Git Mode
- Local-first project version detection and file scan
- Guarded pull, smart push, sync, and force-sync workflows
- Hybrid SemVer release modes (quick/current/custom), guarded tag publication, changelog-derived release notes, and Release Manager nested under menu 6 RELEASE for inspecting/deleting releases and managing tags; unified STATUS with project inventory and recent action history; Undo/Redo utility for revert-based undo, constrained redo, and guarded per-file restore
- Optional GitHub Release creation through the installed `gh` executable
- Project-aware `.gitignore` support and offline utilities
- Semantic terminal presentation and contextual identity signature
- Canonical unittest suite and exact-artifact release preflight
- Project continuity documentation, security baseline, glossary, and Creation Chronicle

## Validation contract

- Canonical tests: `python3 -m unittest discover -s tests -v`
- Exact artifact gate: `python3 tests/release_preflight.py PATH_TO_ZIP`
- ZIP must be flat-rooted, include required source/docs/tests, exclude generated caches, and pass the full test suite after extraction.
- Real Git/GitHub smoke tests are environment-dependent and must use a disposable repository.
- Final SHA-256 must refer to the exact delivered ZIP and is recorded outside the archive.

## Historical validation results for 0.4.9

- Canonical suite: 31 tests passed locally.
- Exact ZIP preflight: pending final package validation.
- Real GitHub publication smoke test is environment-dependent and must use a disposable repository.

## Preserved glossary lineage

The glossary retains its existing 107-entry payload and provenance metadata. Its inherited/adapted/native knowledge content and presentation-template lineage are preserved as an intentional documentation payload; they do not redefine HIKARI's product identity, runtime architecture, or implementation scope. Changes to that knowledge payload require the glossary manifest tests to remain exact.

## Historical 0.4.4 delta

- Corrected ZIP preflight handling for archives without explicit directory entries.
- Replaced stale starter release metadata with HIKARI/.LAB release lineage.
- Synchronized version metadata and continuation state to 0.4.4.
- Recorded the validation repair in CHANGELOG and Creation Chronicle.


## Historical 0.4.4 delta

- Added a dedicated GITHUB REPO menu to create a GitHub repository or connect an existing GitHub URL.
- Repository creation requires explicit visibility and confirmation and does not push project files.
- Canonical tests: 22 tests passed in local suite; real GitHub creation remains unverified without authenticated `gh`.


## 0.4.7 delta

- Added quick/current/custom release choices and CLI flags.
- Refused duplicate local/remote tags and existing GitHub Releases.
- Prevented silent commits of dirty working trees during release.
- Canonical tests and exact-artifact preflight must pass on the final ZIP.


## 0.4.9 delta

- Added Release Manager for listing/viewing GitHub Releases, deleting release objects separately from tags, and explicitly confirmed local/remote tag deletion.
- Revalidate canonical tests and exact ZIP preflight before delivery.


## 0.4.9 delta

- Added menu option 13 and `hikari undo-redo`.
- Undo uses `git revert` to preserve shared history; redo is limited to a current HEAD revert commit.
- Single-file restore only targets explicitly listed unstaged changes in tracked files.
- Commit undo/redo requires a clean working tree.
- Validation: rerun canonical tests and exact-artifact preflight before delivery; remote smoke testing remains environment-dependent.


## 0.5.0 delta

- Added ACTION STATUS menu and CLI command with live repository state and a bounded per-project action history stored outside the target repository.
- Canonical tests and exact-artifact preflight must pass on the final ZIP. Real GitHub smoke testing remains environment-dependent.


## 0.5.4 delta

- Added menu 14 GIT GUIDE with beginner-friendly explanations of commit, push, pull, Pull Request, branch, remote, tag, release, clone, merge, and .gitignore.
- Improved plain-language main-menu descriptions and inline safety/meaning explanations for PULL, PUSH, SYNC, RELEASE, and FORCE SYNC.
- Updated onboarding/tutorial/state/changelog and machine-readable version metadata.

## 0.5.2 delta

- Expanded STATUS and SCAN with project location, scan timestamp, inventory counts and size, latest modified file/time, file-type mix, and largest files.
- Git STATUS/SCAN include branch, remote/upstream, version, last commit, change counts and paths where applicable.
- Added regression coverage for Local and Git SCAN metadata.

## 0.5.1 delta

- Unified live repository/project health and recent action history under menu 1 STATUS; removed the dedicated ACTION STATUS menu entry.
- Retained the `action-status` CLI command as a compatibility alias.
- Canonical tests and exact ZIP preflight must pass on the final ZIP.


## 0.5.2 — Informative Status & Scan
- STATUS includes richer project inventory and action history.
- SCAN reports local timestamp, location, sizes, latest modified file, extension mix, largest files, and Git change context.

## 0.5.4 — Beginner-friendly Git Guide
- Menu 14 explains Git/GitHub concepts and how to choose HIKARI operations safely.


## v0.5.4 delta
- Git commit/tag history and upstream divergence display.
- Read-only automatic diagnosis for dirty worktree, missing remote/upstream, ahead/behind, divergence, and unrelated histories.


## 0.5.5 delta

- Reorganized the interactive dashboard into five categories and contextual submenus while retaining operation dispatch IDs.
- Added Git Readiness guidance for Local Mode and missing remote configuration.
- Validation: canonical tests and exact ZIP preflight must pass on final artifact; real GitHub smoke test remains environment-dependent.

## 0.5.8 delta

- Replaced letter-only category navigation with numeric categories 1–5 and 0 for exit.
- Submenus use existing numeric operation IDs; B returns and X exits, eliminating collisions with operation shortcuts.
- Retained screen clearing and banner redraw. Canonical suite passed (49 tests).


## 0.5.8
- Hybrid navigation: numeric category/operation IDs, B back, X/0 exit; banner and auto-clear retained.
- Persistent banner and numeric category/operation choices with alphabetic back/exit controls.


## 0.6.0 remediation delta

- Centralized version resolution for package, CLI, and banner; aligned current state and UI documentation.
- Standardized the simple/advanced dashboard contract and migrated legacy UI expectations.
- Added a unittest adapter so legacy function-level tests execute under the canonical stdlib runner; renamed the LocalProject transition test accurately and made the local-version/tag test create a real Git tag.
- Centralized filesystem exclusions and hardened symlink handling in inventory/changelog scans.
- Unified local version detection; improved release race handling, action-history warnings, GitHub repo-name validation, origin replacement, rclone command construction, and SQLite identifier quoting.
- Added GitHub Actions matrix coverage for Python 3.10, 3.11, and 3.12 plus tag-triggered exact-artifact preflight.


## Implemented in 0.6.2 — Repository Profile Generator

- Menu 11 GITHUB REPO can generate a local deterministic About description and Topics during new repository creation.
- Profile is previewed; About may be edited; generator and GitHub creation each retain default-N confirmation.
- About is passed to `gh repo create`; Topics are applied after creation. No project files are pushed.
- Canonical suite at the 0.6.2 artifact: 89 unittest tests passed against the exact extracted ZIP.
- Live authenticated GitHub smoke test: not run in this environment.


## Implemented in 0.6.2 — Release Hub validation note

- Menu 6 now combines release creation and Release Manager actions. The dashboard contains 12 contiguous operations; Release Manager is nested under RELEASE, History/Log is nested under MANAGE, and Troubleshoot is operation 11.
- Fixed GitHub release listing to request only supported `gh` JSON fields; the unsupported `url` field is no longer requested.
- The 0.6.2 exact artifact passed its packaged preflight and 89-test suite. No authenticated GitHub smoke test was performed.


## Implemented in 0.6.2 — Dashboard consolidation

The current working artifact groups 12 main-menu operations. Release Manager is nested under RELEASE; Force Sync under SYNC; repository initialization and GitHub setup under REPOSITORY; Undo/Redo and History/Log under MANAGE. Version 0.6.2 synchronized documentation/metadata; version 0.6.3 fixes iterative refresh behavior and continuity-document drift.
