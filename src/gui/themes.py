class AtlasTheme:
    # Colors
    BG_DARK = "#121212"
    BG_PANEL = "#1E1E1E"
    TXT_GREEN = "#00FF00"
    TXT_AMBER = "#FFA500"
    TXT_RED = "#FF0000"
    TXT_WHITE = "#FFFFFF"
    TXT_GREY = "#888888"

    # Stylesheets
    COCKPIT_BG = f"background-color: {BG_DARK}; color: {TXT_WHITE};"
    
    LABEL_HEADING = f"color: {TXT_GREY}; font-size: 14px; font-weight: bold; text-transform: uppercase;"
    
    READOUT_LARGE = (
        f"color: {TXT_GREEN}; "
        f"font-family: 'Courier New'; "
        f"font-size: 60px; "
        f"font-weight: bold; "
        f"background-color: black; "
        f"border: 1px solid #333; "
        f"padding: 10px;"
    )

    BTN_MASTER_ARM = (
        "background-color: #880000; "
        "color: white; "
        "font-weight: bold; "
        "font-size: 20px; "
        "border: 2px solid #550000; "
        "padding: 15px;"
    )

    BTN_CANCEL = (
        "background-color: #333; "
        "color: #888; "
        "font-weight: bold; "
        "font-size: 16px;"
    )
