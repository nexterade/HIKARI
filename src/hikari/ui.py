from __future__ import annotations

import os
import re
import shutil
import sys
import threading
import textwrap
from contextlib import contextmanager
from ._version import get_version

# ─────────────────────────────────────────────────────────────────────────────
# COLOR PALETTE — Tokyo Night Edition 🌊
# ─────────────────────────────────────────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
DIM = "\033[2m"

_SUPPORTS_256 = (
    os.environ.get("COLORTERM") in {"truecolor", "24bit"}
    or "256" in os.environ.get("TERM", "")
    or os.environ.get("TERM", "").startswith("xterm")
)

def _c(code256: str, fallback: str) -> str:
    return code256 if _SUPPORTS_256 else fallback

# ── Tokyo Night palette ──
COMMENT     = _c("\033[38;5;103m",  "\033[94m")     # slate blue — # section
VARIABLE    = _c("\033[38;5;111m",  "\033[96m")     # electric blue — labels
STRING      = _c("\033[38;5;151m",  "\033[92m")     # mint green — string values
KEYWORD     = _c("\033[38;5;176m",  "\033[95m")     # lavender — accent
BOOLEAN     = _c("\033[38;5;222m",  "\033[93m")     # amber
SUCCESS     = _c("\033[38;5;151m",  "\033[92m")     # mint
WARNING     = _c("\033[38;5;222m",  "\033[93m")     # amber
ERROR       = _c("\033[38;5;204m",  "\033[91m")     # rose red

# ── Structure ──
BORDER      = _c("\033[38;5;60m",   "\033[90m")     # deep indigo — borders
OPERATOR    = _c("\033[38;5;245m",  "\033[37m")     # mid gray — operators
DIM_TEXT    = _c("\033[38;5;240m",  "\033[90m")     # slate gray — dim text
STATUS_BAR  = _c("\033[38;5;60m",   "\033[90m")     # deep indigo — status bar

# ── Legacy aliases (for backwards compat with banner) ──
LINENO = BORDER
CYAN = VARIABLE
MAGENTA = COMMENT
DEEP_TEAL = BORDER
SAKURA = KEYWORD
SAKURA_BOLD = KEYWORD
NEON_CYAN = VARIABLE
NEON_MAGENTA = KEYWORD
NEON_YELLOW = WARNING
NEON_GREEN = SUCCESS
NEON_RED = ERROR
NEON_BLUE = KEYWORD
GRAY_LIGHT = STRING
GRAY_MID = OPERATOR
GRAY_DARK = DIM_TEXT
PURPLE_DARK = DIM_TEXT
BLUE = VARIABLE
GREEN = SUCCESS
YELLOW = WARNING
RED = ERROR
WHITE = STRING
WHITE_BOLD = STRING
ICE_BLUE = VARIABLE
ARCTIC_DARK = DIM_TEXT
CYAN_SOFT = VARIABLE
CYAN_BOLD = VARIABLE

IDENTITY = "◈"
SEP = "▸"
_BANNER_VERSION = get_version()


# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def shutil_terminal_width() -> int:
    try:
        return max(24, shutil.get_terminal_size(fallback=(80, 24)).columns)
    except OSError:
        return 80


def clear_screen() -> None:
    if not sys.stdout.isatty():
        return
    print("\033[3J\033[H\033[2J", end="", flush=True)


def terminal_text(text: str) -> str:
    return text


def color(text: str, code: str) -> str:
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb" or not sys.stdout.isatty():
        return text
    return f"{code}{text}{RESET}"


def accent(text: str) -> str:
    return color(text, KEYWORD)


def muted(text: str) -> str:
    return color(text, OPERATOR)


def heading(text: str) -> str:
    return color(text, COMMENT)


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _visible_len(text: str) -> int:
    return len(_strip_ansi(text))


def _rule(width: int, char: str = "─") -> str:
    return char * max(12, width - 2)


