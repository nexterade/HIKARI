# HIKARI/.LAB — Tutorial

## 1. Run the wizard

HIKARI can start against a normal project folder or an existing Git repository:

```bash
hikari /path/to/project
```

From inside the target project:

```bash
cd /path/to/project
hikari
```

The first screen combines the TARGET project/path, live project status, and all 12 operations. Horizontal separators divide TARGET, DASHBOARD, and OPERATIONS; the active target path stays visible on the same screen as the menu. A missing Git repository or missing remote is a mode/state, not a fatal startup error.

## 2. Local Mode

For a project that is not a Git repository, HIKARI still provides:

- local version detection
- project overview
- local file scan/audit
- `.gitignore` generation
- offline/local utilities

Use **Init Repo** when you want to turn the same project into a Git repository:

```text
10  INIT REPO
```

Initialization does not upload anything.

## 3. Configure a GitHub repository

Use menu item `11 GITHUB REPO` to create a new GitHub repository or connect an existing GitHub HTTPS/SSH URL. Creating a repository requires a local Git repository, an authenticated GitHub CLI (`gh`), an explicit private/public choice, and confirmation. HIKARI configures `origin` but does not push project files during creation. Use `PUSH` or `SYNC` separately when ready. Connecting an existing URL only configures `origin`; it does not upload files.

### Repository Profile Generator (menu 11)

Saat membuat repo baru lewat `11 — GITHUB REPO`, jawab `Y` pada prompt `[y/N]` untuk menghasilkan About dan Topics dari README serta `pyproject.toml`. HIKARI menampilkan preview; About dapat diedit. Setelah itu ada konfirmasi terpisah untuk membuat repository GitHub (default `N`). About disertakan saat pembuatan dan Topics ditambahkan setelah remote dibuat. Generator bersifat lokal/deterministik dan tidak menggunakan layanan AI. Jika Topics gagal diterapkan, repository tidak dihapus; tambahkan Topics secara manual di GitHub Settings. Fitur ini tidak berjalan saat hanya menghubungkan URL repository yang sudah ada.

## 4. Scan changes

```bash
hikari /path/to/project scan
```

In Git Mode, the scanner reads `git status --porcelain` and reports modified, added, deleted, and other working-tree entries. In Local Mode it performs a file/project audit without requiring Git.

## 4. Pull

```bash
hikari /path/to/project pull
```

Pull requires a Git repository with an `origin` remote.

## 5. Push

```bash
hikari /path/to/project push
```

If the working tree is clean, HIKARI publishes existing commits. If uncommitted changes exist, interactive PUSH offers:

```text
[1] Commit changes + push
[2] Push existing commits only
[0] Cancel
```

HIKARI never silently creates a commit just because PUSH was selected.

If no `origin` remote exists, PUSH stops with a clear HIKARI-native message instead of invoking `git push origin ...` blindly.

## 6. Sync

```bash
hikari /path/to/project sync
```

With a remote, Sync can pull/reconcile, commit local changes when requested, and push.

Without a remote, Sync remains local: it may create a local commit but never attempts to push to a nonexistent `origin`.

## 7. .GITIGNORE

Select `.GITIGNORE` from the wizard.

If a `.gitignore` already exists:

```text
[1] View
[2] Scan / validate
[3] Replace with recommended
[0] Back
```

Replacement requires explicit confirmation.

If none exists:

```text
[1] Yes
[2] Show preview
[0] Skip
```

The generated recommendation is based on the target project's detected stack. `INIT REPO` also respects an existing `.gitignore` and skips generation automatically.

## 8. Release

```bash
hikari /path/to/project release patch
```

The interactive menu offers **Quick Release** (suggest next SemVer), **Force Release Current** (use the version already declared by project metadata), and **Custom Version**. CLI examples:

```bash
hikari /path/to/project release patch
hikari /path/to/project release --current
hikari /path/to/project release --custom
hikari /path/to/project release --version v1.2.3
```

RELEASE publishes the current committed source snapshot; it does not bump version files or silently commit unrelated working-tree edits. If the working tree is dirty, commit or stash changes first. Release notes prefer an exact target heading, then `Unreleased`, then a clearly labeled commit-derived draft. Existing local/remote tags and existing GitHub Releases are never overwritten. If `gh` cannot verify remote release state, HIKARI stops safely. Without a remote, only a local tag is created. In interactive mode, the preview lets you use the generated notes, edit Markdown one line at a time (finish with a single `.` line), load a saved draft, or save the current draft. Drafts live outside the target repository under HIKARI home (override with `HIKARI_HOME`). Saving a draft does not publish or tag a release. The `--yes` mode does not prompt for editing.

## 9. Force Sync

```bash
hikari /path/to/project force-sync
```

