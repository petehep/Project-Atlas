"""
ATLAS LCD Monitor Display.

A full-resolution rendering surface intended for a standard LCD/HDMI monitor
(as opposed to a physical LED matrix). It presents the exact same public
interface as :class:`gui.led_simulator.AtlasLEDSimulator`:

    * ``update_model(model)``   -- slot connected to engine.model_updated
    * ``set_brightness(value)`` -- slot connected to engine.brightness_changed

so ``main.py`` can wire either display into the same signal/slot architecture
without any other code changes.

Unlike the LED simulator (which emulates discrete LEDs with a 5x7 bitmap
font), this widget uses crisp anti-aliased system fonts and scales to the
window, giving a clean high-resolution readout for monitors.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QFont


class AtlasLCDDisplay(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config

        # Start from a sensible high-resolution window; it stays fully
        # resizable so it can be dragged onto / maximised on any monitor.
        self.setWindowTitle("ATLAS LCD DISPLAY")
        self.setMinimumSize(640, 360)
        self.resize(960, 540)
        self.setStyleSheet("background-color: #000;")

        self.model = None

    # -- signal/slot interface (mirrors AtlasLEDSimulator) -----------------
    def update_model(self, model):
        self.model = model
        self.update()

    def set_brightness(self, value):
        # Store as 0-100; applied as an alpha/scale factor when painting.
        self.config.brightness = value
        self.update()

    # -- rendering ---------------------------------------------------------
    def _brightness_factor(self):
        return max(0, min(100, getattr(self.config, "brightness", 80))) / 100.0

    def _dim(self, color_hex):
        f = self._brightness_factor()
        c = QColor(color_hex)
        c.setRed(int(c.red() * f))
        c.setGreen(int(c.green() * f))
        c.setBlue(int(c.blue() * f))
        return c

    def _font(self, px, bold=True):
        f = QFont("Arial")
        f.setPixelSize(max(8, int(px)))
        f.setBold(bold)
        return f

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)
        p.fillRect(self.rect(), QColor(0, 0, 0))

        if not self.model:
            return

        w = self.width()
        h = self.height()
        # Scale typography to the window so it looks right on any monitor.
        unit = h / 100.0

        # Row 1: Local time (top, cyan).
        p.setPen(self._dim("#00FFFF"))
        p.setFont(self._font(unit * 12))
        p.drawText(0, int(unit * 2), w, int(unit * 16),
                   Qt.AlignHCenter | Qt.AlignVCenter, self.model.local_time)

        if not self.model.is_armed:
            p.setPen(self._dim("#888888"))
            p.setFont(self._font(unit * 22))
            p.drawText(self.rect(), Qt.AlignCenter, "WAITING")
            return

        # Row 2: Heat + thermalling direction (yellow).
        heat_txt = f"HEAT {self.model.heat_number}   {self.model.thermalling_dir}"
        p.setPen(self._dim("#FFFF00"))
        p.setFont(self._font(unit * 10))
        p.drawText(0, int(unit * 20), w, int(unit * 12),
                   Qt.AlignHCenter | Qt.AlignVCenter, heat_txt)

        # Row 3: Planned window (grey).
        win_txt = f"OPEN {self.model.planned_open}    CLOSE {self.model.planned_close}"
        p.setPen(self._dim("#AAAAAA"))
        p.setFont(self._font(unit * 7, bold=False))
        p.drawText(0, int(unit * 33), w, int(unit * 10),
                   Qt.AlignHCenter | Qt.AlignVCenter, win_txt)

        # Row 4: Phase label (phase colour).
        p.setPen(self._dim(self.model.primary_timer_color))
        p.setFont(self._font(unit * 9))
        p.drawText(0, int(unit * 45), w, int(unit * 12),
                   Qt.AlignHCenter | Qt.AlignVCenter, self.model.primary_timer_label)

        # Row 5: Big primary timer (phase colour).
        p.setPen(self._dim(self.model.primary_timer_color))
        p.setFont(self._font(unit * 34))
        p.drawText(0, int(unit * 56), w, int(unit * 34),
                   Qt.AlignHCenter | Qt.AlignVCenter, self.model.primary_timer)

        # Row 6: Status band across the bottom.
        band_h = int(unit * 6)
        p.fillRect(0, h - band_h, w, band_h, self._dim(self.model.band_color))
