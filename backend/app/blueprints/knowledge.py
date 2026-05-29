"""
Knowledge Blueprint: aerospace valve engineering knowledge base.
"""

from flask import Blueprint, request, render_template, jsonify
from app.utils.clean import prepare_json

knowledge_bp = Blueprint('knowledge', __name__)


@knowledge_bp.route('/knowledge')
def knowledge_page():
    return render_template('knowledge.html')


@knowledge_bp.route('/api/knowledge/chapters')
def chapters():
    from knowledge_base import get_all_chapters
    return jsonify(prepare_json(get_all_chapters()))


@knowledge_bp.route('/api/knowledge/chapter/<chapter_id>')
def chapter(chapter_id):
    from knowledge_base import get_chapter_detail
    result = get_chapter_detail(chapter_id)
    if result:
        return jsonify(prepare_json(result))
    return jsonify({'error': 'Chapter not found'}), 404


@knowledge_bp.route('/api/knowledge/section/<chapter_id>/<section_id>')
def section(chapter_id, section_id):
    from knowledge_base import get_section
    result = get_section(chapter_id, section_id)
    if result:
        return jsonify(prepare_json(result))
    return jsonify({'error': 'Section not found'}), 404


@knowledge_bp.route('/api/knowledge/search')
def search():
    from knowledge_base import search_knowledge
    q = request.args.get('q', '')
    return jsonify(prepare_json(search_knowledge(q)))


@knowledge_bp.route('/api/knowledge/stats')
def stats():
    from knowledge_base import get_stats
    return jsonify(prepare_json(get_stats()))


@knowledge_bp.route('/api/knowledge/glossary')
def glossary():
    from knowledge_base import get_glossary
    return jsonify(prepare_json(get_glossary()))
