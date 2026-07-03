import os

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QTextEdit, QComboBox,
    QLineEdit, QFrame, QCheckBox, QProgressDialog,
    QApplication, QFileDialog, QTabWidget
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

from usb_manager import get_usb_devices, device_display_name
from analyzer import device_info_text, analyze_device
from formatter import restore_usb_device
from iso_writer import iso_info, write_iso_to_usb
from repair import diagnose_device
from system_check import system_report
from dialogs import confirm_restore, confirm_iso_write, show_error, show_info


class MainWindow(QWidget):
    def __init__(self, app_version="1.0.1"):
        super().__init__()

        self.app_version = app_version
        self.setWindowTitle("KStickFix")
        self.resize(1180, 780)

        self.devices = []
        self.iso_path = ""

        main = QVBoxLayout()
        main.setContentsMargins(18, 18, 18, 18)
        main.setSpacing(14)

        main.addLayout(self.create_header())

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_usb_tab(), "💾 USB-Stick")
        self.tabs.addTab(self.create_iso_tab(), "💿 ISO schreiben")
        self.tabs.addTab(self.create_diagnose_tab(), "🩺 Diagnose")
        self.tabs.addTab(self.create_system_tab(), "⚙ Systemprüfung")
        self.tabs.addTab(self.create_about_tab(), "ℹ Über")

        self.footer = QLabel(
            f"KStickFix {self.app_version} • USB-Sticks wiederherstellen, ISO schreiben und diagnostizieren"
        )
        self.footer.setObjectName("Subtitle")

        main.addWidget(self.tabs)
        main.addWidget(self.footer)

        self.setLayout(main)

        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.auto_refresh_devices)
        self.auto_timer.start(5000)

        self.load_devices()
        self.run_system_check()

    def resource_path(self, relative_path):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(base_dir, relative_path)

    def create_header(self):
        header = QHBoxLayout()
        header.setSpacing(14)

        logo = QLabel()
        pixmap = QPixmap(self.resource_path("icons/kstickfix.png"))

        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(78, 78, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        title = QLabel("KStickFix")
        title.setObjectName("Title")

        subtitle = QLabel("USB-Stick-Werkzeugkasten für Linux")
        subtitle.setObjectName("Subtitle")

        title_box = QVBoxLayout()
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.refresh_button = QPushButton("🔄 Aktualisieren")
        self.refresh_button.clicked.connect(self.load_devices)

        header.addWidget(logo)
        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(self.refresh_button)

        return header

    def create_card(self, title_text, content_widget_or_layout):
        frame = QFrame()
        frame.setObjectName("Card")

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setObjectName("CardTitle")
        layout.addWidget(title)

        if isinstance(content_widget_or_layout, QVBoxLayout):
            layout.addLayout(content_widget_or_layout)
        else:
            layout.addWidget(content_widget_or_layout)

        frame.setLayout(layout)
        return frame

    def create_usb_tab(self):
        tab = QWidget()
        content = QHBoxLayout()
        content.setSpacing(14)

        self.device_list = QListWidget()
        self.device_list.itemClicked.connect(self.show_selected_details)
        left_card = self.create_card("💾 USB-Sticks", self.device_list)

        self.status_label = QLabel("⚪ Kein Gerät ausgewählt")
        self.status_label.setObjectName("Subtitle")

        self.details = QTextEdit()
        self.details.setReadOnly(True)

        self.expert_checkbox = QCheckBox("⚙ Expertenmodus")
        self.expert_checkbox.stateChanged.connect(self.update_expert_options)

        self.filesystem_box = QComboBox()
        self.partition_box = QComboBox()

        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("z. B. Urlaub 2026")

        self.update_expert_options()

        self.analyze_button = QPushButton("🔍 Analysieren")
        self.analyze_button.clicked.connect(self.analyze_selected)

        self.restore_button = QPushButton("🛠 Wiederherstellen")
        self.restore_button.setEnabled(False)
        self.restore_button.clicked.connect(self.restore_selected)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        right_layout.addWidget(self.status_label)
        right_layout.addWidget(self.details)

        options1 = QHBoxLayout()
        options1.addWidget(QLabel("Dateisystem:"))
        options1.addWidget(self.filesystem_box)
        options1.addWidget(QLabel("Name:"))
        options1.addWidget(self.label_input)

        options2 = QHBoxLayout()
        options2.addWidget(QLabel("Partitionsschema:"))
        options2.addWidget(self.partition_box)
        options2.addStretch()
        options2.addWidget(self.expert_checkbox)

        actions = QHBoxLayout()
        actions.addWidget(self.analyze_button)
        actions.addWidget(self.restore_button)

        right_layout.addLayout(options1)
        right_layout.addLayout(options2)
        right_layout.addLayout(actions)

        right_card = self.create_card("ℹ Informationen", right_layout)

        content.addWidget(left_card, 1)
        content.addWidget(right_card, 2)

        tab.setLayout(content)
        return tab

    def create_iso_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(14)

        self.iso_device_list = QListWidget()
        self.iso_device_list.itemClicked.connect(self.show_iso_target_details)
        left_card = self.create_card("🎯 Ziel-USB-Stick", self.iso_device_list)

        self.iso_status_label = QLabel("⚪ Keine ISO-Datei ausgewählt")
        self.iso_status_label.setObjectName("Subtitle")

        self.iso_details = QTextEdit()
        self.iso_details.setReadOnly(True)

        self.select_iso_button = QPushButton("📂 ISO-Datei auswählen")
        self.select_iso_button.clicked.connect(self.select_iso_file)

        self.write_iso_button = QPushButton("💿 ISO auf USB schreiben")
        self.write_iso_button.setEnabled(False)
        self.write_iso_button.clicked.connect(self.write_iso_selected)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        right_layout.addWidget(self.iso_status_label)
        right_layout.addWidget(self.iso_details)

        actions = QHBoxLayout()
        actions.addWidget(self.select_iso_button)
        actions.addWidget(self.write_iso_button)

        right_layout.addLayout(actions)

        right_card = self.create_card("💿 ISO schreiben", right_layout)

        layout.addWidget(left_card, 1)
        layout.addWidget(right_card, 2)

        tab.setLayout(layout)
        return tab

    def create_diagnose_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(14)

        self.diagnose_device_list = QListWidget()
        self.diagnose_device_list.itemClicked.connect(self.show_diagnose_device_details)
        left_card = self.create_card("💾 USB-Stick auswählen", self.diagnose_device_list)

        self.diagnose_status_label = QLabel("⚪ Kein Gerät ausgewählt")
        self.diagnose_status_label.setObjectName("Subtitle")

        self.diagnose_details = QTextEdit()
        self.diagnose_details.setReadOnly(True)

        self.diagnose_button = QPushButton("🩺 Diagnose starten")
        self.diagnose_button.clicked.connect(self.run_diagnose)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        right_layout.addWidget(self.diagnose_status_label)
        right_layout.addWidget(self.diagnose_details)
        right_layout.addWidget(self.diagnose_button)

        right_card = self.create_card("🩺 Diagnosebericht", right_layout)

        layout.addWidget(left_card, 1)
        layout.addWidget(right_card, 2)

        tab.setLayout(layout)
        return tab

    def create_system_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(14)

        self.system_details = QTextEdit()
        self.system_details.setReadOnly(True)

        self.system_check_button = QPushButton("⚙ Systemprüfung erneut starten")
        self.system_check_button.clicked.connect(self.run_system_check)

        layout.addWidget(self.create_card("⚙ Systemprüfung", self.system_details))
        layout.addWidget(self.system_check_button)

        tab.setLayout(layout)
        return tab

    def create_about_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(14)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(
            f"KStickFix {self.app_version}\n"
            "================\n\n"
            "KStickFix ist ein grafisches Linux-Werkzeug zum Analysieren, "
            "Wiederherstellen und Beschreiben von USB-Sticks.\n\n"
            "Autor: Christian Wolf\n"
            "E-Mail: christianwolf5@gmx.net\n"
            "Entwicklungspartner: OpenAI ChatGPT\n\n"
            "Projektstatus:\n"
            "Mit Version 1.0.1 gilt dieses Projekt als abgeschlossen. "
            "Der ursprüngliche Autor plant derzeit keine aktive Weiterentwicklung. "
            "Das Projekt kann entsprechend der Lizenz genutzt, verändert und weitergeführt werden.\n\n"
            "Lizenz: MIT\n"
        )

        layout.addWidget(self.create_card("ℹ Über KStickFix", text))
        tab.setLayout(layout)
        return tab

    def update_expert_options(self):
        current_fs = self.filesystem_box.currentText()
        current_partition = self.partition_box.currentText()

        self.filesystem_box.clear()
        self.filesystem_box.addItems(["exFAT", "FAT32"])

        self.partition_box.clear()
        self.partition_box.addItem("MBR")

        if self.expert_checkbox.isChecked():
            self.filesystem_box.addItems(["NTFS", "ext4"])
            self.partition_box.addItem("GPT")

        fs_index = self.filesystem_box.findText(current_fs)
        if fs_index >= 0:
            self.filesystem_box.setCurrentIndex(fs_index)

        partition_index = self.partition_box.findText(current_partition)
        if partition_index >= 0:
            self.partition_box.setCurrentIndex(partition_index)

    def set_status(self, text, status_type="neutral"):
        icons = {"neutral": "⚪", "ok": "🟢", "warning": "🟡", "danger": "🔴"}
        self.status_label.setText(f"{icons.get(status_type, '⚪')} {text}")

    def set_iso_status(self, text, status_type="neutral"):
        icons = {"neutral": "⚪", "ok": "🟢", "warning": "🟡", "danger": "🔴"}
        self.iso_status_label.setText(f"{icons.get(status_type, '⚪')} {text}")

    def set_diagnose_status(self, text, status_type="neutral"):
        icons = {"neutral": "⚪", "ok": "🟢", "warning": "🟡", "danger": "🔴"}
        self.diagnose_status_label.setText(f"{icons.get(status_type, '⚪')} {text}")

    def current_device_paths(self):
        return [device.get("path") or device.get("name") for device in self.devices]

    def auto_refresh_devices(self):
        old_paths = self.current_device_paths()
        new_devices = get_usb_devices()
        new_paths = [device.get("path") or device.get("name") for device in new_devices]

        if old_paths != new_paths:
            self.load_devices()

    def load_devices(self):
        self.device_list.clear()
        self.iso_device_list.clear()
        self.diagnose_device_list.clear()

        self.details.clear()
        self.iso_details.clear()
        self.diagnose_details.clear()

        self.restore_button.setEnabled(False)
        self.write_iso_button.setEnabled(False)

        self.set_status("Geräte werden geladen", "neutral")
        self.set_iso_status("Geräte werden geladen", "neutral")
        self.set_diagnose_status("Geräte werden geladen", "neutral")

        self.devices = get_usb_devices()

        if not self.devices:
            self.device_list.addItem("Kein USB-Stick gefunden.")
            self.iso_device_list.addItem("Kein USB-Stick gefunden.")
            self.diagnose_device_list.addItem("Kein USB-Stick gefunden.")

            self.set_status("Kein USB-Stick gefunden", "warning")
            self.set_iso_status("Kein USB-Stick gefunden", "warning")
            self.set_diagnose_status("Kein USB-Stick gefunden", "warning")
            return

        for device in self.devices:
            text = "💾 " + device_display_name(device)
            self.device_list.addItem(text)
            self.iso_device_list.addItem(text)
            self.diagnose_device_list.addItem(text)

        self.set_status(f"{len(self.devices)} USB-Gerät(e) gefunden", "ok")
        self.set_iso_status(f"{len(self.devices)} USB-Gerät(e) gefunden", "ok")
        self.set_diagnose_status(f"{len(self.devices)} USB-Gerät(e) gefunden", "ok")

        self.update_iso_write_button()

    def selected_device(self):
        index = self.device_list.currentRow()
        if index < 0 or index >= len(self.devices):
            return None
        return self.devices[index]

    def selected_iso_device(self):
        index = self.iso_device_list.currentRow()
        if index < 0 or index >= len(self.devices):
            return None
        return self.devices[index]

    def selected_diagnose_device(self):
        index = self.diagnose_device_list.currentRow()
        if index < 0 or index >= len(self.devices):
            return None
        return self.devices[index]

    def show_selected_details(self):
        device = self.selected_device()
        if not device:
            return

        self.details.setPlainText(device_info_text(device))
        self.set_status("Gerät ausgewählt", "neutral")
        self.restore_button.setEnabled(False)

    def show_iso_target_details(self):
        device = self.selected_iso_device()
        if not device:
            return

        text = "Zielgerät:\n\n"
        text += device_info_text(device)
        text += "\n\n"
        text += iso_info(self.iso_path)

        self.iso_details.setPlainText(text)
        self.set_iso_status("Ziel-USB-Stick ausgewählt", "neutral")
        self.update_iso_write_button()

    def show_diagnose_device_details(self):
        device = self.selected_diagnose_device()
        if not device:
            return

        self.diagnose_details.setPlainText(device_info_text(device))
        self.set_diagnose_status("Gerät ausgewählt", "neutral")

    def analyze_selected(self):
        device = self.selected_device()
        if not device:
            self.set_status("Bitte zuerst einen USB-Stick auswählen", "warning")
            return

        text, can_restore, status = analyze_device(device)
        self.details.setPlainText(text)

        if can_restore:
            self.set_status("Wiederherstellung möglich", status)
            self.restore_button.setEnabled(True)
        else:
            self.set_status("Keine Wiederherstellung nötig", "ok")
            self.restore_button.setEnabled(False)

    def run_diagnose(self):
        device = self.selected_diagnose_device()

        if not device:
            self.set_diagnose_status("Bitte zuerst einen USB-Stick auswählen", "warning")
            return

        report, status = diagnose_device(device)
        self.diagnose_details.setPlainText(report)

        if status == "ok":
            self.set_diagnose_status("Diagnose: keine Auffälligkeiten", "ok")
        elif status == "warning":
            self.set_diagnose_status("Diagnose: Auffälligkeit erkannt", "warning")
        else:
            self.set_diagnose_status("Diagnose abgeschlossen", "neutral")

    def run_system_check(self):
        self.system_details.setPlainText(system_report())

    def restore_selected(self):
        device = self.selected_device()
        if not device:
            self.set_status("Bitte zuerst einen USB-Stick auswählen", "warning")
            return

        filesystem = self.filesystem_box.currentText()
        partition_table = self.partition_box.currentText()
        label = self.label_input.text().strip() or "USBSTICK"

        if not confirm_restore(self, device, filesystem, label, partition_table):
            return

        progress = QProgressDialog("USB-Stick wird wiederhergestellt...", "Abbrechen", 0, 100, self)
        progress.setWindowTitle("KStickFix arbeitet")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        def update_progress(step, total, command):
            percent = int((step / total) * 100)
            progress.setValue(percent)
            progress.setLabelText(f"Schritt {step} von {total}\n{command}")
            QApplication.processEvents()

        self.set_status("Wiederherstellung läuft", "danger")

        success, output, message = restore_usb_device(
            device,
            filesystem,
            label,
            partition_table,
            progress_callback=update_progress
        )

        progress.setValue(100)
        self.details.setPlainText(output)

        if success:
            show_info(self, "Fertig", message)
            self.set_status("USB-Stick wurde wiederhergestellt", "ok")
            self.load_devices()
        else:
            show_error(self, "Fehler", message)
            self.set_status("Fehler bei der Wiederherstellung", "danger")

    def select_iso_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "ISO-Datei auswählen",
            os.path.expanduser("~"),
            "ISO-Dateien (*.iso);;Alle Dateien (*)"
        )

        if not path:
            return

        self.iso_path = path
        self.iso_details.setPlainText(iso_info(path))
        self.set_iso_status("ISO-Datei ausgewählt", "ok")
        self.update_iso_write_button()

    def update_iso_write_button(self):
        has_iso = bool(self.iso_path)
        has_device = self.selected_iso_device() is not None
        self.write_iso_button.setEnabled(has_iso and has_device)

    def write_iso_selected(self):
        device = self.selected_iso_device()

        if not self.iso_path:
            self.set_iso_status("Bitte zuerst eine ISO-Datei auswählen", "warning")
            return

        if not device:
            self.set_iso_status("Bitte zuerst einen Ziel-USB-Stick auswählen", "warning")
            return

        if not confirm_iso_write(self, self.iso_path, device):
            return

        progress = QProgressDialog("ISO wird auf USB-Stick geschrieben...", "Abbrechen", 0, 100, self)
        progress.setWindowTitle("KStickFix schreibt ISO")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        def update_progress(step, total, command):
            percent = int((step / total) * 100)
            progress.setValue(percent)
            progress.setLabelText(f"Schritt {step} von {total}\n{command}")
            QApplication.processEvents()

        self.set_iso_status("ISO wird geschrieben", "danger")

        success, output, message = write_iso_to_usb(
            self.iso_path,
            device,
            progress_callback=update_progress
        )

        progress.setValue(100)
        self.iso_details.setPlainText(output)

        if success:
            show_info(self, "Fertig", message)
            self.set_iso_status("ISO wurde geschrieben", "ok")
            self.load_devices()
        else:
            show_error(self, "Fehler", message)
            self.set_iso_status("Fehler beim Schreiben der ISO", "danger")
