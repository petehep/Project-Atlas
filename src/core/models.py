from pydantic import BaseModel
from typing import Optional

class HeatConfig(BaseModel):
    id: Optional[int] = None
    heat_number: str = "01"
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
    heat_number: str = "--"
    thermalling_dir: str = "---"
    is_armed: bool = False
    # ADDING THESE FOR THE STATIC HEADER:
    planned_open: str = "--:--"
    planned_close: str = "--:--"
