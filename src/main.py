import sys
from PySide6.QtWidgets import QApplication
from core.database import AtlasDatabase
from core.engine import AtlasEngine
from core.config import AtlasConfig  # IMPORT THIS
from gui.windows import OperatorWindow
from gui.led_simulator import AtlasLEDSimulator


def main():
    app = QApplication(sys.argv)
    
    config = AtlasConfig()
    db = AtlasDatabase()
    engine = AtlasEngine(db)
    
    operator = OperatorWindow(engine)
    
    # Primary Display (Face A)
    front_sim = AtlasLEDSimulator(config)
    front_sim.setWindowTitle("ATLAS DISPLAY - SIDE A (FRONT)")
    engine.model_updated.connect(front_sim.update_model)
    front_sim.show()

    # Secondary Display (Face B) - Optional
    if config.double_sided:
        back_sim = AtlasLEDSimulator(config)
        back_sim.setWindowTitle("ATLAS DISPLAY - SIDE B (BACK)")
        engine.model_updated.connect(back_sim.update_model)
        back_sim.show()
    
    operator.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
