import sys
from PySide6.QtWidgets import QApplication
from core.engine import AtlasStateEngine
from gui.windows import OperatorWindow, PublicDisplay

def main():
    app = QApplication(sys.argv)

    # 1. Initialize the Brain
    engine = AtlasStateEngine()

    # 2. Initialize the Windows
    op_console = OperatorWindow(engine)
    public_led = PublicDisplay(engine)

    # 3. Show them
    op_console.show()
    public_led.show()

    # Move public display to second monitor if it exists (Logic for later)
    # For now, they will just pop up on your laptop screen.

    print("[SYSTEM] Project Atlas Skeleton Active.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
