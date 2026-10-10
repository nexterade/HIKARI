# Plan — HIKARI 0.6.8 Editable Release Notes Drafts

## Goal
Allow users to preview, edit, and persist release-note drafts for a target version without modifying the target repository or changing release safety guarantees.

## Impact
MEDIUM — interactive release workflow and data flow change; requires regression tests and synchronized release documentation.

## Scope
- Add per-project, per-version draft storage under HIKARI's home directory, outside the target repository; use a stable hash of the resolved project path to avoid collisions between projects.
- During interactive release preparation, offer a concise preview workflow to use generated notes, edit them, load an existing saved draft, save the current notes, or cancel.
- Collect edited notes line-by-line until a single `.` line; reject empty edited content and preserve multiline Markdown exactly apart from the terminal newline.
- Saved drafts are candidates for later release runs and do not publish, tag, commit, or push by themselves.
- Preserve existing behavior for non-interactive `--yes` releases; they must not unexpectedly prompt for draft editing.
- Keep release notes and draft content out of action history and logs. Never store credentials or command output.
- Update tests, version metadata, changelog, backlog, state, README/tutorial, boot/continuation snapshots, release manifest, and Creation Chronicle as appropriate. No glossary change unless terminology materially changes.

## Files/components
- `src/hikari/release.py`: safe draft path, load/save helpers, project isolation.
- `src/hikari/cli.py`: interactive preview/edit/save/load flow in release preparation.
- `tests/test_release.py`, `tests/test_release_modes.py`, and/or a focused `tests/test_release_drafts.py` discoverable by `unittest`.
- `tests/release_preflight.py`: current-plan and release lineage checks.
- Release/version continuity documents listed above.

## Data flow
1. Generate notes from the target project's changelog, falling back to commit-derived notes as today.
2. In interactive mode, show preview and offer use/edit/load/save/cancel options.
3. Save drafts under `$HIKARI_HOME/release-drafts/<project-hash>/<version>.md` (default `$HOME/.hikari/...`), never under the target repository.
4. Use the selected notes only after the existing explicit release confirmation; tagging/publishing safety guards remain unchanged.

## Edge cases
- Missing or unreadable draft directory: report a concise warning and continue without breaking release preparation.
- Missing saved draft: do not treat it as an error; keep generated notes available.
- Empty edit: reject and return to preview/options without overwriting a saved draft.
- Path/version isolation: same version in different projects must not collide; normalize version to a safe filename.
- Non-interactive `--yes`: preserve existing no-extra-prompt behavior and use generated notes.
- Working tree becoming dirty during preparation: retain the existing fail-safe cancellation.

## Acceptance criteria
- Users can preview generated notes, edit multiline Markdown, save a draft, and load a previously saved draft for the same project/version.
- Drafts persist across process runs and are stored outside the target repository.
- Draft editing/saving alone never creates a Git commit/tag, pushes, or publishes a GitHub Release.
- Existing release safety guards and `--yes` behavior remain intact.
- Focused tests and the canonical `python3 -m unittest discover -s tests -v` suite pass.
- Final flat-root ZIP passes `python3 tests/release_preflight.py PATH_TO_ZIP` against the exact delivered artifact.
- Version and release metadata consistently identify 0.6.8; GitHub smoke testing remains explicitly pending if `gh`/credentials are unavailable.

## Test plan
1. Unit-test draft save/load, project/version isolation, empty content, and filesystem errors.
2. Test interactive editing and loading paths with mocked input; assert no release mutation occurs before confirmation.
3. Run the canonical unittest suite.
4. Package the flat-root ZIP without caches and run the exact-artifact preflight, which must run the canonical suite after extraction.
5. Record only observed test and packaging outcomes in the release manifest.
