# ATLAS Master Flightline Clock — Project Handover Dossier
## UPDATED VERSION — July 26, 2026 (Session 2)

> **Document Purpose:** Comprehensive handover for any future AI assistant working on Project ATLAS.
> Read every section before touching anything. Read the user's actual files before changing anything.
> **Previous handover:** `ATLAS_PROJECT_HANDOVER_Sun_26_July.md` (earlier today — now superseded by this document)
> **System Version:** v1.6.0 — fully working on Mac and ready for Windows deployment

---

## CRITICAL CHANGES SINCE LAST HANDOVER

These are the most important things that changed during Session 2. Read these first.

### 1. Project Location Changed (IMPORTANT)
The project was moved from `~/Documents/project_atlas/` to `~/project_atlas/`.
**Do not reference the old Documents path anywhere.** The new canonical location is:
```
/Users/petehep/project_atlas/
```

### 2. iCloud Was Destroying the PySide6 Install — Now Fixed
The recurring "cocoa platform plugin not found" crash was caused by iCloud Drive syncing the `.venv` folder and creating conflicted copies of Qt `.dylib` files. Moving the project out of `~/Documents/` permanently fixed this. Full details in Section 7.

### 3. Windows Deployment Files Created
A `windows/` subfolder now exists inside the project containing Windows-specific launcher scripts. The Mac source files were NOT modified for this — the launchers are completely separate. Full details in Section 9.

### 4. Two Source Files Patched
`src/core/database.py` and `src/gui/windows.py` have been updated with cross-platform fixes. These patches are applied on the Mac. Full details in Section 5.

### 5. Python Version Correction
The previous handover incorrectly stated Python 3.14. The actual version is **Python 3.12**. This has been corrected throughout this document.

---

## 1. Project Identity & Purpose

### What Is ATLAS?
**ATLAS** is a **specialised 6-row digital display system** designed to manage and synchronise race timing, pilot insertion windows, and heat data during competitive aviation events — specifically **F3K model glider competitions**.

It syncs with the local PC clock for real-time accuracy and guides pilots through two distinct phases:
1. **Pre-Race Phase** — Countdown to track opening, displaying upcoming heat info
2. **Active-Race Phase** — Live timing showing entry windows and heat countdowns

### User Context
- **User:** Peter ("petehep"), based in **Adelaide, South Australia**
- **Competition context:** F3K model glider events — multiple heats per day, each with defined track-open/track-close windows and thermalling directions
- **Target deployment:** Standalone "appliance" at a flying field — visible to pilots from a distance
- **Hardware ambitions:** Physical LED matrix panels (P5/P10) — currently using software simulator
- **Development machine:** MacBook Air (username `petehep`, macOS 15.5 Sequoia)
- **Target deployment hardware:** Windows PC (confirmed — Windows setup now complete)

### Communication Style — IMPORTANT
- Peter is direct, casual, and technical. Swearing is normal, don't be precious about it.
- He values things that work over elegant theory.
- **Do not change code without showing him first.**
- **Ask before assuming** — if files seem wrong or missing, ask him.
- If you break something, own it immediately and fix it cleanly without excuses.
- Humour is fine and welcome.

---

## 2. Current Project Location & Structure

### CANONICAL LOCATION (Updated Session 2)
```
/Users/petehep/project_atlas/
```
**NOT** `~/Documents/project_atlas/` — that location no longer exists. The project was moved to the home folder to prevent iCloud interference.

