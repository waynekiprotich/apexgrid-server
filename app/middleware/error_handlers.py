from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": {"code": "BAD_REQUEST", "message": str(e.description), "status": 400}}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Missing or invalid token", "status": 401}}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Resource not found", "status": 404}}), 404

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({"error": {"code": "RATE_LIMITED", "message": "Too many requests", "status": 429}}), 429

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        # Catch all other HTTP exceptions (like 405, 415, 422, etc)
        # 500 errors raised explicitly via abort(500) will also come here
        code_name = getattr(e, "name", "HTTP_EXCEPTION").upper().replace(" ", "_").replace("-", "_")
        return jsonify({"error": {"code": code_name, "message": str(e.description), "status": getattr(e, "code", 500)}}), getattr(e, "code", 500)

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        traceback.print_exc()
        return jsonify({"error": {"code": "INTERNAL_ERROR", "message": "Internal server error", "status": 500}}), 500
