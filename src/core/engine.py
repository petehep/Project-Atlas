import time
from PySide6.QtCore import QObject, Signal, QTimer, QDateTime
from core.models import AtlasDisplayModel, HeatConfig

class AtlasStateEngine(QObject):
    model_updated = Signal(AtlasDisplayModel)

    def __init__(self):
        super().__init__()
        self._state = "IDLE"
        self._config = None  # HeatConfig set by operator

        # The single heartbeat. That's all the timer does.
        self._pulse = QTimer()
        self._pulse.timeout.connect(self._heartbeat)
        self._pulse.start(100)  # 10Hz

    def arm(self, config: HeatConfig):
        """Operator has validated and submitted a heat configuration."""
        self._config = config
        self._state = "ARMED"
        print(f"[ENGINE] Armed. Track opens at {config.track_open}")

    def cancel(self):
        """Operator has aborted the heat."""
        self._config = None
        self._state = "IDLE"
        print("[ENGINE] Cancelled. Returning to IDLE.")

    def _heartbeat(self):
        """Called 10x per second. Asks 'what time is it?' and broadcasts."""
        now = time.time()

        if self._state == "IDLE" or self._config is None:
            self._broadcast_idle()
            return

        cfg = self._config

        if now < cfg.track_open:
            # Waiting for track to open
            remaining = cfg.track_open - now
            self._state = "ARMED"
            self._broadcast(
                timer=self._fmt(remaining),
                label="TRACK OPENS IN",
                timer_color="#FFA500",
                band_color="#FFA500"
            )

        elif now < cfg.track_close:
            # Insertion window is open
            remaining = cfg.track_close - now
            self._state = "INSERTION"
            self._broadcast(
                timer=self._fmt(remaining),
                label="TRACK ENTRY REMAINING",
                timer_color="#00FF00",
                band_color="#00FF00"
            )

        elif now < cfg.heat_end:
            # Heat is running
            remaining = cfg.heat_end - now
            self._state = "HEAT_RUNNING"
            self._broadcast(
                timer=self._fmt(remaining),
                label="HEAT TIME REMAINING",
                timer_color="#FF4444",
                band_color="#FF4444"
            )

        else:
            # Heat is complete
            self._state = "HEAT_COMPLETE"
            self._broadcast(
                timer="00:00",
                label="HEAT COMPLETE",
                timer_color="#555555",
                band_color="#555555"
            )

    def _broadcast(self, timer, label, timer_color, band_color):
        cfg = self._config
        model = AtlasDisplayModel(
            local_time=QDateTime.currentDateTime().toString("HH:mm:ss"),
            primary_timer=timer,
            primary_timer_label=label,
            primary_timer_color=timer_color,
            band_color=band_color,
            heat_number=cfg.heat_number,
            thermalling_dir=cfg.thermalling_dir,
            is_armed=True
        )
        self.model_updated.emit(model)

    def _broadcast_idle(self):
        model = AtlasDisplayModel(
            local_time=QDateTime.currentDateTime().toString("HH:mm:ss"),
        )
        self.model_updated.emit(model)

    @staticmethod
    def _fmt(seconds: float) -> str:
        """Formats seconds into MM:SS."""
        s = max(0, int(seconds))
        mins, secs = divmod(s, 60)
        return f"{mins:02d}:{secs:02d}"