### Full Directory Structure
```
~/project_atlas/
├── .git/                           ← Git repository (active, many commits)
├── .gitignore                      ← Includes .venv/ — correct, do not remove
├── .venv/                          ← Python virtual environment (rebuilt fresh at new location)
├── archive/                        ← Old/archived files
├── assets/                         ← Static assets
├── atlas_config.json               ← Legacy JSON config (not used by main.py, harmless)
├── atlas.sh                        ← Legacy startup script (may be outdated)
├── config/                         ← Config directory
├── data/
│   └── atlas.db                    ← SQLite database (heats + settings)
├── docs/                           ← Project documentation (38 items)
├── requirements.txt                ← Python dependencies
├── run_atlas.sh                    ← PRIMARY MAC LAUNCHER (updated Session 2)
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               ← Legacy JSON config loader (not used, harmless)
│   │   ├── database.py             ← PATCHED Session 2 — cross-platform path fix
│   │   ├── engine.py               ← 1Hz state machine, heat phase logic (untouched)
│   │   ├── models.py               ← Pydantic data models (untouched)
│   │   └── timers.py               ← Legacy standalone timer (not used, harmless)
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── fonts.py                ← 5×7 bitmap font data (untouched, correct)
│   │   ├── lcd_display.py          ← Full-resolution LCD backend (added Session 1)
│   │   ├── led_simulator.py        ← LED pixel simulator (untouched)
│   │   ├── themes.py               ← Qt CSS styling constants (untouched)
│   │   └── windows.py              ← PATCHED Session 2 — EXIT TO DESKTOP fix
│   └── main.py                     ← Application entry point (updated Session 1)
├── tests/
├── tools/
└── windows/                        ← NEW Session 2 — Windows-specific files only
    ├── .gitkeep
    ├── run_atlas.bat               ← Windows CMD launcher
    ├── run_atlas.ps1               ← Windows PowerShell launcher
    └── SETUP_WINDOWS.md            ← Windows setup guide
```

### How to Launch on Mac
```bash
cd ~/project_atlas
./run_atlas.sh
```

The `run_atlas.sh` at the project root is the correct launcher. It handles venv activation, PYTHONPATH and Qt plugin path automatically.

If you get a permission denied error:
```bash
chmod +x run_atlas.sh
./run_atlas.sh
```

---

## 3. Technical Architecture

### Pattern: Model-View-Controller (MVC)
PySide6 (Qt for Python) + SQLite.

```
                      main.py
               (Entry point & wiring)
                    /           \
              CORE                  GUI
         engine.py            windows.py        (Operator Console)
         database.py          led_simulator.py  (LED display)
         models.py            lcd_display.py    (LCD display)
         timers.py*           fonts.py          (bitmap font data)
         config.py*           themes.py         (CSS styling)

         * = legacy, not actively used
```

### Signal/Slot Architecture
- **`engine.model_updated`** → `display.update_model(model)` — 1Hz tick
- **`engine.brightness_changed`** → `display.set_brightness(value)` — on operator slider change

### AtlasDisplayModel (Pydantic — the data contract)
```python
class AtlasDisplayModel(BaseModel):
    local_time: str = "00:00:00"
    primary_timer: str = "--:--"
    primary_timer_label: str = "SYSTEM IDLE"
    primary_timer_color: str = "#888888"
    band_color: str = "#333333"
    heat_number: str = "--"
    thermalling_dir: str = "---"
    is_armed: bool = False
    planned_open: str = "--:--"
    planned_close: str = "--:--"
```

### Display Backends
Two backends, selectable from Settings tab (requires restart):

| Backend | ID | File | Description |
|---|---|---|---|
| LED Simulator | `"simulator"` | `led_simulator.py` | Pixel-art LED emulation, 5×7 bitmap font |
| LCD Monitor | `"lcd"` | `lcd_display.py` | Full-resolution anti-aliased, system fonts |

Both implement the same interface: `update_model(model)` and `set_brightness(value)`.

Backend selected by factory function in `main.py`:
```python
def _create_display(backend_id, config):
    if backend_id == "lcd":
        return AtlasLCDDisplay(config)
    return AtlasLEDSimulator(config)
```

