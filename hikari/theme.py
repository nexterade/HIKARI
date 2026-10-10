"""
HIKARI Color Palette — Solana-Inspired Theme
=============================================
Palet warna konsisten untuk semua modul CLI HIKARI.

Filosofi:
- Ocean Blue (#03E1FF) → primary accent, fokus visual
- Surge Green (#00FFA3) → label & secondary accent
- Purple Dino (#DC1FFF) → brand signature HIKARI only
- Gray Scale (238/245) → struktur & metadata
"""
from __future__ import annotations

import os
import re
import sys

# ─────────────────────────────────────────────────────────────────────────────
# ANSI RESET & MODIFIERS
# ─────────────────────────────────────────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# ─────────────────────────────────────────────────────────────────────────────
# 256-COLOR DETECTION
# ─────────────────────────────────────────────────────────────────────────────
_SUPPORTS_256 = (
    os.environ.get("COLORTERM") in {"truecolor", "24bit"}
    or "256" in os.environ.get("TERM", "")
    or os.environ.get("TERM", "").startswith("xterm")
)

def _c(code256: str, fallback: str) -> str:
    """Return 256-color code if supported, else 16-color fallback."""
    return code256 if _SUPPORTS_256 else fallback


# ─────────────────────────────────────────────────────────────────────────────
# PRIMARY ACCENT — Ocean Blue
# ─────────────────────────────────────────────────────────────────────────────
OCEAN_BLUE = _c("\033[38;5;45m",    "\033[96m")     # #03E1FF
OCEAN_BOLD = _c("\033[1;38;5;45m",  "\033[1;96m")

# ─────────────────────────────────────────────────────────────────────────────
# SECONDARY ACCENT — Surge Green
# ─────────────────────────────────────────────────────────────────────────────
SURGE_GREEN = _c("\033[38;5;49m",   "\033[92m")     # #00FFA3
SURGE_BOLD  = _c("\033[1;38;5;49m", "\033[1;92m")

# ─────────────────────────────────────────────────────────────────────────────
# BRAND SIGNATURE — Purple Dino (HIKARI only)
# ─────────────────────────────────────────────────────────────────────────────
PURPLE_DINO = _c("\033[38;5;165m",  "\033[95m")     # #DC1FFF
PURPLE_BOLD = _c("\033[1;38;5;165m","\033[1;95m")

# ─────────────────────────────────────────────────────────────────────────────
# NEUTRAL — Gray Scale
# ─────────────────────────────────────────────────────────────────────────────
GRAY_BORDER = _c("\033[38;5;238m",  "\033[90m")     # #444    — border/separator
GRAY_LABEL  = _c("\033[38;5;242m",  "\033[37m")     # #6c6c6c — label alt
GRAY_VALUE  = _c("\033[38;5;245m",  "\033[37m")     # #8a8a8a — value/metadata
GRAY_DIM    = _c("\033[38;5;240m",  "\033[90m")     # #585858 — very dim

# ─────────────────────────────────────────────────────────────────────────────
# SEMANTIC ALIASES (untuk konsistensi makna)
# ─────────────────────────────────────────────────────────────────────────────
# Struktur
BORDER   = GRAY_BORDER
OPERATOR = GRAY_BORDER
DIM_TEXT = GRAY_VALUE

# Konten
COMMENT  = OCEAN_BLUE    # judul section `#`
VARIABLE = SURGE_GREEN   # label field
STRING   = GRAY_VALUE    # value default

# Aksi
KEYWORD  = OCEAN_BLUE    # prompt, next, nomor menu
BOOLEAN  = GRAY_VALUE

# Status (di Solana theme, semua status = blue)
SUCCESS  = OCEAN_BLUE
WARNING  = OCEAN_BLUE
ERROR    = OCEAN_BLUE
INFO     = GRAY_VALUE

# Brand (HIKARI only)
HIKARI      = PURPLE_BOLD
HIKARI_SOFT = PURPLE_DINO

# ─────────────────────────────────────────────────────────────────────────────
# SYMBOLS / GLYPHS
# ─────────────────────────────────────────────────────────────────────────────
IDENTITY = "◈"
SEP      = "▸"
BULLET   = "·"
CHECK    = "✓"
CROSS    = "✗"
WARN     = "⚠"
ARROW    = "→"
PROMPT   = "❯"


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def color(text: str, code: str) -> str:
    """Apply ANSI color, respecting NO_COLOR and non-TTY."""
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return text
    if not sys.stdout.isatty():
        return text
    return f"{code}{text}{RESET}"


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes for width calculation."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def visible_len(text: str) -> int:
    """Return visible length (without ANSI codes)."""
    return len(strip_ansi(text))


def brand() -> str:
    """Return 'HIKARI' in brand purple."""
    return color("HIKARI", HIKARI)


def rule(width: int = 60, char: str = "─") -> str:
    """Return a horizontal rule with the given width."""
    return color(char * max(12, width), BORDER)


# ─────────────────────────────────────────────────────────────────────────────
# EXPORTS
# ─────────────────────────────────────────────────────────────────────────────
__all__ = [
    # Modifiers
    "RESET", "BOLD", "DIM", "ITALIC", "UNDERLINE",
    # Accents
    "OCEAN_BLUE", "OCEAN_BOLD",
    "SURGE_GREEN", "SURGE_BOLD",
    "PURPLE_DINO", "PURPLE_BOLD",
    # Grays
    "GRAY_BORDER", "GRAY_LABEL", "GRAY_VALUE", "GRAY_DIM",
    # Semantic
    "BORDER", "OPERATOR", "DIM_TEXT", "COMMENT",
    "VARIABLE", "STRING", "KEYWORD", "BOOLEAN",
    "SUCCESS", "WARNING", "ERROR", "INFO",
    "HIKARI", "HIKARI_SOFT",
    # Symbols
    "IDENTITY", "SEP", "BULLET", "CHECK", "CROSS", "WARN",
    "ARROW", "PROMPT",
    # Functions
    "color", "strip_ansi", "visible_len", "brand", "rule",
]