# System Patterns — ATLAS

## High-level architecture
ATLAS follows a clean **Model-View-Controller / Mediated Observer** style split
into two packages plus a bootstrap entry point. The `AtlasEngine` acts as the
central mediator; all display surfaces are observers wired via Qt signals/slots.

```
src/main.py                        ← bootstrap / wiring (QApplication, Fusion style)
├── src/core/
│   ├── engine.py        AtlasEngine          (QObject, 1 Hz tick, phase logic)
│   ├── database.py      AtlasDatabase        (sqlite3 persistence)
│   ├── models.py        Pydantic models      (HeatConfig, AtlasDisplayModel)
│   ├── timers.py        AtlasTimerEngine     (UNUSED / legacy)
│   └── config.py        AtlasConfig          (legacy JSON config, UNUSED)
└── src/gui/
    ├── windows.py       OperatorWindow       (3-tab console: LIVE/SCHEDULE/SETTINGS)
    ├── led_simulator.py AtlasLEDSimulator    (virtual LED matrix, full+compact)
    ├── lcd_display.py   AtlasLCDDisplay + AtlasHDMIOutput
    ├── themes.py        CSS stylesheet constants
    └── fonts.py         AtlasBitmapFont       (5×7 pixel font definitions)
```

## Key patterns & decisions

### Signal/slot contract
`AtlasEngine` emits two signals:
- `model_updated(object)` — carries an `AtlasDisplayModel` snapshot every second.
- `brightness_changed(int)` — live brightness (0–100), applied without restart.

Every display backend implements the **same interface** so `main.py` can swap
them without other changes:
- `update_model(model)`
- `set_brightness(value)`

### Display backends (selected via `display_backend` setting)
| id | class | notes |
|----|-------|-------|
| `simulator` | `AtlasLEDSimulator` | default; emulated LEDs via QPainter |
| `lcd` | `AtlasLCDDisplay` | anti-aliased full-res monitor view |
| `hdmi` | `AtlasHDMIOutput` | frameless 64×32 px window, 1:1 for NovaStar TB40 → P10 panels |

### Display content (6-row layout)
- Row 2 shows the heat identity as **`RD{round} HT{heat} GP{group} {arrow}`**, where
  the thermalling direction is rendered as a `←`/`→` arrow (glyphs added to the
  5×7 bitmap font). e.g. `RD1 HT2 GPA ←`.
- The vertical status-colour side bars were **removed** (Oct 2026); the HDMI
  output now uses the full 64-col width for text. Phase is still communicated via
  text colour on the label/timer rows.

### Engine phase logic (1 Hz `tick()`)
1. No active heat → find next `READY` heat with `track_close` in the future.
   - If it opens within 900 s → auto-`ACTIVE`.
   - Else → show `WAITING` (armed=true, "WAITING", `--:--`).
2. Active heat, by `now` vs timestamps:
   - `now < track_open`   → "TRACK OPENS IN" (yellow `#FFFF00`)
   - `now < track_close`  → "ENTER NOW" (green `#00FF00`)
   - `now < heat_end`     → "HEAT TIME REMAINING" (red `#FF0000`)
   - else → mark `COMPLETED`, disarm.

### Heat status lifecycle
`READY → ACTIVE → COMPLETED` (or `CANCELLED` via abort).

### Persistence (raw `sqlite3`, NOT SQLAlchemy)
Two tables in `data/atlas.db`:
- `heats(id, round_number, heat_number, group_letter, thermalling_dir, track_open, track_close, heat_end, status)`
- `settings(key, value)` — flat key/value store (all values stored as strings).

Known settings: `display_backend`, `auto_boot_enabled`, `display_width`,
`display_height`, `led_scale`, `brightness`, `competition_name`.

### Cross-platform path hardening
`database.py` resolves the DB path from `__file__` (three `dirname()` calls up:
`core → src → project_root`) instead of relying on the CWD. The DB always lives at
`<project_root>/data/atlas.db`.

### Configuration authority
**SQLite `settings` is authoritative.** The legacy `core/config.py` and
`atlas_config.json` are vestigial and not in the critical path. `main.py`'s
`DisplayConfig` reads from the DB.

## Legacy / dead code (safe to clean, currently harmless)
- `src/core/timers.py` — orphaned `AtlasTimerEngine` (pre-v0.8.0).
- `src/core/config.py` — legacy JSON config loader, unused.
- `atlas_config.json` — vestigial JSON config.
- `atlas.sh` — likely outdated duplicate of `run_atlas.sh`.
- `.bak` files: `src/main_Bak.py`, `src/gui/windows_bak.py`,
  `src/gui/lcd_display_bak.py`, `src/gui/lcd_display_bak2.py`.
- Duplicate `_draw_char` in `led_simulator.py` (brightness-aware version wins).
- `fonts.py` has no `'X'` glyph (blank fallback); `'Y'` is duplicated in place of `'X'`.
