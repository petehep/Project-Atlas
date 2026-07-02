import json
import os

class AtlasConfig:
    """Central configuration manager for Project Atlas."""
    
    def __init__(self, config_path="atlas_config.json"):
        self.config_path = config_path
        
        # Default Hardware Specs (The Baseline)
        self.panels_wide = 2
        self.panels_high = 4
        self.double_sided = False
        self.led_scale = 10
        
        # Load from file if it exists
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                data = json.load(f)
                display = data.get("display", {})
                self.panels_wide = display.get("panels_wide", self.panels_wide)
                self.panels_high = display.get("panels_high", self.panels_high)
                self.double_sided = display.get("double_sided", self.double_sided)
                self.led_scale = display.get("led_scale", self.led_scale)

    @property
    def display_width(self):
        return self.panels_wide * 32

    @property
    def display_height(self):
        # P10 panels are 16 pixels high
        return self.panels_high * 16