Force Sync is destructive: it aligns the current branch with `origin/<branch>` and removes untracked files. Confirmation is mandatory by default.

Automation may explicitly opt in:

```bash
hikari /path/to/project force-sync --yes
```

## Requirements

- Python 3.10+
- Git for Git Mode operations
- GitHub CLI (`gh`) for GitHub Release creation
- Authenticated `gh` session for publishing GitHub releases


## RELEASE & MANAGER

Open menu option `6 — RELEASE & MANAGER`. Choose `[1]` to create a release or `[2]` to manage GitHub Releases and Git tags. The direct CLI alias `hikari release-manager` remains available for compatibility. You can list GitHub Releases, view details, delete a GitHub Release while keeping its Git tag, list local tags, or delete local/remote tags separately. Every deletion asks for confirmation. Deleting a GitHub Release does not delete tags or rewrite Git history. GitHub actions require `origin` and authenticated `gh`.

## Undo / Redo

From the main menu choose `13 — UNDO / REDO`. `Undo last commit` creates a new `git revert` commit rather than rewriting history. `Redo last undo` is available only when the current HEAD commit is a revert and creates another commit to reverse it. `Restore one file` lists unstaged tracked-file changes and asks for the exact path and confirmation; staged and untracked files are intentionally excluded. Commit undo/redo requires a clean working tree.


## STATUS and SCAN reports

Choose `1 — STATUS` for a combined project/repository health report and recent HIKARI action history. It includes location, timestamp, file inventory and size, latest modified file, version, Git branch/remote/upstream, working-tree counts, and last commit.

Choose `2 — SCAN` for a deeper inventory: file types, largest files, sizes and timestamps, plus Git change totals and paths when the target is a repository. Common VCS, dependency, and cache directories are excluded from the inventory to keep reports useful and avoid counting generated bulk.


## Beginner guide: what the Git words mean

Use main-menu option `13 — GIT GUIDE` whenever a term is unfamiliar. In short:

- **Commit:** save a snapshot into local Git history; it does not upload files.
- **Push:** send saved commits to a remote copy, such as GitHub.
- **Pull:** bring remote commits into the current local branch. It is different from a **Pull Request**, which proposes changes for review/merge.
- **Branch:** a separate line of work. **Merge** combines branch changes.
- **Remote/origin:** the named connection to another repository.
- **Tag:** a label pointing to one commit. **Release:** a version announcement/page, commonly built around a tag and release notes.
- **Clone:** create a local copy of a remote repository.
- **.gitignore:** tell Git which untracked files to normally ignore.

### Which HIKARI action should I choose?

- Want to understand project/repository state? Choose **STATUS**. Want detailed file inventory and change paths? Choose **SCAN**.
- Want to bring remote work to this device? Choose **PULL**. Want to send saved local commits to the remote? Choose **PUSH**.
- Want guided synchronization? Choose **SYNC**. Read the proposed action and confirm only if it matches your intention.
- Want to mark/publish a version? Choose **RELEASE**. This is different from opening a Pull Request.
- Want to discard/reset local state to match origin? **FORCE SYNC is high risk** and may delete untracked files. Back up or commit important work first.
- **INIT REPO** starts local Git tracking and does not upload files. **GITHUB REPO** creates/connects a remote but does not upload files by itself.

When unsure, choose `0`/cancel and consult GIT GUIDE first.


## Category dashboard (v0.5.5)

The interactive menu is organized into five categories:

1. **Project Overview** — STATUS and SCAN.
2. **Git Workflow** — PULL, PUSH, SYNC, FORCE SYNC, HISTORY / LOG.
3. **GitHub & Releases** — RELEASE & MANAGER, GITHUB REPO.
4. **Diagnostics & Recovery** — AUTO TROUBLESHOOT and UNDO / REDO.
5. **Learn & Utilities** — GIT GUIDE, .GITIGNORE, MISCELLANEOUS, INIT REPO.

If a Git operation is chosen in Local Mode, HIKARI explains why Git is needed and offers to route to `INIT REPO`. Initialization creates local Git metadata only; it does not upload files. If a remote is missing, HIKARI explains that a remote must be connected before PULL/PUSH/FORCE SYNC. Use `0` in a submenu to return to the dashboard.


## Hybrid dashboard navigation (v0.6.4)

The first screen shows the target project path, live project health, and the complete operation list (1–12) together. Each major section has a horizontal separator. Choose the exact operation ID shown in the list; `0`, `X`, or `Q` exits HIKARI. Dashboard status is read-only and does not fetch, commit, push, or modify project files by itself.


## Terminal orientation
The dashboard is intentionally kept in one column in both portrait and landscape so menu numbers and descriptions remain aligned. Long project paths, status summaries, and commit subjects wrap within a bounded terminal width; on narrow terminals the HIKARI banner switches to a compact form.
