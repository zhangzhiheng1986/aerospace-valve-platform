"""
Users Blueprint: admin user management (CRUD, statistics).
Depends on auth_system module.
"""

from flask import Blueprint, request, jsonify
from app.utils.response import error_response
from app.utils.clean import prepare_json

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


def _get_auth():
    from auth_system import auth
    return auth


def _require_admin():
    """Check admin token, return (user, None) or (None, error_response)."""
    auth = _get_auth()
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None, error_response('No token', 401)
    is_valid, user = auth.verify_session(token)
    if not is_valid:
        return None, error_response('Token invalid', 401)
    if user.get('role') != 'admin':
        return None, error_response('Admin only', 403)
    return user, None


@users_bp.route('/statistics')
def statistics():
    user, err = _require_admin()
    if err:
        return err
    auth = _get_auth()
    return jsonify(prepare_json(auth.get_user_statistics()))


@users_bp.route('/list')
def list_users():
    user, err = _require_admin()
    if err:
        return err
    auth = _get_auth()
    return jsonify(prepare_json(auth.get_all_users()))


@users_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    user, err = _require_admin()
    if err:
        return err
    data = request.get_json() or {}
    auth = _get_auth()
    success, msg = auth.update_user(user_id, **data)
    if success:
        return jsonify(prepare_json({'message': msg}))
    return error_response(msg, 400)


@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user, err = _require_admin()
    if err:
        return err
    auth = _get_auth()
    success, msg = auth.delete_user(user_id)
    if success:
        return jsonify(prepare_json({'message': msg}))
    return error_response(msg, 400)


@users_bp.route('/change-password', methods=['POST'])
def change_password():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth = _get_auth()
    is_valid, user = auth.verify_session(token)
    if not is_valid:
        return error_response('Invalid token', 401)
    data = request.get_json() or {}
    old_pwd = data.get('old_password', '')
    new_pwd = data.get('new_password', '')
    success, msg = auth.change_password(user['id'], old_pwd, new_pwd)
    if success:
        return jsonify(prepare_json({'message': msg}))
    return error_response(msg, 400)