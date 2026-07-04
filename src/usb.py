import json
import re

from tools import run


def get_usb_devices():
    result = run([
        "lsblk",
        "-J",
        "-o",
        "NAME,PATH,SIZE,MODEL,VENDOR,SERIAL,TRAN,RM,TYPE,FSTYPE,LABEL,MOUNTPOINTS",
    ])

    if result.returncode != 0:
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    devices = []

    for device in data.get("blockdevices", []):
        if is_usb_disk(device):
            devices.append(device)

    return devices


def is_usb_disk(device):
    return (
        device.get("type") == "disk"
        and (
            device.get("tran") == "usb"
            or device.get("rm") is True
        )
    )


def device_path(device):
    return device.get("path") or f"/dev/{device.get('name', '')}"


def device_display_name(device):
    path = device_path(device)
    size = device.get("size") or "?"
    vendor = (device.get("vendor") or "").strip()
    model = (device.get("model") or "Unbekannt").strip()
    return f"{path} | {size} | {vendor} {model}".strip()


def partitions(device):
    return device.get("children", []) or []


def filesystems(device):
    found = []
    for child in partitions(device):
        fstype = child.get("fstype")
        if fstype:
            found.append(fstype.lower())
    return found


def mountpoints(device):
    found = []
    for child in partitions(device):
        for mountpoint in child.get("mountpoints") or []:
            if mountpoint:
                found.append(mountpoint)
    return found


def parse_size_to_bytes(size_text):
    if not size_text:
        return None

    text = str(size_text).strip().replace(",", ".")
    match = re.match(r"^([0-9.]+)\s*([KMGTPE]?)(i?B)?$", text, re.IGNORECASE)

    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2).upper()

    factor = {
        "": 1,
        "K": 1024,
        "M": 1024 ** 2,
        "G": 1024 ** 3,
        "T": 1024 ** 4,
        "P": 1024 ** 5,
        "E": 1024 ** 6,
    }.get(unit, 1)

    return int(number * factor)


def device_size_bytes(device):
    return parse_size_to_bytes(device.get("size"))


def device_info(device):
    text = ""
    text += f"Gerät: {device_path(device)}\n"
    text += f"Hersteller: {(device.get('vendor') or 'Unbekannt').strip()}\n"
    text += f"Modell: {(device.get('model') or 'Unbekannt').strip()}\n"
    text += f"Seriennummer: {device.get('serial') or 'Nicht verfügbar'}\n"
    text += f"Größe: {device.get('size') or 'Unbekannt'}\n"
    text += f"Verbindung: {device.get('tran') or 'Unbekannt'}\n"
    text += f"Wechseldatenträger: {'Ja' if device.get('rm') else 'Nein'}\n\n"

    parts = partitions(device)

    if not parts:
        text += "Partitionen: Keine gefunden\n"
        return text

    text += "Partitionen:\n"

    for child in parts:
        path = child.get("path") or f"/dev/{child.get('name', '')}"
        text += f"\n{path}\n"
        text += f"  Größe: {child.get('size') or 'Unbekannt'}\n"
        text += f"  Dateisystem: {child.get('fstype') or 'Unbekannt'}\n"
        text += f"  Name: {child.get('label') or 'Kein Name'}\n"
        clean_mountpoints = [m for m in child.get("mountpoints") or [] if m]
        text += f"  Eingehängt: {', '.join(clean_mountpoints) if clean_mountpoints else 'Nein'}\n"

    return text


def analyze(device):
    text = device_info(device)
    text += "\nAnalyse:\n"

    parts = partitions(device)
    fs = filesystems(device)

    if not parts:
        text += "⚠ Keine Partitionen gefunden. Wiederherstellung ist sinnvoll.\n"
        return text, "warning", True

    if "iso9660" in fs:
        text += "⚠ ISO-/Installationsstick erkannt. Wiederherstellung ist sinnvoll, wenn du den Stick wieder normal nutzen möchtest.\n"
        return text, "warning", True

    if len(parts) > 1:
        text += "⚠ Mehrere Partitionen erkannt. Das kann von Linux-ISOs, Ventoy oder Spezialtools kommen.\n"
        return text, "warning", True

    if "exfat" in fs or "vfat" in fs:
        text += "✅ Normaler USB-Stick erkannt. Keine Reparatur nötig.\n"
        return text, "ok", True

    if "ntfs" in fs or "ext4" in fs:
        text += "ℹ Spezial-Dateisystem erkannt. Wiederherstellung ist möglich.\n"
        return text, "neutral", True

    text += "⚠ Unbekannte Struktur erkannt. Wiederherstellung ist möglich.\n"
    return text, "warning", True
