"""
convert.py — DOCX ↔ PDF conversion endpoint.
"""

from flask import Blueprint, request, jsonify
from services.file_manager import get_file_path
from services.converter import convert_document
from utils.validators import validate_file_id, ValidationError
from utils.helpers import human_file_size, generate_uuid

convert_bp = Blueprint("convert", __name__)


@convert_bp.route("/api/convert", methods=["POST"])
def convert_file():
    """
    Convert a document between DOCX and PDF formats.

    Expects JSON: { "file_id": "...", "target_format": "pdf" | "docx" }
    Returns the converted file's metadata.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "JSON body required."}), 400

    file_id = data.get("file_id")
    target_format = data.get("target_format", "").lower()

    if not file_id:
        return jsonify({"success": False, "error": "file_id is required."}), 400

    if target_format not in ("pdf", "docx"):
        return jsonify({"success": False, "error": "target_format must be 'pdf' or 'docx'."}), 400

    try:
        validate_file_id(file_id)
        input_path = get_file_path(file_id)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), e.status_code
    except FileNotFoundError:
        return jsonify({"success": False, "error": f"File not found: {file_id}"}), 404

    try:
        output_path = convert_document(input_path, target_format)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Conversion failed: {str(e)}"}), 500

    # Extract new file_id from the output filename
    new_file_id = output_path.stem

    return jsonify({
        "success": True,
        "message": f"Converted to {target_format.upper()} successfully.",
        "data": {
            "file_id": new_file_id,
            "file_name": output_path.name,
            "file_type": target_format,
            "file_size_bytes": output_path.stat().st_size,
            "file_size_human": human_file_size(output_path.stat().st_size),
        }
    })
