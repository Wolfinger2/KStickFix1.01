import os
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


def iso_info(path):
    if not path:
        return "Keine ISO-Datei ausgewählt."

    if not os.path.exists(path):
        return "ISO-Datei wurde nicht gefunden."

    size_bytes = os.path.getsize(path)
    size_gib = size_bytes / (1024 ** 3)

    return (
        f"ISO-Datei:\n{path}\n\n"
        f"Größe: {size_gib:.2f} GiB\n"
    )


def write_iso_to_usb(iso_path, device, progress_callback=None):
    try:
        dd = find_tool("dd")
        sync = find_tool("sync")
    except FileNotFoundError as error:
        return False, "", str(error)

    dev_path = device_path(device)

    if not iso_path or not os.path.exists(iso_path):
        return False, "", "Keine gültige ISO-Datei ausgewählt."

    commands = [
        ["pkexec", dd, f"if={iso_path}", f"of={dev_path}", "bs=4M", "status=progress", "conv=fsync"],
        [sync],
    ]

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

    return True, output, "Die ISO-Datei wurde erfolgreich auf den USB-Stick geschrieben."
