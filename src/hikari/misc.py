from __future__ import annotations
from .constants import SKIP_DIRS

import ast
import hashlib
import html
import os
import re
import shutil
import sqlite3
import subprocess
import textwrap
import zipfile
from datetime import datetime
from pathlib import Path

from .action_tracking import error, success, warning
from .ui import BOLD, CYAN, DIM, GREEN, MAGENTA, RED, WHITE, YELLOW, color, section, spinner

# Shared with Git/local inventory and changelog discovery via hikari.constants.
DATA_EXTS = {".json", ".md", ".txt", ".yaml", ".yml", ".toml", ".html", ".css", ".js", ".cfg", ".ini", ".env"}
STDLIB = set("os sys json re time datetime math random hashlib itertools functools collections pathlib shutil glob subprocess argparse logging unittest typing dataclasses enum io textwrap string ast importlib traceback socket http urllib base64 binascii csv sqlite3 pickle copy pprint uuid secrets hmac tempfile contextlib warnings platform getopt configparser webbrowser zipfile tarfile gzip struct array queue threading multiprocessing asyncio concurrent signal".split())


def _files(root: Path):
    root = Path(root).resolve()
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not (Path(base) / d).is_symlink()]
        for name in names:
            p = Path(base) / name
            if not p.is_symlink():
                yield p


def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024**2:
        return f"{n/1024:.1f} KB"
    if n < 1024**3:
        return f"{n/1024**2:.1f} MB"
    return f"{n/1024**3:.2f} GB"


