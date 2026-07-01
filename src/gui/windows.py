from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt

class OperatorWindow(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Operator Console")
        self.resize(400, 300)

        layout = QVBoxLayout()
        self.status_label = QLabel(f"Current State: {self.engine.get_state()}")
        layout.addWidget(self.status_label)

        self.timer_label = QLabel("T-Minus: --:--")
        self.timer_label.setStyleSheet("font-size: 20px; font-weight: bold; color: blue;")
        layout.addWidget(self.timer_label)

        self.activate_btn = QPushButton("ACTIVATE TEST HEAT (15m)")
        self.activate_btn.clicked.connect(self.request_activation)
        layout.addWidget(self.activate_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Signal Connections
        self.engine.state_changed.connect(self.update_ui)
        self.engine.timer_tick.connect(self.update_timer)

    def request_activation(self):
        # We tell the engine to activate a 15-minute window
        self.engine.activate_heat(900) 

    def update_ui(self, state):
        self.status_label.setText(f"Current State: {state}")

    def update_timer(self, time_str):
        self.timer_label.setText(f"T-Minus: {time_str}")

class PublicDisplay(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Public Display")
        self.setStyleSheet("background-color: black; color: white;")
        self.resize(800, 480)

        layout = QVBoxLayout()
        self.clock_label = QLabel("00:00")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("font-size: 120px; font-family: 'Courier New'; color: green;")
        layout.addWidget(self.clock_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.engine.timer_tick.connect(self.update_display)

    def update_display(self, time_str):
        self.clock_label.setText(time_str)
