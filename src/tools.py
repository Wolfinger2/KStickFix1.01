import shutil
import subprocess


TOOL_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"


def which(name):
    return shutil.which(name, path=TOOL_PATH)


def run(command):
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
