# ATLAS-DES-002: Software Architecture Specification

## 1. Pattern
**Mediated Observer Pattern**: The `AtlasStateEngine` is the mediator. All other modules are observers.

## 2. Package Structure
```text
src/
├── core/
│   ├── engine.py     # AtlasStateEngine
│   ├── timers.py     # High-precision heartbeat
│   └── persistence.py # SQLite/Data access
├── gui/
│   ├── operator.py   # Admin interface
│   └── renderer.py   # LED Matrix display
└── main.py           # Application Bootstrap
```

## 3. Communication Strategy
- **Signals**: We will use PySide6 `QueuedConnection` signals to ensure that if a timer thread "ticks", it doesn't crash the GUI thread.
- **Data Models**: Use Pydantic classes for "Snapshots" of heat data to ensure type safety.

## 4. State Transitions
The Engine maintains a strictly sequential transition logic:
`STARTUP -> READY -> ARMED -> RUNNING -> FINISHED`
