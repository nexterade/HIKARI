# hikari — Project Boot

## Identity

`hikari` is HIKARI/.LAB, a standalone safety-first CLI that automates repetitive Git/GitHub workflows for a local project path.

## Current version

`0.6.8`

## Current state

Workflow-polished implementation in `src/hikari/` with Local Mode + Git Mode, remote-aware operations, smart PUSH, hybrid quick/current/custom releases with guarded tags and Release Hub (menu 6), and project-aware `.gitignore`, conservative Undo/Redo utility, and STATUS action history with live repository state plus bounded recent-action history and outcome-accurate SUCCESS/FAILED/CANCELLED/BLOCKED summaries, editable and persistent release-note drafts stored outside the target repository, enriched STATUS/SCAN inventory, menu 10 Git Guide for beginners, menu 9 MANAGE (Undo/Redo + History/Log), menu 11 read-only AUTO TROUBLESHOOT, menu 12 MISC utilities, hybrid TARGET + live-status dashboard, compact aligned 12-module operations list, consistent layout separators, and contextual Git readiness routing.

## Canonical test

```bash
python3 -m unittest discover -s tests -v
```

## First read

1. `docs/CHECKPOINT.md`
2. `README.md`
3. `docs/STATE.md`
4. `docs/BACKLOG.md`
5. `docs/CHANGELOG.md`
6. `docs/ARCHITECTURE.md`
7. `docs/TUTORIAL.md`
8. `docs/SECURITY.md`
9. `docs/Creation-Chronicle.html`
10. `docs/Glosarium.html`

## Historical UI update — 0.5.6 Category Dashboard & Git Readiness

Historical note: earlier dashboard snapshots exposed Git Guide, History/Log, and Troubleshoot as separate menu IDs. The current mapping below is authoritative.


Latest UI update (0.5.6): five category dashboard with focused submenus; Local Mode Git-dependent selections route through explicit Git readiness guidance before INIT REPO.


Latest UI fix (0.5.6): automatically clear stale terminal output before dashboard and category submenu redraws to keep navigation clean on mobile terminals.


## Historical navigation note (0.5.10)
Dashboard categories use 1–5 and 0 exits. Submenus use stable numeric operation IDs, B returns one level, and X exits HIKARI. Banner is redrawn after screen clear.


## Current UI update — 0.6.0 Hybrid Dashboard + Full Operations

The initial screen combines the target project name/absolute path, live project health, and all 12 operations. TARGET, DASHBOARD, and OPERATIONS are rendered on one screen with explicit horizontal separators; status rendering is read-only.


## Current dashboard mapping (2026-10)

The authoritative main dashboard now has 12 entries: 1 STATUS, 2 SCAN, 3 PULL, 4 PUSH, 5 SYNC (submenu: guided sync / FORCE SYNC), 6 RELEASE (submenu: create release / manage releases and tags), 7 REPOSITORY (submenu: initialize local Git / GitHub repo configuration), 8 .GITIGNORE, 9 MANAGE (submenu: UNDO/REDO / HISTORY/LOG), 10 GIT GUIDE, 11 TROUBLESHOOT, 12 MISCELLANEOUS. Older menu-number references elsewhere in this continuity file describe prior snapshots; use this mapping for the current implementation. High-risk operations retain explicit confirmation with default N.


## Latest dashboard presentation update

The main dashboard uses `OPERATIONS / 12 MODULES`, a compact aligned one-line description for each menu, and the corrected `Choose operation [0–12]` prompt. Detailed instructions remain inside operation/submenus and Git Guide. Menu 12 is displayed as `MISC` without changing its internal selection ID or utility behavior.


## Latest terminal layout update
The dashboard uses a responsive, single-column renderer for portrait and landscape Termux. The banner compacts on narrow terminals; long paths/status values wrap to the measured width. No Git workflow semantics or menu IDs changed.


## Current action-history behavior — 0.6.7

New interactive action records use SUCCESS, FAILED, CANCELLED, or BLOCKED with operation-specific result details. Read-only reports and local utilities record their concrete result; partial success and skipped remote publication are summarized without storing command output or credentials. Git-required actions in Local Mode are BLOCKED; explicit cancellation and nested back navigation are not reported as generic completion.
