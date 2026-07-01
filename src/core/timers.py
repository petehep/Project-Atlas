import time
from PySide6.QtCore import QObject, QTimer, Signal

class AtlasTimerEngine(QObject):
    """The precision heartbeat of Project Atlas."""
    tick = Signal(str)  # Emits the 'MM:SS' string for the display
    finished = Signal() # Emits when countdown hits zero

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_tick)
        
        self.target_end_time = 0
        self.is_running = False

    def start_countdown(self, duration_seconds):
        """Starts a countdown from now for N seconds."""
        self.target_end_time = time.time() + duration_seconds
        self.is_running = True
        self.timer.start(100) # 10Hz pulse (100ms)
        print(f"[TIMER] Countdown started for {duration_seconds}s")

    def stop(self):
        self.timer.stop()
        self.is_running = False
        print("[TIMER] Stopped")

    def _process_tick(self):
        remaining = self.target_end_time - time.time()
        
        if remaining <= 0:
            self.tick.emit("00:00")
            self.stop()
            self.finished.emit()
            return

        # Convert to MM:SS format
        mins, secs = divmod(int(remaining), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.tick.emit(time_str)
