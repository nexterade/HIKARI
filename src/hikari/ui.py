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
# COLOR PALETTE — Solana-Inspired (Final Tweak)
# Ocean Blue (primary) × Surge Green (labels) × Purple (HIKARI brand only)
# ─────────────────────────────────────────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

_SUPPORTS_256 = (
    os.environ.get("COLORTERM") in {"truecolor", "24bit"}
    or "256" in os.environ.get("TERM", "")
    or os.environ.get("TERM", "").startswith("xterm")
)

def _c(code256: str, fallback: str) -> str:
    return code256 if _SUPPORTS_256 else fallback

# ── Primary accent: Ocean Blue ──
OCEAN_BLUE  = _c("\033[38;5;45m",   "\033[96m")     # #03E1FF
OCEAN_BOLD  = _c("\033[1;38;5;45m", "\033[1;96m")

# ── Secondary accent: Surge Green (labels) ──
SURGE_GREEN = _c("\033[38;5;49m",   "\033[92m")     # #00FFA3
SURGE_BOLD  = _c("\033[1;38;5;49m", "\033[1;92m")

# ── Brand signature: Purple (HIKARI only) ──
PURPLE_DINO = _c("\033[38;5;165m",  "\033[95m")     # #DC1FFF
PURPLE_BOLD = _c("\033[1;38;5;165m","\033[1;95m")

# ── Neutral gray scale ──
GRAY_BORDER = _c("\033[38;5;238m",  "\033[90m")     # #444    — border/separator
GRAY_LABEL  = _c("\033[38;5;242m",  "\033[37m")     # #6c6c6c — unused
GRAY_VALUE  = _c("\033[38;5;245m",  "\033[37m")     # #8a8a8a — value/metadata

# ── Semantic mapping ──
COMMENT     = OCEAN_BLUE            # section title `#`
VARIABLE    = SURGE_GREEN           # label → GREEN
STRING      = GRAY_VALUE            # value → light gray
KEYWORD     = OCEAN_BLUE            # next / prompt → BLUE
BOOLEAN     = GRAY_VALUE
SUCCESS     = OCEAN_BLUE            # success → BLUE (Solana style)
WARNING     = OCEAN_BLUE            # warning → BLUE
ERROR       = OCEAN_BLUE            # error → BLUE

# ── Structure ──
BORDER      = GRAY_BORDER
OPERATOR    = GRAY_BORDER
DIM_TEXT    = GRAY_VALUE
STATUS_BAR  = GRAY_BORDER

# ── Brand (HIKARI only) ──
HIKARI      = PURPLE_BOLD
HIKARI_SOFT = PURPLE_DINO

