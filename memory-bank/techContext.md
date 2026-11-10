# Tech Context — ATLAS

## Stack
| Concern | Choice |
|---------|--------|
| Language | Python |
| GUI / event loop | PySide6 (Qt6) — 6.11.1 |
| Data models | Pydantic 2.x |
| Persistence | **raw `sqlite3`** (SQLAlchemy is in requirements but *unused* in code) |
| Fonts / LED glyphs | Custom 5×7 bitmap font (`gui/fonts.py`) |
| Config | SQLite `settings` table (authoritative); legacy JSON vestigial |
| VCS | Git / GitHub (`petehep/Project-Atlas`) |

## Development vs deployment environment — IMPORTANT
- **Created & tested on:** Apple **Mac Mini M4** (macOS), user `petehep`.
- **Installed & executed on:** a **Windows PC** in the field.
- Treat both as first-class: anything added on the Mac (dev) must also run on
  Windows (production). Watch cross-platform concerns — absolute vs relative
  paths, path separators, line endings (CRLF vs LF), Qt platform plugins, and
  launcher scripts (`run_atlas.sh` vs `run_atlas.bat`/`.ps1`).

## Python version — RESOLVED (was ambiguous)
- **Current interpreter: Python 3.13.18**, managed by **`uv`** (not Homebrew).
- History: README said 3.13, handover said 3.12, an old `.venv` was built on
  Homebrew Python 3.14. **Homebrew was later removed from the Mac**, which left
  `.venv/bin/python3` as a dangling symlink and broke the app.
- **Fix (done 2026-10-28):** rebuilt the venv with uv at 3.13.18.
- `requirements.txt` pins `PySide6==6.11.1` (abi3 wheels work across versions).
- Windows wheels cached are `cp312` (3.12).

## Rebuilding the macOS venv (if it breaks again)
```bash
cd ~/project_atlas
rm -rf .venv
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python -r requirements.txt
```
(`uv` is installed at `~/.local/bin/uv`; it auto-downloads CPython as needed.)

## Dependencies (`requirements.txt`)
- `PySide6`, `PySide6_Addons`, `PySide6_Essentials`, `shiboken6` == 6.11.1
- `pydantic` 2.13.4, `pydantic_core` 2.46.4
- `SQLAlchemy` 2.0.51 (present but not currently imported)
- `typing_extensions`, `typing-inspection`, `annotated-types`

## Running the app
- **macOS:** `./run_atlas.sh` — `cd`s to project root, activates `.venv`, sets
  `PYTHONPATH=.../src`, resolves the Qt platform plugin path, sets
  `QT_QPA_PLATFORM=cocoa`, then runs `python3 src/main.py`.
- **Windows:** `windows/run_atlas.bat` (double-click) or `windows/run_atlas.ps1`.
  Offline wheel cache lives in `windows/windows_packages/`.
- `src/main.py` forces **Fusion** style for cross-platform consistency.

## Setting up on a second machine (dev Mac)
VS Code **Settings Sync** transfers the editor config (settings, keybindings,
extensions — including the Cline extension) between the owner's Macs. It does
**NOT** transfer secrets, project files, or the venv.

**Carries over automatically:**
- Cline extension + other VS Code extensions
- VS Code settings / keybindings

**Does NOT carry over — redo these on machine 2:**
1. **Cline API key (DeepSeek)** — stored in the macOS Keychain (SecretStorage),
   deliberately not synced. Open Cline and paste the key once.
2. **Project files** — `~/project_atlas/` is not synced. Clone from GitHub:
   ```bash
   git clone https://github.com/petehep/Project-Atlas.git ~/project_atlas
   ```
3. **`.venv`** — gitignored + not synced. Rebuild with `uv`:
   ```bash
   cd ~/project_atlas
   uv venv .venv --python 3.13
   uv pip install --python .venv/bin/python -r requirements.txt
   ```
   (Install `uv` first if needed: `curl -LsSf https://astral.sh/uv/install.sh | sh`.)
4. **`data/atlas.db`** — runtime data; a fresh DB is auto-created on first launch.
5. **Desktop launcher `ATLAS.app`** — created manually on the Desktop (not in git);
   recreate it, or just run `./run_atlas.sh`.

The **memory bank** (`memory-bank/`) is committed to the repo, so it clones along
with the code.

## Environment constraints / gotchas
1. **iCloud corrupts PySide6.** Do NOT keep the project (or `.venv`) under
   `~/Documents`, `~/Desktop`, or `~/Downloads`. iCloud creates conflicted
   `.dylib` copies (e.g. `libqcocoa 2.dylib`) and strips permissions, causing
   `qt.qpa.plugin: Could not find ... "cocoa"` / `Abort trap: 6`. The project was
   moved to `~/project_atlas/` to escape iCloud. **Never move it back.**
2. **venv symlinks are path-specific** — moving the project requires rebuilding
   `.venv` (`rm -rf .venv && python3 -m venv .venv && pip install -r requirements.txt`).
3. `.venv/`, `__pycache__/`, `.DS_Store`, `.vscode/`, `*.log`, `*.db-journal`,
   `.agent/` are gitignored.
4. `data/atlas.db` is runtime-created; deleting it resets settings + heats.
5. Cross-platform DB path is `__file__`-relative (not CWD-relative).

## Hardware (planned / target)
- **Brain:** Intel NUC (Windows).
- **Public display path:** HDMI → NovaStar TB40 → HUB75 → P10 panels
  (64×32 = 4 panels, 2 wide × 2 tall). `AtlasHDMIOutput` renders a frameless
  64×32 px window for the TB40 to capture.
- **Power:** 200 Ah Lithium + DC-DC converters.
- CAD/STL files for the physical clock enclosure live in `3D Print Files/`.

## Workflow notes
- **User-provided images/screenshots** live in **`/Users/petehep/images/`** (`~/images`).
  When the owner says "I'll put images in petehep/images", look there first.
