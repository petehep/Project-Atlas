import sys
import os
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from core.database import AtlasDatabase
from core.engine import AtlasEngine
from gui.windows import OperatorWindow
from gui.led_simulator import AtlasLEDSimulator
from gui.lcd_display import AtlasLCDDisplay, AtlasHDMIOutput

# Unique name for the single-instance local socket.
SERVER_NAME = "project-atlas-clock"

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

    # ---- Single-instance guard -------------------------------------------
    # If another copy of Atlas is already running, ask it to come to the
    # foreground and then exit this new instance. This stops multiple LED
    # windows from piling up at the top-left of the screen.
    probe = QLocalSocket()
    probe.connectToServer(SERVER_NAME)
    if probe.waitForConnected(200):
        probe.write(b"show")
        probe.flush()
        probe.waitForBytesWritten(200)
        probe.disconnectFromServer()
        return

    server = QLocalServer()
    server.removeServer(SERVER_NAME)  # clear any stale socket from a crash
    if not server.listen(SERVER_NAME):
        # Another instance grabbed the name in a race — just exit.
        return

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

    operator_win = None
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

    # When a second launch connects, bring this instance to the foreground.
    def _bring_to_front():
        if operator_win is not None:
            operator_win.show()
            operator_win.raise_()
            operator_win.activateWindow()
        display.show()
        display.raise_()
        display.activateWindow()

    def _on_new_connection():
        conn = server.nextPendingConnection()
        if conn is not None:
            conn.deleteLater()
        _bring_to_front()

    server.newConnection.connect(_on_new_connection)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
