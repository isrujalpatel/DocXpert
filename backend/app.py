"""
app.py — Flask application entry point for DocXpert.

Initialises the Flask app with CORS, registers all route blueprints,
serves the frontend static files, and runs the development server.
"""

import sys
from pathlib import Path

# Add backend directory to Python path so imports work
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from flask import Flask, send_from_directory
from flask_cors import CORS
from config.settings import settings
from routes import register_routes


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        static_folder=None,  # We'll serve frontend files manually
    )

    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = settings.MAX_UPLOAD_SIZE_BYTES

    # Enable CORS
    CORS(app, origins=settings.CORS_ORIGINS)

    # Create required directories
    settings.ensure_dirs()

    # Register API routes
    register_routes(app)

    # ── Serve Frontend Static Files ──────────────────────────────
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

    @app.route("/")
    def serve_index():
        """Serve the main landing page."""
        return send_from_directory(str(frontend_dir), "index.html")

    @app.route("/workspace")
    def serve_workspace():
        """Serve the workspace page."""
        return send_from_directory(str(frontend_dir), "workspace.html")

    @app.route("/<path:filename>")
    def serve_static(filename):
        """Serve frontend static files (CSS, JS, images)."""
        return send_from_directory(str(frontend_dir), filename)

    # ── Error Handlers ───────────────────────────────────────────

    @app.errorhandler(413)
    def too_large(e):
        return {
            "success": False,
            "error": f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB."
        }, 413

    @app.errorhandler(404)
    def not_found(e):
        return {"success": False, "error": "Resource not found."}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"success": False, "error": "Internal server error."}, 500

    return app


# ── Main Entry Point ─────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()

    print(f"\n{'='*52}")
    print(f"  DocXpert API Server")
    print(f"  http://localhost:{settings.PORT}")
    print(f"  Workspace: http://localhost:{settings.PORT}/workspace")
    print(f"{'='*52}\n")

    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG,
    )
