import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContinuityTemplateTests(unittest.TestCase):
    def test_required_boot_files_exist(self):
        required = [
            "PROJECT_BOOT.md",
            "PROJECT_STATE.json",
            "PROJECT_CONTINUATION.md",
            "PROJECT_CONTINUATION_PROMPT.md",
            "docs/CHECKPOINT.md",
            "docs/STATE.md",
            "docs/BACKLOG.md",
            "docs/CHANGELOG.md",
            "docs/ARCHITECTURE.md",
            "docs/TUTORIAL.md",
            "docs/RELEASE-MANIFEST.md",
            "docs/Glosarium.html",
            "docs/Creation-Chronicle.html",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_machine_state_is_valid(self):
        data = json.loads((ROOT / "PROJECT_STATE.json").read_text(encoding="utf-8"))
        self.assertTrue(data["continuity_layer"]["chat_is_ephemeral"])
        self.assertTrue(data["continuity_layer"]["artifact_is_continuous"])

    def test_checkpoint_contains_core_continuity_rules(self):
        text = (ROOT / "docs/CHECKPOINT.md").read_text(encoding="utf-8")
        self.assertIn("CHAT IS EPHEMERAL. ARTIFACT IS CONTINUOUS.", text)
        self.assertIn("PROJECT_BOOT", text)
        self.assertIn("CREATION CHRONICLE + GLOSARIUM (WAJIB)", text)
        self.assertIn("CO-DEVELOPER", text)
        self.assertIn("COST-AWARE / RESOURCE-AWARE", text)


if __name__ == "__main__":
    unittest.main()
