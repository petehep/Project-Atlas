from pydantic import BaseModel
from typing import Optional

class HeatConfig(BaseModel):
    """The formal definition of a Heat's parameters."""
    id: Optional[int] = None
    heat_number: str = "01"
    thermalling_dir: str = "LEFT"
    track_open: float = 0.0    # Unix timestamp
    track_close: float = 0.0   # Unix timestamp
    heat_end: float = 0.0      # Unix timestamp
    status: str = "READY"

class AtlasDisplayModel(BaseModel):
    """The snapshot used by the renderers to draw the screen."""
    local_time: str = "00:00:00"
    primary_timer: str = "--:--"
    primary_timer_label: str = "SYSTEM IDLE"
    primary_timer_color: str = "#888888"
    band_color: str = "#333333"
    heat_number: str = "--"
    thermalling_dir: str = "---"
    is_armed: bool = False
