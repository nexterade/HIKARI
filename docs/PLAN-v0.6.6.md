# Plan — HIKARI 0.6.6 Action Outcome Accuracy

## Goal
Replace coarse `FINISHED` history records for interactive dashboard actions with outcomes derived from the operation's terminal result and a concise, privacy-conscious summary.

## Scope
- `src/hikari/cli.py`: active-action result context, safe wrappers around existing terminal success/warning/error output, explicit summaries for read-only actions and Git readiness blocks, and explicit back/cancel results in top-level hubs.
- `tests/test_action_status.py`: status-classification and wizard integration regression tests.
- `docs/BACKLOG.md`, `docs/STATE.md`, `docs/CHANGELOG.md`, `README.md`, boot/continuation snapshots, `PROJECT_STATE.json`, `docs/Creation-Chronicle.html`, `docs/RELEASE-MANIFEST.md`: version and behavior synchronization.
- `tests/release_preflight.py`: require the current action-outcome contract in the release docs if appropriate.

## Data flow
A per-interactive-action ContextVar is initialized before dispatch. Existing `success`, `warning`, and `error` calls update the active result only while a dashboard action is running. The `finally` block records one terminal status/detail. Direct CLI invocations and utility flows outside the wizard keep their existing console behavior and do not create wizard history implicitly.

## Edge cases
- Nested submenu cancellation must not be recorded as successful completion.
- Git-dependent actions in Local Mode are BLOCKED, not SUCCESS.
- A follow-up failure after a partial success must not be hidden by the earlier success message.
- A local release tag may succeed even if remote publication is skipped; summarize the skip without falsely claiming the local operation failed.
- Unexpected exceptions must be recorded as FAILED and then re-raised.
- History remains bounded and stores no command output, credentials, or secret data.

## Acceptance criteria
- Dashboard history records only SUCCESS, FAILED, CANCELLED, or BLOCKED terminal outcomes, not generic FINISHED.
- Details summarize the operation result in at most the existing 180-character field.
- Explicitly canceled hub actions and Git-readiness blocks get correct statuses.
- Existing tests remain green and new regression tests are discovered by canonical unittest discovery.
- Documentation and exact packaged ZIP are version-consistent and pass `tests/release_preflight.py`.

## Test plan
Run focused action-status tests, the full canonical `python3 -m unittest discover -s tests -v` suite, build a flat-root ZIP, then run `python3 tests/release_preflight.py` against that exact ZIP. Real authenticated GitHub smoke testing remains a separate environment-dependent gate because `gh` is not available here.

## Knowledge-surface impact
CHRONICLE: record the material action-history behavior change. GLOSSARY: NONE; the four status labels are implementation states rather than a new project-governing vocabulary requiring a new dictionary entry.
