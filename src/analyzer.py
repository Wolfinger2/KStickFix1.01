from usb_manager import (
    device_path,
    list_filesystems,
    list_mountpoints,
    looks_like_iso_stick,
    looks_like_ventoy,
)


def device_info_text(device):
    path = device_path(device)
    size = device.get("size") or "Unbekannt"
    model = (device.get("model") or "Unbekannt").strip()
    vendor = (device.get("vendor") or "Unbekannt").strip()
    serial = device.get("serial") or "Nicht verfügbar"
    tran = device.get("tran") or "Unbekannt"
    rm = device.get("rm")

    text = ""
    text += f"Gerät: {path}\n"
    text += f"Hersteller: {vendor}\n"
    text += f"Modell: {model}\n"
    text += f"Seriennummer: {serial}\n"
    text += f"Größe: {size}\n"
    text += f"Verbindung: {tran}\n"
    text += f"Wechseldatenträger: {'Ja' if rm else 'Nein'}\n\n"

    children = device.get("children", []) or []

    if children:
        text += "Partitionen:\n"

        for child in children:
            cname = child.get("path") or f"/dev/{child.get('name', '')}"
            csize = child.get("size") or "Unbekannt"
            cfstype = child.get("fstype") or "Unbekannt/kein Dateisystem"
            clabel = child.get("label") or "Kein Name"
            mountpoints = child.get("mountpoints") or []
            clean_mountpoints = [m for m in mountpoints if m is not None]
            mounted = ", ".join(clean_mountpoints) if clean_mountpoints else "Nicht eingehängt"

            text += f"\n{cname}\n"
            text += f"  Größe: {csize}\n"
            text += f"  Dateisystem: {cfstype}\n"
            text += f"  Name: {clabel}\n"
            text += f"  Eingehängt: {mounted}\n"
    else:
        text += "Partitionen: Keine gefunden\n"

    return text


def analyze_device(device):
    text = device_info_text(device)
    text += "\n\nAnalyse:\n"

    children = device.get("children", []) or []
    filesystems = list_filesystems(device)
    mountpoints = list_mountpoints(device)

    can_restore = True
    status = "warning"

    if looks_like_ventoy(device):
        text += "⚠ Ventoy-Struktur erkannt.\n"
        text += "Empfehlung: Wenn du Ventoy entfernen willst, kann KStickFix den Stick wieder normal einrichten.\n"
        status = "warning"

    elif looks_like_iso_stick(device):
        text += "⚠ Linux-/ISO-Installationsstick erkannt.\n"
        text += "Empfehlung: Wiederherstellung sinnvoll, wenn du den Stick wieder normal nutzen möchtest.\n"
        status = "warning"

    elif not children:
        text += "⚠ Keine Partitionen gefunden.\n"
        text += "Empfehlung: Stick kann wahrscheinlich wiederhergestellt werden.\n"
        status = "warning"

    elif len(children) > 1:
        text += "⚠ Mehrere Partitionen erkannt.\n"
        text += "Empfehlung: Das kann von Linux-ISOs, Ventoy oder Spezialtools stammen.\n"
        status = "warning"

    elif "vfat" in filesystems or "exfat" in filesystems:
        text += "✅ Normaler USB-Stick erkannt.\n"
        text += "Wiederherstellung ist möglich, aber wahrscheinlich nicht nötig.\n"
        status = "ok"

    elif "ntfs" in filesystems or "ext4" in filesystems:
        text += "ℹ Experten-Dateisystem erkannt.\n"
        text += "Wiederherstellung ist möglich, falls du den Stick neu einrichten möchtest.\n"
        status = "neutral"

    else:
        text += "⚠ Unbekannte oder ungewöhnliche Struktur erkannt.\n"
        text += "Empfehlung: Wiederherstellung möglich.\n"
        status = "warning"

    if mountpoints:
        text += "\nHinweis: Der Stick ist aktuell eingehängt. KStickFix versucht ihn vor dem Formatieren auszuhängen.\n"

    return text, can_restore, status
