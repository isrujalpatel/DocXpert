"""
replace.py — Find & replace endpoint.
"""

from flask import Blueprint, request, jsonify
from services.file_manager import get_file_path
from services.text_replacer import replace_in_document
from utils.validators import validate_file_id, ValidationError
from utils.helpers import human_file_size

replace_bp = Blueprint("replace", __name__)


@replace_bp.route("/api/find-replace", methods=["POST"])
def find_replace():
    """
    Find and replace text in a document.

    Expects JSON:
    {
        "file_id": "...",
        "find_text": "search term",
        "replace_text": "replacement",
        "use_regex": false,
        "case_sensitive": true
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "JSON body required."}), 400

    file_id = data.get("file_id")
    find_text = data.get("find_text", "")
    replace_text = data.get("replace_text", "")
    use_regex = data.get("use_regex", False)
    case_sensitive = data.get("case_sensitive", True)

    if not file_id:
        return jsonify({"success": False, "error": "file_id is required."}), 400
    if not find_text:
        return jsonify({"success": False, "error": "find_text is required."}), 400

    try:
        validate_file_id(file_id)
        input_path = get_file_path(file_id)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), e.status_code
    except FileNotFoundError:
        return jsonify({"success": False, "error": f"File not found: {file_id}"}), 404

    ext = input_path.suffix.lower().lstrip(".")
    if ext != "docx":
        return jsonify({
            "success": False,
            "error": "Find & replace only works with DOCX files. Convert to DOCX first."
        }), 400

    try:
        result = replace_in_document(input_path, find_text, replace_text, use_regex, case_sensitive)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Replace failed: {str(e)}"}), 500

    new_file_id = result.output_path.stem

    return jsonify({
        "success": True,
        "message": f"Replaced {result.replacements_made} occurrence(s).",
        "data": {
            "file_id": new_file_id,
            "file_name": result.output_path.name,
            "replacements_made": result.replacements_made,
            "file_size_bytes": result.output_path.stat().st_size,
            "file_size_human": human_file_size(result.output_path.stat().st_size),
        }
    })
