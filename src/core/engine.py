import time
from PySide6.QtCore import QObject, Signal, QTimer, QDateTime
from core.models import AtlasDisplayModel, HeatConfig
from core.database import AtlasDatabase

class AtlasStateEngine(QObject):
    """
    The brain of Project Atlas. 
    Manages the state transitions and broadcasts the display model.
    """
    model_updated = Signal(AtlasDisplayModel)

    def __init__(self):
        super().__init__()
        self.db = AtlasDatabase()
        self._state = "IDLE"
        self._config = None
        self._active_heat_id = None

        # 10Hz Heartbeat (Smooth enough for 1-second ticks)
        self._pulse = QTimer()
        self._pulse.timeout.connect(self._heartbeat)
        self._pulse.start(100)

    def _heartbeat(self):
        """Called every 100ms to evaluate the timeline."""
        now = time.time()

        # Phase 1: Search for Work
        # If we are idle, check the database for the next upcoming heat
        if self._state == "IDLE":
            schedule = self.db.get_todays_schedule()
            for h_dict in schedule:
                # We want a heat that is 'READY' and hasn't finished yet
                if h_dict['status'] == 'READY' and h_dict['heat_end'] > now:
                    self._config = HeatConfig(**h_dict)
                    self._active_heat_id = h_dict['id']
                    self._state = "ARMED"
                    print(f"[ENGINE] Next Heat Identified: H{self._config.heat_number}")
                    break

        # Phase 2: Processing / Broadcasting
        if self._state == "IDLE" or not self._config:
            # Broadcast a blank standby model
            self.model_updated.emit(AtlasDisplayModel(
                local_time=QDateTime.currentDateTime().toString("HH:mm:ss")
            ))
            return

        # Timeline Logic (The 'V-Model' of race states)
        cfg = self._config
        
        if now < cfg.track_open:
            # State: Waiting for Track Open
            self._broadcast(cfg.track_open - now, "TRACK OPENS IN", "#FFA500")
            
        elif now < cfg.track_close:
            # State: Track Entry Window
            if self._state != "INSERTION":
                self._state = "INSERTION"
            self._broadcast(cfg.track_close - now, "TRACK ENTRY REMAINING", "#00FF00")
            
        elif now < cfg.heat_end:
            # State: Live Race
            if self._state != "RUNNING":
                self._state = "RUNNING"
                # Update DB to reflect live status
                self.db.update_heat_status(self._active_heat_id, "ACTIVE")
            self._broadcast(cfg.heat_end - now, "HEAT TIME REMAINING", "#FF4444")
            
        else:
            # State: Heat Complete
            print(f"[ENGINE] Heat H{cfg.heat_number} completed.")
            self.db.update_heat_status(self._active_heat_id, "COMPLETED")
            self._state = "IDLE" 
            self._config = None
            self._active_heat_id = None

    def _broadcast(self, rem, label, color):
        """Formats data and sends it to the Renderers."""
        mins, secs = divmod(int(rem), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        # Format the static planned times for the pilot display header
        p_open = QDateTime.fromSecsSinceEpoch(int(self._config.track_open)).toString("HH:mm")
        p_close = QDateTime.fromSecsSinceEpoch(int(self._config.track_close)).toString("HH:mm")

        model = AtlasDisplayModel(
            local_time=QDateTime.currentDateTime().toString("HH:mm:ss"),
            primary_timer=time_str,
            primary_timer_label=label,
            primary_timer_color=color,
            band_color=color,
            heat_number=self._config.heat_number,
            thermalling_dir=self._config.thermalling_dir,
            is_armed=True,
            planned_open=p_open,
            planned_close=p_close
        )
        self.model_updated.emit(model)

    def cancel_active_heat(self):
        """Manual override from Operator Console."""
        if self._active_heat_id:
            self.db.update_heat_status(self._active_heat_id, "CANCELLED")
            print(f"[ENGINE] Heat Cancellation Triggered for ID: {self._active_heat_id}")
            self._state = "IDLE"
            self._config = None
            self._active_heat_id = None
