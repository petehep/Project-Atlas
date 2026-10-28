# Active Context — ATLAS

## Current status
- **Version:** v1.9.0 (HEAD, branch `main`)
- **State:** Fully working Mac prototype; Windows launchers present. Software
  LED simulator + LCD/HDMI output all functional. Physical LED hardware not yet
  integrated.
- **Git:** `main` is **18 commits ahead of `origin/main`** (not pushed). Many
  uncommitted changes are also present in the working tree (see below).

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

## Uncommitted work-in-progress (working tree)
⚠️ The documentation was **reorganized but not committed**:
- All files previously under `docs/` were moved to
  `docs/Development Documentation/` and `docs/Operating Instructions/`.
- In git, the old `docs/*` paths show as **deleted**, and the new folders are
  **untracked**. This needs a `git add -A` + commit to reconcile.
- Also modified: `.gitignore` (adds `.agent/`), `atlas_config.json`, `data/atlas.db`,
  `requirements.txt`, `README.md`, `Windows/*` (incl. `windows_packages/` offline
  wheel cache), `3D Print Files/*`, `tools/NovaLCT V5.5.0.zip`, plus most `src/*`.
- New untracked CAD files under `3D Print Files/` (Clockbox01 parts, "CoBurn
  Flight Gear.stl", "Individual Parts/", "Printer Settings/").

## Next steps / open threads (from handover + analysis docs)
- [ ] Push `main` to origin and commit the pending doc reorganisation.
- [ ] Verify Windows setup on an actual Windows PC.
- [ ] Physical LED hardware integration (P5/P10 panels, HUB75 / NovaStar TB40).
- [ ] macOS LaunchAgent for appliance-mode auto-start.
- [ ] Additional display backends (Artnet DMX, Serial/UART).
- [ ] Pre-loaded competition schedules.
- [ ] Optional cleanup of legacy files (see systemPatterns.md).

## Known quirks / risks to keep in mind
- There is a **broken git ref** named `main 2` (from `git branch`). Harmless but
  should be cleaned up (`git branch -D "main 2"`).
- `data/atlas.db` is tracked but changes frequently (heat/settings data).
- `.venv/` must never be committed or placed under an iCloud-synced folder (see
  techContext.md — iCloud corrupts PySide6).
