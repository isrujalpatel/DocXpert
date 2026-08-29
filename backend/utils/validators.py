"""
validators.py — Input validation helpers.

Provides reusable validation functions for file uploads
and other user inputs. Flask-compatible (no FastAPI dependencies).
"""

from config.settings import settings


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def validate_file_extension(filename: str) -> str:
    """
    Validate that the file has an allowed extension.
    Returns the lowercase extension without the dot.

    Raises:
        ValidationError if extension is not allowed.
    """
    if not filename or "." not in filename:
        raise ValidationError(
            f"Invalid filename: '{filename}'. Must have an extension.",
            status_code=400,
        )

    extension = filename.rsplit(".", 1)[-1].lower()

    if extension not in settings.ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type '.{extension}' is not supported. "
            f"Allowed types: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}",
            status_code=400,
        )

    return extension


def validate_file_size(file_storage) -> int:
    """
    Validate that the uploaded file does not exceed the size limit.
    Works with Flask's FileStorage objects.

    Returns:
        The file size in bytes.

    Raises:
        ValidationError if file is too large.
    """
    import os

    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)

    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError(
            f"File size ({file_size / (1024 * 1024):.1f} MB) exceeds the "
            f"maximum allowed size ({settings.MAX_UPLOAD_SIZE_MB} MB).",
            status_code=413,
        )

    return file_size


def validate_file_upload(file_storage) -> tuple:
    """
    Run all upload validations on a Flask FileStorage object.
    Returns (extension, file_size_bytes).

    Raises:
        ValidationError on validation failure.
    """
    extension = validate_file_extension(file_storage.filename)
    file_size = validate_file_size(file_storage)
    return extension, file_size


def validate_file_id(file_id: str) -> str:
    """
    Validate that a file_id looks like a valid UUID string.

    Raises:
        ValidationError if invalid.
    """
    import uuid

    try:
        uuid.UUID(file_id)
    except ValueError:
        raise ValidationError(
            f"Invalid file ID: '{file_id}'. Must be a valid UUID.",
            status_code=400,
        )

    return file_id
