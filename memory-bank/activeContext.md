# Active Context — ATLAS

## Current status
- **Version:** v1.9.0 (branch `main`)
- **State:** Fully working Mac prototype; Windows launchers present. Software
  LED simulator + LCD/HDMI output all functional. Physical LED hardware not yet
  integrated.
- **Git:** `main` is **pushed and up to date with `origin/main`** (HEAD `8496cca`,
  repo `petehep/Project-Atlas`). History was rewritten to purge large binaries.
- **Tooling:** `gh` CLI v2.103.3 installed at `~/.local/bin/gh` (not yet authenticated).
  Git identity set to `petehep <petehep@gmail.com>`.

## Most recent work (git log, newest first)
- `v1.9.0` — Moved status colour bars to left/right edges; added spacing before row 4.
- `v1.8.0` — Direct-to-LED (HDMI) display added; display shrinks and positions at (0,0).
- `v1.7.0` — Added Windows launcher folder; moved repo to `petehep`.
- `v1.6.0` — Appliance controls (brightness, display config, restart/exit).
- `v1.5.0` — Live brightness control with environmental presets.
- `v1.4.0` — Unified config: settings fully migrated to SQLite (JSON deps removed).
- `v1.3.0` — Display-aware rendering; "Compact Mode" for 64×64.
- `v1.2.0` — Custom nav-bar (replaced native TabWidget) for macOS contrast.
- `v1.1.0` — Automatic heat scheduler / timeline engine.
- `v1.0.0` — Hardware-agnostic config abstraction.

## Resolved work (done 2026-10-28)
- Docs were reorganized (`docs/` → `docs/Development Documentation/` +
  `docs/Operating Instructions/`) and committed.
- `memory-bank/` (this Cline Memory Bank) created and committed.
- New 3D-print CAD/STL files committed.
- **Large binaries removed from git** (GitHub rejects files >100 MB):
  - `tools/NovaLCT V5.5.0.zip` (271 MB)
  - `Windows/windows_packages/pyside6_addons-6.11.1-cp310-abi3-win_amd64.whl` (161 MB)
  - `Windows/windows_packages/pyside6_essentials-6.11.1-cp310-abi3-win_amd64.whl` (74 MB)
  These are now `.gitignore`d and were purged from history with `git filter-repo`
  (history rewritten + force-pushed). The files remain on disk locally and are
  **backed up to the owner's Google Drive** (external host).
- Broken git ref `"main 2"` deleted.
- Git identity + `gh` CLI installed; everything pushed to GitHub.

## Next steps / open threads
- [x] Authenticate `gh` (done — logged in as `petehep`, scopes: repo/read:org/workflow).
- [x] Host the three large binaries externally (done — copied to Google Drive).
- [ ] Optionally add a Google Drive link to `Windows/SETUP_WINDOWS.md` +
      deployment docs so the offline installers can be re-fetched.
- [ ] Verify Windows setup on an actual Windows PC.
- [ ] Physical LED hardware integration (P5/P10 panels, HUB75 / NovaStar TB40).
- [ ] macOS LaunchAgent for appliance-mode auto-start.
- [ ] Additional display backends (Artnet DMX, Serial/UART).
- [ ] Pre-loaded competition schedules.
- [ ] Optional cleanup of legacy files (see systemPatterns.md).

## Known quirks / risks to keep in mind
- `data/atlas.db` is tracked but changes frequently (heat/settings data).
- `.venv/` must never be committed or placed under an iCloud-synced folder (see
  techContext.md — iCloud corrupts PySide6).
- Do **not** re-add `tools/NovaLCT V5.5.0.zip` or the large PySide6 wheels to git
  (they exceed GitHub's limits); they are intentionally gitignored.
