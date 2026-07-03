import json
import subprocess


def run_command(command):
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False
    )


def get_usb_devices():
    result = run_command([
        "lsblk",
        "-J",
        "-o",
        "NAME,PATH,SIZE,MODEL,VENDOR,SERIAL,TRAN,RM,TYPE,FSTYPE,LABEL,MOUNTPOINTS"
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
    device_type = device.get("type")
    transport = device.get("tran")
    removable = device.get("rm")

    return (
        device_type == "disk"
        and (
            transport == "usb"
            or removable is True
        )
    )


def device_path(device):
    return device.get("path") or f"/dev/{device.get('name', '')}"


def device_display_name(device):
    path = device_path(device)
    size = device.get("size") or "Unbekannte Größe"
    vendor = (device.get("vendor") or "").strip()
    model = (device.get("model") or "Unbekanntes Modell").strip()

    return f"{path} | {size} | {vendor} {model}".strip()


def list_filesystems(device):
    filesystems = []

    for child in device.get("children", []) or []:
        fstype = child.get("fstype")
        if fstype:
            filesystems.append(fstype.lower())

    return filesystems


def list_mountpoints(device):
    mountpoints = []

    for child in device.get("children", []) or []:
        for mountpoint in child.get("mountpoints") or []:
            if mountpoint:
                mountpoints.append(mountpoint)

    return mountpoints


def looks_like_iso_stick(device):
    return "iso9660" in list_filesystems(device)


def looks_like_ventoy(device):
    labels = []

    for child in device.get("children", []) or []:
        label = child.get("label")
        if label:
            labels.append(label.lower())

    return any("ventoy" in label for label in labels)
