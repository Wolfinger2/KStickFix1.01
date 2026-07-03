from PySide6.QtWidgets import QMessageBox

from usb_manager import device_path


def confirm_restore(parent, device, filesystem, label, partition_table="MBR"):
    dev_path = device_path(device)
    size = device.get("size") or "Unbekannte Größe"
    model = (device.get("model") or "Unbekannt").strip()
    vendor = (device.get("vendor") or "").strip()

    notes = []

    if filesystem == "NTFS":
        notes.append("NTFS ist sinnvoll, wenn der Stick hauptsächlich mit Windows genutzt wird.")

    if filesystem == "ext4":
        notes.append("ext4 ist ein Linux-Dateisystem. Windows kann es normalerweise nicht ohne Zusatzsoftware lesen.")

    if partition_table == "GPT":
        notes.append("GPT ist modern, aber ältere Geräte kommen teilweise besser mit MBR zurecht.")

    note_text = ""
    if notes:
        note_text = "\n\nHinweise:\n- " + "\n- ".join(notes)

    warning = (
        "ACHTUNG!\n\n"
        "Dieser USB-Stick wird komplett gelöscht:\n\n"
        f"{dev_path}\n"
        f"{vendor} {model}\n"
        f"{size}\n\n"
        f"Partitionsschema: {partition_table}\n"
        f"Dateisystem: {filesystem}\n"
        f"Name: {label}"
        f"{note_text}\n\n"
        "Alle Daten darauf gehen verloren."
    )

    answer = QMessageBox.warning(parent, "USB-Stick löschen?", warning, QMessageBox.Yes | QMessageBox.No)

    if answer != QMessageBox.Yes:
        return False

    confirm = QMessageBox.question(
        parent,
        "Wirklich sicher?",
        f"Letzte Sicherheitsabfrage:\n\nSoll {dev_path} wirklich gelöscht und neu formatiert werden?",
        QMessageBox.Yes | QMessageBox.No
    )

    return confirm == QMessageBox.Yes


def confirm_iso_write(parent, iso_path, device):
    dev_path = device_path(device)
    size = device.get("size") or "Unbekannte Größe"
    model = (device.get("model") or "Unbekannt").strip()
    vendor = (device.get("vendor") or "").strip()

    warning = (
        "ACHTUNG!\n\n"
        "Diese ISO-Datei wird direkt auf den USB-Stick geschrieben:\n\n"
        f"{iso_path}\n\n"
        "Ziel-USB-Stick:\n\n"
        f"{dev_path}\n"
        f"{vendor} {model}\n"
        f"{size}\n\n"
        "Alle Daten auf dem USB-Stick gehen verloren."
    )

    answer = QMessageBox.warning(parent, "ISO auf USB-Stick schreiben?", warning, QMessageBox.Yes | QMessageBox.No)

    if answer != QMessageBox.Yes:
        return False

    confirm = QMessageBox.question(
        parent,
        "Wirklich sicher?",
        f"Letzte Sicherheitsabfrage:\n\nSoll die ISO wirklich auf {dev_path} geschrieben werden?",
        QMessageBox.Yes | QMessageBox.No
    )

    return confirm == QMessageBox.Yes


def show_error(parent, title, message):
    QMessageBox.critical(parent, title, message)


def show_info(parent, title, message):
    QMessageBox.information(parent, title, message)
