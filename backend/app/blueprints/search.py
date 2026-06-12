"""
Search Blueprint — Vector semantic search API
==============================================
Exposes vector_store search as REST API endpoints.
"""

from flask import Blueprint, request, jsonify

from vector_store import KnowledgeIndexer, get_search

search_bp = Blueprint("search", __name__, url_prefix="/api/search")

# Lazy-built indexer
_indexer: KnowledgeIndexer = None


def _ensure_index():
    global _indexer
    if _indexer is None:
        _indexer = get_search()
    return _indexer


@search_bp.route("/semantic", methods=["POST"])
def semantic_search():
    """POST /api/search/semantic
    Body: { "query": "...", "top_k": 8, "source": "all|knowledge|formulas|materials" }
    """
    body = request.get_json(silent=True) or {}
    query = (body.get("query") or "").strip()
    if not query:
        return jsonify({"success": False, "error": "query is required"}), 400

    top_k = min(int(body.get("top_k", 8)), 20)
    source = body.get("source", "all")

    idx = _ensure_index()

    if source == "all":
        results = idx.unified_search(query, top_k=top_k)
    elif source in idx.stores:
        results = idx.stores[source].search(query, top_k=top_k)
    else:
        return jsonify({"success": False, "error": f"unknown source: {source}"}), 400

    return jsonify({
        "success": True,
        "query": query,
        "source": source,
        "total": len(results),
        "results": results,
    })


@search_bp.route("/semantic", methods=["GET"])
def semantic_search_get():
    """GET /api/search/semantic?q=...&top_k=8&source=all"""
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"success": False, "error": "q parameter is required"}), 400

    top_k = min(int(request.args.get("top_k", 8)), 20)
    source = request.args.get("source", "all")

    idx = _ensure_index()

    if source == "all":
        results = idx.unified_search(q, top_k=top_k)
    elif source in idx.stores:
        results = idx.stores[source].search(q, top_k=top_k)
    else:
        return jsonify({"success": False, "error": f"unknown source: {source}"}), 400

    return jsonify({
        "success": True,
        "query": q,
        "source": source,
        "total": len(results),
        "results": results,
    })


@search_bp.route("/rebuild", methods=["POST"])
def rebuild_index():
    """Force rebuild all search indexes."""
    global _indexer
    _indexer = KnowledgeIndexer()
    stores = _indexer.build_all()
    stats = {name: store.stats() for name, store in stores.items()}
    return jsonify({
        "success": True,
        "message": "Index rebuilt",
        "stats": stats,
    })


@search_bp.route("/stats", methods=["GET"])
def search_stats():
    """Get index statistics."""
    idx = _ensure_index()
    stats = {name: store.stats() for name, store in idx.stores.items()}
    return jsonify({"success": True, "stats": stats})
