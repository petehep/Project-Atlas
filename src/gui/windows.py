from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt

class OperatorWindow(QMainWindow):
    """The interface for Peter (IT Director/Operator)."""
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Operator Console")
        self.resize(400, 300)

        # UI Layout
        layout = QVBoxLayout()
        self.status_label = QLabel(f"Current State: {self.engine.get_state()}")
        layout.addWidget(self.status_label)

        self.activate_btn = QPushButton("READY SYSTEM")
        self.activate_btn.clicked.connect(self.request_ready)
        layout.addWidget(self.activate_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Listen to engine
        self.engine.state_changed.connect(self.update_ui)

    def request_ready(self):
        self.engine.set_state("READY")

    def update_ui(self, state):
        self.status_label.setText(f"Current State: {state}")

class PublicDisplay(QMainWindow):
    """The high-visibility interface for the Pilots (HDMI Output)."""
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Atlas Public Display")
        self.setStyleSheet("background-color: black; color: white;")
        self.resize(800, 480) # Placeholder size for LED matrix

        self.label = QLabel("WAITING FOR SYSTEM...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 40px; font-weight: bold;")
        self.setCentralWidget(self.label)

        # Listen to engine
        self.engine.state_changed.connect(self.update_display)

    def update_display(self, state):
        self.label.setText(f"STATE: {state}")