# ─────────────────────────────────────────────────────────────────────────────
# BANNER — Tokyo Night with accent
# ─────────────────────────────────────────────────────────────────────────────
def banner(version: str) -> None:
    """Render the console identity/header and remember it for screen redraws."""
    global _BANNER_VERSION
    _BANNER_VERSION = version
    print()
    width = shutil_terminal_width()
    title = "H I K A R I  / . L A B  //  LOCAL WORKSPACE"
    subtitle = f"v{version.lstrip('v')}  •  光  •  OFFLINE-FIRST  •  LOCAL + OPTIONAL GIT"

    if width < 68:
        # Compact mode with Tokyo Night accent
        print(
            color("HIKARI", BOLD + VARIABLE)
            + color(" /.LAB", COMMENT)
            + color(" // ", DIM_TEXT)
            + color("LOCAL WORKSPACE", BOLD + STRING)
        )
        print(color(subtitle, DIM_TEXT))
    else:
        inner = min(width - 2, 76)
        title = title[:inner - 2]
        subtitle = subtitle[:inner - 2]
        print(color("╔" + "═" * inner + "╗", BORDER))
        print(
            color("║", BORDER)
            + color("  " + title, BOLD + VARIABLE)
            + " " * max(0, inner - len(title) - 2)
            + color("║", BORDER)
        )
        print(
            color("║", COMMENT)
            + color("  " + subtitle, DIM_TEXT)
            + " " * max(0, inner - len(subtitle) - 2)
            + color("║", BORDER)
        )
        print(color("╚" + "═" * inner + "╝", BORDER))


# ─────────────────────────────────────────────────────────────────────────────
# TARGET PROJECT PANEL
# ─────────────────────────────────────────────────────────────────────────────
def target(
    repo_name: str,
    root: str,
    branch: str,
    remote: str,
    version: str | None = None,
    version_source: str | None = None,
) -> None:
    width = max(24, min(shutil_terminal_width(), 88))
    rule = _rule(width, "─")

    print(color(rule, BORDER))
    print(color("  # TARGET PROJECT", COMMENT))
    print(color(rule, BORDER))

    def field(label: str, value: str, value_color: str = STRING) -> None:
        pad = " " * max(1, 14 - len(label))
        print(
            f"  {color(label, VARIABLE)}{pad} "
            f"{color(':', OPERATOR)}  "
            f"{color(f'\"{value}\"', value_color)}"
        )

    field("project", repo_name + (f" v{version}" if version else ""))
    field("path", root)
    field("branch", branch, SUCCESS)
    field("remote", remote or "(none)")
    if version_source:
        print(f"  {color('# version source:', COMMENT)} {color(version_source, DIM_TEXT)}")
    print(color(rule, BORDER))


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _simplify_changes(changes_raw: str) -> str:
    """Simplify changes string into compact inline format."""
    if "·" not in changes_raw:
        return changes_raw
    parts = [p.strip() for p in changes_raw.split("·")]
    if parts and "path" in parts[0].lower():
        parts = parts[1:]
    return ", ".join(parts) if parts else changes_raw


