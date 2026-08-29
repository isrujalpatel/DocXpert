"""
routes/__init__.py — Blueprint registration for all API routes.
"""


def register_routes(app):
    """Register all route blueprints with the Flask app."""
    from routes.upload import upload_bp
    from routes.convert import convert_bp
    from routes.replace import replace_bp
    from routes.ai_routes import ai_bp
    from routes.compare import compare_bp
    from routes.spelling import spelling_bp
    from routes.apply import apply_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(convert_bp)
    app.register_blueprint(replace_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(compare_bp)
    app.register_blueprint(spelling_bp)
    app.register_blueprint(apply_bp)
