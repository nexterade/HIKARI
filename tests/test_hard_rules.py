import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from release_preflight import archive_path_present

ROOT = Path(__file__).resolve().parents[1]

class HardRuleTests(unittest.TestCase):
    def test_universal_hard_rules_are_present(self):
        text=(ROOT/"docs/CHECKPOINT.md").read_text(encoding="utf-8")
        for phrase in [
            "3.29.1 TEST DISCOVERY CONTRACT",
            "3.33.1 DATA CLASSIFICATION & PRIVACY BOUNDARY",
            "3.34.1 RAW IDEA → REQUIREMENT → PROMPT TRANSLATION",
            "3.34.2 KNOWLEDGE-SURFACE IMPACT CHECK",
            "Artifact Compliance Gate yang dapat dieksekusi",
            "ENCODING INTEGRITY WAJIB",
            "3.24 GLOSSARY AUTO-UPDATE — \"BUKU BESAR\" (STRICT!)",
            "MULTI-TAG CONTRACT — WAJIB DAN KETAT",
            "tepat 1 PRIMARY TAG",
            "maksimum = 4 tag",
            "Tag index bersifat INFORMASIONAL",
        ]:
            self.assertIn(phrase,text)

    def test_security_baseline_exists_and_contains_secret_boundary(self):
        text=(ROOT/"docs/SECURITY.md").read_text(encoding="utf-8")
        for phrase in ["Normal Data","Sensitive Data","Secret Data","Secret Vault","Encoding/Base64 bukan security boundary"]:
            self.assertIn(phrase,text)
        self.assertNotRegex(text,r"(?:sk-live-|ghp_|AKIA|-----BEGIN PRIVATE KEY-----)")

    def test_release_preflight_is_executable_contract(self):
        p=ROOT/"tests/release_preflight.py"
        text=p.read_text(encoding="utf-8")
        self.assertIn("unittest",text)
        self.assertIn("extract",text)
        self.assertIn("exact artifact",text.lower())

    def test_release_preflight_accepts_zip_without_directory_entries(self):
        files = {"src/hikari/cli.py", "tests/test_hikari.py"}
        self.assertTrue(archive_path_present("src", files))
        self.assertTrue(archive_path_present("tests", files))
        self.assertFalse(archive_path_present("docs", files))

    def test_glossary_encoding_guard(self):
        raw=(ROOT/"docs/Glosarium.html").read_bytes()
        decoded=raw.decode("utf-8")
        self.assertNotIn("�",decoded)
        self.assertNotRegex(decoded,r"[\u0080-\u009f]")
        self.assertNotRegex(decoded,r"(?:â|Â)[\x80-\xbf]")


if __name__ == "__main__":
    unittest.main()
