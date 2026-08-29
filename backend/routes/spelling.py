"""
spelling.py — AI spell check endpoint (feature 7).
"""

from flask import Blueprint, request, jsonify
from services.file_manager import get_file_path
from services.spell_checker import check_document
from utils.validators import validate_file_id, ValidationError

spelling_bp = Blueprint("spelling", __name__)


@spelling_bp.route("/api/ai/spell-check", methods=["POST"])
def spell_check():
    """
    Feature 7 — AI spell check.

    Integrates LanguageTool to flag spelling/grammar issues with
    suggested corrections.

    Expects JSON: { "file_id": "..." }
    Returns a list of SuggestedChange objects.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "JSON body required."}), 400

    file_id = data.get("file_id")
    if not file_id:
        return jsonify({"success": False, "error": "file_id is required."}), 400

    try:
        validate_file_id(file_id)
        file_path = get_file_path(file_id)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), e.status_code
    except FileNotFoundError:
        return jsonify({"success": False, "error": f"File not found: {file_id}"}), 404

    try:
        suggestions = check_document(file_path)
    except Exception as e:
        return jsonify({"success": False, "error": f"Spell check failed: {str(e)}"}), 500

    return jsonify({
        "success": True,
        "message": f"Found {len(suggestions)} issue(s).",
        "data": {
            "file_id": file_id,
            "suggestions": [s.to_dict() for s in suggestions],
            "total": len(suggestions),
        }
    })
