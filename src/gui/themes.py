class AtlasTheme:
    COCKPIT_BG = "background-color: #0A0A0A; color: #EEE; font-family: 'Segoe UI', sans-serif;"
    
    BTN_MASTER_ARM = "background-color: #0066CC; color: white; border-radius: 5px; font-weight: bold; border: 1px solid #004488;"
    
    BTN_CANCEL = "background-color: #880000; color: white; border-radius: 5px; font-weight: bold; border: 1px solid #550000;"




    TABS = """
    QTabWidget {
        background-color: #111;
    }
    QTabWidget::pane { 
        border: 1px solid #333; 
        background-color: #111;
        top: -1px;
    }
    QTabBar {
        background-color: #111;
    }
    QTabBar::tab {
        background-color: #2A2A2A;
        color: #999;
        padding: 12px 30px;
        margin-right: 2px;
        border: 1px solid #444;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-weight: bold;
        font-size: 13px;
    }
    QTabBar::tab:selected {
        background-color: #0066CC;
        color: #FFFFFF;
        border: 2px solid #00FFFF;
        border-bottom: none;
        font-size: 14px;
    }
    QTabBar::tab:!selected {
        background-color: #2A2A2A;
        color: #AAAAAA;
    }
    QTabBar::tab:hover:!selected {
        background-color: #444;
        color: #FFF;
    }
    """


