"""Shared filesystem scanning policy for HIKARI/.LAB."""

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build", ".next", "vendor", "target", ".idea", ".vscode",
}
