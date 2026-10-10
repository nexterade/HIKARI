# Plan — HIKARI 0.6.7 Operation-specific Outcome Summaries

## Goal
Make dashboard action history state what the selected operation actually accomplished, including utility results, read-only reports, partial success, and skipped steps. Avoid generic "inspect output" summaries when the terminal feedback already contains a meaningful result.

## Scope
- `src/hikari/action_tracking.py`: keep the current bounded/privacy-conscious outcome contract and ensure warning/success feedback preserves partial-result context.
- `src/hikari/cli.py`: add explicit concise summaries for read-only STATUS, GIT GUIDE, and TROUBLESHOOT flows; preserve specific results for PULL/PUSH/SYNC/RELEASE and repository/manage actions.
- `src/hikari/misc.py`: route utility success/warning/error feedback through the active action tracker without changing standalone utility behavior.
- `tests/test_action_status.py`: cover utility-result propagation, read-only summaries, partial success, and skipped remote publication.
- Version/document synchronization: README, PROJECT_BOOT, PROJECT_CONTINUATION, PROJECT_CONTINUATION_PROMPT, PROJECT_STATE.json, docs/STATE, BACKLOG, CHANGELOG, RELEASE-MANIFEST, Creation Chronicle, and release preflight contract.

## Safety constraints
- No change to Git operation ordering, confirmation prompts, default-N behavior, or remote guards.
- No command output, credentials, tokens, or full exception traces persisted in action history.
- History details remain capped at 180 characters and records remain bounded.
- A successful local operation with skipped remote publication stays SUCCESS with the skip explained; a failed follow-up after a real change must say partial success and identify the failed step.

## Acceptance criteria
- Dashboard action history has a useful concise result for STATUS, SCAN, Git Guide, Troubleshoot, and utility actions.
- PULL/PUSH/SYNC/RELEASE summaries identify the actual local/remote result, cancellation, or skip.
- Utility success and warning messages update the active dashboard action result without affecting direct utility calls.
- Regression tests cover utility feedback and partial success/skipped publication.
- Canonical tests and exact extracted ZIP preflight pass; release metadata is synchronized to 0.6.7.

## Test plan
1. Run focused action-status tests.
2. Run `python3 -m unittest discover -s tests -v`.
3. Package a flat-root ZIP without runtime caches.
4. Run `python3 tests/release_preflight.py PATH_TO_ZIP` against the exact final ZIP.
5. Keep authenticated live GitHub smoke testing explicitly pending unless `gh` and a disposable authenticated repository are available.

## Knowledge-surface impact
CHRONICLE: record operation-specific summary behavior. GLOSSARY: NONE; this is a behavior/implementation refinement and adds no project-governing terminology.
