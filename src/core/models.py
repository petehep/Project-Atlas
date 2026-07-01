from pydantic import BaseModel

class HeatConfig(BaseModel):
    """The operator-defined parameters for a single heat."""
    heat_number: str = "01"
    thermalling_dir: str = "LEFT"
    track_open: float = 0.0    # Unix timestamp
    track_close: float = 0.0   # Unix timestamp
    heat_end: float = 0.0      # Unix timestamp

class AtlasDisplayModel(BaseModel):
    """The immutable snapshot of what the renderer should paint."""
    local_time: str = "00:00:00"
    primary_timer: str = "--:--"
    primary_timer_label: str = "AWAITING CONFIGURATION"
    primary_timer_color: str = "#888888"
    band_color: str = "#333333"
    heat_number: str = "--"
    thermalling_dir: str = "---"
    is_armed: bool = False
