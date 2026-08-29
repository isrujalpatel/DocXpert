"""
file_manager.py — Upload/download file management.

Handles saving uploaded files to disk, retrieving stored files,
generating unique storage names, and cleaning up temporary files.
Flask-compatible (synchronous I/O).
"""

import os
import time
from pathlib import Path

from config.settings import settings
from utils.helpers import generate_uuid


def save_upload(file_storage, extension: str) -> dict:
    """
    Save an uploaded file (Flask FileStorage) to the uploads directory.

    Args:
        file_storage: The uploaded file from Flask's request.files.
        extension: Validated file extension (e.g. 'docx').

    Returns:
        dict with keys: file_id, stored_name, upload_path, file_size_bytes
    """
    settings.ensure_dirs()

    file_id = generate_uuid()
    stored_name = f"{file_id}.{extension}"
    upload_path = settings.UPLOAD_DIR / stored_name

    # Write file to disk synchronously
    file_storage.save(str(upload_path))
    file_size = upload_path.stat().st_size

    return {
        "file_id": file_id,
        "stored_name": stored_name,
        "upload_path": str(upload_path),
        "file_size_bytes": file_size,
    }


def get_file_path(file_id: str) -> Path:
    """
    Find the stored file by its file_id (UUID).
    Searches the upload directory for any file starting with that UUID.

    Returns:
        Path object to the file.

    Raises:
        FileNotFoundError if the file doesn't exist.
    """
    if not settings.UPLOAD_DIR.exists():
        raise FileNotFoundError(f"Upload directory does not exist")

    # Look for any file matching the file_id prefix
    for file_path in settings.UPLOAD_DIR.iterdir():
        if file_path.is_file() and file_path.stem == file_id:
            return file_path

    # Also try exact name match (file_id might include extension)
    if "." in file_id:
        exact = settings.UPLOAD_DIR / file_id
        if exact.exists():
            return exact

    raise FileNotFoundError(f"File not found: {file_id}")


def get_file_extension(file_id: str) -> str:
    """Get the extension of a stored file by its file_id."""
    path = get_file_path(file_id)
    return path.suffix.lower().lstrip(".")


def delete_file(file_id: str) -> bool:
    """
    Delete a stored file by its file_id.

    Returns:
        True if deleted, False if file didn't exist.
    """
    try:
        file_path = get_file_path(file_id)
        file_path.unlink()
        return True
    except FileNotFoundError:
        return False


def cleanup_old_files(max_age_hours: int = 24) -> int:
    """
    Remove uploaded files older than the specified age.

    Args:
        max_age_hours: Maximum age in hours before a file is deleted.

    Returns:
        Number of files deleted.
    """
    deleted_count = 0
    cutoff = time.time() - (max_age_hours * 3600)

    if not settings.UPLOAD_DIR.exists():
        return 0

    for file_path in settings.UPLOAD_DIR.iterdir():
        if file_path.is_file() and file_path.stat().st_mtime < cutoff:
            file_path.unlink()
            deleted_count += 1

    # Also clean temp dir
    if settings.TEMP_DIR.exists():
        for file_path in settings.TEMP_DIR.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff:
                file_path.unlink()
                deleted_count += 1

    return deleted_count
