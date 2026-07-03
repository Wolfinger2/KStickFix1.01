import shutil

from usb_manager import device_path, run_command


TOOL_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"


def find_tool(name):
    path = shutil.which(name, path=TOOL_PATH)
    if not path:
        raise FileNotFoundError(
            f"{name} wurde nicht gefunden. Bitte das passende Paket installieren."
        )
    return path


def restore_usb_device(device, filesystem, label, partition_table="MBR", progress_callback=None):
    try:
        wipefs = find_tool("wipefs")
        parted = find_tool("parted")
        udisksctl = find_tool("udisksctl")

        mkfs_exfat = find_tool("mkfs.exfat") if filesystem == "exFAT" else None
        mkfs_vfat = find_tool("mkfs.vfat") if filesystem == "FAT32" else None
        mkfs_ntfs = find_tool("mkfs.ntfs") if filesystem == "NTFS" else None
        mkfs_ext4 = find_tool("mkfs.ext4") if filesystem == "ext4" else None

    except FileNotFoundError as error:
        return False, "", str(error)

    dev_path = device_path(device)
    part_path = f"{dev_path}1"

    commands = []

    for child in device.get("children", []) or []:
        child_path = child.get("path") or f"/dev/{child.get('name', '')}"
        mountpoints = child.get("mountpoints") or []

        if any(m is not None for m in mountpoints):
            commands.append([udisksctl, "unmount", "-b", child_path])

    parted_label = "gpt" if partition_table == "GPT" else "msdos"

    commands.append(["pkexec", wipefs, "-a", dev_path])
    commands.append(["pkexec", parted, "-s", dev_path, "mklabel", parted_label])
    commands.append(["pkexec", parted, "-s", dev_path, "mkpart", "primary", "1MiB", "100%"])

    if filesystem == "exFAT":
        commands.append(["pkexec", mkfs_exfat, "-n", label, part_path])

    elif filesystem == "FAT32":
        commands.append(["pkexec", mkfs_vfat, "-F", "32", "-n", label[:11], part_path])

    elif filesystem == "NTFS":
        commands.append(["pkexec", mkfs_ntfs, "-f", "-L", label, part_path])

    elif filesystem == "ext4":
        commands.append(["pkexec", mkfs_ext4, "-F", "-L", label, part_path])

    else:
        return False, "", f"Unbekanntes Dateisystem: {filesystem}"

    output = ""
    total = len(commands)

    for index, cmd in enumerate(commands, start=1):
        if progress_callback:
            progress_callback(index, total, " ".join(cmd))

        result = run_command(cmd)

        output += f"$ {' '.join(cmd)}\n"
        output += result.stdout
        output += result.stderr
        output += "\n"

        if result.returncode != 0:
            return False, output, "Befehl fehlgeschlagen:\n" + " ".join(cmd)

    return True, output, "Der USB-Stick wurde erfolgreich wiederhergestellt."
