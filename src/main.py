import sys
from PySide6.QtWidgets import QApplication
from core.database import AtlasDatabase
from core.engine import AtlasEngine
from gui.windows import OperatorWindow
from gui.led_simulator import AtlasLEDSimulator

def main():
    app = QApplication(sys.argv)
    
    db = AtlasDatabase()
    engine = AtlasEngine(db)
    
    # NEW: We are phasing out the old PublicDisplay class 
    # to focus entirely on the LED Simulator hardware logic.
    operator = OperatorWindow(engine)
    led_sim = AtlasLEDSimulator()
    
    engine.model_updated.connect(operator.refresh)
    engine.model_updated.connect(led_sim.update_model)
    
    operator.show()
    led_sim.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
