

def test_build_changelog_notes_finds_nested_changelog(tmp_path):
    from hikari.release import build_changelog_notes
    changelog = tmp_path / "docs" / "CHANGELOG.md"
    changelog.parent.mkdir(parents=True)
    changelog.write_text("# Changelog\n\n## v1.2.4\n\n- Added KAMUSORA export flow\n", encoding="utf-8")
    assert "Added KAMUSORA export flow" in build_changelog_notes(tmp_path, "v1.2.4")


def test_build_changelog_notes_prefers_exact_version_to_unreleased(tmp_path):
    from hikari.release import build_changelog_notes
    (tmp_path / "CHANGELOG.md").write_text("## Unreleased\n\n- Future work\n", encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "CHANGELOG.md").write_text("## v1.2.4\n\n- Released change\n", encoding="utf-8")
    assert "Released change" in build_changelog_notes(tmp_path, "v1.2.4")
    assert "Future work" not in build_changelog_notes(tmp_path, "v1.2.4")


def test_build_changelog_notes_discovers_project_specific_location(tmp_path):
    from hikari.release import build_changelog_notes
    custom = tmp_path / "project-meta" / "version-history.rst"
    custom.parent.mkdir(parents=True)
    custom.write_text("## v2.3.1\n\n- Project-specific release note\n", encoding="utf-8")
    assert "Project-specific release note" in build_changelog_notes(tmp_path, "v2.3.1")


def test_changelog_discovery_does_not_privilege_docs_folder(tmp_path):
    from hikari.release import build_changelog_notes
    from hikari.git import find_changelogs
    docs = tmp_path / "docs" / "CHANGELOG.md"
    docs.parent.mkdir(parents=True)
    docs.write_text("## Unreleased\n\n- Future docs change\n", encoding="utf-8")
    custom = tmp_path / "project-meta" / "release-notes.txt"
    custom.parent.mkdir(parents=True)
    custom.write_text("## v2.3.1\n\n- Correct versioned note\n", encoding="utf-8")
    candidates = find_changelogs(tmp_path)
    assert custom in candidates
    assert "Correct versioned note" in build_changelog_notes(tmp_path, "v2.3.1")
