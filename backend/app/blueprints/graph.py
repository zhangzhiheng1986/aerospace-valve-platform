"""Knowledge Graph API Blueprint — Sprint 7

Endpoints:
  GET  /api/graph/stats           — graph statistics
  GET  /api/graph/entity/<id>    — get entity by ID
  GET  /api/graph/search?q=...&type=...&limit=...  — search entities
  GET  /api/graph/neighbors/<id>?relation=...&dir=...  — get neighbors
  GET  /api/graph/path?from=...&to=...  — find shortest path
  POST /api/graph/subgraph       — extract subgraph
  GET  /api/graph/centrality?top_k=...  — most central entities
"""
from flask import Blueprint, request, jsonify
from knowledge_graph import get_knowledge_graph, get_graph_query

graph_bp = Blueprint('graph', __name__)


@graph_bp.route('/stats')
def stats():
    """Get graph statistics."""
    g = get_knowledge_graph()
    return jsonify({'success': True, **g.get_stats()})


@graph_bp.route('/entity/<path:entity_id>')
def get_entity(entity_id):
    """Get a single entity by ID."""
    q = get_graph_query()
    entity = q.get_entity(entity_id)
    if entity:
        return jsonify({'success': True, 'entity': entity})
    return jsonify({'success': False, 'error': f'Entity not found: {entity_id}'}), 404


@graph_bp.route('/search')
def search():
    """Search entities by query string."""
    q = get_graph_query()
    query_str = request.args.get('q', '')
    entity_type = request.args.get('type')  # Optional filter
    limit = int(request.args.get('limit', 20))
    
    results = q.search_entity(query_str, entity_type=entity_type, limit=limit)
    return jsonify({
        'success': True,
        'query': query_str,
        'type': entity_type,
        'total': len(results),
        'results': results,
    })


@graph_bp.route('/neighbors/<path:entity_id>')
def get_neighbors(entity_id):
    """Get neighbors of an entity."""
    q = get_graph_query()
    relation = request.args.get('relation')
    direction = request.args.get('dir', 'both')
    limit = int(request.args.get('limit', 50))
    
    neighbors = q.get_neighbors(entity_id, relation=relation, direction=direction, limit=limit)
    entity = q.get_entity(entity_id)
    return jsonify({
        'success': True,
        'entity': entity,
        'neighbors': neighbors,
        'total': len(neighbors),
    })


@graph_bp.route('/path')
def find_path():
    """Find shortest path between two entities."""
    q = get_graph_query()
    from_id = request.args.get('from', '')
    to_id = request.args.get('to', '')
    max_depth = int(request.args.get('max_depth', 5))
    
    if not from_id or not to_id:
        return jsonify({'success': False, 'error': 'Both from and to required'}), 400
    
    path = q.find_path(from_id, to_id, max_depth=max_depth)
    return jsonify({
        'success': True,
        'from': from_id,
        'to': to_id,
        'path': path,
        'length': len(path),
    })


@graph_bp.route('/subgraph', methods=['POST'])
def subgraph():
    """Extract a subgraph around given entities."""
    q = get_graph_query()
    data = request.get_json(force=True) or {}
    entity_ids = data.get('entity_ids', data.get('ids', []))
    depth = int(data.get('depth', 1))
    
    if not entity_ids:
        return jsonify({'success': False, 'error': 'entity_ids required'}), 400
    
    result = q.get_subgraph(entity_ids, depth=depth)
    result['success'] = True
    return jsonify(result)


@graph_bp.route('/centrality')
def centrality():
    """Get most central entities by degree."""
    q = get_graph_query()
    top_k = int(request.args.get('top_k', 20))
    results = q.get_centrality(top_k=top_k)
    return jsonify({
        'success': True,
        'top_k': top_k,
        'results': results,
    })
