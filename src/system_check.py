from tools import which


CORE_TOOLS = [
    ("lsblk", "util-linux"),
    ("wipefs", "util-linux"),
    ("parted", "parted"),
    ("mkfs.exfat", "exfatprogs"),
    ("mkfs.vfat", "dosfstools"),
    ("mkfs.ntfs", "ntfs-3g"),
    ("mkfs.ext4", "e2fsprogs"),
    ("udisksctl", "udisks2"),
    ("pkexec", "polkit"),
]

ISO_TOOLS = [
    ("isoimagewriter", "KDE ISO Image Writer"),
    ("imagewriter", "SUSE Studio Imagewriter"),
    ("gnome-disks", "GNOME Laufwerke"),
]


def system_report():
    text = "Systemprüfung\n"
    text += "=============\n\n"

    missing_core = []

    text += "Basis-Werkzeuge:\n"

    for tool, package in CORE_TOOLS:
        path = which(tool)
        if path:
            text += f"✅ {tool}: {path}\n"
        else:
            text += f"❌ {tool} fehlt. Paket: {package}\n"
            missing_core.append(package)

    text += "\nISO-Schreiber:\n"

    iso_found = False

    for binary, name in ISO_TOOLS:
        path = which(binary)
        if path:
            text += f"✅ {name}: {path}\n"
            iso_found = True
        else:
            text += f"ℹ {name} nicht gefunden ({binary})\n"

    if iso_found:
        text += "\n✅ ISO-Schreiber gefunden. Die ISO-Funktion ist nutzbar.\n"
    else:
        text += "\n❌ Kein ISO-Schreiber gefunden.\n"
        text += "Empfohlen unter openSUSE:\n"
        text += "sudo zypper install imagewriter\n"

    if missing_core:
        text += "\nFehlende Basis-Pakete unter openSUSE installieren:\n"
        text += "sudo zypper install " + " ".join(sorted(set(missing_core))) + "\n"

    return text
