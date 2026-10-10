from __future__ import annotations

import os
import re
import shutil
import sys
import threading
import textwrap
import time
from contextlib import contextmanager
from ._version import get_version

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
ICE_BLUE = "\033[96m"
ARCTIC_DARK = "\033[38;5;24m"
DEEP_TEAL = "\033[38;5;30m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
IDENTITY = "✦"
_BANNER_VERSION = get_version()




def shutil_terminal_width() -> int:
    """Return a conservative terminal width for responsive mobile menus."""
    try:
        return max(24, shutil.get_terminal_size(fallback=(80, 24)).columns)
    except OSError:
        return 80


def clear_screen() -> None:
    """Clear the interactive terminal screen when running on a TTY."""
    if not sys.stdout.isatty():
        return
    # ANSI 2J clears the visible screen; 3J also clears terminal scrollback
    # where supported, preventing the previous operation log from piling up.
    print("\033[3J\033[H\033[2J", end="", flush=True)


def terminal_text(text: str) -> str:
    """Compatibility helper; identity is now used contextually, not per line."""
    return text


def color(text: str, code: str) -> str:
    """Apply a semantic terminal color when the terminal supports color."""
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb" or not sys.stdout.isatty():
        return text
    return f"{code}{text}{RESET}"


def accent(text: str) -> str:
    return color(text, CYAN)


def muted(text: str) -> str:
    return color(text, DIM)


def heading(text: str) -> str:
    return color(text, BOLD + CYAN)


def banner(version: str) -> None:
    """Render the console identity/header and remember it for screen redraws."""
    global _BANNER_VERSION
    _BANNER_VERSION = version
    print()
    width = shutil_terminal_width()
    title = "H I K A R I  / . L A B  //  LOCAL WORKSPACE"
    subtitle = f"v{version.lstrip('v')}  •  光  •  OFFLINE-FIRST  •  LOCAL + OPTIONAL GIT"
    # Fixed-width box art breaks on mobile landscape/portrait when terminal
    # column counts differ from the visible viewport. Use compact, unboxed
    # identity on narrow terminals and a width-safe banner elsewhere.
    if width < 68:
        print(color("HIKARI /.LAB // LOCAL WORKSPACE", BOLD + CYAN))
        print(color(subtitle, DIM))
    else:
        inner = min(width - 2, 76)
        title = title[:inner - 2]
        subtitle = subtitle[:inner - 2]
        print(color("╔" + "═" * inner + "╗", DEEP_TEAL))
        print(color("║", DEEP_TEAL) + color("  " + title, BOLD + CYAN) + " " * max(0, inner - len(title) - 2) + color("║", DEEP_TEAL))
        print(color("║", MAGENTA) + color("  " + subtitle, DIM) + " " * max(0, inner - len(subtitle) - 2) + color("║", DEEP_TEAL))
        print(color("╚" + "═" * inner + "╝", DEEP_TEAL))


def target(repo_name: str, root: str, branch: str, remote: str, version: str | None = None, version_source: str | None = None) -> None:
    """Render the current project target without duplicating the main banner."""
    print(color("┌─ TARGET", BLUE) + color("────────────────────────────────────────────────────", DIM))
    project_value = repo_name + (f"  {version}" if version else "")
    print(f"  {color('PROJECT', CYAN):<22} {project_value}")
    print(f"  {color('PATH', CYAN):<22} {root}")
    print(f"  {color('BRANCH', CYAN):<22} {branch}")
    print(f"  {color('REMOTE', CYAN):<22} {remote or '(none)'}")
    if version_source:
        print(f"  {color('VERSION SRC', CYAN):<22} {version_source} (local)")
    print(color("└────────────────────────────────────────────────────────────", DIM))

