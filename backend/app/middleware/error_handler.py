"""
Global error handling middleware.
Registers handlers for common exceptions so route code stays clean.
"""

from flask import jsonify, request
from app.extensions import logger


def register_error_handlers(app):
    """Register all error handlers on the given app."""

    @app.errorhandler(400)
    def bad_request(e):
        logger.warning('400 Bad Request: %s %s', request.method, request.path)
        return jsonify({
            'success': False,
            'message': str(e.description) if hasattr(e, 'description') else 'Bad request'
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            'success': False,
            'message': 'Forbidden'
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            'success': False,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({
            'success': False,
            'message': str(e.description) if hasattr(e, 'description') else 'Unprocessable entity'
        }), 422

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception('500 Internal Server Error: %s %s', request.method, request.path)
        original = getattr(e, 'original_exception', None)
        detail = str(original) if original else str(e)
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'details': detail if app.debug else None
        }), 500

    logger.info('Error handlers registered')