# ── Legacy aliases ──
LINENO = BORDER
CYAN = OCEAN_BLUE
MAGENTA = PURPLE_DINO
DEEP_TEAL = GRAY_BORDER
SAKURA = KEYWORD
SAKURA_BOLD = PURPLE_BOLD
NEON_CYAN = OCEAN_BLUE
NEON_MAGENTA = PURPLE_DINO
NEON_YELLOW = OCEAN_BLUE
NEON_GREEN = OCEAN_BLUE
NEON_RED = OCEAN_BLUE
NEON_BLUE = OCEAN_BLUE
GRAY_LIGHT = GRAY_VALUE
GRAY_MID = GRAY_LABEL
GRAY_DARK = GRAY_BORDER
PURPLE_DARK = GRAY_BORDER
BLUE = OCEAN_BLUE
GREEN = SURGE_GREEN
YELLOW = OCEAN_BLUE
RED = OCEAN_BLUE
WHITE = GRAY_VALUE
WHITE_BOLD = GRAY_VALUE
ICE_BLUE = OCEAN_BLUE
ARCTIC_DARK = GRAY_BORDER
CYAN_SOFT = OCEAN_BLUE
CYAN_BOLD = OCEAN_BOLD

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
# BANNER
# ─────────────────────────────────────────────────────────────────────────────
def banner(version: str) -> None:
    global _BANNER_VERSION
    _BANNER_VERSION = version
    print()
    width = shutil_terminal_width()
    title = "H I K A R I  / . L A B  //  LOCAL WORKSPACE"
    subtitle = f"v{version.lstrip('v')}  •  光  •  OFFLINE-FIRST  •  LOCAL + OPTIONAL GIT"

    if width < 68:
        print(
            color("HIKARI", HIKARI)                 # 💜 brand
            + color(" /.LAB", OCEAN_BLUE)
            + color(" // ", GRAY_BORDER)
            + color("LOCAL WORKSPACE", OCEAN_BOLD)
        )
        print(color(subtitle, GRAY_VALUE))
    else:
        inner = min(width - 2, 76)
        title = title[:inner - 2]
        subtitle = subtitle[:inner - 2]
        print(color("╔" + "═" * inner + "╗", GRAY_BORDER))
        print(
            color("║", GRAY_BORDER)
            + color("  H I K A R I", PURPLE_BOLD)   # 💜 brand
            + color("  / . L A B", OCEAN_BLUE)
            + color("  //  ", GRAY_BORDER)
            + color("LOCAL WORKSPACE", OCEAN_BOLD)
            + " " * max(0, inner - 42)
            + color("║", GRAY_BORDER)
        )
        print(
            color("║", OCEAN_BLUE)
            + color("  " + subtitle, GRAY_VALUE)
            + " " * max(0, inner - len(subtitle) - 2)
            + color("║", GRAY_BORDER)
        )
        print(color("╚" + "═" * inner + "╝", GRAY_BORDER))


# ─────────────────────────────────────────────────────────────────────────────
# TARGET PROJECT PANEL
# ─────────────────────────────────────────────────────────────────────────────
def target(repo_name, root, branch, remote, version=None, version_source=None):
    width = max(24, min(shutil_terminal_width(), 88))
    rule = _rule(width, "─")

    print(color(rule, BORDER))
    print(color("  # ", OCEAN_BLUE) + color("TARGET PROJECT", OCEAN_BOLD))
    print(color(rule, BORDER))

    def field(label, value, value_color=STRING):
        pad = " " * max(1, 14 - len(label))
        print(
            f"  {color(label, VARIABLE)}{pad} "
            f"{color(':', OPERATOR)}  "
            f"{color(value, value_color)}"
        )

    field("project", repo_name + (f" v{version}" if version else ""))
    field("path", root)
    field("branch", branch, OCEAN_BLUE)
    field("remote", remote or "(none)")
    if version_source:
        print(f"  {color('# version source:', OCEAN_BLUE)} {color(version_source, DIM_TEXT)}")
    print(color(rule, BORDER))


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _simplify_changes(changes_raw: str) -> str:
    if "·" not in changes_raw:
        return changes_raw
    parts = [p.strip() for p in changes_raw.split("·")]
    if parts and "path" in parts[0].lower():
        parts = parts[1:]
    return ", ".join(parts) if parts else changes_raw


def _changes_color(changes_str: str) -> str:
    """Clean → gray; dirty → blue."""
    if not changes_str or changes_str.lower() in {"not inspected", "clean"}:
        return GRAY_VALUE
    numbers = [int(n) for n in re.findall(r"\b(\d+)\b", changes_str)]
    if not numbers or all(n == 0 for n in numbers):
        return GRAY_VALUE
    return OCEAN_BLUE


