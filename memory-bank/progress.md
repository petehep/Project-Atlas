# Progress — ATLAS

## Current version: v1.9.0 (main branch)

## Version history (git tags/commits, oldest → newest)
| Version | Milestone |
|---------|-----------|
| v0.1.0 | Skeleton baseline — dual-window architecture, state engine signal binding |
| v0.2.0 | High-precision heartbeat, real-time countdown |
| v0.3.1 | Documentation baseline + Python package plumbing |
| v0.4.0 | Timeline engine — auto-transitioning phase countdown |
| v0.5.0 | Persistence layer — SQLite backend, auto-resume |
| v0.6.0 | 6th-row LED hardware-aligned layout; Phase 0 architecture complete |
| v0.7.0 | Validation shielding, UI scaling, auto-incrementing workflow |
| v0.7.5 | Persistence upgrade, Settings tab, interactive heat management |
| v0.8.0 | Single Source of Truth architecture; stateless timing engine |
| v0.9.0 | Hardware emulator tier (128×64 P10 virtual LED matrix + bitmap renderer) |
| v0.9.5 | LED simulator baseline |
| v1.0.0 | Configuration abstraction layer (hardware-agnostic via JSON) |
| v1.1.0 | Automatic heat scheduler / timeline engine |
| v1.2.0 | Custom nav-bar (retired native TabWidget) |
| v1.3.0 | Display-aware rendering — "Compact Mode" for 64×64 |
| v1.4.0 | Unified configuration — settings migrated to SQLite (JSON deps removed) |
| v1.5.0 | Live brightness control with environmental presets |
| v1.6.0 | Appliance controls (brightness, display config, restart/exit) |
| v1.7.0 | Windows launcher folder; repo moved to `petehep` |
| v1.8.0 | Direct-to-LED (HDMI) display; display positions at (0,0) |
| v1.9.0 | Status colour bars moved to screen edges; spacing before row 4 |

## What works today
- Operator Console (LIVE / SCHEDULE / SETTINGS) with custom nav-bar.
- Heat CRUD (add / edit / delete) with validation (close > open).
- Automatic heat arming + phase transitions from the real-time clock.
- Abort / cancel active heat.
- Three display backends: LED simulator (full + compact), LCD monitor, HDMI/LED.
- Live brightness control (applies immediately via signal).
- Settings persistence across restarts (SQLite).
- Auto-boot to clock-only mode (no operator console).
- Restart / exit system controls.

## Known issues / gaps
- **No physical LED hardware integration yet** (simulator + HDMI capture only).
- **Windows setup not yet verified** on real hardware.
- Uncommitted doc reorganisation (`docs/` → `docs/Development Documentation/`).
- `main` is 18 commits ahead of `origin/main` (not pushed).
- Broken git ref `main 2`.
- Legacy dead code (see systemPatterns.md) not yet cleaned up.
- `fonts.py` missing `'X'` glyph; `led_simulator.py` has duplicate `_draw_char`.

## Roadmap (future)
- Physical LED integration (P5/P10, HUB75, NovaStar TB40).
- macOS LaunchAgent for appliance auto-start.
- Additional backends (Artnet DMX, Serial/UART).
- Pre-loaded competition schedules.
- Hardware Abstraction Layer (HAL) / `DisplayBackend` abstract base.

## Source metrics (approximate)
- `main.py` ~71 lines; `engine.py` ~91; `database.py` ~128; `models.py` ~24;
  `windows.py` ~369; `led_simulator.py` ~171; `lcd_display.py` ~311;
  `themes.py` ~52; `fonts.py` ~46; plus legacy `timers.py` ~41, `config.py` ~36.
