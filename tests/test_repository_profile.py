import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from hikari.profile import generate_repository_profile
from hikari.cli import github_repo_menu
from hikari.git import GitRepo


class RepositoryProfileTests(unittest.TestCase):
    def test_generates_description_and_relevant_topics_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "sample-tool"\ndescription = "Python CLI for Git workflow automation and backup management"\n',
                encoding="utf-8",
            )
            (root / "README.md").write_text("# Sample\n\nA command-line tool for Git workflows.\n", encoding="utf-8")
            result = generate_repository_profile(root)
        self.assertEqual(result["name"], "sample-tool")
        self.assertEqual(result["description"], "Python CLI for Git workflow automation and backup management")
        self.assertIn("python", result["topics"])
        self.assertIn("git", result["topics"])
        self.assertIn("automation", result["topics"])
        self.assertIn("backup", result["topics"])
        self.assertIn("no network/AI", result["source"])

    def test_fallback_description_and_topic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = generate_repository_profile(root)
        self.assertEqual(result["description"], f"Tools and workflow utilities for {root.name}.")
        self.assertEqual(result["topics"], ["developer-tools"])

    def test_menu_11_applies_generated_profile_without_pushing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "sample-tool"\ndescription = "Python CLI for Git workflow automation"\n',
                encoding="utf-8",
            )
            import subprocess
            subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
            repo = GitRepo(root)
            answers = iter(["1", "sample-tool", "2", "", ""])
            with patch("hikari.cli.input", side_effect=lambda *a, **k: next(answers)), \
                 patch("hikari.cli.confirm", side_effect=[True, True, True]), \
                 patch.object(repo, "run_gh", side_effect=["https://github.com/example/sample-tool", "", "", "", ""]) as run_gh:
                github_repo_menu(repo)
            create_call = run_gh.call_args_list[0].args
            self.assertIn("--description", create_call)
            self.assertIn("Python CLI for Git workflow automation", create_call)
            topic_calls = [call.args for call in run_gh.call_args_list[1:]]
            self.assertTrue(any("--add-topic" in call for call in topic_calls))
            self.assertFalse(any("push" in call for call in run_gh.call_args_list))

    def test_description_is_limited_to_github_length(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text('[project]\ndescription = "' + ('x' * 400) + '"\n', encoding="utf-8")
            result = generate_repository_profile(root)
        self.assertLessEqual(len(result["description"]), 300)


if __name__ == "__main__":
    unittest.main()
