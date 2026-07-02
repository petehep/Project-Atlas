import sys
import os
from PySide6.QtWidgets import QApplication, QStyleFactory
from core.database import AtlasDatabase
from core.engine import AtlasEngine
from gui.windows import OperatorWindow
from gui.led_simulator import AtlasLEDSimulator

# Simple data class to mimic our old JSON config
class DisplayConfig:
    def __init__(self, db):
        self.display_width = int(db.get_setting("display_width", 128))
        self.display_height = int(db.get_setting("display_height", 64))
        self.led_scale = int(db.get_setting("led_scale", 8))

def main():
    app = QApplication(sys.argv)
    
    # Force Fusion style for cross-platform consistency (especially macOS tabs)
    app.setStyle(QStyleFactory.create("Fusion"))

    # Initialize Database
    db = AtlasDatabase()
    
    # Initialize Engine
    engine = AtlasEngine(db)

    # Load Dynamic Display Config from Database
    config = DisplayConfig(db)

    # Launch Operator Console
    operator_win = OperatorWindow(engine)
    operator_win.show()

    # Launch LED Simulator
    led_sim = AtlasLEDSimulator(config)
    engine.model_updated.connect(led_sim.update_model)
    led_sim.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
