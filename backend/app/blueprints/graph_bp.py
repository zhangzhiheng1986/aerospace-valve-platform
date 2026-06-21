# -*- coding: utf-8 -*-
"""Legacy Knowledge Graph Blueprint — thin wrapper over knowledge_graph module.
Sprint 7 graphs moved to avis; this preserves backward-compatible /api/graph/* routes."""
from flask import Blueprint, request, jsonify

graph_bp = Blueprint('graph', __name__, url_prefix='/api/graph')


@graph_bp.route('/stats', methods=['GET'])
def stats():
    try:
        from knowledge_graph import get_graph_query
        q = get_graph_query()
        b = q.builder
        return jsonify({'success': True, 'stats': {
            'entities': len(b.entities),
            'edges': len(b.edges),
        }})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@graph_bp.route('/search', methods=['GET'])
def search():
    try:
        from knowledge_graph import get_graph_query
        q = get_graph_query()
        query = request.args.get('query', '')
        results = q.search_entity(query, limit=20)
        return jsonify({'success': True, 'query': query, 'results': results, 'hits': len(results)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@graph_bp.route('/entity/<entity_id>', methods=['GET'])
def entity(entity_id):
    try:
        from knowledge_graph import get_graph_query
        q = get_graph_query()
        info = q.get_entity(entity_id)
        return jsonify({'success': info is not None, 'entity': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@graph_bp.route('/neighbors/<entity_id>', methods=['GET'])
def neighbors(entity_id):
    try:
        from knowledge_graph import get_graph_query
        q = get_graph_query()
        nbrs = q.get_neighbors(entity_id)
        return jsonify({'success': True, 'neighbors': nbrs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
