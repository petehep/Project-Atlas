from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
                                QWidget, QPushButton, QTimeEdit, QTabWidget, 
                                QLineEdit, QFormLayout, QFrame, QTableWidget, 
                                QTableWidgetItem, QHeaderView, QMessageBox)
from PySide6.QtCore import Qt, QDateTime, QTimer
from gui.themes import AtlasTheme
from core.models import HeatConfig

class OperatorWindow(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Operator Console")
        self.setStyleSheet(AtlasTheme.COCKPIT_BG)
        self.resize(850, 750)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._setup_control_tab()
        self._setup_schedule_tab()

        self.engine.model_updated.connect(self.refresh)

    def _setup_control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.status_header = QLabel("LIVE FLIGHTLINE STATUS")
        self.status_header.setStyleSheet("color: #888; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.status_header)

        self.heat_status = QLabel("SYSTEM IDLE")
        self.heat_status.setStyleSheet("color: #00FF00; font-family: 'Courier New'; font-size: 50px; font-weight: bold; background: black; border: 2px solid #333; padding: 20px;")
        self.heat_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.heat_status)

        layout.addStretch()

        self.cancel_btn = QPushButton("ABORT / CANCEL ACTIVE HEAT")
        self.cancel_btn.setStyleSheet(AtlasTheme.BTN_CANCEL)
        self.cancel_btn.setFixedHeight(80) # Fixed the height issue
        self.cancel_btn.clicked.connect(self.engine.cancel_active_heat)
        layout.addWidget(self.cancel_btn)

        self.tabs.addTab(tab, "1. LIVE CONTROL")

    def _setup_schedule_tab(self):
        tab = QWidget()
        main_layout = QVBoxLayout(tab)

        # FORM SECTION
        form_group = QFrame()
        form_group.setStyleSheet("background: #1A1A1A; border: 1px solid #333; border-radius: 5px;")
        form_layout = QFormLayout(form_group)

        self.edit_heat_no = QLineEdit()
        self.edit_dir = QLineEdit("LEFT")
        self.edit_open = QTimeEdit(); self.edit_open.setDisplayFormat("HH:mm")
        self.edit_close = QTimeEdit(); self.edit_close.setDisplayFormat("HH:mm")
        self.edit_end = QTimeEdit(); self.edit_end.setDisplayFormat("HH:mm")

        input_css = "color: white; background: #222; border: 1px solid #444; font-size: 18px; padding: 8px;"
        for w in [self.edit_heat_no, self.edit_dir, self.edit_open, self.edit_close, self.edit_end]:
            w.setStyleSheet(input_css)

        form_layout.addRow("Heat Number:", self.edit_heat_no)
        form_layout.addRow("Thermalling Dir:", self.edit_dir)
        form_layout.addRow("Track Opens:", self.edit_open)
        form_layout.addRow("Track Closes:", self.edit_close)
        form_layout.addRow("Heat Ends:", self.edit_end)
        main_layout.addWidget(form_group)

        # ACTION BUTTONS
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("SAVE HEAT TO SCHEDULE")
        self.save_btn.setStyleSheet(AtlasTheme.BTN_MASTER_ARM) 
        self.save_btn.setFixedHeight(60) # Taller to prevent text clipping
        self.save_btn.clicked.connect(self._save_to_db)
        btn_layout.addWidget(self.save_btn)

        main_layout.addLayout(btn_layout)

        # THE TABLE
        self.schedule_table = QTableWidget(0, 5)
        self.schedule_table.setHorizontalHeaderLabels(["Heat", "Dir", "Open", "Close", "Status"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.setStyleSheet("background: #111; color: #EEE; gridline-color: #333; font-size: 14px;")
        main_layout.addWidget(self.schedule_table)

        self.tabs.addTab(tab, "2. DAILY SCHEDULE")
        self._update_schedule_table()
        self._prep_new_heat()

    def _prep_new_heat(self):
        """Auto-increments the heat number for convenience."""
        heats = self.engine.db.get_todays_schedule()
        next_no = len(heats) + 1
        self.edit_heat_no.setText(str(next_no))
        # Default the times to now + some buffers
        now = QDateTime.currentDateTime().time()
        self.edit_open.setTime(now.addSecs(300))
        self.edit_close.setTime(now.addSecs(600))
        self.edit_end.setTime(now.addSecs(3600))

    def _save_to_db(self):
        today = QDateTime.currentDateTime().date()
        def to_unix(qtime): return QDateTime(today, qtime.time()).toSecsSinceEpoch()

        # Simple Validation
        t_open = to_unix(self.edit_open)
        t_close = to_unix(self.edit_close)
        
        if t_close <= t_open:
            QMessageBox.critical(self, "Validation Error", "Track Close must be after Track Open!")
            return

        config = HeatConfig(
            heat_number=self.edit_heat_no.text(),
            thermalling_dir=self.edit_dir.text(),
            track_open=t_open,
            track_close=t_close,
            heat_end=to_unix(self.edit_end)
        )
        
        self.engine.db.save_heat(config)
        self._update_schedule_table()
        self._prep_new_heat() # Ready for the next one

    def _update_schedule_table(self):
        heats = self.engine.db.get_todays_schedule()
        self.schedule_table.setRowCount(len(heats))
        for row, h in enumerate(heats):
            self.schedule_table.setItem(row, 0, QTableWidgetItem(h['heat_number']))
            self.schedule_table.setItem(row, 1, QTableWidgetItem(h['thermalling_dir']))
            t_open = QDateTime.fromSecsSinceEpoch(int(h['track_open'])).toString("HH:mm")
            t_close = QDateTime.fromSecsSinceEpoch(int(h['track_close'])).toString("HH:mm")
            self.schedule_table.setItem(row, 2, QTableWidgetItem(t_open))
            self.schedule_table.setItem(row, 3, QTableWidgetItem(t_close))
            
            status_item = QTableWidgetItem(h['status'])
            if h['status'] == 'ACTIVE': status_item.setForeground(Qt.green)
            elif h['status'] == 'COMPLETED': status_item.setForeground(Qt.gray)
            elif h['status'] == 'CANCELLED': status_item.setForeground(Qt.red)
            self.schedule_table.setItem(row, 4, status_item)

    def refresh(self, model):
        if model.is_armed:
            msg = f"H{model.heat_number} | {model.thermalling_dir}\n{model.primary_timer}"
        else:
            msg = "STANDBY"
        self.heat_status.setText(msg)

class PublicDisplay(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Public Display")
        self.setStyleSheet("background-color: black;")
        self.resize(1024, 768)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        self.local_time = QLabel("00:00:00")
        self.local_time.setStyleSheet("color: white; font-family: 'Courier New'; font-size: 40px;")
        self.local_time.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.local_time)

        self.heat_dir_row = QLabel("HEAT: -- | DIR: ---")
        self.heat_dir_row.setStyleSheet("color: #00FFFF; font-size: 45px; font-weight: bold; border-top: 1px solid #222;")
        self.heat_dir_row.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.heat_dir_row)

        self.window_row = QLabel("OPEN: --:--   CLOSE: --:--")
        self.window_row.setStyleSheet("color: #00FF00; font-family: 'Courier New'; font-size: 45px; font-weight: bold;")
        self.window_row.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.window_row)

        self.phase_label = QLabel("SYSTEM IDLE")
        self.phase_label.setStyleSheet("color: #888; font-size: 35px; font-weight: bold; background: #111;")
        self.phase_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.phase_label)

        self.timer = QLabel("--:--")
        self.timer.setStyleSheet("font-size: 320px; font-family: 'Courier New'; font-weight: bold; color: #444;")
        self.timer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.timer)

        self.band = QWidget()
        self.band.setFixedHeight(30)
        self.band.setStyleSheet("background-color: #333;")
        main_layout.addWidget(self.band)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.engine.model_updated.connect(self.refresh)

    def refresh(self, model):
        self.local_time.setText(model.local_time)
        self.heat_dir_row.setText(f"HEAT: {model.heat_number} | DIR: {model.thermalling_dir}")
        self.window_row.setText(f"OPEN: {model.planned_open}   CLOSE: {model.planned_close}")
        self.timer.setText(model.primary_timer)
        self.timer.setStyleSheet(f"color: {model.primary_timer_color}; font-size: 320px; font-family: 'Courier New'; font-weight: bold;")
        self.phase_label.setText(model.primary_timer_label)
        self.phase_label.setStyleSheet(f"color: {model.primary_timer_color}; font-size: 35px; font-weight: bold; background: #050505;")
        self.band.setStyleSheet(f"background-color: {model.band_color};")
