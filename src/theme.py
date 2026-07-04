def app_stylesheet():
    return """
    QWidget {
        background-color: #1f2128;
        color: #f0f0f0;
        font-size: 14px;
        font-family: Noto Sans;
    }

    QFrame#Card {
        background-color: #2b2d36;
        border: 1px solid #444;
        border-radius: 12px;
    }

    QLabel#Title {
        font-size: 30px;
        font-weight: bold;
        color: white;
    }

    QLabel#Subtitle {
        color: #b8b8b8;
        font-size: 13px;
    }

    QLabel#CardTitle {
        font-size: 18px;
        font-weight: bold;
        color: #3daee9;
    }

    QLabel#Warning {
        color: #ffb86c;
        font-weight: bold;
    }

    QLabel#OkText {
        color: #7bd88f;
        font-weight: bold;
    }

    QLabel#BadText {
        color: #ff6b6b;
        font-weight: bold;
    }

    QListWidget {
        background-color: #30323b;
        border: 1px solid #505050;
        border-radius: 10px;
        padding: 6px;
        outline: none;
    }

    QListWidget::item {
        padding: 8px;
        border-radius: 6px;
    }

    QListWidget::item:selected {
        background-color: #3daee9;
        color: black;
    }

    QTextEdit {
        background-color: #30323b;
        border: 1px solid #505050;
        border-radius: 10px;
        padding: 8px;
        font-family: Monospace;
    }

    QPushButton {
        background-color: #3daee9;
        color: black;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #63c4ff;
    }

    QPushButton:disabled {
        background-color: #555;
        color: #aaa;
    }

    QComboBox,
    QLineEdit {
        background-color: #30323b;
        border: 1px solid #505050;
        border-radius: 8px;
        padding: 6px;
    }

    QCheckBox {
        padding: 6px;
    }

    QTabWidget::pane {
        border: 1px solid #444;
        border-radius: 8px;
        padding: 4px;
    }

    QTabBar::tab {
        background: #2b2d36;
        padding: 9px 16px;
        margin-right: 3px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }

    QTabBar::tab:selected {
        background: #3daee9;
        color: black;
        font-weight: bold;
    }
    """
