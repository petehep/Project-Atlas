import sys
import os
from PySide6.QtWidgets import QApplication, QStyleFactory
from core.database import AtlasDatabase
from core.engine import AtlasEngine
from gui.windows import OperatorWindow
from gui.led_simulator import AtlasLEDSimulator
from gui.lcd_display import AtlasLCDDisplay, AtlasHDMIOutput

# Simple data class to mimic our old JSON config
class DisplayConfig:
    def __init__(self, db):
        self.display_width = int(db.get_setting("display_width", 128))
        self.display_height = int(db.get_setting("display_height", 64))
        self.led_scale = int(db.get_setting("led_scale", 8))
        self.brightness = int(db.get_setting("brightness", 80))

def _create_display(backend_id, config):
    """Pick the display module based on the saved 'display_backend' setting.

    "simulator" -> AtlasLEDSimulator (default, current behaviour)
    "lcd"       -> AtlasLCDDisplay   (full-resolution monitor view)

    Both share the same update_model / set_brightness interface, so the
    signal wiring below is identical regardless of choice.
    """
    if backend_id == "lcd":
        return AtlasLCDDisplay(config)
    if backend_id == "hdmi":
        return AtlasHDMIOutput(config)
    return AtlasLEDSimulator(config)

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

    # Read appliance-mode preferences (both default to the CURRENT behaviour).
    auto_boot = db.get_bool_setting("auto_boot_enabled", False)
    backend_id = db.get_setting("display_backend", "simulator")

    # Build the chosen display and wire it to the engine (same slots either way)
    display = _create_display(backend_id, config)
    engine.model_updated.connect(display.update_model)
    engine.brightness_changed.connect(display.set_brightness)

    if auto_boot:
        # Clock mode: show only the display window (no operator console).
        display.show()
        display.raise_()
        display.activateWindow()
    else:
        # DEFAULT behaviour (unchanged): operator console + display window.
        operator_win = OperatorWindow(engine)
        operator_win.show()
        display.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
