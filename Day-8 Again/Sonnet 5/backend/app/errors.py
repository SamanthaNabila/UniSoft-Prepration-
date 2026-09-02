"""Custom exceptions and centralised error handling.

Every error response has the shape ``{"error": "message", "details": {...}}`` so
the frontend can rely on it, and raw exceptions/tracebacks are never sent to the
client.
"""

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    """Base class for expected, client-facing errors."""

    status_code = 400

    def __init__(self, message, status_code=None, details=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.details = details or {}

    def to_dict(self):
        body = {"error": self.message}
        if self.details:
            body["details"] = self.details
        return body


class ValidationError(ApiError):
    status_code = 400

    def __init__(self, details, message="Validation failed"):
        super().__init__(message, details=details)


class NotFoundError(ApiError):
    status_code = 404

    def __init__(self, message="Resource not found"):
        super().__init__(message)


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err):
        app.logger.info("Request rejected (%s): %s", err.status_code, err.message)
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        # Covers unknown routes (404), wrong method (405), malformed request (400)...
        app.logger.info("HTTP %s on %s", err.code, err.name)
        return jsonify({"error": err.description or err.name}), err.code

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(err):  # noqa: ARG001 - message intentionally generic
        app.logger.exception("Database error")
        return jsonify({"error": "A database error occurred. Please try again."}), 500

    @app.errorhandler(Exception)
    def handle_unexpected(err):  # noqa: ARG001
        app.logger.exception("Unhandled exception")
        return jsonify({"error": "An unexpected error occurred."}), 500
