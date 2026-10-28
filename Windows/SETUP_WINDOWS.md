# Project ATLAS — Windows Setup Guide
**Version:** 1.6.0  
**Platform:** Windows 10 / 11 (64-bit)  
**Date:** July 2026

---

## Overview

This guide sets up Project ATLAS from scratch on a Windows machine.  
The application runs identically on Windows to macOS — same Python source, same PySide6 UI.  
The only Windows-specific files are the launchers in this `windows\` folder.

---

## Step 1 — Install Python 3.12

1. Go to: **https://www.python.org/downloads/windows/**
2. Download **Python 3.12.x** (Windows installer, 64-bit)
3. Run the installer.  
   ⚠️ **CRITICAL:** On the first screen, tick **"Add Python 3.12 to PATH"** before clicking Install.
4. Verify the install worked — open Command Prompt and run:
   ```
   python --version
   ```
   Expected output: `Python 3.12.x`

---

## Step 2 — Copy the Project to the Windows Machine

Copy the entire `project_atlas\` folder to a location on the Windows machine.  
**Recommended location:** `C:\project_atlas\`

The folder structure should look like this:
```
project_atlas\
├── src\
│   ├── main.py
│   ├── core\
│   │   ├── database.py
│   │   ├── engine.py
│   │   ├── models.py
│   │   └── timers.py
│   └── gui\
│       ├── windows.py
│       ├── lcd_display.py
│       ├── led_simulator.py
│       ├── themes.py
│       └── fonts.py
├── data\
│   └── atlas.db
├── windows\                  ← Windows-specific files (this folder)
│   ├── run_atlas.bat
│   ├── run_atlas.ps1
│   └── SETUP_WINDOWS.md
├── requirements.txt
└── atlas_config.json
```

> **Note:** The `data\` folder and `atlas.db` may not exist yet on a fresh install.  
> Atlas will create them automatically on first launch.

---

## Step 3 — Create the Virtual Environment

Open **Command Prompt** (not PowerShell for this step), navigate to the project root, and run:

```cmd
cd C:\project_atlas
python -m venv .venv
```

This creates a `.venv\` folder inside the project. This is the isolated Python environment.

---

## Step 4 — Install Dependencies

With the virtual environment created, install all required packages:

```cmd
cd C:\project_atlas
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

This will download and install PySide6 and other dependencies. It may take a few minutes.

Verify PySide6 installed correctly:
```cmd
python -c "import PySide6; print(PySide6.__version__)"
```
Expected output: `6.11.1`

---

## Step 5 — Launch Atlas

### Option A — Double-click (Easiest)
Navigate to `project_atlas\windows\` in File Explorer and double-click **`run_atlas.bat`**.

### Option B — Command Prompt
```cmd
cd C:\project_atlas
windows\run_atlas.bat
```

### Option C — PowerShell
If you prefer PowerShell, you may need to allow scripts first (one-time setup):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then launch Atlas:
```powershell
cd C:\project_atlas
.\windows\run_atlas.ps1
```

---

## Troubleshooting

### "Python not found in PATH"
Python was installed without adding it to PATH. Fix: Re-run the Python installer, choose "Modify", and tick "Add Python to environment variables".

### "Virtual environment not found"
The `.venv\` folder doesn't exist yet. Run Step 3 again.

### "No module named PySide6"
The virtual environment exists but dependencies weren't installed. Run Step 4 again.

### Qt Platform Plugin Error on Windows
If you see an error about Qt platform plugins, force-reinstall PySide6:
```cmd
cd C:\project_atlas
.venv\Scripts\activate.bat
pip install --force-reinstall --no-cache-dir PySide6==6.11.1
```

### Atlas opens but the display window is black / wrong size
The display backend may be set to `lcd` but the window geometry is off. Open the SETTINGS tab in the Operator Console and try switching the Display Backend to **"LED Simulator (Software)"** first, then restart.

### Database errors on startup
Atlas expects the database at `data\atlas.db` relative to the project root. If you see SQLite errors, check that the project folder structure matches Step 2 exactly.

---

## Post-Install Verification Checklist

- [ ] Python 3.12 installed and visible in PATH
- [ ] `.venv\` folder exists in project root
- [ ] `pip install -r requirements.txt` completed without errors
- [ ] `run_atlas.bat` launches the Atlas Operator Console
- [ ] Both the Operator Window and the display window (simulator or LCD) appear
- [ ] SCHEDULE tab: can add and delete a test heat
- [ ] SETTINGS tab: Display Backend selector and Brightness slider work
- [ ] Heat data persists after closing and restarting Atlas (database is working)

---

## Offline Installer Packages (`windows_packages`)

For machines **without internet access**, the `windows_packages\` folder contains
offline installers (the Python 3.12 installer + pip `.whl` wheels).

> ⚠️ **Three large artifacts are NOT stored in this repository.** GitHub rejects
> files over 100 MB, so these are hosted on the **owner's Google Drive** instead:

| File | Size | Where to get it |
|------|------|-----------------|
| `pyside6_addons-6.11.1-cp310-abi3-win_amd64.whl` | 161 MB | Owner's Google Drive |
| `pyside6_essentials-6.11.1-cp310-abi3-win_amd64.whl` | 74 MB | Owner's Google Drive |
| `NovaLCT V5.5.0.zip` (LED panel config tool) | 271 MB | Owner's Google Drive |

To perform a fully-offline install, copy these three files back into the project
— the two `.whl` files into `windows_packages\`, and `NovaLCT V5.5.0.zip` into
`tools\` — before running the install steps above.

> **Share link:** https://drive.google.com/drive/folders/1Kw5pX9y-wmYYnq9MFY6Wdwa_gvAiQVWR?usp=drive_link

---

## Notes for Field Deployment

- The `atlas.db` database file lives in `project_atlas\data\`. Back this up before any update.
- If moving the project folder, the launchers use relative paths and will still work — no hardcoded paths.
- The `windows\` folder is for Windows-only. Do not mix these files into the Mac project folder.
- To reset all settings and heat data, delete `data\atlas.db` — Atlas will recreate it fresh on next launch.

---

*Project ATLAS — Windows Setup Guide — July 2026*
