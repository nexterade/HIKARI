import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class RuntimeVersionPrecedenceTests(unittest.TestCase):
    def _load_resolver(self, root: Path):
        package = root / "src" / "hikari"
        package.mkdir(parents=True, exist_ok=True)
        module_file = package / "_version.py"
        source_file = Path(__file__).resolve().parents[1] / "src" / "hikari" / "_version.py"
        spec = importlib.util.spec_from_file_location("hikari_version_test", source_file)
        module = importlib.util.module_from_spec(spec)
        exec(compile(source_file.read_text(encoding="utf-8"), str(module_file), "exec"), module.__dict__)
        module.__file__ = str(module_file)
        return module

    def test_source_checkout_version_wins_over_stale_installed_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "VERSION").write_text("0.6.0\n", encoding="utf-8")
            module = self._load_resolver(root)
            with patch.object(module, "metadata_version", return_value="0.5.11"):
                self.assertEqual(module.get_version(), "0.6.0")

    def test_installed_metadata_is_fallback_when_source_version_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            module = self._load_resolver(root)
            with patch.object(module, "metadata_version", return_value="0.6.0"):
                self.assertEqual(module.get_version(), "0.6.0")
