import sys

from PySide6.QtWidgets import QApplication

from mainwindow import MainWindow
from theme import app_stylesheet


APP_NAME = "KStickFix"
APP_VERSION = "1.0.1"


def main():
    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setOrganizationName("KStickFix")
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(app_stylesheet())

    window = MainWindow(app_version=APP_VERSION)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
