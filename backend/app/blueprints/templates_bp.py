"""
Templates Blueprint: R&D document/layout template library (SQLite-backed).
"""

from flask import Blueprint, request, render_template, jsonify
from app.utils.clean import prepare_json
from app.middleware.auth import require_auth

templates_bp = Blueprint('templates', __name__)


@templates_bp.route('/templates')
def templates_page():
    return render_template('template_library.html')


@templates_bp.route('/api/templates/categories', methods=['GET'])
def categories():
    import template_library as tlib
    return jsonify(prepare_json(tlib.get_all_categories()))


@templates_bp.route('/api/templates/categories/<int:cat_id>', methods=['GET'])
def category(cat_id):
    import template_library as tlib
    result = tlib.get_category(cat_id)
    return jsonify(prepare_json(result))


@templates_bp.route('/api/templates/stats', methods=['GET'])
def stats():
    import template_library as tlib
    return jsonify(prepare_json(tlib.get_template_stats()))


@templates_bp.route('/api/templates', methods=['GET'])
def list_templates():
    import template_library as tlib
    cat = request.args.get('category', '')
    search = request.args.get('search', '')
    return jsonify(prepare_json(tlib.get_templates(
        category_id=cat or None, search=search or None)))


@templates_bp.route('/api/templates/<int:template_id>', methods=['GET'])
def get_template(template_id):
    import template_library as tlib
    result = tlib.get_template(template_id)
    if result:
        return jsonify(prepare_json(result))
    return jsonify({'success': False, 'message': 'Not found'}), 404


@templates_bp.route('/api/templates', methods=['POST'])
@require_auth('engineer')
def create_template(current_user):
    import template_library as tlib
    data = request.get_json() or {}
    result = tlib.create_template(
        title=data.get('title', ''),
        content=data.get('content', ''),
        category_id=data.get('category_id'),
        description=data.get('description', ''),
        standard_refs=data.get('standard_refs', ''),
        version=data.get('version', '1.0')
    )
    return jsonify(prepare_json(result))


@templates_bp.route('/api/templates/<int:template_id>', methods=['PUT'])
@require_auth('engineer')
def update_template(current_user, template_id):
    import template_library as tlib
    data = request.get_json() or {}
    result = tlib.update_template(template_id, **data)
    return jsonify(prepare_json(result))


@templates_bp.route('/api/templates/<int:template_id>', methods=['DELETE'])
@require_auth('admin')
def delete_template(current_user, template_id):
    import template_library as tlib
    result = tlib.delete_template(template_id)
    return jsonify(prepare_json(result))