from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QBrush, QPen
from .fonts import AtlasBitmapFont

class AtlasLEDSimulator(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.cols = config.display_width
        self.rows = config.display_height
        self.scale = config.led_scale

        # Compact mode is intended for half-size / narrow displays.
        # Example: 64x64 display = compact.
        # Example: 128x64 display = full.
        self.compact_mode = self.cols <= 96
        
        self.setWindowTitle(f"ATLAS VIRTUAL LED [{self.cols}x{self.rows}]")
        self.setFixedSize(self.cols * self.scale, self.rows * self.scale)
        self.model = None

    def update_model(self, model):
        self.model = model
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(5, 5, 5))

        if not self.model:
            return

        if self.compact_mode:
            self._paint_compact(p)
        else:
            self._paint_full(p)

    def _paint_full(self, p):
        # Row 1: Time
        self._draw_string(p, 40, 2, self.model.local_time, "#00FFFF")

        if self.model.is_armed:
            # Row 2: Heat Info
            heat_txt = f"H{self.model.heat_number} {self.model.thermalling_dir}"
            self._draw_string(p, 40, 12, heat_txt, "#FFFF00")

            # Row 3: Window
            win_txt = f"O {self.model.planned_open} C {self.model.planned_close}"
            self._draw_string(p, 18, 22, win_txt, "#AAAAAA")

            # Row 4: Label
            label_txt = self._format_label(self.model.primary_timer_label)
            self._draw_string(p, 2, 35, label_txt, self.model.primary_timer_color)

            # Row 5: Big Timer
            self._draw_string(p, 40, 45, self.model.primary_timer, self.model.primary_timer_color, scale=2)
            
            # Row 6: Status Band
            p.fillRect(0, 62 * self.scale, self.cols * self.scale, 2 * self.scale, QColor(self.model.band_color))
        else:
            self._draw_string(p, 2, 35, "WAITING", "#888888")








    def _paint_compact(self, p):
        # Compact layout for 64x64 / half-width displays.
        # Six-row display strategy:
        # 1. Local Time
        # 2. Heat + Direction
        # 3. Track Open
        # 4. Track Close
        # 5. Phase Label
        # 6. Primary Timer

        self._draw_centered_string(p, 2, self.model.local_time, "#00FFFF")

        if self.model.is_armed:
            direction = self._format_direction(self.model.thermalling_dir)
            heat_txt = f"H{self.model.heat_number} {direction}"
            self._draw_centered_string(p, 12, heat_txt, "#FFFF00")

            open_txt = f"O {self.model.planned_open}"
            close_txt = f"C {self.model.planned_close}"
            self._draw_centered_string(p, 22, open_txt, "#AAAAAA")
            self._draw_centered_string(p, 32, close_txt, "#AAAAAA")

            label_txt = self._format_label(self.model.primary_timer_label)
            self._draw_centered_string(p, 42, label_txt, self.model.primary_timer_color)

            # Timer at normal scale here so all six rows breathe properly on 64x64.
            # Double scale is gorgeous, but it dominates the compact display.
            self._draw_centered_string(p, 53, self.model.primary_timer, self.model.primary_timer_color)

            # Status Band
            p.fillRect(0, 62 * self.scale, self.cols * self.scale, 2 * self.scale, QColor(self.model.band_color))
        else:
            self._draw_centered_string(p, 28, "WAIT", "#888888")


    def _format_label(self, label):
        if not self.compact_mode:
            return label

        compact_labels = {
            "TRACK OPENS IN": "OPEN IN",
            "ENTER NOW": "ENTER",
            "HEAT TIME REMAINING": "HEAT LEFT",
            "WAITING": "WAIT",
        }

        return compact_labels.get(label, label)

    def _format_direction(self, direction):
        d = str(direction).strip().upper()

        if d.startswith("L"):
            return "L"
        if d.startswith("R"):
            return "R"

        return d[:1] if d else "-"

    def _text_width(self, string, scale=1):
        # Font is 5px wide plus 1px spacing per character.
        # Existing renderer advances by 6px per char.
        if not string:
            return 0

        return len(string) * 6 * scale

    def _draw_centered_string(self, p, y, string, color_hex, scale=1):
        width = self._text_width(string, scale)
        x = max(0, int((self.cols - width) / 2))
        self._draw_string(p, x, y, string, color_hex, scale)

    def _draw_char(self, p, x, y, char, color_hex, scale=1):
        bitmap = AtlasBitmapFont.FONT_5x7.get(char.upper(), AtlasBitmapFont.FONT_5x7[' '])
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(color_hex)))

        for col_idx, col_data in enumerate(bitmap):
            for row_idx in range(7):
                if col_data & (1 << row_idx):
                    rect_x = (x + (col_idx * scale)) * self.scale
                    rect_y = (y + (row_idx * scale)) * self.scale
                    size = self.scale * scale
                    p.drawEllipse(rect_x, rect_y, size - 1, size - 1)

    def _draw_string(self, p, x, y, string, color_hex, scale=1):
        cur_x = x
        for char in string:
            self._draw_char(p, cur_x, y, char, color_hex, scale)
            cur_x += (6 * scale)
