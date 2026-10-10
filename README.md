<div align="center">

# HIKARI /.LAB

**光 · Developer Automation Laboratory**

_Connect. Automate. Ship._

[![Version](https://img.shields.io/badge/version-0.6.8-03E1FF?style=flat-square)](https://github.com/nexterade/hikari/releases)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-00FFA3?style=flat-square)](LICENSE)
[![Made with](https://img.shields.io/badge/made%20with-%E2%9D%A4%EF%B8%8F-DC1FFF?style=flat-square)](#)

[Quick Start](#-quick-start) · [Commands](#-commands) · [Safety](#%EF%B8%8F-safety-first) · [Themes](#-themes) · [Docs](docs/) · [Troubleshoot](#-troubleshooting)

</div>

---

**HIKARI** adalah CLI interaktif untuk inspeksi project dan otomasi workflow Git/GitHub. Bekerja **pada folder target** — tidak perlu dipasang di dalam repo. Dashboard & utilitas lokal berjalan **tanpa internet dan tanpa Git**; operasi remote hanya saat dipilih eksplisit.

> 🛡️ **Safety-first.** Konfirmasi `[y/N]` — default selalu **N**. Baca prompt, tinjau target, backup untuk yang berisiko.

---

## ⚡ Quick Start

    # 1. Install
    git clone https://github.com/nexterade/hikari.git
    cd hikari && python -m pip install .

    # 2. Jalankan pada project target
    hikari /path/to/your/project

    # 3. Mulai dari yang read-only
    # Pilih: 1 — STATUS  atau  2 — SCAN

**Requirements:** Python 3.10+ · Git (untuk Git Mode) · `gh` (untuk fitur GitHub)

---

## 🎯 Commands

| Interactive | Non-interactive |
|---|---|
| `hikari /path` | `hikari /path status` · `scan` · `pull` · `push` · `sync` |
| Dashboard hybrid, 12 menu | `release patch` · `--current` · `--custom` · `--version v1.2.3` |
| Prompt `[0–12]` | `release-manager` · `undo-redo` · `force-sync` |

> ⚠️ `--yes` melewati konfirmasi. **Bukan** mode lebih aman. Gunakan hanya untuk otomasi dengan target terverifikasi.

---

## 🧭 12 Menu

| # | Menu | Fungsi |
|:-:|---|---|
| **1** | **STATUS** | Ringkasan target, Git state, riwayat. *Read-only.* |
| **2** | **SCAN** | Inventaris file, tipe, ukuran, Git summary |
| **3** | **PULL** | Ambil perubahan `origin` → lokal |
| **4** | **PUSH** | Kirim commit lokal ke remote |
| **5** | **SYNC** | Guided sync / **FORCE SYNC** (high risk) |
| **6** | **RELEASE** | Buat release / kelola GitHub Releases & tags |
| **7** | **REPOSITORY** | Init Git lokal / connect GitHub remote |
| **8** | **.GITIGNORE** | Lihat / buat / ganti sesuai stack |
| **9** | **MANAGE** | Undo/Redo & History/Log |
| **10** | **GIT GUIDE** | Glosarium Git/GitHub |
| **11** | **TROUBLESHOOT** | Diagnostik read-only |
| **12** | **MISC** | Tree, Grep, Hasher, Backup Rotator, dll |

### Status Riwayat

`SUCCESS` · `FAILED` · `CANCELLED` · `BLOCKED` — disimpan **di luar** folder project. Token & credential **tidak** disimpan.

---

## 🛡️ Safety-first

Konfirmasi interaktif: **`[y/N]`** → default **N**.

| Tindakan | Risiko | Cek Sebelum Lanjut |
|---|---|---|
| **FORCE SYNC** | Perubahan lokal & untracked hilang | Branch, `origin`, backup |
| **Restore Backup** | File tujuan ditimpa | Arsip, tujuan, overwrite count |
| **Replace `.gitignore`** | Aturan project tertimpa | Preview & salinan lama |
| **Delete release/tag** | Referensi hilang dari scope | Nama persis & beda release vs tag |
| **Undo/Redo & Restore file** | Source/history berubah | Path, working tree, target commit |

> Jika target, branch, remote, atau tag **tidak sesuai harapan** → **batalkan.**

---

## 🎨 Themes

Default: **Solana-Inspired** — Ocean Blue × Surge Green × Purple Dino × Gray.

| Peran | Warna | Kode |
|---|---|---|
| **Primary accent** — prompt, section, menu | 🟦 Ocean Blue | `45` |
| **Label field** | 🟩 Surge Green | `49` |
| **Brand signature** — *hanya* "HIKARI" | 🟪 Purple Dino | `165` |
| **Value metadata** | ⬜ Gray | `245` |
| **Border & separator** | ⬛ Gray | `238` |

**Fallback:** `NO_COLOR=1` · `TERM=dumb` · terminal non-TTY.

---

## 📁 Structure

    hikari/
    ├── src/hikari/          # Source code
    │   ├── ui.py            # UI & rendering
    │   └── commands/        # Per-command modules
    ├── tests/               # Test suite
    ├── docs/                # Detail docs
    └── pyproject.toml

---

## 🧪 Development

    python -m pip install -e .               # Editable install
    python -m unittest discover -s tests -v  # Test semua
    python -m coverage run -m unittest discover -s tests

> Perubahan workflow **wajib disertai regression tests** — terutama operasi yang mengubah file, history, tag, atau remote.

---

## 🔧 Troubleshooting

| Masalah | Solusi |
|---|---|
| `hikari: command not found` | `python -m pip install .` atau `python -m hikari` |
| Python terlalu lama | Cek `python --version` (butuh 3.10+) |
| Git tidak ditemukan | `git --version`, cek `PATH`. Local Mode tetap jalan. |
| `origin` hilang | `git remote -v` → **REPOSITORY** untuk connect |
| `gh` belum login | `gh auth status` |
| PUSH ditolak (dirty) | `git status` → commit/stash dulu |
| Warna berantakan | `NO_COLOR=1 hikari /path` |

Detail lengkap → [docs/TUTORIAL.md](docs/TUTORIAL.md) · [docs/SECURITY.md](docs/SECURITY.md) · [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🤝 Contributing

    git checkout -b feat/nama-fitur
    git commit -m "feat: deskripsi"
    git push origin feat/nama-fitur

**Conventional Commits:** `feat:` · `fix:` · `docs:` · `refactor:` · `test:` · `chore:`

---

<div align="center">

**HIKARI /.LAB** · _Connect. Automate. Ship._

光 · MIT License

</div>