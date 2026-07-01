from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
                                QWidget, QPushButton, QTimeEdit, QTabWidget, 
                                QLineEdit, QFormLayout)
from PySide6.QtCore import Qt, QDateTime
from gui.themes import AtlasTheme
from core.models import HeatConfig

class OperatorWindow(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Operator Console")
        self.setStyleSheet(AtlasTheme.COCKPIT_BG)
        self.resize(600, 500)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Build Tabs
        self._setup_control_tab()
        self._setup_schedule_tab()

        self.engine.model_updated.connect(self.refresh)

    def _setup_control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.heat_status = QLabel("SYSTEM IDLE")
        self.heat_status.setStyleSheet(AtlasTheme.READOUT_LARGE)
        layout.addWidget(self.heat_status)

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

        form.addRow("Heat Number:", self.edit_heat_no)
        form.addRow("Thermalling Dir:", self.edit_dir)
        form.addRow("Track Opens:", self.edit_open)
        form.addRow("Track Closes:", self.edit_close)
        form.addRow("Heat Ends:", self.edit_end)
        
        layout.addLayout(form)

        save_btn = QPushButton("ADD HEAT TO SCHEDULE")
        save_btn.setStyleSheet(AtlasTheme.BTN_MASTER_ARM) # Reusing style
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
        print(f"[UI] Heat {config.heat_number} saved to database.")

    def refresh(self, model):
        self.heat_status.setText(f"{model.heat_number} | {model.primary_timer}")

class PublicDisplay(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Public Display")
        self.setStyleSheet("background-color: black;")
        self.resize(800, 480)

        layout = QVBoxLayout()
        self.local_time = QLabel("00:00:00")
        self.local_time.setStyleSheet("color: white; font-family: 'Courier New'; font-size: 30px;")
        self.local_time.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.local_time)

        self.band = QWidget(); self.band.setFixedHeight(10); layout.addWidget(self.band)

        self.label = QLabel("READY")
        self.label.setStyleSheet("color: #888; font-size: 20px;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.timer = QLabel("--:--")
        self.timer.setStyleSheet("font-size: 180px; font-family: 'Courier New'; font-weight: bold;")
        self.timer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timer)

        container = QWidget(); container.setLayout(layout); self.setCentralWidget(container)
        self.engine.model_updated.connect(self.refresh)

    def refresh(self, model):
        self.local_time.setText(model.local_time)
        self.timer.setText(model.primary_timer)
        self.timer.setStyleSheet(f"color: {model.primary_timer_color}; font-size: 180px; font-family: 'Courier New'; font-weight: bold;")
        self.label.setText(model.primary_timer_label)
        self.label.setStyleSheet(f"color: {model.primary_timer_color}; font-size: 20px;")
        self.band.setStyleSheet(f"background-color: {model.band_color};")
