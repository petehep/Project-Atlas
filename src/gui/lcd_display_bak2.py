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
from PySide6.QtGui import QColor, QPainter, QFont, QBrush
from .fonts import AtlasBitmapFont


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



# ---------------------------------------------------------------------------
# AtlasHDMIOutput — NovaStar TB40 / P10 LED Panel output window
# ---------------------------------------------------------------------------
class AtlasHDMIOutput(QWidget):
    """
    64×32 pixel frameless output window — sized 1:1 to the physical P10 LED
    panel array (4× P10 panels, 2 wide × 2 tall = 64 cols × 32 rows).

    The NovaStar TB40 captures this 64×32 region from the main monitor and
    maps each pixel directly to one LED.  Rendering uses the same 5×7 bitmap
    font as AtlasLEDSimulator (solid 1×1 px squares, no anti-aliasing) so
    every pixel is crisp and intentional at LED scale.

    Layout in 32 rows (5×7 bitmap font, 1px spacing between rows):
        Row 1  y= 1  Local time          (cyan)
        Row 2  y=10  Heat + direction     (yellow)  |  "WAIT" when unarmed
        Row 3  y=19  Phase label          (phase colour)
        Row 4  y=24  Primary timer        (phase colour)
        Band        Status colour strip  (bottom 2 rows)

    • Starts at screen position (0, 0).
    • Frameless — no title-bar bleeds onto the panels.
    • Left-click drag to reposition.
    • Right-click menu: toggle Always-On-Top / close.
    """

    COLS = 64
    ROWS = 32

    def __init__(self, config):
        super().__init__()
        self.config = config

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(self.COLS, self.ROWS)
        self.move(0, 0)
        self.setWindowTitle("ATLAS HDMI OUTPUT")
        self.setStyleSheet("background-color: #000;")

        self._drag_pos = None
        self.model = None

    # ── frameless drag support ───────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = (event.globalPosition().toPoint()
                              - self.frameGeometry().topLeft())
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ── right-click context menu ─────────────────────────────────────────────
    def contextMenuEvent(self, event):
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background:#111; color:white; border:1px solid #444; }"
            "QMenu::item:selected { background:#333; }")
        on_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        act_top = menu.addAction(
            f"📌  Always On Top: {'ON  (click to disable)' if on_top else 'OFF (click to enable)'}")
        menu.addSeparator()
        act_close = menu.addAction("✕  Close Output Window")
        chosen = menu.exec(event.globalPos())
        if chosen == act_top:
            flags = self.windowFlags()
            if on_top:
                self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
            self.show()
        elif chosen == act_close:
            self.close()

    # ── signal / slot interface ──────────────────────────────────────────────
    def update_model(self, model):
        self.model = model
        self.update()

    def set_brightness(self, value):
        self.config.brightness = value
        self.update()

    # ── internal helpers ─────────────────────────────────────────────────────
    def _apply_brightness(self, color_hex):
        brightness = getattr(self.config, "brightness", 80) / 100.0
        c = QColor(color_hex)
        c.setRed(int(c.red() * brightness))
        c.setGreen(int(c.green() * brightness))
        c.setBlue(int(c.blue() * brightness))
        return c

    def _text_width(self, text):
        """Width in pixels of text at scale=1 (6px per character)."""
        return len(text) * 6

    def _draw_centered(self, p, y, text, color_hex):
        """Draw bitmap text centred horizontally in the 64-col grid."""
        x = max(0, (self.COLS - self._text_width(text)) // 2)
        self._draw_string(p, x, y, text, color_hex)

    def _draw_string(self, p, x, y, text, color_hex):
        p.setPen(Qt.NoPen)
        p.setBrush(self._apply_brightness(color_hex))
        cur_x = x
        for char in text:
            self._draw_char(p, cur_x, y, char)
            cur_x += 6

    def _draw_char(self, p, x, y, char):
        bitmap = AtlasBitmapFont.FONT_5x7.get(
            char.upper(), AtlasBitmapFont.FONT_5x7[' '])
        for col_idx, col_data in enumerate(bitmap):
            for row_idx in range(7):
                if col_data & (1 << row_idx):
                    p.drawRect(x + col_idx, y + row_idx, 1, 1)

    # ── painting ─────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        # No anti-aliasing — every pixel must map cleanly to one LED.
        p.fillRect(self.rect(), QColor(0, 0, 0))

        if not self.model:
            return

        # Row 1 (y=1): Local time — cyan
        self._draw_centered(p, 1, self.model.local_time, "#00FFFF")

        if not self.model.is_armed:
            # "WAIT" centred in the lower half when not armed
            self._draw_centered(p, 13, "WAIT", "#888888")
        else:
            # Row 2 (y=10): Heat + short direction — yellow
            dir_short = str(self.model.thermalling_dir).strip().upper()
            dir_short = "L" if dir_short.startswith("L") else (
                        "R" if dir_short.startswith("R") else dir_short[:1])
            heat_txt = f"H{self.model.heat_number} {dir_short}"
            self._draw_centered(p, 10, heat_txt, "#FFFF00")

            # Row 3 (y=19): Phase label — phase colour (truncated to 10 chars)
            label_short = {
                "TRACK OPENS IN": "OPEN IN",
                "ENTER NOW":      "ENTER",
                "HEAT TIME REMAINING": "HEAT LEFT",
            }.get(self.model.primary_timer_label,
                  self.model.primary_timer_label)[:10]
            self._draw_centered(p, 19, label_short,
                                self.model.primary_timer_color)

            # Row 4 (y=25): Primary timer — phase colour
            self._draw_centered(p, 25, self.model.primary_timer,
                                self.model.primary_timer_color)

        # Status band — bottom 2 rows
        p.fillRect(0, self.ROWS - 2, self.COLS, 2,
                   self._apply_brightness(self.model.band_color))
