"""Resolve HIKARI version without allowing stale installed metadata to override a checkout."""
from importlib.metadata import PackageNotFoundError, version as metadata_version
from pathlib import Path
import re


def _valid_version(value: str) -> bool:
    return bool(re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", value.strip()))


def get_version() -> str:
    # A source checkout is authoritative. This prevents an older globally installed
    # hikari-lab distribution from making a newer checkout display the old version.
    version_file = Path(__file__).resolve().parents[2] / "VERSION"
    try:
        source_version = version_file.read_text(encoding="utf-8").strip()
        if _valid_version(source_version):
            return source_version
    except OSError:
        pass

    # Installed-wheel fallback: VERSION may not be present outside a source checkout.
    try:
        installed_version = metadata_version("hikari-lab").strip()
        if _valid_version(installed_version):
            return installed_version
    except PackageNotFoundError:
        pass
    return "0+unknown"
