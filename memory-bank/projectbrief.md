# Project Brief — ATLAS (Master Flightline Clock)

## Identity
- **Project name:** Project ATLAS (internal development codename)
- **Product name:** Master Flightline Clock
- **Owner / Author:** Peter ("petehep") Lochhead Hepburn — Adelaide, South Australia
- **Repository:** `petehep/project_atlas` (GitHub)
- **Canonical local path:** `/Users/petehep/project_atlas/` (moved out of `~/Documents/` July 2026)

## What it is
ATLAS is a mission-critical timing and display system for **competitive F3K model
glider racing** (Southern Soaring League). It manages race heats by driving a
large public-facing display (LED matrix or monitor) so pilots can see timing from
a distance (50–100 m).

It presents a **6-row display** that walks pilots through each heat:
1. Local time
2. Heat number + thermalling direction
3. Planned open/close window
4. Phase label (e.g. "TRACK OPENS IN" / "ENTER NOW" / "HEAT TIME REMAINING")
5. Large primary countdown timer
6. Status colour band (colour-coded by phase)

## Core capabilities
- Real-time race timing (synced to host PC clock)
- Automatic heat scheduling / arming (arms 15 min before track open)
- Pilot insertion window management (track open / close / heat end)
- Phase countdown management with colour-coded states
- Dual-display operator + public interface
- Deterministic, state-based operation
- SQLite persistence (auto-resume across restarts)
- Event/heat management (add, edit, delete, cancel)

## Project goals (from README)
- Reliability
- Simplicity
- Maintainability
- Expandability
- Deterministic behaviour

## Deployment context
- Standalone "appliance" at a flying field, visible to pilots at distance.
- **Dev machine:** MacBook Air (macOS Sequoia), user `petehep`.
- **Target deployment hardware:** Windows PC (Intel NUC) driving physical LED
  panels via HDMI → NovaStar TB40 → HUB75 (P10 panels).
- Currently a software **simulator** renders the LED matrix on screen; physical
  hardware integration is a future milestone.
