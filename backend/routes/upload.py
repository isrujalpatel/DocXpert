"""
upload.py — File upload, metadata, download, and delete endpoints.
"""

from flask import Blueprint, request, jsonify, send_file
from services.file_manager import save_upload, get_file_path, delete_file
from utils.validators import validate_file_upload, validate_file_id, ValidationError
from utils.helpers import human_file_size, utc_now_iso

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/api/upload", methods=["POST"])
def upload_file():
    """
    Upload a document file (DOCX, DOC, or PDF).

    Expects multipart/form-data with a 'file' field.
    Returns file metadata including a file_id for subsequent operations.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided. Send a 'file' field."}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"success": False, "error": "No file selected."}), 400

    try:
        extension, file_size = validate_file_upload(file)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), e.status_code

    result = save_upload(file, extension)

    return jsonify({
        "success": True,
        "message": "File uploaded successfully.",
        "data": {
            "file_id": result["file_id"],
            "original_name": file.filename,
            "file_type": extension,
            "file_size_bytes": result["file_size_bytes"],
            "file_size_human": human_file_size(result["file_size_bytes"]),
            "uploaded_at": utc_now_iso(),
        }
    }), 201


@upload_bp.route("/api/files/<file_id>", methods=["GET"])
def get_file_metadata(file_id):
    """Get metadata for a stored file."""
    try:
        validate_file_id(file_id)
        file_path = get_file_path(file_id)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), e.status_code
    except FileNotFoundError:
        return jsonify({"success": False, "error": f"File not found: {file_id}"}), 404

    stat = file_path.stat()

    return jsonify({
        "success": True,
        "data": {
            "file_id": file_id,
            "file_name": file_path.name,
            "file_type": file_path.suffix.lower().lstrip("."),
            "file_size_bytes": stat.st_size,
            "file_size_human": human_file_size(stat.st_size),
        }
    })


@upload_bp.route("/api/files/<file_id>/download", methods=["GET"])
def download_file(file_id):
    """Download a stored file."""
    try:
        validate_file_id(file_id)
        file_path = get_file_path(file_id)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), e.status_code
    except FileNotFoundError:
        return jsonify({"success": False, "error": f"File not found: {file_id}"}), 404

    # Use the original filename if provided via query param, else use stored name
    download_name = request.args.get("name", file_path.name)

    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=download_name,
    )


@upload_bp.route("/api/files/<file_id>", methods=["DELETE"])
def delete_uploaded_file(file_id):
    """Delete a stored file."""
    try:
        validate_file_id(file_id)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), e.status_code

    deleted = delete_file(file_id)

    if deleted:
        return jsonify({"success": True, "message": "File deleted."})
    else:
        return jsonify({"success": False, "error": "File not found."}), 404
