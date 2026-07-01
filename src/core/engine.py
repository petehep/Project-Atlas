import time
from PySide6.QtCore import QObject, Signal, QTimer, QDateTime
from core.models import AtlasDisplayModel, HeatConfig
from core.database import AtlasDatabase

class AtlasStateEngine(QObject):
    model_updated = Signal(AtlasDisplayModel)

    def __init__(self):
        super().__init__()
        self.db = AtlasDatabase()
        self._state = "IDLE"
        self._config = None
        self._active_heat_id = None
        self.current_countdown = "--:--"

        # 10Hz Heartbeat
        self._pulse = QTimer()
        self._pulse.timeout.connect(self._heartbeat)
        self._pulse.start(100)

    def _heartbeat(self):
        now = time.time()

        # If Idle, look for next heat in DB
        if self._state == "IDLE":
            schedule = self.db.get_todays_schedule()
            for h_dict in schedule:
                if h_dict['status'] == 'READY' and h_dict['heat_end'] > now:
                    self._config = HeatConfig(**h_dict)
                    self._active_heat_id = h_dict['id']
                    self._state = "ARMED"
                    break

        if self._state == "IDLE" or not self._config:
            self.model_updated.emit(AtlasDisplayModel(
                local_time=QDateTime.currentDateTime().toString("HH:mm:ss")
            ))
            return

        # Timeline Logic
        cfg = self._config
        if now < cfg.track_open:
            self._broadcast(cfg.track_open - now, "TRACK OPENS IN", "#FFA500")
        elif now < cfg.track_close:
            self._state = "INSERTION"
            self._broadcast(cfg.track_close - now, "TRACK ENTRY REMAINING", "#00FF00")
        elif now < cfg.heat_end:
            if self._state != "RUNNING":
                self._state = "RUNNING"
                self.db.update_heat_status(self._active_heat_id, "ACTIVE")
            self._broadcast(cfg.heat_end - now, "HEAT TIME REMAINING", "#FF4444")
        else:
            self._state = "IDLE" # Return to Idle to seek next heat
            self.db.update_heat_status(self._active_heat_id, "COMPLETED")
            self._config = None

    def _broadcast(self, rem, label, color):
        mins, secs = divmod(int(rem), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        model = AtlasDisplayModel(
            local_time=QDateTime.currentDateTime().toString("HH:mm:ss"),
            primary_timer=time_str,
            primary_timer_label=label,
            primary_timer_color=color,
            band_color=color,
            heat_number=self._config.heat_number,
            thermalling_dir=self._config.thermalling_dir,
            is_armed=True
        )
        self.model_updated.emit(model)

    def cancel_active_heat(self):
        if self._active_heat_id:
            self.db.update_heat_status(self._active_heat_id, "CANCELLED")
            self._state = "IDLE"
            self._config = None
