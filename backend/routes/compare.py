"""
compare.py — Document comparison endpoint (feature 5).
"""

from flask import Blueprint, request, jsonify
from services.file_manager import get_file_path, save_upload
from services.doc_comparator import compare_documents
from utils.validators import validate_file_id, validate_file_upload, ValidationError

compare_bp = Blueprint("compare", __name__)


@compare_bp.route("/api/ai/compare", methods=["POST"])
def compare_docs():
    """
    Feature 5 — AI document comparison.

    Accepts two files or two file_ids, extracts text, runs a diff,
    and highlights additions/deletions/changes.

    Option A — JSON with two file_ids:
        { "file_id_a": "...", "file_id_b": "..." }

    Option B — Multipart with two files:
        file_a=@doc1.docx, file_b=@doc2.docx
    """
    # Determine input mode
    if request.content_type and "multipart" in request.content_type:
        # Mode B: Two file uploads
        file_a = request.files.get("file_a")
        file_b = request.files.get("file_b")

        if not file_a or not file_b:
            return jsonify({
                "success": False,
                "error": "Two files required: 'file_a' and 'file_b'."
            }), 400

        try:
            ext_a, _ = validate_file_upload(file_a)
            ext_b, _ = validate_file_upload(file_b)
        except ValidationError as e:
            return jsonify({"success": False, "error": e.message}), e.status_code

        result_a = save_upload(file_a, ext_a)
        result_b = save_upload(file_b, ext_b)

        path_a = get_file_path(result_a["file_id"])
        path_b = get_file_path(result_b["file_id"])
    else:
        # Mode A: Two file_ids
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "error": "JSON body or multipart files required."}), 400

        file_id_a = data.get("file_id_a")
        file_id_b = data.get("file_id_b")

        if not file_id_a or not file_id_b:
            return jsonify({
                "success": False,
                "error": "Both file_id_a and file_id_b are required."
            }), 400

        try:
            validate_file_id(file_id_a)
            validate_file_id(file_id_b)
            path_a = get_file_path(file_id_a)
            path_b = get_file_path(file_id_b)
        except ValidationError as e:
            return jsonify({"success": False, "error": e.message}), e.status_code
        except FileNotFoundError as e:
            return jsonify({"success": False, "error": str(e)}), 404

    try:
        result = compare_documents(path_a, path_b)
    except Exception as e:
        return jsonify({"success": False, "error": f"Comparison failed: {str(e)}"}), 500

    return jsonify({
        "success": True,
        "message": f"Found {result.total_differences} difference(s).",
        "data": {
            "suggestions": [d.to_dict() for d in result.differences],
            "total": result.total_differences,
            "similarity_score": result.similarity_score,
            "paragraphs_a": result.paragraphs_a,
            "paragraphs_b": result.paragraphs_b,
        }
    })
