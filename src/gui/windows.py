from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
                    QWidget, QPushButton, QTimeEdit, QLineEdit, 
                    QFormLayout, QFrame, QTableWidget, QTableWidgetItem, 
                    QHeaderView, QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt, QDateTime
from gui.themes import AtlasTheme
from core.models import HeatConfig

class OperatorWindow(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Operator Console")
        self.setStyleSheet(AtlasTheme.COCKPIT_BG)
        self.resize(900, 850)

        self._selected_heat_id = None

        # Main Layout Container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # STEP 1: Custom Navigation Bar
        nav_bar = QHBoxLayout()
        self.btn_live = QPushButton("LIVE")
        self.btn_schedule = QPushButton("SCHEDULE")
        self.btn_settings = QPushButton("SETTINGS")
        
        self.nav_buttons = [self.btn_live, self.btn_schedule, self.btn_settings]
        
        for i, btn in enumerate(self.nav_buttons):
            btn.setFixedHeight(50)
            btn.setFixedWidth(290)
            btn.clicked.connect(lambda checked=False, index=i: self._switch_tab(index))
            nav_bar.addWidget(btn)
        
        main_layout.addLayout(nav_bar)

        # STEP 2: The Content Stack
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self._setup_control_tab()
        self._setup_schedule_tab()
        self._setup_settings_tab()

        # Start on LIVE
        self._switch_tab(0)

        self.engine.model_updated.connect(self.refresh)

    def _switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        
        # Style the buttons to show which one is active
        active_css = "background-color: #0066CC; color: white; font-weight: bold; border: 2px solid #00FFFF; font-size: 16px;"
        inactive_css = "background-color: #333; color: white; border: 1px solid #555; font-size: 16px;"
        
        for i, btn in enumerate(self.nav_buttons):
            btn.setStyleSheet(active_css if i == index else inactive_css)

    def _setup_control_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        self.status_header = QLabel("LIVE FLIGHTLINE STATUS")
        self.status_header.setStyleSheet("color: #888; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.status_header)

        self.heat_status = QLabel("WAITING")
        self.heat_status.setStyleSheet("color: #00FF00; font-family: 'Courier New'; font-size: 50px; font-weight: bold; background: black; border: 2px solid #333; padding: 20px;")
        self.heat_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.heat_status)

        layout.addStretch()

        self.cancel_btn = QPushButton("ABORT / CANCEL ACTIVE HEAT")
        self.cancel_btn.setStyleSheet(AtlasTheme.BTN_CANCEL)
        self.cancel_btn.setFixedHeight(80)
        self.cancel_btn.clicked.connect(self.engine.cancel_active_heat)
        layout.addWidget(self.cancel_btn)

        self.stack.addWidget(page)

    def _setup_schedule_tab(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)

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

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("ADD NEW HEAT")
        self.save_btn.setStyleSheet(AtlasTheme.BTN_MASTER_ARM) 
        self.save_btn.setFixedHeight(60)
        self.save_btn.clicked.connect(self._save_to_db)
        btn_layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton("NEW / CLEAR")
        self.clear_btn.setStyleSheet("background: #444; color: white; border-radius: 5px; font-weight: bold;")
        self.clear_btn.setFixedHeight(60)
        self.clear_btn.clicked.connect(self._prep_new_heat)
        btn_layout.addWidget(self.clear_btn)

        self.delete_btn = QPushButton("DELETE")
        self.delete_btn.setStyleSheet("background: #700; color: white; border-radius: 5px; font-weight: bold;")
        self.delete_btn.setFixedHeight(60)
        self.delete_btn.setVisible(False)
        self.delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(self.delete_btn)
        main_layout.addLayout(btn_layout)

        self.schedule_table = QTableWidget(0, 6)
        self.schedule_table.setHorizontalHeaderLabels(["ID", "Heat", "Dir", "Open", "Close", "Status"])
        self.schedule_table.setColumnHidden(0, True)
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.schedule_table.setStyleSheet("background: #111; color: #EEE; gridline-color: #333; font-size: 14px;")
        self.schedule_table.cellClicked.connect(self._on_row_selected)
        main_layout.addWidget(self.schedule_table)

        self.stack.addWidget(page)
        self._update_schedule_table()
        self._prep_new_heat()

    def _setup_settings_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        form_group = QFrame()
        form_group.setStyleSheet("background: #1A1A1A; border: 1px solid #333; border-radius: 5px;")
        form_layout = QFormLayout(form_group)

        input_css = "color: white; background: #222; border: 1px solid #444; font-size: 18px; padding: 8px;"

        self.edit_comp_name = QLineEdit()
        self.edit_comp_name.setStyleSheet(input_css)
        self.edit_comp_name.setPlaceholderText("e.g. Strathalbyn Summer Regionals 2026")
        self.edit_comp_name.setText(self.engine.db.get_setting("competition_name", ""))

        self.edit_comp_date = QLineEdit()
        self.edit_comp_date.setStyleSheet(input_css)
        self.edit_comp_date.setPlaceholderText("e.g. 2026-07-01")
        self.edit_comp_date.setText(self.engine.db.get_setting("competition_date", ""))

        form_layout.addRow("Competition Name:", self.edit_comp_name)
        form_layout.addRow("Competition Date:", self.edit_comp_date)
        layout.addWidget(form_group)

        save_btn = QPushButton("SAVE SETTINGS")
        save_btn.setStyleSheet(AtlasTheme.BTN_MASTER_ARM)
        save_btn.setFixedHeight(60)
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()
        self.stack.addWidget(page)

    def _save_settings(self):
        self.engine.db.save_setting("competition_name", self.edit_comp_name.text())
        self.engine.db.save_setting("competition_date", self.edit_comp_date.text())
        QMessageBox.information(self, "Settings Saved", "Competition settings have been saved successfully.")

    def _on_row_selected(self, row, column):
        self._selected_heat_id = int(self.schedule_table.item(row, 0).text())
        self.edit_heat_no.setText(self.schedule_table.item(row, 1).text())
        self.edit_dir.setText(self.schedule_table.item(row, 2).text())
        t_open = QDateTime.fromString(self.schedule_table.item(row, 3).text(), "HH:mm").time()
        t_close = QDateTime.fromString(self.schedule_table.item(row, 4).text(), "HH:mm").time()
        self.edit_open.setTime(t_open)
        self.edit_close.setTime(t_close)
        self.save_btn.setText("UPDATE SELECTED HEAT")
        self.delete_btn.setVisible(True)

    def _prep_new_heat(self):
        self._selected_heat_id = None
        self.save_btn.setText("ADD NEW HEAT")
        self.delete_btn.setVisible(False)
        heats = self.engine.db.get_todays_schedule()
        next_no = len(heats) + 1
        self.edit_heat_no.setText(str(next_no))
        now = QDateTime.currentDateTime().time()
        self.edit_open.setTime(now.addSecs(300))
        self.edit_close.setTime(now.addSecs(600))
        self.edit_end.setTime(now.addSecs(3600))

    def _save_to_db(self):
        today = QDateTime.currentDateTime().date()
        def to_unix(qtime): return QDateTime(today, qtime.time()).toSecsSinceEpoch()
        t_open = to_unix(self.edit_open)
        t_close = to_unix(self.edit_close)
        
        if t_close <= t_open:
            QMessageBox.critical(self, "Validation Error", "Track Close must be after Track Open!")
            return

        config = HeatConfig(
            id=self._selected_heat_id,
            heat_number=self.edit_heat_no.text(),
            thermalling_dir=self.edit_dir.text(),
            track_open=t_open,
            track_close=t_close,
            heat_end=to_unix(self.edit_end)
        )
        self.engine.db.save_heat(config)
        self._update_schedule_table()
        self._prep_new_heat()

    def _delete_selected(self):
        if self._selected_heat_id:
            reply = QMessageBox.question(self, 'Confirm', 'Delete this heat?', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.engine.db.delete_heat(self._selected_heat_id)
                self._update_schedule_table()
                self._prep_new_heat()

    def _update_schedule_table(self):
        heats = self.engine.db.get_todays_schedule()
        self.schedule_table.setRowCount(len(heats))
        for row, h in enumerate(heats):
            self.schedule_table.setItem(row, 0, QTableWidgetItem(str(h['id'])))
            self.schedule_table.setItem(row, 1, QTableWidgetItem(h['heat_number']))
            self.schedule_table.setItem(row, 2, QTableWidgetItem(h['thermalling_dir']))
            t_open = QDateTime.fromSecsSinceEpoch(int(h['track_open'])).toString("HH:mm")
            t_close = QDateTime.fromSecsSinceEpoch(int(h['track_close'])).toString("HH:mm")
            self.schedule_table.setItem(row, 3, QTableWidgetItem(t_open))
            self.schedule_table.setItem(row, 4, QTableWidgetItem(t_close))
            status_item = QTableWidgetItem(h['status'])
            if h['status'] == 'ACTIVE': status_item.setForeground(Qt.green)
            elif h['status'] == 'COMPLETED': status_item.setForeground(Qt.gray)
            elif h['status'] == 'CANCELLED': status_item.setForeground(Qt.red)
            self.schedule_table.setItem(row, 5, status_item)

    def refresh(self, model):
        if model.is_armed:
            msg = f"H{model.heat_number} | {model.thermalling_dir}\n{model.primary_timer}"
        else:
            msg = "WAITING"
        self.heat_status.setText(msg)
