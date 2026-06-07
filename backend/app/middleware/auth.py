"""
JWT-based authentication middleware.
Provides @require_auth and @require_role decorators for route protection.
Compatible with the existing auth_system module.
"""

from flask import request, jsonify, redirect
import functools

# Lazy import to avoid circular deps — actual auth lives in the backend auth_system
_auth = None

def _get_auth():
    global _auth
    if _auth is None:
        import auth_system as _auth_mod
        _auth = _auth_mod.auth
    return _auth


def require_auth(permission='viewer'):
    """
    API route decorator. Validates JWT Bearer token and checks permission.

    Usage:
        @app.route('/api/...')
        @require_auth('engineer')
        def my_route(current_user):
            ...
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            auth = _get_auth()
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'success': False, 'message': 'No token provided'}), 401

            is_valid, user = auth.verify_session(token)
            if not is_valid:
                return jsonify({'success': False, 'message': 'Token invalid or expired'}), 401

            if not auth.check_permission(user['id'], permission):
                return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403

            return f(user, *args, **kwargs)
        return wrapped
    return decorator


def login_required_page(f):
    """
    Page route decorator. Checks Cookie auth, redirects to /login if unauthenticated.
    Passes `current_user` as first arg.
    """
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        auth = _get_auth()
        token = request.cookies.get('auth_token', '')
        if token:
            is_valid, user = auth.verify_session(token)
            if is_valid:
                return f(user, *args, **kwargs)
        return redirect('/login?redirect=' + request.path)
    return wrapped


def admin_required_page(f):
    """Page route decorator. Requires ADMIN role."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        auth = _get_auth()
        token = request.cookies.get('auth_token', '')
        if token:
            is_valid, user = auth.verify_session(token)
            if is_valid and user.get('role') == 'admin':
                return f(user, *args, **kwargs)
        return redirect('/login?redirect=' + request.path)
    return wrapped