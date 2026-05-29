"""
CMS Blueprint: content management system for articles/categories/tags.
"""

from flask import Blueprint, request, render_template, jsonify
from app.utils.clean import prepare_json
from app.middleware.auth import require_auth, admin_required_page

cms_bp = Blueprint('cms', __name__)


# ==================== CMS Admin Pages ====================

@cms_bp.route('/cms_admin')
@admin_required_page
def cms_admin_page(current_user):
    return render_template('cms_admin.html')


@cms_bp.route('/knowledge_articles')
def articles_page():
    return render_template('knowledge_articles.html')


@cms_bp.route('/knowledge_articles/<slug_or_id>')
def article_detail(slug_or_id):
    return render_template('knowledge_articles.html')


# ==================== CMS Stats ====================

@cms_bp.route('/api/cms/stats', methods=['GET'])
def stats():
    from cms_module import get_stats
    return jsonify(prepare_json(get_stats()))


# ==================== Articles CRUD ====================

@cms_bp.route('/api/cms/articles', methods=['GET'])
def list_articles():
    from cms_module import get_articles
    category = request.args.get('category', '')
    tag = request.args.get('tag', '')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    return jsonify(prepare_json(get_articles(
        category=category or None,
        tag=tag or None,
        search=search or None,
        page=page
    )))


@cms_bp.route('/api/cms/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    from cms_module import get_article
    result = get_article(article_id)
    if result:
        return jsonify(prepare_json(result))
    return jsonify({'success': False, 'message': 'Article not found'}), 404


@cms_bp.route('/api/cms/articles', methods=['POST'])
@require_auth('engineer')
def create_article(current_user):
    from cms_module import create_article as _create
    data = request.get_json() or {}
    result = _create(data, current_user['id'])
    return jsonify(prepare_json(result))


@cms_bp.route('/api/cms/articles/<int:article_id>', methods=['PUT'])
@require_auth('engineer')
def update_article(current_user, article_id):
    from cms_module import update_article as _update
    data = request.get_json() or {}
    result = _update(article_id, data)
    return jsonify(prepare_json(result))


@cms_bp.route('/api/cms/articles/<int:article_id>', methods=['DELETE'])
@require_auth('admin')
def delete_article(current_user, article_id):
    from cms_module import delete_article as _delete
    result = _delete(article_id)
    return jsonify(prepare_json(result))


# ==================== Categories CRUD ====================

@cms_bp.route('/api/cms/categories', methods=['GET'])
def list_categories():
    from cms_module import get_categories
    return jsonify(prepare_json(get_categories()))


@cms_bp.route('/api/cms/categories', methods=['POST'])
@require_auth('admin')
def create_category(current_user):
    from cms_module import create_category as _create
    data = request.get_json() or {}
    result = _create(data)
    return jsonify(prepare_json(result))


@cms_bp.route('/api/cms/categories/<int:category_id>', methods=['PUT'])
@require_auth('admin')
def update_category(current_user, category_id):
    from cms_module import update_category as _update
    data = request.get_json() or {}
    result = _update(category_id, data)
    return jsonify(prepare_json(result))


@cms_bp.route('/api/cms/categories/<int:category_id>', methods=['DELETE'])
@require_auth('admin')
def delete_category(current_user, category_id):
    from cms_module import delete_category as _delete
    result = _delete(category_id)
    return jsonify(prepare_json(result))


# ==================== Tags ====================

@cms_bp.route('/api/cms/tags', methods=['GET'])
def list_tags():
    from cms_module import get_tags
    return jsonify(prepare_json(get_tags()))
