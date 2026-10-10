import ast
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = ROOT / "docs/Glosarium.html"
MANIFEST = ROOT / "tests/glossary_entry_manifest.json"

def load_entries():
    text = GLOSSARY.read_text(encoding="utf-8")
    match = re.search(r"const entries\s*=\s*(\[.*?\]);", text, re.S)
    if not match:
        raise AssertionError("canonical glossary entries array not found")
    return ast.literal_eval(match.group(1))

class GlossaryTests(unittest.TestCase):
    def test_glossary_utf8_and_mojibake_guard(self):
        text = GLOSSARY.read_text(encoding="utf-8")
        self.assertNotIn("�", text)
        self.assertNotRegex(text, r"[\u0080-\u009f]")
        self.assertNotRegex(text, r"(?:â|Â)[\x80-\xbf]")

    def test_all_entries_preserved_with_provenance(self):
        entries = load_entries()
        self.assertEqual(len(entries), 107)
        self.assertEqual(sum(e[4] == "inherited" for e in entries), 93)
        self.assertEqual(sum(e[4] == "adapted" for e in entries), 7)
        self.assertEqual(sum(e[4] == "native" for e in entries), 7)
        self.assertTrue(all(len(e) == 7 for e in entries))

    def test_entry_manifest_prevents_silent_loss(self):
        entries = load_entries()
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual([e[0] for e in entries], expected)

    def test_pernah_glossary_template_contract(self):
        text = GLOSSARY.read_text(encoding="utf-8")
        for marker in [
            'aria-label="Project Genesis navigation"',
            'GENESIS',
            'id="tagIndex"',
            'id="alphabet"',
            'id="themeToggle"',
            'id="print"',
            'id="sidebarToggle"',
            'class="letter-group"',
            'const highlight',
            'tag-chip',
            'tag-index-item',
            'prefers-reduced-motion',
        ]:
            self.assertIn(marker, text)
        self.assertNotIn("fonts.googleapis.com", text)
        self.assertNotIn("fonts.cdnfonts.com", text)
        self.assertNotIn("musicDock", text)
        self.assertNotIn("youtube.com/embed", text)
        self.assertNotIn('id="categories"', text)

    def test_pernah_favicon_contract(self):
        html = GLOSSARY.read_text(encoding="utf-8")
        favicon = (ROOT / "favicon.svg").read_text(encoding="utf-8")
        self.assertIn('href="../favicon.svg"', html)
        self.assertIn('<svg', favicon)
        self.assertIn('PERNAH Continuity P', favicon)

    def test_book_besar_multitag_contract(self):
        entries = load_entries()
        for entry in entries:
            self.assertEqual(len(entry), 7)
            tags = entry[6]
            self.assertGreaterEqual(len(tags), 1)
            self.assertLessEqual(len(tags), 4)
            self.assertEqual(len(tags), len(set(tags)), entry[0])
            self.assertTrue(all(isinstance(tag, str) and tag.strip() for tag in tags), entry[0])
            self.assertEqual(tags[0], tags[0].strip(), entry[0])
            self.assertLessEqual(max(len(tag) for tag in tags), 40)

    def test_book_besar_tag_manifest_is_exact(self):
        entries = load_entries()
        expected = json.loads((ROOT / "tests/glossary_tag_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([[e[0], e[6]] for e in entries], expected)

    def test_book_besar_search_contract_includes_tags(self):
        text = (GLOSSARY.read_text(encoding="utf-8"))
        self.assertIn("e.join(' ').toLocaleLowerCase()", text)
        self.assertIn('e[6].forEach', text)


if __name__ == "__main__":
    unittest.main()
