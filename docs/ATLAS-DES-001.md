# ATLAS-DES-001: System & Software Architecture Design

## 1. Hardware Overview
- **Brain**: Intel NUC (Windows).
- **Control**: Small LCD (Operator).
- **Public**: LED Matrix via HDMI-to-HUB75.
- **Power**: 200Ah Lithium + DCDC Converters.

## 2. Software Architecture
The Atlas Engine is composed of decoupled modules:
1. **AtlasState**: Central State Machine.
2. **AtlasUI**: Operator input (PySide6).
3. **AtlasRenderer**: Public display output (PySide6 Canvas).
4. **AtlasTimers**: Precision countdown logic.
5. **AtlasData**: Persistence (SQLite/JSON).

## 3. Communication Strategy
Modules observe the central State. Input triggers change requests; the Engine approves or denies them based on valid state transitions.
