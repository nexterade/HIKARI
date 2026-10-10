## 0.6.8 — Editable release notes drafts
- [x] Preview generated release notes before the release confirmation.
- [x] Edit multiline Markdown notes in the interactive release flow.
- [x] Save and reload per-project, per-version drafts outside the target repository.
- [x] Preserve generated-notes behavior for `--yes` and retain release safety guards.
- [x] Add regression coverage for persistence, isolation, edit/load/cancel, and empty drafts.

## 0.6.7 — Operation-specific outcome summaries
- [x] Record concrete result summaries for read-only STATUS, Git Guide, and Troubleshoot flows.
- [x] Route utility success/warning/error feedback through the active dashboard action tracker.
- [x] Replace generic fallback summaries with truthful “no change/result reported” details.
- [x] Add regression tests for utility feedback and read-only action summaries.

## 0.6.6 — Action outcome accuracy
- [x] Classify interactive action history as SUCCESS, FAILED, CANCELLED, or BLOCKED based on terminal operation feedback.
- [x] Add concise per-action result details, including cancellation reasons and Local Mode Git-readiness blocks.
- [x] Track local utility success/warning feedback without persisting command output or credentials.
- [x] Add regression tests for classification, bounded summaries, Local Mode blocking, and submenu cancellation.

## 0.6.5 — Real Git integration and artifact lineage gate
- [x] Exercise remote tag presence, absence, and deletion against a disposable local bare Git remote.
- [x] Verify real Git remote command failure is not treated as tag absence.
- [x] Extend exact-artifact preflight to check current version in boot/continuation snapshots and release manifest/changelog lineage.
- [ ] Run authenticated GitHub smoke tests when `gh` and a disposable authenticated repository are available.


## 0.6.4 — Release Manager remote-state safety
- [x] Distinguish remote tag absence from remote query failure; fail closed before remote tag deletion when origin state is unknown.
- [x] Add regression coverage for remote lookup errors and deletion guard behavior.

# HIKARI/.LAB — Backlog

## 0.6.0 — Hybrid Dashboard + Full Operations
- [x] Combine target project context/path and live status in the dashboard screen.
- [x] (Historical milestone) Display the then-current operation IDs in one list with mobile-friendly wrapping; current dashboard has 12 top-level entries with nested submenus.
- [x] Add explicit separators between TARGET, DASHBOARD, and OPERATIONS layouts.
- [x] Preserve local-first behavior and read-only dashboard status inspection.


## Milestone 1 — MVP

- [x] Define project identity and scope.
- [x] Define architecture boundaries.
- [x] Define canonical test command.
- [x] Implement interactive wizard.
- [x] Implement repository status and file-change scan.
- [x] Implement pull and push.
- [x] Implement sync flow.
- [x] Implement guarded force sync.
- [x] Implement SemVer release flow.
- [x] Generate release description from project changelog.
- [x] Create GitHub Release through `gh`.
- [x] Add regression tests.
- [x] Sync documentation.

## Milestone 2 — Workflow polish

- [x] Support Local Mode before Git initialization.
- [x] Add local-first project version detection.
- [x] Make SYNC and RELEASE remote-aware.
- [x] Add smart PUSH with explicit commit+push choice.
- [x] Add project-aware `.gitignore` management.
- [x] Add semantic terminal color layer and contextual identity signature.
- [x] Clear operation logs before returning to the main wizard.
- [x] Clear stale dashboard/submenu output between category navigation steps.
- [x] Add conservative UNDO / REDO utility: revert-based commit undo, constrained redo, and confirmed single-file restore for unstaged tracked edits.
- [ ] Add configurable default branch/remote.
- [x] Add GitHub Repo menu to create a repository or connect an existing GitHub remote with explicit visibility/confirmation and no implicit push.
- [ ] Add `--dry-run` for every mutating operation.
- [x] Make PUSH/SYNC `auto` scan changed paths and project docs to derive a meaningful commit subject.
- [x] Discover project-specific changelog/history filenames recursively across all folders; select matching version content without privileging a fixed path.
- [x] Add hybrid RELEASE choices: quick next version, force current version, or custom version.
- [x] Refuse duplicate local/remote tags and duplicate GitHub Releases; fail closed when remote release state is unknown.
- [x] Add RELEASE MANAGER under menu 6 RELEASE & MANAGER to list/view/delete GitHub Releases and manage local/remote tags with explicit confirmation.
- [x] Cancel release safely when the working tree is dirty rather than silently committing unrelated changes.
- [ ] Add richer diff summary and rename detection.
- [x] Add unified STATUS with live repository state and recent per-project HIKARI action history outside the target repository.
- [x] Enrich STATUS/SCAN with file metadata, timestamps, sizes, location, inventory, and Git context.
- [x] Add beginner Git Guide menu and plain-language explanations for key operations.
- [x] Add Git HISTORY / LOG with commit metadata, tags, upstream and divergence counts.
- [x] Add read-only AUTO TROUBLESHOOT for common branch/remote/history problems with safe guidance.
- [ ] Add confirmed guided recovery actions after diagnosis, with backups and conflict handling.
- [x] Group the main console into category dashboard and contextual submenus.
- [x] Add contextual Git Readiness routing for Git-dependent actions in Local Mode and missing-remote guidance.
- [ ] Add richer per-category readiness checks for Git executable, repository root, branch, upstream, and remote reachability.
- [x] Add concise per-operation result summaries (what changed, what was skipped, and why) across PULL/PUSH/SYNC/RELEASE and utility actions.
- [x] Improve operation-specific outcomes so nested cancellations and handled errors are classified as CANCELLED/FAILED instead of generic FINISHED.
- [x] Add editable release notes preview/save flow with persistent drafts outside the target repository.
- [ ] Add GitHub issue/PR shortcuts.

## Repository profile metadata
- [x] Add opt-in deterministic About/Topics generation to menu 7 REPOSITORY new GitHub repository creation.
- [x] Preview suggestions and allow About editing before explicit repository-creation confirmation.
- [ ] Consider optional provider-neutral AI enhancement only behind a separate opt-in and privacy review.

## Milestone 3 — Optional intelligence

- [ ] Optional AI-generated release descriptions.
- [ ] Optional changelog generation.
- [ ] Optional PR description generation.
- [ ] Provider-neutral AI boundary.

## Out of scope

- Automatic merge to protected branches.
- Secret vault or credential management.
- Autonomous coding agent.
- Background daemon/webhook server.
- Silent destructive Git operations.



- [ ] Add optional arrow-key navigation after stable hybrid numeric/letter controls are validated across Termux terminals.
