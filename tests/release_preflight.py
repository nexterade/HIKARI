#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "VERSION", "README.md", "PROJECT_BOOT.md", "PROJECT_CONTINUATION.md",
    "PROJECT_CONTINUATION_PROMPT.md", "PROJECT_STATE.json", "docs/CHECKPOINT.md",
    "docs/STATE.md", "docs/BACKLOG.md", "docs/CHANGELOG.md", "docs/ARCHITECTURE.md",
    "docs/TUTORIAL.md", "docs/RELEASE-MANIFEST.md", "docs/SECURITY.md",
    "docs/Creation-Chronicle.html", "docs/Glosarium.html", "docs/PLAN-v0.6.8.md",
    "src/hikari/action_tracking.py", "tests", "src",
}

def fail(msg):
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def archive_path_present(path, files):
    if path in files:
        return True
    if path in {"src", "tests"}:
        prefix = path.rstrip("/") + "/"
        return any(name.startswith(prefix) for name in files)
    return False

def main():
    if len(sys.argv) != 2:
        fail("usage: python3 tests/release_preflight.py PATH_TO_ZIP")
    artifact = Path(sys.argv[1]).resolve()
    if not artifact.is_file():
        fail(f"artifact not found: {artifact}")
    with zipfile.ZipFile(artifact) as zf:
        files = {n.rstrip("/") for n in zf.namelist() if n}
        version = zf.read("VERSION").decode("utf-8").strip() if "VERSION" in files else None
        if not version:
            fail("VERSION missing or empty")
        missing = sorted(x for x in REQUIRED if not archive_path_present(x, files))
        if missing:
            fail("required files missing: " + ", ".join(missing))
        top = {n.split("/", 1)[0] for n in files}
        if artifact.stem in top or any(n.startswith(artifact.stem + "/") for n in files):
            fail("archive has an enclosing wrapper directory; flat-root contract violated")
        if any("__pycache__/" in n or n.endswith((".pyc", ".pyo")) or n == ".pytest_cache" or n.startswith(".pytest_cache/") for n in files):
            fail("generated test/runtime cache artifact found in ZIP")
        checkpoint = zf.read("docs/CHECKPOINT.md").decode("utf-8")
        pyproject = zf.read("pyproject.toml").decode("utf-8")
        readme = zf.read("README.md").decode("utf-8")
        state = zf.read("docs/STATE.md").decode("utf-8")
        project_state = json.loads(zf.read("PROJECT_STATE.json").decode("utf-8"))
        pyproject_match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', pyproject, re.MULTILINE)
        readme_match = re.search(r'^\*\*Version `([^`]+)`\*\*', readme, re.MULTILINE)
        state_match = re.search(r'^- Version: `([^`]+)`$', state, re.MULTILINE)
        if not pyproject_match or pyproject_match.group(1) != version:
            fail("VERSION and pyproject.toml version disagree")
        if not readme_match or readme_match.group(1) != version:
            fail("VERSION and README version disagree")
        if not state_match or state_match.group(1) != version:
            fail("VERSION and docs/STATE.md version disagree")
        if project_state.get("version") != version:
            fail("VERSION and PROJECT_STATE.json version disagree")
        boot = zf.read("PROJECT_BOOT.md").decode("utf-8")
        continuation = zf.read("PROJECT_CONTINUATION.md").decode("utf-8")
        manifest = zf.read("docs/RELEASE-MANIFEST.md").decode("utf-8")
        changelog = zf.read("docs/CHANGELOG.md").decode("utf-8")
        for label, content in (("PROJECT_BOOT.md", boot), ("PROJECT_CONTINUATION.md", continuation)):
            if not re.search(rf"(?im)^##?\s+(?:Current version|Current|HIKARI/.LAB)\b[^\n]*\n(?:[^\n]*\n){{0,2}}[^\n]*\b{re.escape(version)}\b", content):
                if version not in content:
                    fail(f"VERSION {version} missing from {label}")
        if f"Version: `{version}`" not in manifest:
            fail("VERSION and docs/RELEASE-MANIFEST.md disagree")
        if f"hikari-lab-v{version}.zip" not in manifest:
            fail("release manifest artifact filename does not match VERSION")
        if version == "0.6.8" and not re.search(r"Canonical test result: \*\*\d+ unittest tests passed\*\* against the exact extracted artifact\.", manifest):
            fail("release manifest is missing the exact-artifact canonical test result")
        if version == "0.6.8" and f"Exact ZIP preflight: **PASS** against `hikari-lab-v{version}.zip`" not in manifest:
            fail("release manifest is missing the exact-artifact preflight result")
        if not re.search(rf"(?m)^##\s+{re.escape(version)}\b", changelog):
            fail("docs/CHANGELOG.md has no current-version entry")
        if "12 menu dashboard hybrid" not in readme.lower() or "16 menu dashboard hybrid" in readme.lower():
            fail("README dashboard title/anchor does not match the current 12-operation dashboard")
        action_tracking = zf.read("src/hikari/action_tracking.py").decode("utf-8")
        cli_source = zf.read("src/hikari/cli.py").decode("utf-8")
        for status in ("SUCCESS", "FAILED", "CANCELLED", "BLOCKED"):
            if status not in action_tracking:
                fail(f"action outcome tracker is missing status: {status}")
        if '"FAILED" if action_failed else "FINISHED"' in cli_source:
            fail("interactive action history still uses generic FINISHED outcomes")
        if "Riwayat hasil aksi" not in readme or "hasil konkret" not in readme:
            fail("README is missing the action-history outcome contract")
        for phrase in [
            "TEST DISCOVERY CONTRACT", "DATA CLASSIFICATION & PRIVACY BOUNDARY",
            "RAW IDEA → REQUIREMENT → PROMPT TRANSLATION",
            "KNOWLEDGE-SURFACE IMPACT CHECK", "Artifact Compliance Gate",
        ]:
            if phrase not in checkpoint:
                fail(f"CHECKPOINT missing required hard rule: {phrase}")
    with tempfile.TemporaryDirectory(prefix="genesis-release-preflight-") as td:
        extract = Path(td) / "artifact"; extract.mkdir()
        with zipfile.ZipFile(artifact) as zf: zf.extractall(extract)
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=extract, text=True,
        )
        if result.returncode:
            fail("full test suite failed against exact extracted artifact")
    print(f"PASS: exact artifact validated ({version})")

if __name__ == "__main__":
    main()