# ─────────────────────────────────────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────────────────────────────────────
def menu(
    is_git: bool = True,
    has_remote: bool = True,
    snapshot: dict | None = None,
    target_context: dict | None = None,
) -> str:
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
    width = max(24, min(shutil_terminal_width(), 88))
    rule = _rule(width, "─")
    narrow = width < 50

    while True:
        clear_screen()
        banner(_BANNER_VERSION)

        def emit(text: str) -> None:
            print(text)

        def emit_raw(text: str) -> None:
            print(text)

        def emit_field(label: str, value: object, value_color: str | None = None) -> None:
            """Emit a field with proper wrap indentation."""
            pad = " " * max(1, 14 - len(label))
            prefix = f"  {color(label, VARIABLE)}{pad} {color(':', OPERATOR)}  "
            prefix_visible_len = _visible_len(prefix)
            indent = " " * prefix_visible_len

            value_str = str(value)
            available = max(8, width - prefix_visible_len - 3)
            chunks = textwrap.wrap(
                value_str, width=available,
                break_long_words=False, break_on_hyphens=False,
            ) or [""]

            vc = value_color if value_color else STRING
            print(f"{prefix}{color(f'\"{chunks[0]}\"', vc)}")
            for chunk in chunks[1:]:
                print(f"{indent}{color(f'\"{chunk}\"', vc)}")

        # ── TARGET PROJECT ───────────────────────────────────────────────
        emit_raw(color(rule, BORDER))
        emit(color("  # TARGET PROJECT", COMMENT))
        emit_field("project", context.get("name", "(not provided)"))
        emit_field("path", context.get("root", "(not provided)"))
        emit_field("branch", context.get("branch", "not inspected"), SUCCESS)
        emit_field("remote", context.get("remote", "(none)") or "(none)")
        if context.get("version"):
            emit_field("version", context["version"], SUCCESS)
        emit_raw(color(rule, BORDER))

        # ── DASHBOARD ────────────────────────────────────────────────────
        emit(color("  # DASHBOARD", COMMENT))
        emit_field(
            "mode",
            "git" if is_git else "local",
            VARIABLE if is_git else BOOLEAN,
        )

        if is_git:
            wt = snapshot.get("working_tree", "not inspected")
            wt_upper = wt.upper()
            wt_color = STRING
            if wt_upper == "CLEAN":
                wt_color = SUCCESS
            elif wt_upper == "DIRTY":
                wt_color = WARNING
            emit_field("working_tree", wt, wt_color)

            # changes → dim
            changes_display = _simplify_changes(
                snapshot.get("changes", "not inspected")
            )
            emit_field("changes", changes_display, DIM_TEXT)

            # sync → dim
            sync = snapshot.get("sync", "not checked")
            emit_field("sync", sync, DIM_TEXT)

            emit_field("last_commit", snapshot.get("last_commit", "not inspected"))
        else:
            emit_field("version", snapshot.get("version", "not detected"), SUCCESS)
            emit_field("files", snapshot.get("files", "use SCAN for inventory"), OPERATOR)
            emit_field("safety", "local-only; nothing is uploaded automatically", SUCCESS)

        if snapshot.get("next_step"):
            emit_field("next", snapshot["next_step"], KEYWORD)

        # ── OPERATIONS ───────────────────────────────────────────────────
        emit_raw(color(rule, BORDER))
        emit(color("  # OPERATIONS", COMMENT))
        label_width = max(len(label) for _, label, _ in operations)

        for key, label, description in operations:
            if narrow:
                emit(
                    f"  {color(SEP, OPERATOR)} {color(key.rjust(2), VARIABLE)}  "
                    f"{color(label, STRING)}"
                )
                if description:
                    max_desc = max(8, width - 8)
                    desc = (
                        description[: max_desc - 3] + "..."
                        if len(description) > max_desc
                        else description
                    )
                    emit(f"      {color(desc, DIM_TEXT)}")
                continue

            prefix_plain = f"  {SEP} {key.rjust(2)}  {label.ljust(label_width)}  · "
            available = max(12, width - len(prefix_plain) - 4)
            wrapped = textwrap.wrap(
                description, width=available, break_long_words=False
            ) or [""]
            emit(
                f"  {color(SEP, OPERATOR)} {color(key.rjust(2), VARIABLE)}  "
                f"{color(label.ljust(label_width), STRING)}  "
                f"{color('·', OPERATOR)} {color(wrapped[0], DIM_TEXT)}"
            )
            if len(wrapped) > 1:
                indent = " " * (label_width + 8)
                for cont in wrapped[1:]:
                    emit(f"{indent}{color(cont, DIM_TEXT)}")

        # ── EXIT ─────────────────────────────────────────────────────────
        emit_raw("")
        emit(f"  {color(SEP, OPERATOR)} {color('0', VARIABLE)}  {color('EXIT HIKARI', ERROR)}")

        # ── STATUS BAR ───────────────────────────────────────────────────
        print(color(rule, BORDER))
        branch = context.get("branch", "?")
        changes = snapshot.get("changes", "")
        sync = snapshot.get("sync", "")
        status_parts = [
            color(f" HIKARI v{_BANNER_VERSION.lstrip('v')}", STATUS_BAR),
            color("│", BORDER),
            color(f"● {branch}", SUCCESS if is_git else BOOLEAN),
        ]
        if is_git and changes:
            n_changes = changes.split(" ")[0] if changes.split(" ")[0].isdigit() else ""
            if n_changes and n_changes != "0":
                status_parts.append(color("│", BORDER))
                status_parts.append(color(f"⚠ {n_changes} change", DIM_TEXT))
            else:
                status_parts.append(color("│", BORDER))
                status_parts.append(color("✓ clean", DIM_TEXT))
        if is_git and sync:
            if "no upstream" in sync.lower():
                status_parts.append(color("│", BORDER))
                status_parts.append(color("no upstream", DIM_TEXT))
        print("".join(status_parts))
        print(color(rule, BORDER))

        # ── INPUT ────────────────────────────────────────────────────────
        print()
        selected = input(f"{color('❯', KEYWORD)} ").strip().upper()

        if selected in {"0", "X", "Q"}:
            return "0"

        chosen = next((item for item in operations if item[0] == selected), None)
        if not chosen:
            warning("Choose an operation from 1–12, or 0 to exit.")
            input(f"  {color('Press ENTER to continue...', DIM_TEXT)}")
            continue

        if selected in {"3", "4", "5", "6", "9", "11"} and not is_git:
            warning(
                "This operation needs Git. Use 7 REPOSITORY to enable local history; "
                "this does not upload files."
            )
            input(f"  {color('Press ENTER to continue...', DIM_TEXT)}")
            continue

        if selected in {"3", "4"} and is_git and not has_remote:
            warning(
                "No remote is configured. Use 7 REPOSITORY to connect one; "
                "this does not upload files by itself."
            )
            input(f"  {color('Press ENTER to continue...', DIM_TEXT)}")
            continue

        return selected


