import shutil

TOOL_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

TOOLS = [
    ("wipefs", "util-linux"),
    ("parted", "parted"),
    ("mkfs.exfat", "exfatprogs"),
    ("mkfs.vfat", "dosfstools"),
    ("mkfs.ntfs", "ntfs-3g"),
    ("mkfs.ext4", "e2fsprogs"),
    ("dd", "coreutils"),
    ("udisksctl", "udisks2"),
    ("pkexec", "polkit"),
]


def check_tools():
    rows = []
    for tool, package in TOOLS:
        path = shutil.which(tool, path=TOOL_PATH)
        rows.append({
            "tool": tool,
            "package": package,
            "path": path or "",
            "available": bool(path),
        })
    return rows


def system_report():
    rows = check_tools()

    text = "Systemprüfung\n"
    text += "=============\n\n"

    missing = []

    for row in rows:
        if row["available"]:
            text += f"✅ {row['tool']} gefunden: {row['path']}\n"
        else:
            text += f"❌ {row['tool']} fehlt. Paket: {row['package']}\n"
            missing.append(row["package"])

    if missing:
        unique = sorted(set(missing))
        text += "\nFehlende Pakete unter openSUSE installieren:\n\n"
        text += "sudo zypper install " + " ".join(unique) + "\n"
    else:
        text += "\nAlle benötigten Werkzeuge wurden gefunden.\n"

    return text
