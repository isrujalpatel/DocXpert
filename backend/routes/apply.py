"""
apply.py — Apply accepted AI changes endpoint (feature 8).
"""

from flask import Blueprint, request, jsonify
from services.file_manager import get_file_path
from services.change_applier import apply_changes
from models.document import SuggestedChange
from utils.validators import validate_file_id, ValidationError
from utils.helpers import human_file_size

apply_bp = Blueprint("apply", __name__)


@apply_bp.route("/api/ai/apply-changes", methods=["POST"])
def apply_accepted_changes():
    """
    Feature 8 — Apply accepted AI suggestions to a document.

    Expects JSON:
    {
        "file_id": "...",
        "accepted_change_ids": ["chg_xxx", "chg_yyy"],
        "all_changes": [{ full SuggestedChange objects }]
    }

    Returns the new file_id with changes applied.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "JSON body required."}), 400

    file_id = data.get("file_id")
    accepted_ids = data.get("accepted_change_ids", [])
    all_changes = data.get("all_changes", [])

    if not file_id:
        return jsonify({"success": False, "error": "file_id is required."}), 400

    if not accepted_ids:
        return jsonify({"success": False, "error": "No changes accepted."}), 400

    try:
        validate_file_id(file_id)
        file_path = get_file_path(file_id)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), e.status_code
    except FileNotFoundError:
        return jsonify({"success": False, "error": f"File not found: {file_id}"}), 404

    ext = file_path.suffix.lower().lstrip(".")
    if ext != "docx":
        return jsonify({
            "success": False,
            "error": "Changes can only be applied to DOCX files. Convert first."
        }), 400

    # Filter to only accepted changes
    accepted_changes = []
    for change_data in all_changes:
        if change_data.get("id") in accepted_ids:
            try:
                change = SuggestedChange.from_dict(change_data)
                accepted_changes.append(change)
            except Exception:
                continue

    if not accepted_changes:
        return jsonify({
            "success": False,
            "error": "None of the accepted change IDs matched the provided changes."
        }), 400

    try:
        output_path = apply_changes(file_path, accepted_changes)
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to apply changes: {str(e)}"}), 500

    new_file_id = output_path.stem

    return jsonify({
        "success": True,
        "message": f"Applied {len(accepted_changes)} change(s) successfully.",
        "data": {
            "file_id": new_file_id,
            "file_name": output_path.name,
            "changes_applied": len(accepted_changes),
            "file_size_bytes": output_path.stat().st_size,
            "file_size_human": human_file_size(output_path.stat().st_size),
        }
    })
