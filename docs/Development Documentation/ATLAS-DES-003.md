# ATLAS-DES-003: Timing Logic Specification

## 1. Goal
Ensure zero-drift countdowns over 60-minute durations using a 10Hz polling strategy.

## 2. Logic
- **Reference**: `time.time()` (Unix Epoch).
- **Calculation**: Always subtract current time from target end time. 
- **Resolution**: 100ms internal pulse, 1.0s display update.

## 3. Class: AtlasTimerEngine
- Inherits from `QObject`.
- Owns a `QTimer`.
- Emits `tick(formatted_time: str)`.