def menu(
    is_git: bool = True,
    has_remote: bool = True,
    snapshot: dict | None = None,
    target_context: dict | None = None,
) -> str:
    """Render the hybrid live-status dashboard and the complete operation list."""
    operations = [
        ("1", "STATUS", "Inspect project health"),
        ("2", "SCAN", "Review files and changes"),
        ("3", "PULL", "Get remote changes"),
        ("4", "PUSH", "Publish local commits"),
        ("5", "SYNC", "Reconcile local and remote"),
        ("6", "RELEASE", "Tags and GitHub releases"),
        ("7", "REPOSITORY", "Local init and GitHub"),
        ("8", ".GITIGNORE", "Manage ignore rules"),
        ("9", "MANAGE", "History and recovery"),
        ("10", "GIT GUIDE", "Learn Git and GitHub"),
        ("11", "TROUBLESHOOT", "Read-only diagnostics"),
        ("12", "MISC", "Local utilities"),
    ]
    snapshot = snapshot or {}
    context = target_context or {}
    # Keep a single predictable column in both orientations. A bounded content
    # width prevents landscape terminals from creating oversized lines and
    # leaves spare horizontal space instead of letting sections drift apart.
    width = max(24, min(shutil_terminal_width(), 88))
    rule = "─" * max(12, width - 2)

    while True:
        clear_screen()
        banner(_BANNER_VERSION)
        def field(label: str, value: object) -> None:
            prefix = f"│ {label:<13}: "
            available = max(8, width - len(prefix) - 1)
            chunks = textwrap.wrap(str(value), width=available, break_long_words=True,
                                   break_on_hyphens=False) or [""]
            print(prefix + chunks[0])
            for chunk in chunks[1:]:
                print("│ " + " " * (len(label) + 2) + "  " + chunk)

        print(color("┌─ TARGET PROJECT", CYAN))
        field("Project", context.get("name", "(not provided)"))
        field("Path", context.get("root", "(not provided)"))
        field("Branch", context.get("branch", "not inspected"))
        field("Remote", context.get("remote", "(none)") or "(none)")
        if context.get("version"):
            field("Version", f"{context['version']} ({context.get('version_source', 'local metadata')})")
        print(color("└" + rule, DIM))

        print(color("┌─ HIKARI DASHBOARD · HYBRID MODE / LIVE PROJECT STATUS", CYAN))
        field("Mode", "Git repository" if is_git else "LOCAL MODE · no Git required")
        if is_git:
            field("Working tree", snapshot.get("working_tree", "not inspected"))
            field("Changes", snapshot.get("changes", "not inspected"))
            field("Sync", snapshot.get("sync", "not checked"))
            field("Last commit", snapshot.get("last_commit", "not inspected"))
        else:
            field("Version", snapshot.get("version", "not detected"))
            field("Files", snapshot.get("files", "use SCAN for inventory"))
            field("Safety", "local-only; nothing is uploaded automatically")
        if snapshot.get("next_step"):
            field("NEXT", snapshot["next_step"])
        print(color("└" + rule, DIM))

        print(color("┌─ OPERATIONS / 12 MODULES", CYAN))
        label_width = max(len(label) for _, label, _ in operations)
        for key, label, description in operations:
            label_cell = f"{key.rjust(2)} {label:<{label_width}}"
            prefix_plain = f"│ {label_cell}  · "
            available = max(12, width - len(prefix_plain) - 2)
            wrapped = textwrap.wrap(description, width=available, break_long_words=False) or [""]
            print(f"{color('│', CYAN)} {color(key.rjust(2), MAGENTA)} {color(label.ljust(label_width), BOLD + WHITE)}  {color('·', DIM)} {color(wrapped[0], DIM)}")
            continuation_indent = "│ " + " " * (label_width + 5)
            for continuation in wrapped[1:]:
                print(f"{continuation_indent}{color(continuation, DIM)}")
        print(color("└" + rule, DIM))
        print("  0  EXIT HIKARI")
        selected = input(color("\n❯ Choose operation [0–12]: ", CYAN)).strip().upper()
        if selected in {"0", "X", "Q"}:
            return "0"
        chosen = next((item for item in operations if item[0] == selected), None)
        if not chosen:
            warning("Choose an operation from 1–12, or 0 to exit.")
            input("  Press ENTER to continue...")
            continue
        if selected in {"3", "4", "5", "6", "9", "11"} and not is_git:
            warning("This operation needs Git. Use 7 REPOSITORY to enable local history; this does not upload files.")
            input("  Press ENTER to continue...")
            continue
        if selected in {"3", "4"} and is_git and not has_remote:
            warning("No remote is configured. Use 7 REPOSITORY to connect one; this does not upload files by itself.")
            input("  Press ENTER to continue...")
            continue
        return selected


def section(title: str) -> None:
    print(f"\n{accent('◆')} {heading(title.upper())} {accent(IDENTITY)}")


def success(message: str) -> None:
    print(f"{color('✓', GREEN)} {message}")


def warning(message: str) -> None:
    print(f"{color('⚠', YELLOW)} {message}")


def error(message: str) -> None:
    print(f"{color('✗', RED)} {message}")


@contextmanager
def spinner(message: str):
    frames = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    stop = threading.Event()

    def animate() -> None:
        if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
            return
        i = 0
        while not stop.is_set():
            print(f"\r{color(frames[i % len(frames)], MAGENTA)} {message}", end="", flush=True)
            i += 1
            stop.wait(0.08)
        width = len(re.sub(r"\x1b\[[0-9;]*m", "", message)) + 4
        print("\r" + " " * width + "\r", end="", flush=True)

    thread = threading.Thread(target=animate, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=0.2)
        if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
            return
        width = len(re.sub(r"\x1b\[[0-9;]*m", "", message)) + 4
        print("\r" + " " * width + "\r", end="", flush=True)


def footer() -> None:
    print(color("\n  ───────────────────────────────────────────────────────────", DIM))
    print(color("  HIKARI/.LAB", MAGENTA) + color(" • deterministic git • GitHub via gh • credentials stay external", DIM) + " " + accent(IDENTITY))
