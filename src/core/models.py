from pydantic import BaseModel
from typing import Optional

class HeatConfig(BaseModel):
    id: Optional[int] = None
    round_number: str = "1"
    heat_number: str = "01"
    group_letter: str = "A"
    thermalling_dir: str = "LEFT"
    track_open: float = 0.0
    track_close: float = 0.0
    heat_end: float = 0.0
    status: str = "READY"

class AtlasDisplayModel(BaseModel):
    local_time: str = "00:00:00"
    primary_timer: str = "--:--"
    primary_timer_label: str = "SYSTEM IDLE"
    primary_timer_color: str = "#888888"
    band_color: str = "#333333"
    round_number: str = "--"
    heat_number: str = "--"
    group_letter: str = "-"
    thermalling_dir: str = "---"
    direction_arrow: str = "-"
    is_armed: bool = False
    # ADDING THESE FOR THE STATIC HEADER:
    planned_open: str = "--:--"
    planned_close: str = "--:--"
