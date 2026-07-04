import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from external_iso import (
    available_writers,
    install_imagewriter,
    iso_info,
    iso_size_bytes,
    start_writer,
    writer_install_hint,
)
from formatter import restore
from system_check import system_report
from usb import (
    analyze,
    device_display_name,
    device_info,
    device_path,
    device_size_bytes,
    get_usb_devices,
    mountpoints,
)


class MainWindow(QWidget):
    def __init__(self, version):
        super().__init__()

        self.version = version
        self.devices = []
        self.iso_path = ""

        self.setWindowTitle("KStickFix")
        self.resize(1180, 780)

        main = QVBoxLayout()
        main.setContentsMargins(18, 18, 18, 18)
        main.setSpacing(14)

        main.addLayout(self.header())

        self.tabs = QTabWidget()
        self.tabs.addTab(self.usb_tab(), "💾 USB-Stick")
        self.tabs.addTab(self.iso_tab(), "💿 ISO-Schreiber")
        self.tabs.addTab(self.diagnose_tab(), "🩺 Diagnose")
        self.tabs.addTab(self.system_tab(), "⚙ Systemprüfung")
        self.tabs.addTab(self.about_tab(), "ℹ Über")

        main.addWidget(self.tabs)

        footer = QLabel(f"KStickFix {self.version} • saubere Version")
        footer.setObjectName("Subtitle")
        main.addWidget(footer)

        self.setLayout(main)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_refresh)
        self.timer.start(5000)

        self.load_devices()
        self.run_system_check()

    def resource_path(self, relative):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", relative))

    def header(self):
        layout = QHBoxLayout()

        logo = QLabel()
        pixmap = QPixmap(self.resource_path("icons/kstickfix.png"))
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(78, 78, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        title = QLabel("KStickFix")
        title.setObjectName("Title")

        subtitle = QLabel("USB-Stick-Werkzeugkasten für Linux")
        subtitle.setObjectName("Subtitle")

        title_box = QVBoxLayout()
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.refresh_button = QPushButton("🔄 Aktualisieren")
        self.refresh_button.clicked.connect(self.load_devices)

        layout.addWidget(logo)
        layout.addLayout(title_box)
        layout.addStretch()
        layout.addWidget(self.refresh_button)

        return layout

    def card(self, title, content):
        frame = QFrame()
        frame.setObjectName("Card")

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        label = QLabel(title)
        label.setObjectName("CardTitle")
        layout.addWidget(label)

        if isinstance(content, QVBoxLayout):
            layout.addLayout(content)
        else:
            layout.addWidget(content)

        frame.setLayout(layout)
        return frame

    def usb_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()

        self.device_list = QListWidget()
        self.device_list.itemClicked.connect(self.show_usb_info)
        layout.addWidget(self.card("💾 USB-Sticks", self.device_list), 1)

        right = QVBoxLayout()

        self.usb_status = QLabel("⚪ Kein USB-Stick ausgewählt")
        self.usb_status.setObjectName("Subtitle")

        self.usb_info = QTextEdit()
        self.usb_info.setReadOnly(True)

        self.fs_box = QComboBox()
        self.fs_box.addItems(["exFAT", "FAT32", "NTFS", "ext4"])

        self.schema_box = QComboBox()
        self.schema_box.addItems(["MBR", "GPT"])

        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Name, z. B. USBSTICK")

        self.restore_button = QPushButton("🛠 Wiederherstellen")
        self.restore_button.clicked.connect(self.restore_selected)
        self.restore_button.setEnabled(False)

        options = QHBoxLayout()
        options.addWidget(QLabel("Dateisystem:"))
        options.addWidget(self.fs_box)
        options.addWidget(QLabel("Schema:"))
        options.addWidget(self.schema_box)
        options.addWidget(QLabel("Name:"))
        options.addWidget(self.label_input)

        right.addWidget(self.usb_status)
        right.addWidget(self.usb_info)
        right.addLayout(options)
        right.addWidget(self.restore_button)

        layout.addWidget(self.card("ℹ Analyse und Wiederherstellung", right), 2)

        tab.setLayout(layout)
        return tab

    def iso_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()

        self.iso_device_list = QListWidget()
        self.iso_device_list.itemClicked.connect(self.show_iso_target)
        layout.addWidget(self.card("🎯 Ziel-USB-Stick", self.iso_device_list), 1)

        right = QVBoxLayout()

        self.iso_status = QLabel("⚪ ISO-Schreiber bereit")
        self.iso_status.setObjectName("Subtitle")

        self.iso_info = QTextEdit()
        self.iso_info.setReadOnly(True)

        self.iso_warning = QLabel(
            "⚠ Das Schreiben übernimmt ein externes Werkzeug. "
            "Bitte wähle dort denselben USB-Stick wie hier in KStickFix."
        )
        self.iso_warning.setObjectName("Warning")
        self.iso_warning.setWordWrap(True)

        self.iso_confirm = QCheckBox(
            "Ich habe verstanden, dass der ISO-Schreiber den Ziel-USB-Stick löscht."
        )
        self.iso_confirm.stateChanged.connect(self.update_iso_button)

        self.select_iso_button = QPushButton("📂 ISO-Datei auswählen")
        self.select_iso_button.clicked.connect(self.select_iso)

        self.reset_iso_button = QPushButton("↩ Auswahl zurücksetzen")
        self.reset_iso_button.clicked.connect(self.reset_iso_selection)

        self.install_writer_button = QPushButton("📦 Imagewriter installieren")
        self.install_writer_button.clicked.connect(self.install_writer)

        self.start_writer_button = QPushButton("💿 ISO-Schreiber öffnen")
        self.start_writer_button.clicked.connect(self.open_iso_writer)
        self.start_writer_button.setEnabled(False)

        actions = QHBoxLayout()
        actions.addWidget(self.select_iso_button)
        actions.addWidget(self.reset_iso_button)
        actions.addWidget(self.install_writer_button)
        actions.addWidget(self.start_writer_button)

        right.addWidget(self.iso_status)
        right.addWidget(self.iso_info)
        right.addWidget(self.iso_warning)
        right.addWidget(self.iso_confirm)
        right.addLayout(actions)

        layout.addWidget(self.card("💿 ISO über externen Schreiber", right), 2)

        tab.setLayout(layout)
        return tab

    def diagnose_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()

        self.diag_device_list = QListWidget()
        self.diag_device_list.itemClicked.connect(self.run_diagnose)
        layout.addWidget(self.card("💾 USB-Stick auswählen", self.diag_device_list), 1)

        self.diag_info = QTextEdit()
        self.diag_info.setReadOnly(True)
        layout.addWidget(self.card("🩺 Diagnose", self.diag_info), 2)

        tab.setLayout(layout)
        return tab

    def system_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.system_info = QTextEdit()
        self.system_info.setReadOnly(True)

        button = QPushButton("⚙ Systemprüfung erneut starten")
        button.clicked.connect(self.run_system_check)

        layout.addWidget(self.card("⚙ Systemprüfung", self.system_info))
        layout.addWidget(button)

        tab.setLayout(layout)
        return tab

    def about_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(
            f"KStickFix {self.version}\n"
            "====================\n\n"
            "Saubere, stabile Basisversion.\n\n"
            "Autor: Christian Wolf\n"
            "E-Mail: christianwolf5@gmx.net\n"
            "Entwicklungspartner: OpenAI ChatGPT\n\n"
            "Funktionen:\n"
            "- USB-Sticks erkennen\n"
            "- USB-Sticks analysieren\n"
            "- USB-Sticks wiederherstellen\n"
            "- externe ISO-Schreiber starten\n"
            "- Diagnose\n"
            "- Systemprüfung\n\n"
            "Lizenz: MIT\n"
        )

        layout.addWidget(self.card("ℹ Über KStickFix", text))
        tab.setLayout(layout)
        return tab

    def selected_from(self, widget):
        index = widget.currentRow()
        if index < 0 or index >= len(self.devices):
            return None
        return self.devices[index]

    def selected_usb(self):
        return self.selected_from(self.device_list)

    def selected_iso_usb(self):
        return self.selected_from(self.iso_device_list)

    def selected_diag_usb(self):
        return self.selected_from(self.diag_device_list)

    def set_label(self, label, text, kind="neutral"):
        icons = {
            "neutral": "⚪",
            "ok": "🟢",
            "warning": "🟡",
            "danger": "🔴",
        }
        label.setText(f"{icons.get(kind, '⚪')} {text}")

    def load_devices(self):
        self.devices = get_usb_devices()

        self.device_list.clear()
        self.iso_device_list.clear()
        self.diag_device_list.clear()

        if not self.devices:
            for widget in [self.device_list, self.iso_device_list, self.diag_device_list]:
                widget.addItem("Kein USB-Stick gefunden.")
            self.restore_button.setEnabled(False)
            self.update_iso_button()
            self.refresh_iso_text()
            return

        for device in self.devices:
            text = "💾 " + device_display_name(device)
            self.device_list.addItem(text)
            self.iso_device_list.addItem(text)
            self.diag_device_list.addItem(text)

        self.update_iso_button()
        self.refresh_iso_text()

    def auto_refresh(self):
        old = [d.get("path") or d.get("name") for d in self.devices]
        new = get_usb_devices()
        new_paths = [d.get("path") or d.get("name") for d in new]
        if old != new_paths:
            self.load_devices()

    def show_usb_info(self):
        device = self.selected_usb()
        if not device:
            return

        text, status, can_restore = analyze(device)
        self.usb_info.setPlainText(text)
        self.set_label(self.usb_status, "USB-Stick analysiert", status)
        self.restore_button.setEnabled(can_restore)

    def show_iso_target(self):
        self.refresh_iso_text()
        self.update_iso_button()

    def refresh_iso_text(self):
        text = ""

        text += "Auswahl in KStickFix\n"
        text += "====================\n\n"

        if self.iso_path:
            text += iso_info(self.iso_path)
        else:
            text += "ISO-Datei: Keine ausgewählt\n\n"

        device = self.selected_iso_usb()

        if device:
            text += "Ziel-USB-Stick:\n"
            text += f"{device_path(device)}\n"
            text += f"{device_display_name(device)}\n\n"
        else:
            text += "Ziel-USB-Stick: Kein USB-Stick ausgewählt\n\n"

        text += "Gefundene ISO-Schreiber:\n"
        writers = available_writers()
        if writers:
            for name, binary, path in writers:
                text += f"✅ {name}: {path}\n"
            self.install_writer_button.setEnabled(False)
        else:
            text += "❌ Kein unterstützter ISO-Schreiber gefunden.\n"
            self.install_writer_button.setEnabled(True)

        text += "\nHinweis für Imagewriter:\n"
        text += "Bitte wähle im externen ISO-Schreiber dieselbe ISO-Datei und denselben USB-Stick aus.\n"

        warnings = self.iso_warnings()
        if warnings:
            text += "\nWarnungen:\n"
            for warning in warnings:
                text += f"⚠ {warning}\n"

        self.iso_info.setPlainText(text)

    def iso_warnings(self):
        warnings = []

        device = self.selected_iso_usb()

        if not self.iso_path or not device:
            return warnings

        iso_size = iso_size_bytes(self.iso_path)
        usb_size = device_size_bytes(device)

        if iso_size and usb_size and usb_size < iso_size:
            warnings.append("Der USB-Stick ist kleiner als die ISO-Datei.")

        mounts = mountpoints(device)
        if mounts:
            warnings.append("Der USB-Stick ist aktuell eingehängt. Der ISO-Schreiber kann ihn eventuell selbst aushängen.")

        return warnings

    def select_iso(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "ISO-Datei auswählen",
            os.path.expanduser("~"),
            "ISO-Dateien (*.iso);;Alle Dateien (*)",
        )

        if not path:
            return

        self.iso_path = path
        self.iso_confirm.setChecked(False)
        self.refresh_iso_text()
        self.update_iso_button()

    def reset_iso_selection(self):
        self.iso_path = ""
        self.iso_confirm.setChecked(False)
        self.iso_device_list.clearSelection()
        self.refresh_iso_text()
        self.update_iso_button()
        self.set_label(self.iso_status, "Auswahl zurückgesetzt", "neutral")

    def update_iso_button(self):
        ready = bool(self.iso_path) and self.selected_iso_usb() is not None and self.iso_confirm.isChecked()
        self.start_writer_button.setEnabled(ready)

    def install_writer(self):
        ok, message = install_imagewriter()
        if ok:
            QMessageBox.information(self, "Installation gestartet", message)
        else:
            QMessageBox.critical(self, "Fehler", message)

    def open_iso_writer(self):
        if not self.iso_path:
            self.set_label(self.iso_status, "Bitte zuerst eine ISO-Datei auswählen", "warning")
            return

        device = self.selected_iso_usb()

        if not device:
            self.set_label(self.iso_status, "Bitte zuerst einen Ziel-USB-Stick auswählen", "warning")
            return

        if not self.iso_confirm.isChecked():
            self.set_label(self.iso_status, "Bitte Warnung bestätigen", "warning")
            return

        warning_text = (
            "KStickFix öffnet jetzt den externen ISO-Schreiber.\n\n"
            "Bitte wähle dort:\n\n"
            f"ISO-Datei:\n{self.iso_path}\n\n"
            f"USB-Stick:\n{device_path(device)}\n{device_display_name(device)}\n\n"
            "Achte darauf, dass du im externen Programm denselben USB-Stick auswählst."
        )

        QMessageBox.information(self, "Hinweis", warning_text)

        ok, message = start_writer(self.iso_path)

        if ok:
            self.set_label(self.iso_status, "ISO-Schreiber wurde gestartet", "ok")
            QMessageBox.information(self, "ISO-Schreiber gestartet", message)
            self.load_devices()
        else:
            self.set_label(self.iso_status, "ISO-Schreiber konnte nicht gestartet werden", "danger")
            QMessageBox.critical(self, "Fehler", message)

    def run_diagnose(self):
        device = self.selected_diag_usb()
        if not device:
            return

        text, status, _ = analyze(device)
        self.diag_info.setPlainText(text)

    def run_system_check(self):
        self.system_info.setPlainText(system_report())

    def restore_selected(self):
        device = self.selected_usb()
        if not device:
            return

        filesystem = self.fs_box.currentText()
        schema = self.schema_box.currentText()
        label = self.label_input.text().strip() or "USBSTICK"

        answer = QMessageBox.warning(
            self,
            "USB-Stick löschen?",
            "ACHTUNG!\n\n"
            "Der ausgewählte USB-Stick wird komplett gelöscht.\n\n"
            f"Dateisystem: {filesystem}\n"
            f"Schema: {schema}\n"
            f"Name: {label}\n\n"
            "Fortfahren?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        progress = QProgressDialog("USB-Stick wird wiederhergestellt...", "Abbrechen", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)

        def update(step, total, command):
            percent = int((step / total) * 100)
            progress.setValue(percent)
            progress.setLabelText(f"Schritt {step} von {total}\n{command}")
            QApplication.processEvents()

        success, output, message = restore(device, filesystem, label, schema, update)

        progress.setValue(100)
        self.usb_info.setPlainText(output)

        if success:
            self.set_label(self.usb_status, "USB-Stick wurde wiederhergestellt", "ok")
            QMessageBox.information(self, "Fertig", message)
            self.load_devices()
        else:
            self.set_label(self.usb_status, "Wiederherstellung fehlgeschlagen", "danger")
            QMessageBox.critical(self, "Fehler", message)
