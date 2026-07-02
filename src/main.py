import sys
from PySide6.QtWidgets import QApplication
from core.database import AtlasDatabase
from core.engine import AtlasEngine
from core.config import AtlasConfig  # IMPORT THIS
from gui.windows import OperatorWindow
from gui.led_simulator import AtlasLEDSimulator

def main():
    app = QApplication(sys.argv)
    
    # 0. Load Configuration
    config = AtlasConfig()
    
    # 1. Initialize Core
    db = AtlasDatabase()
    engine = AtlasEngine(db)
    
    # 2. Initialize UI (Passing config where needed)
    operator = OperatorWindow(engine)
    led_sim = AtlasLEDSimulator(config) # Pass config here
    
    # 3. Connections
    engine.model_updated.connect(operator.refresh)
    engine.model_updated.connect(led_sim.update_model)
    
    operator.show()
    led_sim.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
