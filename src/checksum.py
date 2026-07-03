import hashlib


def sha256_file(path, progress_callback=None):
    sha256 = hashlib.sha256()
    total_read = 0

    with open(path, "rb") as file:
        while True:
            chunk = file.read(1024 * 1024)
            if not chunk:
                break

            sha256.update(chunk)
            total_read += len(chunk)

            if progress_callback:
                progress_callback(total_read)

    return sha256.hexdigest()
