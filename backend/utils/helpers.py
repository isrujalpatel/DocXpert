"""
helpers.py — General utility functions.

Provides common helpers used across the backend: unique ID generation,
timestamps, human-readable file sizes, etc.
"""

import uuid
from datetime import datetime, timezone


def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Return the current UTC datetime as an ISO 8601 string."""
    return utc_now().isoformat()


def human_file_size(size_bytes: int) -> str:
    """
    Convert a file size in bytes to a human-readable string.

    Examples:
        human_file_size(1024)       -> "1.0 KB"
        human_file_size(1_048_576)  -> "1.0 MB"
    """
    if size_bytes < 0:
        raise ValueError("File size cannot be negative")

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.1f} PB"


def safe_filename(filename: str) -> str:
    """
    Sanitize a filename by removing path separators and dangerous characters.
    Keeps the extension intact.
    """
    import re

    # Remove any path components
    filename = filename.replace("\\", "/").split("/")[-1]

    # Remove non-alphanumeric characters except dots, hyphens, underscores
    name, _, ext = filename.rpartition(".")
    if not name:
        name = ext
        ext = ""

    name = re.sub(r"[^\w\-]", "_", name)

    return f"{name}.{ext}" if ext else name


def get_file_extension(filename: str) -> str:
    """Extract the lowercase file extension without the dot."""
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()
