from PySide6.QtCore import QObject, Signal

class AtlasStateEngine(QObject):
    """The central authority for Project Atlas state and logic."""
    state_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._current_state = "STARTUP"
        print(f"[ENGINE] Initialized in state: {self._current_state}")

    def get_state(self):
        return self._current_state

    def set_state(self, new_state):
        self._current_state = new_state
        print(f"[ENGINE] State Transition -> {new_state}")
        self.state_changed.emit(new_state)
