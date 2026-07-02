from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QBrush, QPen
from gui.fonts import AtlasBitmapFont

class AtlasLEDSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.cols = 128
        self.rows = 64
        self.scale = 8 # Size of each 'LED' on your Mac screen
        self.setWindowTitle("ATLAS P10 VIRTUAL MATRIX (64x64)")
        self.setFixedSize(self.cols * self.scale, self.rows * self.scale)
        self.model = None

    def update_model(self, model):
        self.model = model
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(5, 5, 5)) # Deep black base

        if not self.model: return

        # Row 1: Time (Cyan)
        self._draw_string(p, 40, 2, self.model.local_time, "#00FFFF")

        if self.model.is_armed:
            # Row 2: Heat Info
            heat_txt = f"H{self.model.heat_number} {self.model.thermalling_dir}"
            self._draw_string(p, 40, 12, heat_txt, "#FFFFFF")

            # Row 3: Window
            win_txt = f"O {self.model.planned_open} C {self.model.planned_close}"
            self._draw_string(p, 18, 22, win_txt, "#AAAAAA")

            # Row 4: Label
            self._draw_string(p, 2, 35, self.model.primary_timer_label, self.model.primary_timer_color)

            # Row 5: BIG TIMER (Double Scale)
            self._draw_string(p, 40, 45, self.model.primary_timer, self.model.primary_timer_color, scale=2)
            
            # Row 6: Status Band
            p.fillRect(0, 62 * self.scale, 64 * self.scale, 2 * self.scale, QColor(self.model.band_color))
        else:
            self._draw_string(p, 2, 35, "SYSTEM IDLE", "#444444")

    def _draw_char(self, p, x, y, char, color_hex, scale=1):
        bitmap = AtlasBitmapFont.FONT_5x7.get(char.upper(), AtlasBitmapFont.FONT_5x7[' '])
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(color_hex)))

        for col_idx, col_data in enumerate(bitmap):
            for row_idx in range(7):
                if col_data & (1 << row_idx):
                    # Draw a single 'LED' circle
                    rect_x = (x + (col_idx * scale)) * self.scale
                    rect_y = (y + (row_idx * scale)) * self.scale
                    size = self.scale * scale
                    p.drawEllipse(rect_x, rect_y, size - 1, size - 1)

    def _draw_string(self, p, x, y, string, color_hex, scale=1):
        cur_x = x
        for char in string:
            self._draw_char(p, cur_x, y, char, color_hex, scale)
            cur_x += (6 * scale) # Move to next char (5px width + 1px spacing)