### Engine State Machine (1Hz)
1. No heats → `is_armed = False`, display: "WAITING"
2. Next heat > 15 min away → shows heat info, stays WAITING
3. Next heat ≤ 15 min away → auto-activates heat (status → 'ACTIVE')
4. Active, before track_open → Yellow "TRACK OPENS IN" countdown
5. Active, track open → Green "ENTER NOW" countdown
6. Active, track closed, heat not ended → Red "HEAT TIME REMAINING"
7. Heat ended → status → 'COMPLETED', cycle repeats

### Database Schema
SQLite at `data/atlas.db`

**heats table:**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| heat_number | TEXT | e.g. "01" |
| thermalling_dir | TEXT | "LEFT" or "RIGHT" |
| track_open | INTEGER | Unix timestamp |
| track_close | INTEGER | Unix timestamp |
| heat_end | INTEGER | Unix timestamp |
| status | TEXT | 'READY', 'ACTIVE', 'COMPLETED', 'CANCELLED' |

**settings table:**
| Key | Default | Notes |
|---|---|---|
| competition_name | "" | Event name |
| display_width | "128" | "128" or "64" |
| display_height | "64" | |
| led_scale | "8" | Pixel scale factor |
| brightness | "80" | 10–100 |
| display_backend | "simulator" | "simulator" or "lcd" |
| auto_boot_enabled | "0" | "0"=off, "1"=on |

---

## 4. Development Environment

| Item | Detail |
|---|---|
| Machine | MacBook Air |
| Username | `petehep` |
| macOS | 15.5 Sequoia |
| Python | 3.12 |
| Virtual env | `~/project_atlas/.venv/` |
| Key dependency | PySide6 6.11.1 |
| Git | Active, many commits, `.venv/` correctly in `.gitignore` |

---

## 5. Source File Patches Applied (Session 2)

### `src/core/database.py` — Cross-platform path hardening

**Problem:** Default `db_path="data/atlas.db"` is relative to the current working directory. Works on Mac because `run_atlas.sh` does `cd` first, but breaks on Windows if CWD is wrong.

**Fix:** Compute absolute path from `__file__` location:
```python
def __init__(self, db_path=None):
    if db_path is None:
        _this_file    = os.path.abspath(__file__)       # …/src/core/database.py
        _core_dir     = os.path.dirname(_this_file)     # …/src/core
        _src_dir      = os.path.dirname(_core_dir)      # …/src
        _project_root = os.path.dirname(_src_dir)       # …/project_atlas
        db_path = os.path.join(_project_root, "data", "atlas.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    self.db_path = db_path
```

**Status:** Applied on Mac ✅ | Included in Windows copy ✅

### `src/gui/windows.py` — Platform-neutral exit button

**Problem:** Exit button in Settings tab was labelled "EXIT TO MACOS" — wrong on Windows.

**Fix:** Single line change, line 270:
```python
# Before:
exit_btn = QPushButton("EXIT TO MACOS")
# After:
exit_btn = QPushButton("EXIT TO DESKTOP")
```

**Status:** Applied on Mac ✅ | Included in Windows copy ✅

---

## 6. Mac Launcher — `run_atlas.sh`

Current content of `~/project_atlas/run_atlas.sh` (updated Session 2, all band-aids removed):

```bash
#!/bin/bash

# Navigate to project root (wherever this script lives)
cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Set PYTHONPATH so Python finds the src/ packages
export PYTHONPATH=$(pwd)/src

# Set Qt plugin path for PySide6 on macOS
export QT_QPA_PLATFORM_PLUGIN_PATH=$(python3 -c "import PySide6, os; print(os.path.join(os.path.dirname(PySide6.__file__), 'Qt', 'plugins', 'platforms'))")
export QT_QPA_PLATFORM=cocoa

# Launch Atlas
python3 src/main.py
```

**Note:** Uses `python3` not `python` — macOS 15 does not have a bare `python` command.

---

## 7. The iCloud Problem — Root Cause & Permanent Fix