# ─────────────────────────────────────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────────────────────────────────────
def menu(is_git=True, has_remote=True, snapshot=None, target_context=None):
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

        def emit(text): print(text)
        def emit_raw(text): print(text)

        def emit_section(title):
            """Section heading: # in blue, title in blue bold."""
            print(f"  {color('#', OCEAN_BLUE)} {color(title, OCEAN_BOLD)}")

        def emit_field(label, value, value_color=None):
            pad = " " * max(1, 14 - len(label))
            prefix = f"  {color(label, VARIABLE)}{pad} {color(':', OPERATOR)}  "
            prefix_visible_len = _visible_len(prefix)
            indent = " " * prefix_visible_len

            value_str = str(value)
            available = max(8, width - prefix_visible_len - 2)
            chunks = textwrap.wrap(value_str, width=available,
                                   break_long_words=False, break_on_hyphens=False) or [""]

            vc = value_color if value_color else STRING
            print(f"{prefix}{color(chunks[0], vc)}")
            for chunk in chunks[1:]:
                print(f"{indent}{color(chunk, vc)}")

        # ── TARGET PROJECT ──
        emit_raw(color(rule, BORDER))
        emit_section("TARGET PROJECT")
        emit_field("project", context.get("name", "(not provided)"))
        emit_field("path", context.get("root", "(not provided)"))
        emit_field("branch", context.get("branch", "not inspected"), OCEAN_BLUE)
        emit_field("remote", context.get("remote", "(none)") or "(none)")
        if context.get("version"):
            emit_field("version", context["version"])
        emit_raw(color(rule, BORDER))

        # ── DASHBOARD ──
        emit_section("DASHBOARD")
        # mode → Ocean Blue if git, gray if local
        emit_field("mode", "git" if is_git else "local",
                   OCEAN_BLUE if is_git else GRAY_VALUE)

        if is_git:
            wt = snapshot.get("working_tree", "not inspected")
            wt_upper = wt.upper()
            wt_color = GRAY_VALUE
            if wt_upper == "DIRTY":
                wt_color = OCEAN_BLUE
            emit_field("working_tree", wt, wt_color)

            changes_display = _simplify_changes(snapshot.get("changes", "not inspected"))
            emit_field("changes", changes_display, _changes_color(changes_display))

            sync = snapshot.get("sync", "not checked")
            emit_field("sync", sync, GRAY_VALUE)

            emit_field("last_commit", snapshot.get("last_commit", "not inspected"))
        else:
            emit_field("version", snapshot.get("version", "not detected"))
            emit_field("files", snapshot.get("files", "use SCAN for inventory"))
            emit_field("safety", "local-only; nothing is uploaded automatically")

        if snapshot.get("next_step"):
            emit_field("next", snapshot["next_step"], OCEAN_BOLD)

        # ── OPERATIONS ──
        emit_raw(color(rule, BORDER))
        emit_section("OPERATIONS")
        label_width = max(len(label) for _, label, _ in operations)

        for key, label, description in operations:
            if narrow:
                emit(f"  {color(SEP, GRAY_BORDER)} {color(key.rjust(2), OCEAN_BLUE)}  {color(label, GRAY_VALUE)}")
                if description:
                    max_desc = max(8, width - 8)
                    desc = description[:max_desc - 3] + "..." if len(description) > max_desc else description
                    emit(f"      {color(desc, GRAY_VALUE)}")
                continue

            prefix_plain = f"  {SEP} {key.rjust(2)}  {label.ljust(label_width)}  · "
            available = max(12, width - len(prefix_plain) - 4)
            wrapped = textwrap.wrap(description, width=available, break_long_words=False) or [""]
            emit(
                f"  {color(SEP, GRAY_BORDER)} {color(key.rjust(2), OCEAN_BLUE)}  "
                f"{color(label.ljust(label_width), GRAY_VALUE)}  "
                f"{color('·', GRAY_BORDER)} {color(wrapped[0], GRAY_VALUE)}"
            )
            if len(wrapped) > 1:
                indent = " " * (label_width + 8)
                for cont in wrapped[1:]:
                    emit(f"{indent}{color(cont, GRAY_VALUE)}")

        # ── EXIT ──
        # HIKARI purple — satu-satunya purple di UI
        emit_raw("")
        emit(
            f"  {color(SEP, GRAY_BORDER)} {color('0', OCEAN_BLUE)}  "
            f"{color('EXIT', GRAY_VALUE)} {color('HIKARI', HIKARI)}"
        )

        # ── STATUS BAR ──
        print(color(rule, BORDER))
        branch = context.get("branch", "?")
        changes = snapshot.get("changes", "")
        sync = snapshot.get("sync", "")
        status_parts = [
            color(" HIKARI", HIKARI)  # 💜 brand
            + color(f" v{_BANNER_VERSION.lstrip('v')}", GRAY_VALUE),
            color("│", GRAY_BORDER),
            color(f"● {branch}", OCEAN_BLUE),
        ]
        if is_git and changes:
            n_changes = changes.split(" ")[0] if changes.split(" ")[0].isdigit() else ""
            if n_changes and n_changes != "0":
                status_parts.append(color("│", GRAY_BORDER))
                status_parts.append(color(f"⚠ {n_changes} change", OCEAN_BLUE))
            else:
                status_parts.append(color("│", GRAY_BORDER))
                status_parts.append(color("✓ clean", GRAY_VALUE))
        if is_git and sync:
            if "no upstream" in sync.lower():
                status_parts.append(color("│", GRAY_BORDER))
                status_parts.append(color("no upstream", GRAY_VALUE))
        print("".join(status_parts))
        print(color(rule, BORDER))

        # ── INPUT ──
        print()
        selected = input(f"{color('❯', OCEAN_BOLD)} ").strip().upper()

        if selected in {"0", "X", "Q"}:
            return "0"

        chosen = next((item for item in operations if item[0] == selected), None)
        if not chosen:
            warning("Choose an operation from 1–12, or 0 to exit.")
            input(f"  {color('Press ENTER to continue...', GRAY_VALUE)}")
            continue

        if selected in {"3", "4", "5", "6", "9", "11"} and not is_git:
            warning("This operation needs Git. Use 7 REPOSITORY to enable local history; this does not upload files.")
            input(f"  {color('Press ENTER to continue...', GRAY_VALUE)}")
            continue

        if selected in {"3", "4"} and is_git and not has_remote:
            warning("No remote is configured. Use 7 REPOSITORY to connect one; this does not upload files by itself.")
            input(f"  {color('Press ENTER to continue...', GRAY_VALUE)}")
            continue

        return selected


