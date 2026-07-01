# ATLAS-DES-004: Public Display (LED Matrix) UX Design

## 1. Goal
Maximize visibility for pilots at a distance (up to 50-100m) on a P3/P10 LED screen.

## 2. Layout Sections
- **Top**: Local Time (White).
- **Sub-Header**: Heat No & Thermalling Direction.
- **Center**: The Pulse (Big Green/Red Countdown).
- **Divider**: Performance-coded separator band.
- **Bottom**: Window start/stop timestamps.

## 3. Implementation
Use a borderless `QMainWindow` with a custom `paintEvent` or high-performance `QLabel` stack.
