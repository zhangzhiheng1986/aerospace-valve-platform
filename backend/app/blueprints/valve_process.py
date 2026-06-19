"""
Valve Process Blueprint: manufacturing process library (machining/HT/surface/welding/assembly).
"""

from flask import Blueprint, request, render_template, jsonify
from app.utils.clean import prepare_json

valve_process_bp = Blueprint('valve_process', __name__)


@valve_process_bp.route('/valve-process')
def valve_process_page():
    return render_template('valve_process.html')


@valve_process_bp.route('/api/valve-process/catalog', methods=['GET'])
def catalog():
    from valve_process import get_process_catalog
    return jsonify(prepare_json(get_process_catalog()))


@valve_process_bp.route('/api/valve-process/detail', methods=['POST'])
def detail():
    from valve_process import get_process_detail
    data = request.get_json() or {}
    process_id = data.get('process_id', '')
    result = get_process_detail(process_id)
    if result is None:
        return jsonify(prepare_json({'error': 'process_not_found', 'id': process_id})), 404
    return jsonify(prepare_json(result))


@valve_process_bp.route('/api/valve-process/search', methods=['POST'])
def search():
    from valve_process import search_processes
    data = request.get_json() or {}
    results = search_processes(
        keyword=data.get('keyword', ''),
        category=data.get('category', ''),
    )
    return jsonify(prepare_json({'results': results, 'count': len(results)}))


@valve_process_bp.route('/api/valve-process/routes', methods=['GET'])
def routes_list():
    from valve_process import list_process_routes
    return jsonify(prepare_json({'routes': list_process_routes()}))


@valve_process_bp.route('/api/valve-process/route', methods=['POST'])
def route_detail():
    from valve_process import get_process_route
    data = request.get_json() or {}
    route_id = data.get('route_id', '')
    result = get_process_route(route_id)
    if result is None:
        return jsonify(prepare_json({'error': 'route_not_found', 'id': route_id})), 404
    return jsonify(prepare_json(result))


@valve_process_bp.route('/api/valve-process/recommend', methods=['POST'])
def recommend():
    from valve_process import recommend_process_route
    data = request.get_json() or {}
    material = data.get('material', '')
    valve_type = data.get('valve_type', '')
    result = recommend_process_route(material, valve_type)
    return jsonify(prepare_json(result))


@valve_process_bp.route('/api/valve-process/pdf/process', methods=['POST'])
def pdf_process():
    from process_pdf_export import export_process_pdf
    from flask import send_file
    data = request.get_json() or {}
    process_id = data.get('process_id', '')
    buf, filename = export_process_pdf(process_id)
    if buf is None:
        return jsonify(prepare_json({'error': 'process_not_found', 'id': process_id})), 404
    return send_file(buf, mimetype='application/pdf', as_attachment=True,
                     download_name=filename)


@valve_process_bp.route('/api/valve-process/pdf/route', methods=['POST'])
def pdf_route():
    from process_pdf_export import export_route_pdf
    from flask import send_file
    data = request.get_json() or {}
    route_id = data.get('route_id', '')
    buf, filename = export_route_pdf(route_id)
    if buf is None:
        return jsonify(prepare_json({'error': 'route_not_found', 'id': route_id})), 404
    return send_file(buf, mimetype='application/pdf', as_attachment=True,
                     download_name=filename)
