"""
Materials Blueprint: aerospace materials database (21 materials, 7 categories).
"""

from flask import Blueprint, request, render_template, jsonify
from app.utils.clean import prepare_json

materials_bp = Blueprint('materials', __name__)


@materials_bp.route('/materials')
def materials_page():
    return render_template('materials.html')


@materials_bp.route('/api/materials/statistics')
def statistics():
    from materials_database import db as mdb
    return jsonify(prepare_json(mdb.get_statistics()))


@materials_bp.route('/api/materials/list')
def list_materials():
    from materials_database import get_all_materials
    return jsonify(prepare_json(get_all_materials()))


@materials_bp.route('/api/materials/detail')
def detail():
    material_id = request.args.get('id', '')
    from materials_database import get_material_detail
    if not material_id:
        return jsonify({'error': 'Missing material id'}), 400
    result = get_material_detail(material_id)
    if result:
        return jsonify(prepare_json(result))
    return jsonify({'error': 'Material not found'}), 404


@materials_bp.route('/api/materials/search')
def search():
    q = request.args.get('q', '')
    category = request.args.get('category', '') or None
    from materials_database import search_materials
    if q:
        results = search_materials(category=category)
        results = [m for m in results if q.lower() in m.get('name','').lower()
                   or q.lower() in m.get('standard','').lower()]
        return jsonify(prepare_json(results))
    return jsonify(prepare_json(search_materials(category=category)))


@materials_bp.route('/api/materials/recommend', methods=['POST'])
def recommend():
    data = request.get_json() or {}
    from materials_database import db as mdb
    app = data.get('application', 'general')
    reqs = {k: v for k, v in data.items() if k != 'application'}
    return jsonify(prepare_json(mdb.recommend_material(application=app, requirements=reqs)))


@materials_bp.route('/api/materials/calculate-wire', methods=['POST'])
def calculate_wire():
    data = request.get_json() or {}
    from materials_database import db as mdb
    return jsonify(prepare_json(mdb.calculate_wire_properties(
        material_name=data.get('material', 'copper'),
        awg=data.get('awg', 24),
        turns=data.get('turns', 100),
        mean_diameter=data.get('mean_diameter', 20.0)
    )))


@materials_bp.route('/api/materials/awg/<int:awg>')
def awg_detail(awg):
    from materials_database import db as mdb
    return jsonify(prepare_json(mdb.get_awg(awg)))