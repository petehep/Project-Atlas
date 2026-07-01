from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,
                                QWidget, QPushButton, QTimeEdit)
from PySide6.QtCore import Qt, QTime, QDateTime
from gui.themes import AtlasTheme
from core.models import HeatConfig
import time

class OperatorWindow(QMainWindow):
    """The Glass Cockpit. Operator eyes only."""
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Operator Console")
        self.setStyleSheet(AtlasTheme.COCKPIT_BG)
        self.resize(500, 500)

        layout = QVBoxLayout()

        # Status
        self.status_label = QLabel("STATUS: IDLE")
        self.status_label.setStyleSheet(AtlasTheme.LABEL_HEADING)
        layout.addWidget(self.status_label)

        # Time Entry Fields
        def make_row(label_text):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {AtlasTheme.TXT_AMBER}; font-size: 14px;")
            lbl.setFixedWidth(200)
            editor = QTimeEdit()
            editor.setDisplayFormat("HH:mm")
            editor.setStyleSheet(
                f"color: {AtlasTheme.TXT_GREEN}; "
                f"background: black; "
                f"font-size: 20px; "
                f"font-family: 'Courier New'; "
                f"border: 1px solid #333;"
            )
            row.addWidget(lbl)
            row.addWidget(editor)
            container = QWidget()
            container.setLayout(row)
            layout.addWidget(container)
            return editor

        self.track_open_edit = make_row("TRACK OPENS:")
        self.track_close_edit = make_row("TRACK CLOSES:")
        self.heat_end_edit = make_row("HEAT ENDS:")

        # Arm Button
        self.arm_btn = QPushButton("MASTER ARM")
        self.arm_btn.setStyleSheet(AtlasTheme.BTN_MASTER_ARM)
        self.arm_btn.clicked.connect(self._on_arm)
        layout.addWidget(self.arm_btn)

        # Cancel Button
        self.cancel_btn = QPushButton("CANCEL / ABORT")
        self.cancel_btn.setStyleSheet(AtlasTheme.BTN_CANCEL)
        self.cancel_btn.clicked.connect(self.engine.cancel)
        layout.addWidget(self.cancel_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.engine.model_updated.connect(self.refresh)

    def _on_arm(self):
        """Convert QTime entries to Unix timestamps and arm the engine."""
        today = QDateTime.currentDateTime().date()

        def to_unix(qtime):
            dt = QDateTime(today, qtime)
            return dt.toSecsSinceEpoch()

        config = HeatConfig(
            heat_number="01",
            thermalling_dir="LEFT",
            track_open=to_unix(self.track_open_edit.time()),
            track_close=to_unix(self.track_close_edit.time()),
            heat_end=to_unix(self.heat_end_edit.time()),
        )
        self.engine.arm(config)

    def refresh(self, model):
        self.status_label.setText(
            f"STATUS: H{model.heat_number} | "
            f"{model.thermalling_dir} | "
            f"{model.primary_timer_label}"
        )
        self.arm_btn.setEnabled(not model.is_armed)


class PublicDisplay(QMainWindow):
    """The AtlasRenderer. Paints whatever the model says. No logic here."""
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Public Display")
        self.setStyleSheet("background-color: black;")
        self.resize(800, 480)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Local Time
        self.local_time = QLabel("00:00:00")
        self.local_time.setAlignment(Qt.AlignCenter)
        self.local_time.setStyleSheet(
            "color: white; font-family: 'Courier New'; font-size: 36px;"
        )
        layout.addWidget(self.local_time)

        # Separator Band
        self.band = QWidget()
        self.band.setFixedHeight(12)
        self.band.setStyleSheet("background-color: #333;")
        layout.addWidget(self.band)

        # Timer Label (e.g. "TRACK OPENS IN")
        self.timer_label = QLabel("AWAITING CONFIGURATION")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet(
            "color: #888; font-family: 'Courier New'; font-size: 24px; font-weight: bold;"
        )
        layout.addWidget(self.timer_label)

        # Primary Timer (the big number)
        self.primary_timer = QLabel("--:--")
        self.primary_timer.setAlignment(Qt.AlignCenter)
        self.primary_timer.setStyleSheet(
            f"color: #888888; font-family: 'Courier New'; "
            f"font-size: 180px; font-weight: bold;"
        )
        layout.addWidget(self.primary_timer)

        # Heat Info Row
        self.heat_info = QLabel("HEAT: -- | DIR: ---")
        self.heat_info.setAlignment(Qt.AlignCenter)
        self.heat_info.setStyleSheet(
            "color: #555; font-family: 'Courier New'; font-size: 22px;"
        )
        layout.addWidget(self.heat_info)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.engine.model_updated.connect(self.refresh)

    def refresh(self, model):
        """Pure paint. No logic. Just model -> pixels."""
        self.local_time.setText(model.local_time)
        self.primary_timer.setText(model.primary_timer)
        self.primary_timer.setStyleSheet(
            f"color: {model.primary_timer_color}; "
            f"font-family: 'Courier New'; "
            f"font-size: 180px; font-weight: bold;"
        )
        self.timer_label.setText(model.primary_timer_label)
        self.timer_label.setStyleSheet(
            f"color: {model.primary_timer_color}; "
            f"font-family: 'Courier New'; font-size: 24px; font-weight: bold;"
        )
        self.band.setStyleSheet(f"background-color: {model.band_color};")
        self.heat_info.setText(
            f"HEAT: {model.heat_number} | DIR: {model.thermalling_dir}"
        )
