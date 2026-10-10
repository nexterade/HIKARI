<div align="center">

# HIKARI /.LAB

**光 · Developer Automation Laboratory**  
*Connect. Automate. Ship.*

[Quick Start](#quick-start) · [Dashboard](#12-menu-dashboard-hybrid) · [Tutorial](#tutorial-local-mode-dan-git-mode) · [Safety](#protokol-keselamatan-konfirmasi-y--n)

**Version `0.6.8`** · Python CLI · Local-first · Safety-first

</div>

---

HIKARI /.LAB adalah CLI interaktif untuk inspeksi project dan otomasi workflow Git/GitHub. HIKARI bekerja **pada folder project target**—bukan harus dipasang di dalam repository tersebut. Dashboard dan utilitas lokal dapat digunakan tanpa internet dan tanpa Git; operasi remote hanya berjalan ketika dipilih secara eksplisit.

> **Safety baseline:** baca prompt sebelum menjawab, tinjau target dan dampak, buat backup untuk perubahan berisiko, dan batalkan jika ragu. Konfirmasi interaktif menggunakan **`[y/N]`**: default selalu **N (tidak)**.

## Daftar isi

- [Quick Start](#quick-start)
  - [Clone melalui SSH](#clone-melalui-ssh-opsional)
- [Requirements](#requirements)
- [Cara menjalankan CLI](#cara-menjalankan-cli)
- [12 menu dashboard hybrid](#12-menu-dashboard-hybrid)
- [Tutorial Local Mode dan Git Mode](#tutorial-local-mode-dan-git-mode)
- [PUSH, SYNC, dan RELEASE](#push-sync-dan-release)
- [Release Manager](#release-manager)
- [Undo / Redo](#undo--redo)
- [Backup Rotator dan pemulihan](#backup-rotator-dan-pemulihan)
- [Protokol keselamatan konfirmasi Y / N](#protokol-keselamatan-konfirmasi-y--n)
- [Git Guide ringkas](#git-guide-ringkas)
- [Troubleshooting](#troubleshooting)
- [Dokumentasi pendukung](#dokumentasi-pendukung)

## Quick Start

### 1. Siapkan Python dan Git

Pastikan Python 3.10 atau lebih baru tersedia. Git diperlukan untuk workflow Git; GitHub CLI `gh` hanya diperlukan untuk fitur GitHub tertentu.

```bash
python --version
git --version
```

### 2. Clone repository HIKARI

Clone repository resmi HIKARI dari GitHub menggunakan URL HTTPS berikut: [`https://github.com/nexterade/HIKARI`](https://github.com/nexterade/HIKARI).

```bash
git clone https://github.com/nexterade/HIKARI.git
cd HIKARI
```

Perintah clone di atas membuat folder lokal `HIKARI`. Pastikan folder tersebut berisi `pyproject.toml` sebelum melanjutkan instalasi.

Verifikasi bahwa folder dan branch yang aktif benar:

```bash
git status
git remote -v
```

### 3. Pasang HIKARI

Jalankan dari root repository HIKARI yang berisi `pyproject.toml`:


```bash
python -m pip install .
```

Perintah ini memasang package dan menyediakan command `hikari`. Untuk pengembangan lokal, gunakan editable install:

```bash
python -m pip install -e .
```

### 4. Buka dashboard untuk project target

```bash
hikari /path/to/your/project
```

Atau jalankan dari dalam folder target:

```bash
cd /path/to/your/project
hikari
```

Untuk Android/Termux, gunakan path folder yang benar-benar tersedia di perangkat, misalnya folder di bawah `$HOME` atau penyimpanan bersama setelah izin akses dikonfigurasi.

### 5. Mulai dari tindakan read-only

Pilih **`1 — STATUS`** untuk ringkasan kesehatan atau **`2 — SCAN`** untuk inventaris. Periksa nama project dan path target di dashboard sebelum menjalankan operasi yang mengubah file, Git, atau remote.

### Clone melalui SSH (opsional)

Jika akun dan SSH key Git hosting sudah dikonfigurasi, gunakan URL SSH yang diberikan oleh pemilik repository:

```bash
git clone git@github.com:nexterade/HIKARI.git
cd HIKARI
python -m pip install .
```

Jangan menempelkan token akses ke URL/perintah yang tersimpan di shell history. Jika clone gagal karena akses, verifikasi URL dan izin repository terlebih dahulu.

## Requirements

| Komponen | Kebutuhan | Kapan diperlukan |
|---|---|---|
| Python | 3.10+ | Runtime HIKARI |
| Git | Instalasi Git yang dapat dipanggil sebagai `git` | Git Mode dan operasi repository |
| GitHub CLI | `gh` | Membuat/mengelola GitHub Release dan operasi GitHub yang didukung |
| Autentikasi `gh` | Sesi `gh` yang valid | Aksi GitHub yang memerlukan akun |
| Internet | Tidak selalu | Hanya untuk operasi remote/GitHub |

Periksa autentikasi GitHub CLI bila diperlukan:

```bash
gh auth status
```

HIKARI tidak menyimpan token atau password GitHub. Autentikasi dikelola oleh tool eksternal yang bersangkutan.

## Cara menjalankan CLI

### Dashboard interaktif

```bash
hikari /path/to/project
```

Dashboard hybrid menampilkan **TARGET PROJECT**, **HIKARI DASHBOARD**, dan **OPERATIONS / 12 MODULES** dalam satu layar. Masukkan ID menu yang tampil. `0`, `X`, atau `Q` digunakan untuk keluar sesuai prompt yang sedang aktif; di submenu, ikuti petunjuk kembali yang ditampilkan.

### Perintah langsung

```bash
hikari /path/to/project status
hikari /path/to/project scan
hikari /path/to/project pull
hikari /path/to/project push
hikari /path/to/project sync
hikari /path/to/project force-sync
hikari /path/to/project release patch
hikari /path/to/project release --current
hikari /path/to/project release --custom
hikari /path/to/project release --version v1.2.3
hikari /path/to/project release-manager
hikari /path/to/project undo-redo
```

Alias kompatibilitas `action-status` juga tersedia. Perintah langsung dapat melewati wizard interaktif; baca `--help` dan pastikan target benar sebelum menjalankannya. Flag `--yes` tersedia pada perintah tertentu untuk otomasi dan melewati konfirmasi. **Gunakan hanya pada target terverifikasi dan setelah memahami dampaknya**, terutama `force-sync`.

```bash
hikari --help
hikari /path/to/project release --help
```

## 12 menu dashboard hybrid

Dashboard utama menggunakan 12 menu berurutan. Beberapa fungsi lama digabung ke submenu agar navigasi lebih ringkas tanpa menghapus kapabilitas inti.

| ID | Menu | Fungsi |
|---:|---|---|
| 1 | **STATUS** | Ringkasan target, versi, lokasi, inventaris, status Git, branch/remote/upstream, perubahan working tree, commit terakhir, dan riwayat aksi HIKARI. Read-only. |
| 2 | **SCAN** | Inventaris file, tipe file, ukuran, file terbesar, waktu modifikasi, dan ringkasan perubahan Git jika tersedia. |
| 3 | **PULL** | Mengambil perubahan dari `origin` ke branch lokal; memerlukan Git dan remote. Periksa working tree dan kemungkinan konflik terlebih dahulu. |
| 4 | **PUSH** | Mengirim commit ke remote. Perubahan lokal belum di-commit tidak ikut terkirim tanpa pilihan eksplisit commit + push. |
| 5 | **SYNC** | Submenu: `[1]` guided sync/reconciliation dan `[2]` FORCE SYNC berisiko tinggi. Force sync dapat membuang perubahan lokal dan file untracked; default konfirmasi `N`. |
| 6 | **RELEASE** | Submenu untuk membuat release atau mengelola GitHub Releases dan tag lokal/remote. Penghapusan membutuhkan konfirmasi. |
| 7 | **REPOSITORY** | Submenu untuk inisialisasi Git lokal atau membuat/menghubungkan/mengubah remote GitHub. Tidak mengunggah file secara otomatis. |
| 8 | **.GITIGNORE** | Melihat, memeriksa, membuat, atau mengganti rekomendasi `.gitignore` berdasarkan stack project. Penggantian file yang ada memerlukan konfirmasi. |
| 9 | **MANAGE** | Submenu **UNDO / REDO** dan **HISTORY / LOG** untuk pemulihan aman, commit, tag, upstream, dan divergence. |
| 10 | **GIT GUIDE** | Glosarium singkat Git/GitHub dan panduan memilih tindakan dengan lebih aman. |
| 11 | **TROUBLESHOOT** | Diagnostik read-only untuk perubahan belum di-commit, remote/upstream yang hilang, divergence, dan kemungkinan unrelated histories. Memberi saran; tidak memperbaiki otomatis. |
| 12 | **MISC** | Utilitas file/folder lokal, termasuk Tree Printer, Ghost Grep, File Hasher, Backup Rotator, Sync Helper, Sync Remote, dan ColorNote Exporter. |


### Riwayat hasil aksi

Riwayat aksi baru di menu **STATUS** memakai status terminal `SUCCESS`, `FAILED`, `CANCELLED`, atau `BLOCKED`, disertai ringkasan singkat hasil atau alasan aksi tidak dilanjutkan. Ringkasan memprioritaskan hasil konkret dari operasi/utilitas, termasuk tindakan read-only dan partial success ketika langkah lanjutan gagal atau publikasi remote dilewati. Contohnya, operasi Git dari Local Mode dicatat sebagai `BLOCKED`, sementara pembatalan eksplisit dicatat sebagai `CANCELLED`. Riwayat tetap dibatasi dan disimpan di luar folder project; output terminal, token, dan credential tidak disimpan.

### Submenu gabungan

- **5 — SYNC:** `[1] Guided SYNC` atau `[2] FORCE SYNC (HIGH RISK)`. Tinjau backup dan perubahan lokal sebelum memilih force sync.
- **6 — RELEASE:** `[1] Create a release` atau `[2] Manage GitHub Releases and Git tags`.
- **7 — REPOSITORY:** `[1] Initialize local Git history` atau `[2] Create/connect/change GitHub repository`. Repository Profile Generator tersedia saat membuat repository GitHub baru.
- **9 — MANAGE:** `[1] UNDO / REDO` atau `[2] HISTORY / LOG`.

## Repository Profile Generator (menu 7)

Saat memilih **7 — REPOSITORY → [2] Create/connect/change GitHub repository → Create a new GitHub repository**, HIKARI menawarkan generator metadata profil repository. Generator ini membaca `pyproject.toml`, README, dan nama direktori lokal secara deterministik; tidak mengirim isi project ke layanan AI dan tidak membutuhkan network untuk menyusun saran.

Alur aman:

1. Pilih membuat repository baru dan tentukan nama serta visibility.
2. Pada prompt `[y/N]`, jawab `Y` untuk menghasilkan About dan Topics; default `N` melewati generator.
3. Tinjau preview. Pilih konfirmasi untuk menggunakan saran; About dapat diedit sebelum pembuatan.
4. Konfirmasi pembuatan repository GitHub secara terpisah. Default tetap `N`.
5. About diterapkan saat pembuatan, kemudian Topics diterapkan melalui GitHub CLI. Jika penerapan Topics gagal, repository tetap dibuat dan HIKARI menampilkan peringatan.

Generator hanya memberi saran, bukan jaminan klasifikasi sempurna. Periksa Topics dan deskripsi sebelum membagikan repository. Fitur ini hanya berlaku untuk **Create a new GitHub repository**, bukan koneksi URL repository yang sudah ada. Diperlukan `gh` yang terpasang dan sudah terautentikasi. Pembuatan repo tidak melakukan push commit atau file project.

## Tutorial: Local Mode dan Git Mode

### Local Mode — folder belum menjadi repository Git

1. Jalankan `hikari /path/to/project`.
2. Periksa **TARGET PROJECT** dan path absolutnya.
3. Mulai dengan `STATUS` atau `SCAN`; utilitas lokal dan dashboard tidak mensyaratkan Git.
4. Jika memang ingin mulai melacak perubahan, pilih `REPOSITORY → Initialize local Git history` setelah memastikan folder target benar.
5. Tinjau `.gitignore` sebelum membuat commit. File `.gitignore` yang sudah ada dipertahankan secara default.
6. Hubungkan remote melalui `REPOSITORY → GitHub repository` hanya bila diperlukan. Menginisialisasi Git atau mengatur remote tidak dengan sendirinya mengunggah file.

### Git Mode — folder sudah menjadi repository

1. Pastikan `git status` menunjukkan repository yang dimaksud dan periksa branch aktif.
2. Jalankan HIKARI pada folder tersebut; gunakan `STATUS`, `SCAN`, `HISTORY / LOG`, atau `TROUBLESHOOT` untuk memahami kondisi sebelum mengubah state.
3. Jika workflow membutuhkan remote, pastikan `origin` dan upstream benar.
4. Pilih `PUSH`, `PULL`, atau `SYNC` sesuai tujuan. Baca ringkasan dan prompt sebelum menyetujui.
5. Sebelum `FORCE SYNC`, RELEASE, atau pemulihan file, buat backup yang sesuai dan verifikasi apa yang akan ditimpa.

### `.gitignore` dan file project

HIKARI memberikan rekomendasi sesuai stack yang terdeteksi. File `.gitignore` yang sudah ada tidak diganti diam-diam. `REPOSITORY → Initialize local Git history` melewati pembuatan otomatis bila file tersebut sudah ada. Selalu tinjau hasil scan agar secret, credential, file build besar, dan data privat tidak ikut masuk ke Git.

## PUSH, SYNC, dan RELEASE

### PUSH

`PUSH` tidak membuat commit secara diam-diam. Jika working tree kotor, wizard menawarkan:

```text
[1] Commit changes + push
[2] Push existing commits only
[0] Cancel
```

Pilih opsi pertama hanya setelah meninjau file yang berubah dan pesan commit. Pesan commit dapat dikosongkan atau diisi `auto` untuk meminta HIKARI menyusun subject ringkas dari perubahan dan dokumentasi project. Jika `origin` tidak tersedia, PUSH berhenti dengan pesan prasyarat.

### SYNC

Dengan remote, SYNC memandu rekonsiliasi kondisi lokal/remote dan dapat menawarkan commit perubahan lokal sesuai pilihan pengguna. Tinjau ringkasan sebelum konfirmasi. Tanpa remote, SYNC tetap bekerja pada batas lokal yang didukung dan **tidak** mencoba push ke remote yang tidak ada. Bila branch divergen atau konflik muncul, jangan menebak strategi; baca `TROUBLESHOOT` dan periksa Git state secara langsung.

### RELEASE

Contoh:

```bash
hikari /path/to/project release patch
hikari /path/to/project release --current
hikari /path/to/project release --custom
hikari /path/to/project release --version v1.2.3
```

- **Quick release** menghitung versi SemVer berikutnya dari level yang dipilih.
- **Current** menggunakan versi yang terdeteksi dari metadata project.
- **Custom** meminta versi target yang ditentukan pengguna.
- RELEASE menandai snapshot source yang sudah di-commit; ia tidak otomatis menaikkan versi file project atau memasukkan perubahan working tree yang belum di-commit.
- Pastikan working tree bersih terlebih dahulu. Release notes diambil dengan memprioritaskan heading versi target yang tepat, lalu `Unreleased`; fallback berbasis commit ditandai sebagai draft.
- Tag atau GitHub Release yang sudah ada tidak ditimpa. Tanpa remote, HIKARI dapat membuat tag lokal saja. Publikasi GitHub memerlukan remote dan autentikasi `gh` yang valid.
- Dalam mode interaktif, preview catatan rilis dapat diedit, memuat draft tersimpan, atau menyimpan draft untuk digunakan lagi. Draft Markdown disimpan per project dan versi di HIKARI home (atau `HIKARI_HOME`), di luar repository target; menyimpan draft tidak membuat commit/tag atau memublikasikan release. Opsi `--yes` tetap menggunakan catatan yang dihasilkan tanpa prompt tambahan.

## Release Manager

Buka menu **6 — RELEASE → [2] Manage GitHub Releases and Git tags**. Alias CLI berikut tetap tersedia untuk kompatibilitas:

```bash
hikari /path/to/project release-manager
```

Fitur yang tersedia meliputi melihat daftar/detail GitHub Releases, menghapus GitHub Release tanpa otomatis menghapus tag-nya, melihat tag lokal, serta mengelola tag lokal dan remote sebagai tindakan terpisah. Setiap tindakan penghapusan memerlukan konfirmasi. Operasi GitHub memerlukan Git repository, remote yang sesuai, dan autentikasi `gh`.

> Menghapus halaman GitHub Release tidak sama dengan menghapus tag Git dan tidak menghapus commit dari history. Baca nama tag dan target sebelum mengonfirmasi.

## Undo / Redo

Buka menu **12 — UNDO / REDO** atau jalankan `hikari /path/to/project undo-redo`.

- **Undo last commit:** membuat commit `git revert` baru, bukan menulis ulang history.
- **Redo last undo:** hanya tersedia jika commit `HEAD` merupakan revert yang memenuhi syarat; membaliknya dengan commit baru.
- **Restore one file:** memulihkan perubahan unstaged pada satu file tracked yang dipilih secara eksplisit.

Undo/Redo commit mensyaratkan working tree bersih. Pemulihan file meminta path yang tepat dan konfirmasi. File staged dan untracked tidak termasuk dalam opsi pemulihan file ini. Periksa `git status` dan buat backup bila ragu.

## Backup Rotator dan pemulihan

Di dashboard pilih **12 — MISC → 4 — BACKUP ROTATOR**. Backup dibuat sebagai ZIP dari file project yang dipilih oleh enumerator file HIKARI, dengan rotasi retensi.

### Membuat backup

1. Pilih **CREATE BACKUP**.
2. Tentukan folder backup, atau gunakan default `~/.hikari/backups`.
3. Tentukan jumlah backup terbaru yang ingin dipertahankan; default **5**.
4. HIKARI membuat ZIP bertimestamp, lalu menghapus arsip lama yang melewati batas retensi untuk nama project tersebut.
5. Catat lokasi arsip yang ditampilkan dan pastikan file ZIP ada sebelum melakukan operasi berisiko.

Simpan salinan backup penting di lokasi terpisah dari perangkat/folder project bila memungkinkan. Backup lokal bukan pengganti backup off-device. Periksa isi ZIP sebelum mengandalkannya; jangan masukkan secret yang tidak perlu ke arsip.

### Memulihkan backup

1. Pilih **RESTORE BACKUP** dan tentukan direktori backup.
2. Pilih arsip project yang benar dari daftar (terbaru ditampilkan lebih dahulu).
3. Pilih folder tujuan yang **sudah ada**. Default adalah folder project saat ini.
4. Baca ringkasan arsip, tujuan, jumlah file, dan jumlah file yang akan ditimpa.
5. Jika ada keraguan, batalkan dan salin folder tujuan ke lokasi cadangan terlebih dahulu.
6. Ketik `Y` hanya jika target dan overwrite sudah dipahami. Jawaban kosong atau selain `Y` membatalkan pemulihan.

HIKARI menolak path arsip yang absolut atau mengandung traversal `..`, lalu memvalidasi target agar tetap berada di direktori tujuan. Pemulihan tetap dapat **menimpa file yang ada** dan menulis file dari arsip; ini bukan operasi merge dua arah. Gunakan folder kosong sebagai tujuan pemulihan paling aman bila ingin memeriksa isi sebelum mengganti project aktif.

## Protokol keselamatan konfirmasi Y / N

Konfirmasi interaktif memakai pola **`[y/N]`**. Artinya:

- `Y` atau `yes` menyetujui tindakan yang dijelaskan prompt.
- `N`, jawaban kosong, atau input lain membatalkan tindakan.
- Jangan menjawab sebelum memahami **aksi, target, dampak, dan kemungkinan overwrite/penghapusan**.
- Jika nama project/path, branch, remote, tag, file, atau tujuan restore tidak sesuai harapan, batalkan.
- Untuk operasi berisiko, periksa status dan buat backup/commit/branch penyelamat sebelum melanjutkan.
- `--yes` dapat melewati prompt pada perintah yang mendukungnya. Itu bukan mode yang lebih aman; gunakan hanya untuk otomasi terencana dengan target yang telah diverifikasi.

### Tindakan yang butuh perhatian khusus

| Tindakan | Risiko utama | Pemeriksaan sebelum lanjut |
|---|---|---|
| FORCE SYNC | Perubahan lokal dan file untracked dapat hilang | Branch aktif, `origin`, status, backup |
| Restore Backup | File tujuan dapat ditimpa | Arsip, tujuan, jumlah overwrite, backup tujuan |
| Replace `.gitignore` | Aturan ignore project tertimpa | Preview dan salinan aturan lama |
| Delete release/tag | Referensi release/tag dihapus dari scope terkait | Nama persis dan perbedaan release vs tag |
| Restore file / Undo-Redo | Perubahan source atau history berubah | Path, working tree, commit yang menjadi target |

## Git Guide ringkas

- **Working tree:** file saat ini dibandingkan dengan snapshot commit terakhir.
- **Commit:** snapshot lokal dalam Git history; tidak otomatis mengunggah file.
- **Push:** mengirim commit lokal ke remote.
- **Pull:** mengambil dan mengintegrasikan perubahan remote ke branch lokal.
- **Sync:** istilah umum untuk merekonsiliasi keadaan lokal dan remote; strategi spesifik bergantung pada tool.
- **Branch:** jalur history terpisah.
- **Remote / `origin`:** nama koneksi ke repository lain, misalnya repository hosting.
- **Upstream:** branch remote yang terkait dengan branch lokal untuk operasi tracking.
- **Tag:** nama yang menunjuk pada commit tertentu, sering dipakai untuk versi.
- **GitHub Release:** halaman rilis di GitHub yang biasanya terkait dengan tag; bukan hal yang sama dengan tag.
- **Pull Request:** usulan perubahan untuk ditinjau/digabung di layanan hosting; bukan perintah `git pull`.
- **`.gitignore`:** aturan agar file untracked tertentu tidak ditawarkan Git untuk ditambahkan. Ia tidak otomatis menghapus file yang sudah tracked.

Aturan praktis: **commit menyimpan, push mengirim, pull mengambil, tag menamai snapshot, release mengumumkan versi**.

## Troubleshooting

### `hikari: command not found`

Pastikan instalasi berhasil dan environment Python aktif. Coba `python -m pip install .` dari root HIKARI. Jika tidak ingin memasang package, jalankan modul dari environment yang memiliki source tersedia: `python -m hikari`.

### Python terlalu lama

Periksa `python --version`; gunakan Python 3.10+. Pada sistem yang memisahkan executable, coba `python3 --version` dan `python3 -m pip install .`.

### Git tidak ditemukan atau menu Git tidak tersedia

Pastikan `git --version` berhasil dan Git ada di `PATH`. Local Mode tetap dapat dipakai untuk inspeksi/utilitas lokal; Git-dependent operations memerlukan Git dan repository yang sesuai.

### Remote `origin` tidak ditemukan

Periksa `git remote -v`. Jika project memang perlu remote, gunakan **REPOSITORY → GitHub repository** untuk menghubungkan repository yang benar. Menghubungkan remote tidak otomatis push file.

### `gh` belum login atau GitHub Release gagal

Jalankan `gh auth status`, lalu lakukan login melalui alur resmi GitHub CLI jika perlu. Pastikan remote mengarah ke repository yang benar. HIKARI tidak menyimpan credential dan tidak dapat menggantikan izin akun yang kurang.

### PUSH menolak karena working tree kotor

Tinjau `git status`. Pilih commit + push hanya jika perubahan siap dicatat; jika tidak, commit/stash secara sadar atau batalkan. PUSH menyediakan opsi untuk mengirim commit yang sudah ada tanpa memasukkan perubahan baru.

### Branch divergen, upstream hilang, atau histories tidak terkait

Jalankan **MANAGE → HISTORY / LOG** untuk meninjau commit dan tag, atau **11 — TROUBLESHOOT** untuk diagnosis read-only. Jangan langsung force-push atau force-sync sebelum memastikan history mana yang harus dipertahankan.

### RELEASE menolak karena working tree kotor atau tag sudah ada

Commit/stash perubahan yang relevan terlebih dahulu dan periksa tag lokal/remote serta daftar GitHub Releases. HIKARI tidak menimpa tag atau release yang sudah ada secara diam-diam.

### Backup tidak ditemukan atau pemulihan ditolak

Pastikan folder backup benar, nama arsip sesuai pola `<nama-project>-*.zip`, dan tujuan restore sudah ada. Jika ZIP dianggap memiliki path tidak aman, jangan memaksakan ekstraksi; gunakan arsip lain atau periksa arsip di lingkungan terpisah.

### Output terminal berantakan / warna tidak sesuai

HIKARI mendukung fallback tanpa warna untuk terminal yang tidak mendukung warna, `NO_COLOR`, atau `TERM=dumb`. Coba terminal lain atau nonaktifkan warna sesuai dukungan environment.

## Dokumentasi pendukung

- [`PROJECT_BOOT.md`](PROJECT_BOOT.md) — instruksi bootstrap dan canonical test.
- [`PROJECT_CONTINUATION.md`](PROJECT_CONTINUATION.md) — ringkasan handoff/continuation.
- [`docs/CHECKPOINT.md`](docs/CHECKPOINT.md) — checkpoint, governance, dan konteks operasional yang wajib dibaca.
- [`docs/STATE.md`](docs/STATE.md) — state project yang tercatat.
- [`docs/BACKLOG.md`](docs/BACKLOG.md) — pekerjaan tertunda.
- [`docs/CHANGELOG.md`](docs/CHANGELOG.md) — riwayat perubahan.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — batas arsitektur dan sumber kebenaran.
- [`docs/TUTORIAL.md`](docs/TUTORIAL.md) — tutorial workflow lebih lengkap.
- [`docs/SECURITY.md`](docs/SECURITY.md) — baseline keamanan dan klasifikasi data.
- [`docs/RELEASE-MANIFEST.md`](docs/RELEASE-MANIFEST.md) — catatan manifest release.
- [`docs/DASHBOARD-SIMPLE-MODE.md`](docs/DASHBOARD-SIMPLE-MODE.md) — catatan dashboard/navigation.
- [`docs/Creation-Chronicle.html`](docs/Creation-Chronicle.html) — kronik historis project.
- [`docs/Glosarium.html`](docs/Glosarium.html) — glosarium istilah.

## Development dan test

Dari root repository HIKARI:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

HIKARI adalah lapisan orkestrasi tipis, bukan pengganti Git atau GitHub CLI. Source project dan state Git tetap menjadi acuan utama. Perubahan perilaku workflow harus disertai regression tests, khususnya untuk operasi yang mengubah file, history, tag, atau state remote.

---

<div align="center">

**HIKARI /.LAB** · *Connect. Automate. Ship.*

</div>
