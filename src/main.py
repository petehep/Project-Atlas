import sys
from PySide6.QtWidgets import QApplication
from core.database import AtlasDatabase
from core.engine import AtlasEngine
from gui.windows import OperatorWindow, PublicDisplay

def main():
    app = QApplication(sys.argv)

    db = AtlasDatabase()
    engine = AtlasEngine(db)
    op_console = OperatorWindow(engine)
    public_led = PublicDisplay(engine)

    op_console.show()
    public_led.show()

    print("[SYSTEM] Project Atlas Timeline Engine Active.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
