from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
                                QWidget, QPushButton, QTimeEdit, QTabWidget, 
                                QLineEdit, QFormLayout, QFrame)
from PySide6.QtCore import Qt, QDateTime
from gui.themes import AtlasTheme
from core.models import HeatConfig

class OperatorWindow(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Operator Console")
        self.setStyleSheet(AtlasTheme.COCKPIT_BG)
        self.resize(600, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._setup_control_tab()
        self._setup_schedule_tab()

        self.engine.model_updated.connect(self.refresh)

    def _setup_control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.status_header = QLabel("SYSTEM STATUS")
        self.status_header.setStyleSheet("color: #888; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.status_header)

        self.heat_status = QLabel("SYSTEM IDLE")
        self.heat_status.setStyleSheet("color: #00FF00; font-family: 'Courier New'; font-size: 40px; font-weight: bold; background: black; border: 2px solid #333; padding: 10px;")
        self.heat_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.heat_status)

        layout.addStretch()

        self.cancel_btn = QPushButton("ABORT / CANCEL ACTIVE HEAT")
        self.cancel_btn.setStyleSheet(AtlasTheme.BTN_CANCEL)
        self.cancel_btn.clicked.connect(self.engine.cancel_active_heat)
        layout.addWidget(self.cancel_btn)

        self.tabs.addTab(tab, "LIVE CONTROL")

    def _setup_schedule_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        form = QFormLayout()

        self.edit_heat_no = QLineEdit("01")
        self.edit_dir = QLineEdit("LEFT")
        self.edit_open = QTimeEdit(); self.edit_open.setDisplayFormat("HH:mm")
        self.edit_close = QTimeEdit(); self.edit_close.setDisplayFormat("HH:mm")
        self.edit_end = QTimeEdit(); self.edit_end.setDisplayFormat("HH:mm")

        input_css = "color: white; background: #222; border: 1px solid #444; font-size: 16px; padding: 5px;"
        for w in [self.edit_heat_no, self.edit_dir, self.edit_open, self.edit_close, self.edit_end]:
            w.setStyleSheet(input_css)

        form.addRow("Heat Number:", self.edit_heat_no)
        form.addRow("Thermalling Dir:", self.edit_dir)
        form.addRow("Track Opens:", self.edit_open)
        form.addRow("Track Closes:", self.edit_close)
        form.addRow("Heat Ends:", self.edit_end)
        
        layout.addLayout(form)

        save_btn = QPushButton("ADD HEAT TO SCHEDULE")
        save_btn.setStyleSheet(AtlasTheme.BTN_MASTER_ARM) 
        save_btn.setFixedHeight(50)
        save_btn.clicked.connect(self._save_to_db)
        layout.addWidget(save_btn)

        self.tabs.addTab(tab, "DAILY SCHEDULE")

    def _save_to_db(self):
        today = QDateTime.currentDateTime().date()
        def to_unix(qtime): return QDateTime(today, qtime.time()).toSecsSinceEpoch()

        config = HeatConfig(
            heat_number=self.edit_heat_no.text(),
            thermalling_dir=self.edit_dir.text(),
            track_open=to_unix(self.edit_open),
            track_close=to_unix(self.edit_close),
            heat_end=to_unix(self.edit_end)
        )
        self.engine.db.save_heat(config)

    def refresh(self, model):
        if model.is_armed:
            msg = f"H{model.heat_number} | {model.thermalling_dir}\n{model.primary_timer}"
        else:
            msg = "STANDBY"
        self.heat_status.setText(msg)

class PublicDisplay(QMainWindow):
    """Refined 6-Row Layout for P10/P5 LED Compatibility."""
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Public Display")
        self.setStyleSheet("background-color: black;")
        self.resize(1024, 768)

        # Main Vertical Layout (Representing the 6 Hardware Rows)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        # ROW 1: Local Time
        self.local_time = QLabel("00:00:00")
        self.local_time.setStyleSheet("color: white; font-family: 'Courier New'; font-size: 40px;")
        self.local_time.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.local_time)

        # ROW 2: Heat & Direction (Unified Row)
        self.heat_dir_row = QLabel("HEAT: -- | DIR: ---")
        self.heat_dir_row.setStyleSheet("color: #00FFFF; font-size: 45px; font-weight: bold; border-top: 1px solid #222;")
        self.heat_dir_row.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.heat_dir_row)

        # ROW 3: Window Boundaries (Open/Close)
        self.window_row = QLabel("OPEN: --:--   CLOSE: --:--")
        self.window_row.setStyleSheet("color: #00FF00; font-family: 'Courier New'; font-size: 45px; font-weight: bold;")
        self.window_row.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.window_row)

        # ROW 4: Current Phase Label
        self.phase_label = QLabel("SYSTEM IDLE")
        self.phase_label.setStyleSheet("color: #888; font-size: 35px; font-weight: bold; background: #111;")
        self.phase_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.phase_label)

        # ROW 5: The Primary Countdown (The Hero)
        self.timer = QLabel("--:--")
        self.timer.setStyleSheet("font-size: 320px; font-family: 'Courier New'; font-weight: bold; color: #444;")
        self.timer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.timer)

        # ROW 6: Status Band (The visual cue)
        self.band = QWidget()
        self.band.setFixedHeight(30)
        self.band.setStyleSheet("background-color: #333;")
        main_layout.addWidget(self.band)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        self.engine.model_updated.connect(self.refresh)

    def refresh(self, model):
        # Update Time
        self.local_time.setText(model.local_time)
        
        # Update Header Data
        self.heat_dir_row.setText(f"HEAT: {model.heat_number} | DIR: {model.thermalling_dir}")
        self.window_row.setText(f"OPEN: {model.planned_open}   CLOSE: {model.planned_close}")
        
        # Update Primary Countdown
        self.timer.setText(model.primary_timer)
        self.timer.setStyleSheet(f"color: {model.primary_timer_color}; font-size: 320px; font-family: 'Courier New'; font-weight: bold;")
        
        # Update Labels and Band
        self.phase_label.setText(model.primary_timer_label)
        self.phase_label.setStyleSheet(f"color: {model.primary_timer_color}; font-size: 35px; font-weight: bold; background: #050505;")
        self.band.setStyleSheet(f"background-color: {model.band_color};")
