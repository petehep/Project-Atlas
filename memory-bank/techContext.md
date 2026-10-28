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
| VCS | Git / GitHub (`petehep/project_atlas`) |

## Python version — IMPORTANT ambiguity
- `README.md` says **Python 3.13**.
- The handover dossier and `SETUP_WINDOWS.md` say **Python 3.12**.
- `__pycache__` artifacts exist for **3.12 and 3.14**.
- `requirements.txt` pins `PySide6==6.11.1` (abi3 wheels work across versions).
- **Action for future work:** confirm the actual interpreter (e.g. `python3 --version`
  inside `.venv`) before changing tooling. Windows wheels cached are `cp312` (3.12).

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
