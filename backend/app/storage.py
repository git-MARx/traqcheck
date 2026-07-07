import os
import uuid

from werkzeug.utils import secure_filename


class UnsupportedFileType(Exception):
    pass


def save_upload_file(file_storage, upload_folder: str, allowed_extensions: set) -> tuple[str, str]:
    filename = secure_filename(file_storage.filename or "")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in allowed_extensions:
        raise UnsupportedFileType(f"Unsupported file type: .{ext}")

    upload_id = str(uuid.uuid4())
    dest_dir = os.path.join(upload_folder, upload_id)
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = os.path.join(dest_dir, filename)
    file_storage.save(dest_path)

    return dest_path, ext
