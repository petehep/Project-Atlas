# Product Context — ATLAS

## Why this exists
Competitive F3K glider racing runs many heats per day, each with a precise
track-open / track-close window and a thermalling direction. Pilots need to see
the *current* heat status and countdowns clearly from a distance while managing
their launch. A dedicated, reliable flightline clock removes ambiguity and keeps
the day on schedule.

## Problems it solves
- **Visibility** — a large LED/monitor display readable at 50–100 m.
- **Synchronisation** — deterministic timing driven by the host PC clock.
- **Automation** — heats auto-arm and phase-transition from the real-time clock,
  so the operator isn't manually running timers.
- **Recovery** — state persists in SQLite, so a restart resumes cleanly.
- **Operator safety** — explicit ARM / ABORT controls and a clear live status.

## The two audiences
1. **Operator** — uses the "Atlas Operator Console" (3-tab PySide6 window:
   LIVE / SCHEDULE / SETTINGS) to build the day's schedule and manage heats.
2. **Pilots / public** — see the display surface (LED simulator, LCD monitor, or
   HDMI/LED output) showing only the relevant countdown info.

## User / working relationship — IMPORTANT
Peter is direct, casual, and technical. Key preferences to respect:
- **Do not change code without showing him first.**
- **Ask before assuming** — if files look wrong or missing, ask him.
- Swearing is normal; don't be precious about it.
- He values things that *work* over elegant theory.
- If you break something, own it immediately and fix it cleanly — no excuses.
- Humour is welcome.

## Domain terminology
- **Heat** — a single race round with a schedule entry.
- **Track open / close** — the pilot insertion window (when pilots may launch).
- **Heat end** — when the heat is over.
- **Thermalling direction** — LEFT / RIGHT (direction of the thermal turn).
- **Armed** — the display is showing an upcoming/active heat.
- **Phases** — TRACK OPENS IN → ENTER NOW → HEAT TIME REMAINING → COMPLETED.
