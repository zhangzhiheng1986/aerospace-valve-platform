"""
Unified API response helpers.
All API endpoints should use these helpers for consistent JSON responses.
"""

from flask import jsonify


def success_response(data=None, message='', code=200):
    """
    Standard success response.

    Args:
        data:    payload (dict/list/None)
        message: optional human-readable message
        code:    HTTP status code (default 200)

    Returns:
        JSON response with { success, data, message }
    """
    payload = {'success': True, 'data': data}
    if message:
        payload['message'] = message
    return jsonify(payload), code


def error_response(message, code=400, details=None):
    """
    Standard error response.

    Args:
        message: human-readable error description
        code:    HTTP status code (default 400)
        details: optional extra error info (dict/list)

    Returns:
        JSON response with { success, message, details }
    """
    payload = {'success': False, 'message': message}
    if details is not None:
        payload['details'] = details
    return jsonify(payload), code


def validation_error(errors):
    """
    Shortcut for input validation errors (422).
    `errors` is typically a dict of field -> error_msg.
    """
    return error_response('Validation failed', code=422, details=errors)
