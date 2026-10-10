# HIKARI Simple/Advanced Dashboard

The default dashboard is an operational project overview, not only a list of actions.

## Live project health

In Git Mode, the dashboard reports the active branch, working-tree cleanliness, categorized changed paths, configured remote, upstream ahead/behind counts when an upstream is configured, and the last commit. A short next-step hint is derived from the observed state. The dashboard does not fetch from a remote, and therefore does not claim fresh remote state unless the local remote-tracking refs have been updated by the user.

In Local Mode, it reports the detected project version when available, explains that Git is optional, and keeps the local-only boundary explicit.

## Navigation and safety

- Beginner-friendly task labels are shown by default.
- `M` toggles **Show More — Advanced Tools** in-place; `0` exits.
- Existing internal operation IDs and dispatch paths remain unchanged.
- Advanced actions may alter history or discard work; their existing confirmation prompts remain in place.
- The health snapshot is read-only. Remote divergence is based on locally available upstream refs.
- Output adapts menu descriptions to terminal width. Extremely narrow terminals may still wrap long project paths or Git commit subjects.

## Validation

The live snapshot is covered by `tests/test_dashboard_clear.py`. Run `python3 -m unittest discover -s tests -v` before packaging.