### What Was Happening
The project was in `~/Documents/project_atlas/` which iCloud Drive syncs automatically. Every time pip wrote `.dylib` files to `.venv`, iCloud treated it as a sync conflict and created duplicated files with broken permissions:

```
-rwx------  libqcocoa 2.dylib    ← iCloud conflict copy, wrong permissions
-rwx------  libqcocoa 3.dylib    ← another iCloud conflict copy
-rwxr-xr-x  libqcocoa.dylib      ← real file — worked until next iCloud sync
```

Qt cannot load a platform plugin with the wrong filename or permissions. This caused the `cocoa platform plugin not found` crash. Force-reinstalling PySide6 fixed it temporarily, but iCloud broke it again on the next sync.

### Permanent Fix Applied
Project moved to home folder — completely outside iCloud's sync scope:
```bash
mv ~/Documents/project_atlas ~/project_atlas
```

iCloud only syncs `~/Desktop`, `~/Documents`, and `~/Downloads`. The home folder itself is not synced.

After the move, the venv had to be rebuilt (venv symlinks are hardcoded to creation path):
```bash
cd ~/project_atlas
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### If the Cocoa Error Ever Returns
First check: has the project folder somehow ended up back inside `~/Documents/`, `~/Desktop/` or `~/Downloads/`? That's the only way iCloud can touch it again.

If the project location is correct, rebuild the venv:
```bash
cd ~/project_atlas
deactivate && rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run_atlas.sh
```

**Do NOT suggest force-reinstalling PySide6 as a fix** — it was only ever a band-aid. The real fix was moving the project.

---

## 8. Windows Deployment

### Status
Files created, copied to Windows machine via USB stick. Windows machine setup not yet completed/verified.

### Files in `windows/` Subfolder
| File | Purpose |
|---|---|
| `run_atlas.bat` | Primary launcher — double-click to start Atlas |
| `run_atlas.ps1` | PowerShell launcher — alternative to bat file |
| `SETUP_WINDOWS.md` | Full setup guide — start here on a new Windows machine |
| `.gitkeep` | Keeps folder tracked by Git |

### Windows Project Location
```
C:\project_atlas\
```
**Do NOT put it in Documents, Desktop or OneDrive** — OneDrive causes identical problems to iCloud on Windows (will corrupt the venv).

### Windows Setup Sequence (from SETUP_WINDOWS.md)
1. Install Python 3.12 from python.org — tick "Add Python to PATH"
2. Copy project to `C:\project_atlas\`
3. Delete the `.venv` folder from the copy (it's Mac-specific, useless on Windows)
4. Open CMD, navigate to `C:\project_atlas\`
5. `python -m venv .venv`
6. `.venv\Scripts\activate.bat`
7. `pip install -r requirements.txt`
8. Double-click `windows\run_atlas.bat`

### Key Difference from Mac Launcher
The Windows bat/ps1 scripts set `QT_PLUGIN_PATH` (not `QT_QPA_PLATFORM_PLUGIN_PATH`) and do NOT set `QT_QPA_PLATFORM=cocoa` (that's macOS only). Windows PySide6 finds its own platform plugin automatically.

---

## 9. Working Features (Current State)

- ✅ Real-time clock synced to system time (1Hz)
- ✅ Heat scheduling — add, edit, delete heats
- ✅ Automatic heat activation (≤15 min to track open)
- ✅ Phase-based countdown with colour coding (Yellow → Green → Red)
- ✅ LED Simulator display (128×64 and 64×64 layouts)
- ✅ LCD Monitor display (full-resolution alternative)
- ✅ Operator Console — LIVE, SCHEDULE, SETTINGS tabs
- ✅ Brightness control with live preview
- ✅ Display backend selection (restart required)
- ✅ Auto-boot toggle (defaults OFF — stay that way during development)
- ✅ EXIT TO DESKTOP button (platform-neutral label)
- ✅ RESTART ATLAS button
- ✅ Abort/Cancel active heat
- ✅ Settings persist across restarts (SQLite)
- ✅ Cross-platform path handling for database

---

## 10. Known Issues & Open Threads

### Open
- [ ] **Windows machine setup not yet verified** — SETUP_WINDOWS.md has the steps, needs to be walked through on the actual Windows PC
- [ ] **`atlas.sh`** at project root — may be an outdated duplicate of `run_atlas.sh`, worth checking and removing if redundant
- [ ] **`core/timers.py` and `core/config.py`** — legacy files, not used by any active code. Could be cleaned up but harmless to leave
- [ ] **`atlas_config.json`** — legacy JSON config, not used by `main.py`. Harmless but vestigial

### Future / Roadmap
- [ ] Physical LED hardware integration (P5/P10 panels, HUB75 protocol)
- [ ] macOS LaunchAgent for appliance-mode auto-start
- [ ] Additional display backends (Artnet DMX, Serial/UART)
- [ ] Pre-loaded competition schedules

---

## 11. Documentation Set

All documents follow the `ATLAS-XXX-001` naming convention. The authoritative set as of July 26, 2026:

| Document | File | Notes |
|---|---|---|
| README | `README_ATLAS.pdf` | Project overview |
| Architecture | `ATLAS-ARC-001_Current_Architecture_and_System_Status.pdf` | System architecture |
| Actual System Review | `ATLAS-ASR-001_Actual_System_Review_v2.pdf` | What's actually built |
| Deployment Guide | `ATLAS-DEP-001_Deployment_Guide_v2.pdf` | Use v2, not v1 |
| Document Register | `ATLAS-DOC-001_Document_Status_Register.pdf` | Doc index |
| Progress Log | `ATLAS-LOG-003_Progress_Status_July2026.pdf` | Latest progress |
| Interface Control | `ATLAS-ICD-001_Interface_Control_Document.pdf` | Signal/interface spec |
| Mac PySide6 Fix | `MAC_PYSIDE6_FIX.md/.pdf/.docx` | iCloud root cause + fix |
| Windows Setup | `windows/SETUP_WINDOWS.md/.pdf/.docx` | Windows install guide |
| This document | `ATLAS_PROJECT_HANDOVER_Updated.md` | You are here |

---

## 12. Quick Reference

### Launch on Mac
```bash
cd ~/project_atlas && ./run_atlas.sh
```

### Launch on Windows
Double-click `C:\project_atlas\windows\run_atlas.bat`

### If Atlas Won't Start on Mac
```bash
cd ~/project_atlas
deactivate && rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run_atlas.sh
```

### Key File Locations
| What | Where |
|---|---|
| Project root (Mac) | `~/project_atlas/` |
| Project root (Windows) | `C:\project_atlas\` |
| Mac launcher | `~/project_atlas/run_atlas.sh` |
| Windows launcher | `C:\project_atlas\windows\run_atlas.bat` |
| Entry point | `src/main.py` |
| Engine | `src/core/engine.py` |
| Database manager | `src/core/database.py` |
| Operator Console | `src/gui/windows.py` |
| LED Simulator | `src/gui/led_simulator.py` |
| LCD Display | `src/gui/lcd_display.py` |
| Database file | `data/atlas.db` |
| Virtual env (Mac) | `.venv/` — do NOT commit, do NOT let it end up in iCloud/OneDrive |

### Settings That Need a Restart
- Display backend (LED Simulator ↔ LCD Monitor)
- Display size (128×64 ↔ 64×64)
- Auto-boot toggle

### Settings That Apply Immediately
- Brightness slider (live via signal)

---

*End of handover. Future AI: read Peter's actual files before changing anything.  
Confirm what's running on his machine vs what's in any workspace.  
If you broke something, say so and fix it — don't dress it up.*

*Project ATLAS — Updated Handover — July 26, 2026*
