"""Run legacy pytest-style test functions under the canonical stdlib unittest runner."""
import importlib
import inspect
import tempfile
import unittest
from pathlib import Path


class _MonkeyPatch:
    def __init__(self):
        self._undo = []

    def setattr(self, target, name, value=None):
        if isinstance(target, str):
            module_name, attr = target.rsplit(".", 1)
            if value is None:
                value, name = name, attr
            target = importlib.import_module(module_name)
            name = attr
        old = getattr(target, name)
        self._undo.append((target, name, old))
        setattr(target, name, value)

    def undo(self):
        for target, name, old in reversed(self._undo):
            setattr(target, name, old)


class LegacyFunctionTests(unittest.TestCase):
    pass


def _make_test(module_name, function_name):
    def run(self):
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        signature = inspect.signature(function)
        with tempfile.TemporaryDirectory() as tmp:
            args = []
            monkeypatch = _MonkeyPatch()
            try:
                for parameter in signature.parameters:
                    if parameter == "tmp_path":
                        args.append(Path(tmp))
                    elif parameter == "monkeypatch":
                        args.append(monkeypatch)
                    else:
                        self.fail(f"Unsupported fixture {parameter!r} in {module_name}.{function_name}")
                function(*args)
            finally:
                monkeypatch.undo()
    run.__name__ = f"test_{module_name}_{function_name.removeprefix('test_')}"
    run.__doc__ = f"Adapter for {module_name}.{function_name}."
    return run


for _module_name in (
    "test_local_mode", "test_local_version", "test_release",
    "test_auto_commit_message", "test_identity",
):
    _module = importlib.import_module(_module_name)
    for _name, _function in vars(_module).items():
        if _name.startswith("test_") and inspect.isfunction(_function):
            setattr(LegacyFunctionTests, f"test_{_module_name}_{_name.removeprefix('test_')}", _make_test(_module_name, _name))
