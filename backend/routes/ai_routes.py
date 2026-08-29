"""
ai_routes.py — AI formatting enhancement (feature 4) and
AI settings adjustment (feature 6) endpoints.
"""

from flask import Blueprint, request, jsonify
from services.file_manager import get_file_path
from services.document_parser import parse_document
from services.ai_service import analyze_formatting, suggest_settings
from utils.validators import validate_file_id, ValidationError

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/ai/format-enhance", methods=["POST"])
def format_enhance():
    """
    Feature 4 — AI formatting enhancement.

    Analyzes document structure and suggests formatting fixes
    (heading consistency, spacing, list styles).

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
        parsed = parse_document(file_path)
        suggestions = analyze_formatting(parsed.paragraphs)
    except RuntimeError as e:
        return jsonify({"success": False, "error": str(e)}), 503
    except Exception as e:
        return jsonify({"success": False, "error": f"Analysis failed: {str(e)}"}), 500

    return jsonify({
        "success": True,
        "message": f"Found {len(suggestions)} formatting suggestion(s).",
        "data": {
            "file_id": file_id,
            "suggestions": [s.to_dict() for s in suggestions],
            "total": len(suggestions),
        }
    })


@ai_bp.route("/api/ai/adjust-settings", methods=["POST"])
def adjust_settings():
    """
    Feature 6 — AI font/margin/settings adjustment.

    Suggests font, margin, and layout changes based on document type
    or user intent.

    Expects JSON: { "file_id": "...", "intent": "academic paper" }
    Returns a list of SuggestedChange objects.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "JSON body required."}), 400

    file_id = data.get("file_id")
    intent = data.get("intent", "")

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
        parsed = parse_document(file_path)
        suggestions = suggest_settings(
            parsed.paragraphs,
            parsed.fonts_used,
            user_intent=intent,
        )
    except RuntimeError as e:
        return jsonify({"success": False, "error": str(e)}), 503
    except Exception as e:
        return jsonify({"success": False, "error": f"Settings analysis failed: {str(e)}"}), 500

    return jsonify({
        "success": True,
        "message": f"Found {len(suggestions)} setting suggestion(s).",
        "data": {
            "file_id": file_id,
            "suggestions": [s.to_dict() for s in suggestions],
            "total": len(suggestions),
        }
    })
