from usb_manager import device_path, list_filesystems, list_mountpoints, looks_like_iso_stick, looks_like_ventoy


def diagnose_device(device):
    path = device_path(device)
    children = device.get("children", []) or []
    filesystems = list_filesystems(device)
    mountpoints = list_mountpoints(device)

    report = ""
    report += "Diagnosebericht\n"
    report += "==============\n\n"
    report += f"Gerät: {path}\n"
    report += f"Größe: {device.get('size') or 'Unbekannt'}\n"
    report += f"Modell: {(device.get('model') or 'Unbekannt').strip()}\n\n"

    if not children:
        report += "Status: Auffällig\n"
        report += "- Keine Partitionen gefunden.\n"
        report += "- Der Stick kann leer, beschädigt oder falsch beschrieben sein.\n\n"
        report += "Empfehlung:\n"
        report += "- Wiederherstellen mit exFAT oder FAT32.\n"
        return report, "warning"

    if looks_like_ventoy(device):
        report += "Status: Ventoy erkannt\n"
        report += "- Der Stick scheint eine Ventoy-Struktur zu enthalten.\n\n"
        report += "Empfehlung:\n"
        report += "- Wenn du Ventoy entfernen möchtest: Wiederherstellen.\n"
        return report, "warning"

    if looks_like_iso_stick(device):
        report += "Status: ISO-/Installationsstick erkannt\n"
        report += "- Der Stick wurde vermutlich mit einer Linux-ISO beschrieben.\n\n"
        report += "Empfehlung:\n"
        report += "- Wenn du ihn wieder normal nutzen möchtest: Wiederherstellen.\n"
        return report, "warning"

    if len(children) > 1:
        report += "Status: Mehrere Partitionen erkannt\n"
        report += "- Das ist nicht automatisch ein Fehler.\n"
        report += "- Es kann aber von Installationsmedien oder Spezialtools stammen.\n\n"
        report += "Empfehlung:\n"
        report += "- Nur wiederherstellen, wenn du den Stick normal als Datenträger nutzen willst.\n"
        return report, "neutral"

    if "exfat" in filesystems or "vfat" in filesystems:
        report += "Status: Normaler USB-Stick\n"
        report += "- Das Dateisystem ist für normale USB-Nutzung geeignet.\n\n"
        report += "Empfehlung:\n"
        report += "- Keine Reparatur nötig.\n"
        return report, "ok"

    if "ntfs" in filesystems:
        report += "Status: NTFS erkannt\n"
        report += "- Geeignet für Windows und große Dateien.\n\n"
        report += "Empfehlung:\n"
        report += "- Keine Reparatur nötig, wenn du den Stick mit Windows nutzen willst.\n"
        return report, "neutral"

    if "ext4" in filesystems:
        report += "Status: ext4 erkannt\n"
        report += "- Geeignet für Linux.\n"
        report += "- Windows kann ext4 normalerweise nicht lesen.\n\n"
        report += "Empfehlung:\n"
        report += "- Nur wiederherstellen, wenn du Windows/macOS-Kompatibilität brauchst.\n"
        return report, "neutral"

    if mountpoints:
        report += "Status: Eingehängt\n"
        report += "- Der Stick ist aktuell im System eingehängt.\n\n"

    report += "Status: Unbekannte Struktur\n"
    report += "- KStickFix kann die Struktur nicht eindeutig einordnen.\n\n"
    report += "Empfehlung:\n"
    report += "- Wenn der Stick Probleme macht: Wiederherstellen.\n"

    return report, "warning"