def _hash(path: Path, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _pause() -> None:
    input(color("\n  Press ENTER to return to Miscellaneous... ", DIM))


def _header(title: str, desc: str) -> None:
    print()
    print(color("┌─ " + title.upper(), CYAN) + color(" ─────────────────────────────────────────", DIM))
    print(color("│ ", CYAN) + color(desc, DIM))
    print(color("└────────────────────────────────────────────────────────────", CYAN))


def tree_printer(root: Path) -> None:
    _header("Tree Printer", "Project tree + Python dependency/orphan audit")
    pyfiles = list(p for p in _files(root) if p.suffix == ".py")
    all_paths = sorted(p.relative_to(root).as_posix() for p in _files(root))
    for rel in all_paths[:500]:
        depth = rel.count("/")
        name = Path(rel).name
        icon = "📁" if "." not in name else "📄"
        print("  " + "  " * depth + icon + " " + name)
    if len(all_paths) > 500:
        print(color(f"  … {len(all_paths)-500} more files omitted", DIM))

    imported: set[str] = set()
    for p in pyfiles:
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        except (OSError, UnicodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for mod in names:
                top = mod.split(".")[0]
                if top in STDLIB:
                    continue
                candidate = root / (mod.replace(".", "/") + ".py")
                package = root / mod.replace(".", "/") / "__init__.py"
                if candidate.is_file():
                    imported.add(candidate.relative_to(root).as_posix())
                elif package.is_file():
                    imported.add(package.relative_to(root).as_posix())
    orphans = [p.relative_to(root).as_posix() for p in pyfiles if p.name != "__init__.py" and p.relative_to(root).as_posix() not in imported]
    print("\n" + color("Dependency audit", BOLD + CYAN))
    print(f"  Python files : {len(pyfiles)}")
    print(f"  Imported     : {len(imported)}")
    print(f"  Possible orphan files: {len(orphans)}")
    for rel in orphans[:80]:
        print(color(f"    • {rel}", YELLOW))


def ghost_grep(root: Path) -> None:
    _header("Ghost Grep", "Smart project-wide pattern search")
    pattern = input("  Pattern: ").strip()
    if not pattern:
        warning("Pattern kosong.")
        return
    regex = input("  Regex mode? [y/N]: ").strip().lower() in {"y", "yes"}
    try:
        rx = re.compile(pattern if regex else re.escape(pattern), re.I)
    except re.error as exc:
        error(f"Invalid regex: {exc}")
        return
    limit_raw = input("  Max results [300]: ").strip()
    try:
        limit = max(1, int(limit_raw or "300"))
    except ValueError:
        limit = 300
    found = 0
    with spinner("Searching project files"):
        for p in _files(root):
            try:
                with p.open("r", encoding="utf-8") as f:
                    for line_no, line in enumerate(f, 1):
                        if rx.search(line):
                            print(f"  {p.relative_to(root)}:{line_no}: {line.rstrip()[:280]}")
                            found += 1
                            if found >= limit:
                                break
            except (OSError, UnicodeDecodeError):
                continue
            if found >= limit:
                break
    success(f"Found {found} match(es).")


def file_hasher(root: Path) -> None:
    _header("File Hasher", "SHA-256 hashing + integrity verification")
    raw = input(f"  File path [{root}]: ").strip() or str(root)
    path = Path(raw).expanduser().resolve()
    if not path.is_file():
        error("File tidak ditemukan.")
        return
    with spinner("Hashing file"):
        digest = _hash(path)
    print(f"\n  FILE   {path}")
    print(f"  SIZE   {_fmt_size(path.stat().st_size)}")
    print(f"  SHA256 {digest}")
    expected = input("\n  Expected SHA-256 (optional): ").strip().lower()
    if expected:
        success("Integrity verified.") if expected == digest.lower() else error("Integrity mismatch!")


def backup_rotator(root: Path) -> None:
    """Create rotated ZIP backups or safely restore a selected backup."""
    _header("Backup Rotator", "ZIP backup, retention rotation + restore")
    default_dir = Path.home() / ".hikari" / "backups"
    print("  [1] CREATE BACKUP")
    print("  [2] RESTORE BACKUP")
    print("  [Q] Cancel")
    action = input("  Choose action: ").strip().lower()
    if action == "q" or not action:
        warning("Backup operation cancelled.")
        return
    raw = input(f"  Backup directory [{default_dir}]: ").strip()
    backup_dir = Path(raw).expanduser().resolve() if raw else default_dir

    if action == "2":
        archives = sorted(backup_dir.glob(f"{root.name}-*.zip"), key=lambda p: p.stat().st_mtime, reverse=True) if backup_dir.is_dir() else []
        if not archives:
            warning(f"No {root.name}-*.zip backups found in {backup_dir}")
            return
        print("\n  AVAILABLE BACKUPS (newest first)")
        for i, archive in enumerate(archives, 1):
            print(f"  [{i}] {archive.name}  ({_fmt_size(archive.stat().st_size)})")
        selected = input("  Backup number [1, newest] (blank cancels): ").strip()
        if not selected:
            warning("Restore cancelled.")
            return
        try:
            archive = archives[int(selected) - 1]
        except (ValueError, IndexError):
            warning("Invalid backup selection; nothing restored.")
            return
        destination_raw = input(f"  Restore destination [{root}]: ").strip()
        destination = Path(destination_raw).expanduser().resolve() if destination_raw else root.resolve()
        if not destination.is_dir():
            warning("Restore destination must be an existing directory; nothing restored.")
            return
        # Validate all members before writing: reject absolute paths and traversal.
        with zipfile.ZipFile(archive, "r") as z:
            members = z.infolist()
            unsafe = []
            for member in members:
                name = Path(member.filename)
                if name.is_absolute() or ".." in name.parts or not member.filename:
                    unsafe.append(member.filename)
            if unsafe:
                error("Backup contains unsafe paths; restore refused.")
                return
            files = [m for m in members if not m.is_dir()]
            existing = [destination / Path(m.filename) for m in files if (destination / Path(m.filename)).exists()]
            print(f"\n  BACKUP   {archive}")
            print(f"  DEST     {destination}")
            print(f"  FILES    {len(files)}")
            print(f"  OVERWRITE {len(existing)} existing file(s)")
            warning("Restore can overwrite files at the destination.")
            confirm_text = input("  Restore backup? [y/N] ").strip().lower()
            if confirm_text not in {"y", "yes"}:
                warning("Restore cancelled; no files changed.")
                return
            for member in files:
                target = (destination / Path(member.filename)).resolve()
                if target != destination and destination not in target.parents:
                    error("Archive path escaped destination; restore refused.")
                    return
            for member in files:
                target = destination / Path(member.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(member, "r") as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
        success(f"Restored {len(files)} file(s) from {archive.name} to {destination}")
        return

    if action != "1":
        warning("Unknown action; nothing changed.")
        return
    try:
        keep = max(1, int(input("  Keep newest backups [5]: ").strip() or "5"))
    except ValueError:
        keep = 5
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = backup_dir / f"{root.name}-{stamp}.zip"
    with spinner("Creating project backup"):
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
            for p in _files(root):
                z.write(p, p.relative_to(root))
    archives = sorted(backup_dir.glob(f"{root.name}-*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in archives[keep:]:
        old.unlink(missing_ok=True)
    success(f"Backup created: {target}")
    print(f"  Rotation: keeping {min(keep, len(archives))} backup(s).")


def _validate_dirs(a: Path, b: Path) -> tuple[Path, Path]:
    a, b = a.expanduser().resolve(), b.expanduser().resolve()
    if not a.is_dir() or not b.is_dir():
        raise ValueError("Kedua path harus folder yang sudah ada.")
    if a == b or a in b.parents or b in a.parents:
        raise ValueError("Folder tidak boleh sama atau saling berada di dalam folder lain.")
    return a, b


def sync_helper(root: Path) -> None:
    _header("Sync Helper", "Hash-based diff + safe two-folder sync")
    other = Path(input("  Other folder: ").strip()).expanduser().resolve()
    try:
        source, dest = _validate_dirs(root, other)
    except ValueError as exc:
        error(str(exc)); return
    diff = {"new": [], "changed": [], "same": []}
    for p in _files(source):
        rel = p.relative_to(source); q = dest / rel
        if not q.exists(): diff["new"].append(rel)
        elif q.is_file() and _hash(p) == _hash(q): diff["same"].append(rel)
        else: diff["changed"].append(rel)
    print(f"\n  SOURCE   {source}")
    print(f"  DEST     {dest}")
    print(f"  NEW      {len(diff['new'])}")
    print(f"  CHANGED  {len(diff['changed'])}")
    print(f"  SAME     {len(diff['same'])}")
    if not (diff["new"] or diff["changed"]):
        success("Folders are synchronized."); return
    if input("\n  Copy source → destination? [y/N]: ").strip().lower() not in {"y", "yes"}:
        warning("Sync cancelled."); return
    count = 0
    for p in _files(source):
        q = dest / p.relative_to(source)
        if q.exists() and p.relative_to(source) not in diff["changed"] and q.is_file():
            continue
        q.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, q); count += 1
    success(f"Synced {count} file(s).")


def sync_remote(root: Path) -> None:
    _header("Sync Remote", "Sync local project with an rclone remote")
    if not shutil.which("rclone"):
        error("rclone tidak ditemukan di PATH.")
        return
    remote = input("  rclone destination (example: gdrive:Projects/HIKARI): ").strip()
    if not remote or remote.startswith("-"):
        warning("Remote tidak valid."); return
    direction = input("  Direction [upload/download] (default upload): ").strip().lower() or "upload"
    if direction not in {"upload", "download"}:
        warning("Direction harus upload atau download."); return
    if direction == "upload":
        cmd = ["rclone", "copy", str(root), remote]
    else:
        cmd = ["rclone", "copy", remote, str(root)]
    if input(f"\n  Run: {' '.join(cmd)} [y/N]: ").strip().lower() not in {"y", "yes"}:
        warning("Remote sync cancelled."); return
    with spinner("Running rclone sync"):
        proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode:
        error(proc.stderr.strip() or "rclone failed")
        return
    success("Remote sync completed.")
    if proc.stdout.strip(): print(proc.stdout.strip())


def _quote_ident(name: str) -> str:
    """Quote a SQLite identifier using SQLite's double-quote escaping rule."""
    return '"' + name.replace('"', '""') + '"'


def color_note_exporter(root: Path) -> None:
    _header("ColorNote Exporter", "SQLite notes → Markdown + HTML")
    raw = input("  ColorNote database path: ").strip()
    db = Path(raw).expanduser().resolve()
    if not db.is_file():
        error("Database tidak ditemukan."); return
    out = Path.home() / ".hikari" / "exports" / "colornote"
    out.mkdir(parents=True, exist_ok=True)
    notes: list[str] = []
    try:
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
            for table in tables:
                cols = [r[1] for r in conn.execute(f"PRAGMA table_info({_quote_ident(table)})")]
                textcols = [c for c in cols if any(k in c.lower() for k in ("content", "text", "title", "note", "body"))]
                if not textcols: continue
                qtable = _quote_ident(table)
                qcols = ','.join(_quote_ident(c) for c in textcols)
                for row in conn.execute(f"SELECT {qcols} FROM {qtable}"):
                    vals = [str(v) for v in row if v not in (None, "")]
                    if vals: notes.append("\n".join(vals))
        finally:
            conn.close()
    except sqlite3.DatabaseError as exc:
        error(f"SQLite error: {exc}"); return
    if not notes:
        warning("Tidak ada note text yang bisa diekspor."); return
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    md = out / f"colornote-{stamp}.md"
    hp = out / f"colornote-{stamp}.html"
    md.write_text("# ColorNote Export\n\n" + "\n\n---\n\n".join(notes) + "\n", encoding="utf-8")
    cards = "".join(f"<article><pre>{html.escape(n)}</pre></article>" for n in notes)
    hp.write_text(f"<!doctype html><meta charset='utf-8'><title>ColorNote Export</title><h1>ColorNote Export</h1>{cards}", encoding="utf-8")
    success(f"Exported {len(notes)} note(s).")
    print(f"  Markdown: {md}")
    print(f"  HTML:     {hp}")


def miscellaneous(root: Path) -> None:
    """Native HIKARI hybrid of the useful Semut/YookAI file utilities."""
    tools = {
        "1": ("🌳", "TREE PRINTER", "dependency tree + orphan audit", tree_printer),
        "2": ("👁", "GHOST GREP", "smart project-wide search", ghost_grep),
        "3": ("🔐", "FILE HASHER", "SHA-256 + integrity verification", file_hasher),
        "4": ("💾", "BACKUP ROTATOR", "ZIP backup + retention rotation", backup_rotator),
        "5": ("🔄", "SYNC HELPER", "hash-based two-folder diff/sync", sync_helper),
        "6": ("🌐", "SYNC REMOTE", "rclone remote copy", sync_remote),
        "7": ("📝", "COLORNOTE EXPORTER", "SQLite notes → Markdown + HTML", color_note_exporter),
    }
    while True:
        _header("Miscellaneous", "HIKARI utility lab — project files, folders & integrity")
        print(color("  TARGET", CYAN) + f"  {root}")
        for key, (icon, name, desc, _) in tools.items():
            print(f"  {color('['+key+']', MAGENTA)} {icon}  {color(name, BOLD + WHITE):<22} {color(desc, DIM)}")
        print(f"  {color('[Q]', YELLOW)}  Back to Git/GitHub console")
        choice = input(color("\n  ❯ ", MAGENTA)).strip().lower()
        if choice == "q":
            return
        item = tools.get(choice)
        if not item:
            warning("Unknown utility. Choose 1-7 or Q.")
            _pause()
            continue
        try:
            item[3](root)
        except (OSError, ValueError, sqlite3.DatabaseError) as exc:
            error(str(exc))
        _pause()
