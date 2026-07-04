import os
import subprocess

from tools import which


def iso_info(path):
    if not path:
        return "Keine ISO-Datei ausgewählt."

    if not os.path.exists(path):
        return "ISO-Datei wurde nicht gefunden."

    size = os.path.getsize(path) / (1024 ** 3)
    return f"ISO-Datei:\n{path}\n\nGröße: {size:.2f} GiB\n"


def iso_size_bytes(path):
    if not path or not os.path.exists(path):
        return None
    return os.path.getsize(path)


def available_writers():
    candidates = [
        ("KDE ISO Image Writer", "isoimagewriter"),
        ("SUSE Studio Imagewriter", "imagewriter"),
        ("GNOME Laufwerke", "gnome-disks"),
    ]

    found = []
    for name, binary in candidates:
        path = which(binary)
        if path:
            found.append((name, binary, path))
    return found


def best_writer():
    writers = available_writers()
    return writers[0] if writers else None


def writer_install_hint():
    return (
        "Kein unterstützter ISO-Schreiber gefunden.\n\n"
        "Empfohlen unter openSUSE:\n"
        "sudo zypper install imagewriter\n\n"
        "Alternative:\n"
        "sudo zypper install gnome-disk-utility\n\n"
        "KDE ISO Image Writer kann ebenfalls genutzt werden, falls er in deinen Paketquellen verfügbar ist."
    )


def start_writer(iso_path):
    writer = best_writer()
    if not writer:
        return False, writer_install_hint()

    name, binary, path = writer

    commands = []
    if binary in ["isoimagewriter", "imagewriter"]:
        commands = [[path, iso_path], [path]]
    elif binary == "gnome-disks":
        commands = [[path]]

    last = ""

    for command in commands:
        try:
            subprocess.Popen(command)
            return True, f"{name} wurde gestartet.\n\nWenn das Programm die ISO nicht automatisch übernimmt, wähle sie dort manuell aus:\n{iso_path}"
        except Exception as error:
            last = str(error)

    return False, f"{name} konnte nicht gestartet werden.\n\n{last}"


def install_imagewriter():
    command = ["pkexec", "zypper", "install", "-y", "imagewriter"]
    try:
        process = subprocess.Popen(command)
        return True, "Installation wurde gestartet. Folge dem Passwortfenster und starte KStickFix danach neu."
    except Exception as error:
        return False, f"Installation konnte nicht gestartet werden:\n{error}"