# ─────────────────────────────────────────────────────────────────────────────
# STATUS MESSAGES
# ─────────────────────────────────────────────────────────────────────────────
def section(title):
    print(f"\n{color('#', OCEAN_BLUE)} {color(title.upper(), OCEAN_BOLD)} {color(IDENTITY, OCEAN_BLUE)}")


def success(message):
    print(f"{color('✓', OCEAN_BLUE)} {message}")


def warning(message):
    print(f"{color('⚠', OCEAN_BLUE)} {message}")


def error(message):
    print(f"{color('✗', OCEAN_BLUE)} {message}")


# ─────────────────────────────────────────────────────────────────────────────
# SPINNER
# ─────────────────────────────────────────────────────────────────────────────
@contextmanager
def spinner(message):
    frames = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    stop = threading.Event()
    running = False

    def animate():
        nonlocal running
        if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
            return
        running = True
        i = 0
        while not stop.is_set():
            print(f"\r{color(frames[i % len(frames)], OCEAN_BLUE)} {message}", end="", flush=True)
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
def footer():
    width = max(24, min(shutil_terminal_width(), 88))
    rule = _rule(width, "─")
    print()
    print(color(rule, BORDER))
    if width < 60:
        print(
            color("  HIKARI", HIKARI)  # 💜
            + color("  " + SEP + "  ", GRAY_BORDER)
            + color("deterministic git", GRAY_VALUE)
        )
        print(
            color("  GitHub via gh  " + SEP + "  credentials stay external ", GRAY_VALUE)
            + color(IDENTITY, OCEAN_BLUE)
        )
    else:
        print(
            color("  HIKARI", HIKARI)  # 💜
            + color("  " + SEP + "  ", GRAY_BORDER)
            + color("deterministic git", GRAY_VALUE)
            + color("  " + SEP + "  ", GRAY_BORDER)
            + color("GitHub via gh", GRAY_VALUE)
            + color("  " + SEP + "  ", GRAY_BORDER)
            + color("credentials stay external ", GRAY_VALUE)
            + color(IDENTITY, OCEAN_BLUE)
        )