# ─────────────────────────────────────────────────────────────────────────────
# STATUS MESSAGES
# ─────────────────────────────────────────────────────────────────────────────
def section(title: str) -> None:
    print(f"\n{color('#', COMMENT)} {color(title.upper(), COMMENT)} {color(IDENTITY, KEYWORD)}")


def success(message: str) -> None:
    print(f"{color('✓', SUCCESS)} {message}")


def warning(message: str) -> None:
    print(f"{color('⚠', WARNING)} {message}")


def error(message: str) -> None:
    print(f"{color('✗', ERROR)} {message}")


# ─────────────────────────────────────────────────────────────────────────────
# SPINNER
# ─────────────────────────────────────────────────────────────────────────────
@contextmanager
def spinner(message: str):
    frames = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    stop = threading.Event()
    running = False

    def animate() -> None:
        nonlocal running
        if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
            return
        running = True
        i = 0
        while not stop.is_set():
            print(f"\r{color(frames[i % len(frames)], KEYWORD)} {message}", end="", flush=True)
            i += 1
            stop.wait(0.08)
        running = False

    thread = threading.Thread(target=animate, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=0.2)
        if not running and (not sys.stdout.isatty() or os.environ.get("NO_COLOR")):
            return
        w = _visible_len(message) + 4
        print("\r" + " " * w + "\r", end="", flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
def footer() -> None:
    width = max(24, min(shutil_terminal_width(), 88))
    rule = _rule(width, "─")
    print()
    print(color(rule, BORDER))
    if width < 60:
        print(color("  HIKARI", KEYWORD) + color("  " + SEP + "  ", BORDER) + color("deterministic git", STRING))
        print(color("  GitHub via gh  " + SEP + "  credentials stay external ", DIM_TEXT) + color(IDENTITY, KEYWORD))
    else:
        print(
            color("  HIKARI", KEYWORD)
            + color("  " + SEP + "  ", BORDER)
            + color("deterministic git", STRING)
            + color("  " + SEP + "  ", BORDER)
            + color("GitHub via gh", STRING)
            + color("  " + SEP + "  ", BORDER)
            + color("credentials stay external ", DIM_TEXT)
            + color(IDENTITY, KEYWORD)
        )