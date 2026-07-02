class AtlasTheme:
    COCKPIT_BG = "background-color: #0A0A0A; color: #EEE; font-family: 'Segoe UI', sans-serif;"
    
    BTN_MASTER_ARM = "background-color: #0066CC; color: white; border-radius: 5px; font-weight: bold; border: 1px solid #004488;"
    
    BTN_CANCEL = "background-color: #880000; color: white; border-radius: 5px; font-weight: bold; border: 1px solid #550000;"

    TABS = """
    QTabWidget::pane { 
        border: 1px solid #333; 
        background: #111;
    }
    QTabBar::tab {
        background: #222;
        color: #888;
        padding: 12px 30px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-weight: bold;
    }
    QTabBar::tab:selected {
        background: #0066CC;
        color: white;
        border-bottom: 2px solid #00FFFF;
    }
    QTabBar::tab:hover:!selected {
        background: #333;
        color: #BBB;
    }
    """
