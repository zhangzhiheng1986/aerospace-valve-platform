"""
Auth Blueprint: user authentication (login/register/logout/session).
Depends on the existing auth_system module.
"""

from flask import Blueprint, request, jsonify
from app.utils.response import success_response, error_response

auth_bp = Blueprint('auth', __name__)


def _get_auth():
    from auth_system import auth
    return auth


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', username + '@example.com')
    real_name = data.get('real_name', username)
    department = data.get('department', 'Engineering')
    role = data.get('role', 'viewer')

    if not username or not password:
        return error_response('Username and password required', 422)

    auth = _get_auth()
    success, msg = auth.register(username, password, email, real_name, department, role)
    if success:
        return success_response({'username': username}, msg, 201)
    return error_response(msg, 409)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    ip_address = request.remote_addr or '127.0.0.1'
    user_agent = request.headers.get('User-Agent', 'unknown')

    if not username or not password:
        return error_response('Username and password required', 422)

    auth = _get_auth()
    success, msg, user_data = auth.login(username, password, ip_address, user_agent)
    if success:
        token = user_data.get('token', '') if isinstance(user_data, dict) else ''
        role = user_data.get('role', '') if isinstance(user_data, dict) else ''
        resp_body = jsonify({
            'success': True,
            'data': {'token': token, 'username': username, 'role': role},
            'message': msg
        })
        resp_body.set_cookie('auth_token', token,
                            httponly=True, max_age=86400, samesite='Lax')
        return resp_body
    return error_response(msg, 401)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization', '').replace('Bearer ', '') or \
            request.cookies.get('auth_token', '')
    auth = _get_auth()
    if token:
        auth.logout(token)
    resp = jsonify({
        'success': True,
        'data': None,
        'message': 'Logged out'
    })
    resp.delete_cookie('auth_token')
    return resp


@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    token = request.args.get('token', '') or \
            request.headers.get('Authorization', '').replace('Bearer ', '') or \
            request.cookies.get('auth_token', '') or \
            (request.get_json(silent=True) or {}).get('token', '')
    if not token:
        return error_response('No token', 401)

    auth = _get_auth()
    is_valid, user = auth.verify_session(token)
    if is_valid:
        return jsonify({
            'success': True,
            'valid': True,
            'username': user.get('username', ''),
            'role': user.get('role', '')
        })
    return error_response('Token invalid or expired', 401)
