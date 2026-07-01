from PySide6.QtCore import QObject, Signal
from core.timers import AtlasTimerEngine

class AtlasStateEngine(QObject):
    state_changed = Signal(str)
    timer_tick = Signal(str)

    def __init__(self):
        super().__init__()
        self._current_state = "STARTUP"
        self.timer = AtlasTimerEngine()
        
        # Forward the timer signals to the rest of the app
        self.timer.tick.connect(self.timer_tick.emit)
        self.timer.finished.connect(self._on_timer_finished)

    def get_state(self):
        return self._current_state

    def activate_heat(self, seconds):
        if self._current_state != "RUNNING":
            self._current_state = "RUNNING"
            self.state_changed.emit("RUNNING")
            self.timer.start_countdown(seconds)

    def _on_timer_finished(self):
        self._current_state = "FINISHED"
        self.state_changed.emit("FINISHED")
