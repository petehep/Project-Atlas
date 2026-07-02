import time
from PySide6.QtCore import QObject, Signal, QTimer
from core.models import AtlasDisplayModel

class AtlasEngine(QObject):
    model_updated = Signal(object)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.model = AtlasDisplayModel()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def tick(self):
        self.model.local_time = time.strftime("%H:%M:%S")
        self._update_state()
        self.model_updated.emit(self.model)

    def _update_state(self):
        now = int(time.time())
        active_heat = self.db.get_active_heat()

        # Phase 1: Look for the heat we SHOULD be running
        if not active_heat:
            next_heat = self.db.get_next_pending_heat()
            
            if next_heat:
                # If we are within 15 minutes (900s), activate it automatically!
                if (next_heat['track_open'] - now) <= 900:
                    self.db.set_heat_status(next_heat['id'], 'ACTIVE')
                    active_heat = self.db.get_active_heat()
                else:
                    # It's more than 15 mins away. 
                    # We show WHAT is coming, but stay in WAITING mode.
                    self.model.is_armed = True
                    self.model.heat_number = next_heat['heat_number']
                    self.model.thermalling_dir = next_heat['thermalling_dir']
                    self.model.primary_timer_label = "WAITING"
                    self.model.primary_timer = "--:--"
                    self.model.primary_timer_color = "#444444"
                    self.model.band_color = "#222222"
                    return
            else:
                # No heats scheduled at all
                self.model.is_armed = False
                return

        # Phase 2: Handle the ACTIVE heat
        h = active_heat
        self.model.is_armed = True
        self.model.heat_number = h['heat_number']
        self.model.thermalling_dir = h['thermalling_dir']
        
        # We need these formatted for the LED simulator/Public Display
        self.model.planned_open = time.strftime("%H:%M", time.localtime(h['track_open']))
        self.model.planned_close = time.strftime("%H:%M", time.localtime(h['track_close']))

        if now < h['track_open']:
            self.model.primary_timer_label = "TRACK OPENS IN"
            self.model.primary_timer = self._format_seconds(h['track_open'] - now)
            self.model.primary_timer_color = "#FFFF00" # Yellow
            self.model.band_color = "#555500"
        
        elif now < h['track_close']:
            self.model.primary_timer_label = "ENTER NOW"
            self.model.primary_timer = self._format_seconds(h['track_close'] - now)
            self.model.primary_timer_color = "#00FF00" # Green
            self.model.band_color = "#004400"
            
        elif now < h['heat_end']:
            self.model.primary_timer_label = "HEAT TIME REMAINING"
            self.model.primary_timer = self._format_seconds(h['heat_end'] - now)
            self.model.primary_timer_color = "#FF0000" # Red
            self.model.band_color = "#440000"
            
        else:
            # Time's up! Complete this heat.
            self.db.set_heat_status(h['id'], 'COMPLETED')
            self.model.is_armed = False

    def cancel_active_heat(self):
        self.db.cancel_active_heat()
        self.model.is_armed = False

    def _format_seconds(self, seconds):
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02d}:{secs:02d}"
