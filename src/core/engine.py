import time
from PySide6.QtCore import QObject, QTimer, Signal
from core.models import AtlasDisplayModel

class AtlasEngine(QObject):
    """ The Brain of Project Atlas. Stateless, Read-Only, Clock-Driven. """
    model_updated = Signal(AtlasDisplayModel)

    def __init__(self, db):
        super().__init__()
        self.db = db
        
        # Drive the system at 10Hz (100ms)
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_tick)
        self.timer.start(100)

    def _process_tick(self):
        """ The 100ms Heartbeat. Ask the DB, Decide the Phase, Broadcast. """
        now = time.time()
        
        # 1. Ask the Source of Truth for the current heat
        heat = self.db.get_active_scheduled_heat(now)
        
        # 2. Determine Phase and Package for UI
        self._broadcast(now, heat)

    def _broadcast(self, now, heat):
        model = AtlasDisplayModel()
        model.local_time = time.strftime("%H:%M:%S", time.localtime(now))

        if heat:
            model.is_armed = True
            model.heat_number = heat['heat_number']
            model.thermalling_dir = heat['thermalling_dir']
            model.planned_open = time.strftime("%H:%M", time.localtime(heat['track_open']))
            model.planned_close = time.strftime("%H:%M", time.localtime(heat['track_close']))

            # PHASE LOGIC (Derived strictly from time)
            if now < heat['track_open']:
                # Phase 1: Pre-Open
                rem = int(heat['track_open'] - now)
                model.primary_timer, model.primary_timer_label = self._format_mm_ss(rem), "TRACK OPENS IN"
                model.primary_timer_color, model.band_color = "#FFFF00", "#444400" # Yellow
                
            elif now < heat['track_close']:
                # Phase 2: Track Entry window
                rem = int(heat['track_close'] - now)
                model.primary_timer, model.primary_timer_label = self._format_mm_ss(rem), "TRACK ENTRY REMAINING"
                model.primary_timer_color, model.band_color = "#00FF00", "#006400" # Green
            
            else:
                # Phase 3: Active Race
                rem = int(heat['heat_end'] - now)
                model.primary_timer, model.primary_timer_label = self._format_mm_ss(rem), "HEAT TIME REMAINING"
                model.primary_timer_color, model.band_color = "#FF0000", "#640000" # Red
        else:
            # System Idle
            model.is_armed = False
            model.primary_timer, model.primary_timer_label = "--:--", "SYSTEM IDLE"
            model.primary_timer_color, model.band_color = "#444", "#333"

        self.model_updated.emit(model)

    def _format_mm_ss(self, seconds):
        if seconds < 0: return "00:00"
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def cancel_active_heat(self):
        """ Operator override via the Database. """
        now = time.time()
        heat = self.db.get_active_scheduled_heat(now)
        if heat:
            self.db.set_heat_status(heat['id'], 'CANCELLED')
            print(f"ATLAS ENGINE: Heat {heat['heat_number']} was CANCELLED in DB.")
