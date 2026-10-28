# Mac PySide6 Fix — "cocoa platform plugin not found"

**Status:** RESOLVED — July 2026  
**Root cause identified and permanently fixed.**

---

## The Error

```
qt.qpa.plugin: Could not find the Qt platform plugin "cocoa" in
"…/.venv/lib/python3.12/site-packages/PySide6/Qt/plugins/platforms"
Abort trap: 6
```

---

## Root Cause

The project was located in `~/Documents/project_atlas/` which is synced by **iCloud Drive**.

iCloud continuously monitors `~/Documents/` and treats any file modification as a potential sync conflict — including the `.dylib` files that pip writes when installing or updating PySide6. Rather than overwrite either copy, iCloud keeps both, renaming the older one to `libqcocoa 2.dylib`, `libqcocoa 3.dylib` etc. It also strips the execute permissions on these copies down to `700`.

Qt cannot load a platform plugin if the filename is wrong or the permissions are broken. The result was `libqcocoa.dylib` periodically getting clobbered or replaced, causing Atlas to crash on launch.

Evidence of the problem — duplicated files visible via `ls -la`:
```
-rwx------   libqcocoa 2.dylib    ← iCloud conflict copy
-rwx------   libqcocoa 3.dylib    ← iCloud conflict copy
-rwxr-xr-x   libqcocoa.dylib      ← real file, worked until next iCloud sync
```

Force-reinstalling PySide6 restored the real file temporarily, but iCloud would break it again on the next sync cycle. This is why the error kept recurring even after successful reinstalls.

---

## Permanent Fix Applied (July 2026)

The project was moved out of `~/Documents/` entirely, to the home folder:

```bash
mv ~/Documents/project_atlas ~/project_atlas
```

iCloud Drive only syncs `~/Desktop`, `~/Documents`, and `~/Downloads`. The home folder itself (`~/`) is not synced. Moving the project one level up puts it completely outside iCloud's reach — permanently, with no ongoing maintenance required.

After the move the `.venv` had to be rebuilt because Python venv symlinks are hardcoded to the path they were created at:

```bash
cd ~/project_atlas
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Atlas then launched cleanly and the platform plugins have remained intact.

---

## Current Project Location

| What | Where |
|---|---|
| Project root | `~/project_atlas/` |
| Virtual environment | `~/project_atlas/.venv/` |
| Launch script | `~/project_atlas/run_atlas.sh` |
| Database | `~/project_atlas/data/atlas.db` |
| iCloud exposure | **None** |

---

## If This Error Ever Recurs

It shouldn't — but if it does, first check whether the project folder has somehow ended up back inside `~/Documents/`, `~/Desktop/`, or `~/Downloads/`. That's the only way iCloud can touch it again.

If the project location is correct and it still fails, rebuild the venv:

```bash
cd ~/project_atlas
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run_atlas.sh
```

---

*Mac PySide6 / iCloud Fix — Project ATLAS — July 2026*
