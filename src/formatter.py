from tools import which, run
from usb import device_path


def require_tool(name, package):
    path = which(name)
    if not path:
        raise FileNotFoundError(f"{name} fehlt. Paket installieren: {package}")
    return path


def restore(device, filesystem, label, schema, progress=None):
    try:
        wipefs = require_tool("wipefs", "util-linux")
        parted = require_tool("parted", "parted")
        udisksctl = require_tool("udisksctl", "udisks2")

        mkfs = {
            "exFAT": require_tool("mkfs.exfat", "exfatprogs"),
            "FAT32": require_tool("mkfs.vfat", "dosfstools"),
            "NTFS": require_tool("mkfs.ntfs", "ntfs-3g"),
            "ext4": require_tool("mkfs.ext4", "e2fsprogs"),
        }[filesystem]

    except Exception as error:
        return False, "", str(error)

    dev = device_path(device)
    part = f"{dev}1"

    commands = []

    for child in device.get("children", []) or []:
        child_path = child.get("path") or f"/dev/{child.get('name', '')}"
        mounts = child.get("mountpoints") or []
        if any(m for m in mounts):
            commands.append([udisksctl, "unmount", "-b", child_path])

    table = "gpt" if schema == "GPT" else "msdos"

    commands.append(["pkexec", wipefs, "-a", dev])
    commands.append(["pkexec", parted, "-s", dev, "mklabel", table])
    commands.append(["pkexec", parted, "-s", dev, "mkpart", "primary", "1MiB", "100%"])

    if filesystem == "exFAT":
        commands.append(["pkexec", mkfs, "-n", label, part])
    elif filesystem == "FAT32":
        commands.append(["pkexec", mkfs, "-F", "32", "-n", label[:11], part])
    elif filesystem == "NTFS":
        commands.append(["pkexec", mkfs, "-f", "-L", label, part])
    elif filesystem == "ext4":
        commands.append(["pkexec", mkfs, "-F", "-L", label, part])

    output = ""

    for index, command in enumerate(commands, start=1):
        if progress:
            progress(index, len(commands), " ".join(command))

        result = run(command)

        output += "$ " + " ".join(command) + "\n"
        output += result.stdout
        output += result.stderr
        output += "\n"

        if result.returncode != 0:
            return False, output, "Befehl fehlgeschlagen:\n" + " ".join(command)

    return True, output, "USB-Stick wurde erfolgreich wiederhergestellt."
