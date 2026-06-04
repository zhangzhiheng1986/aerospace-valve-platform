"""
Fluid Mechanics Super Calculator Blueprint
122 formulas across 12 categories with Chinese/English i18n.
"""

from flask import Blueprint, request, render_template, jsonify
from app.utils.clean import prepare_json

fm_bp = Blueprint('fluid_mechanics', __name__)


@fm_bp.route('/fluid_mechanics')
def fluid_mechanics_page():
    return render_template('fluid_mechanics.html')


@fm_bp.route('/api/fluid_mechanics/formulas')
def get_formula_catalog():
    """Return full 12-category formula catalog (EN names only)."""
    from fluid_mechanics_calc import get_all_formulas
    return jsonify(prepare_json(get_all_formulas()))


@fm_bp.route('/api/fluid_mechanics/i18n')
def get_i18n():
    """Return complete Chinese internationalization metadata."""
    try:
        from fluid_mechanics_i18n import FORMULA_I18N, CATEGORY_I18N, FLUID_I18N, PIPE_ROUGHNESS_I18N
        return jsonify(prepare_json({
            'formulas': FORMULA_I18N,
            'categories': CATEGORY_I18N,
            'fluids': FLUID_I18N,
            'pipe_roughness': PIPE_ROUGHNESS_I18N
        }))
    except ImportError:
        return jsonify({'formulas': {}, 'categories': {}, 'fluids': {}, 'pipe_roughness': {}})


@fm_bp.route('/api/fluid_mechanics/fluids')
def get_fluids():
    """Return 14 aerospace fluid properties database."""
    from fluid_mechanics_calc import FLUID_PROPERTIES
    return jsonify(prepare_json(FLUID_PROPERTIES))


@fm_bp.route('/api/fluid_mechanics/pipe_roughness')
def get_pipe_roughness():
    """Return pipe roughness values."""
    from fluid_mechanics_calc import PIPE_ROUGHNESS
    return jsonify(prepare_json(PIPE_ROUGHNESS))


@fm_bp.route('/api/fluid_mechanics/compute', methods=['POST'])
def compute_formula():
    """Compute a formula by ID with given inputs."""
    from fluid_mechanics_calc import compute_formula as cm
    data = request.get_json() or {}
    formula_id = data.get('formula_id', '')
    inputs = data.get('inputs', {})
    return jsonify(prepare_json(cm(formula_id, inputs)))


@fm_bp.route('/api/fluid_mechanics/search-index')
def get_search_index():
    """Return compact search index for frontend fuzzy matching."""
    try:
        from fluid_mechanics_i18n import FORMULA_I18N
    except ImportError:
        return jsonify(prepare_json([]))
    index = []
    for fid, fv in sorted(FORMULA_I18N.items()):
        index.append({
            'id': fid,
            'name_zh': fv.get('name_zh', ''),
            'name_en': fv.get('name_en', ''),
            'category': fv.get('category', ''),
            'keywords': fv.get('keywords', fv.get('name_zh', '')),
        })
    return jsonify(prepare_json(index))


@fm_bp.route('/api/fluid_mechanics/defaults')
def get_default_inputs():
    """Return default inputs for all formulas."""
    from fluid_mechanics_calc import DEFAULT_INPUTS
    return jsonify(prepare_json(DEFAULT_INPUTS))


@fm_bp.route('/api/fluid_mechanics/unit-systems')
def get_unit_systems():
    """Return all unit system definitions and conversion tables."""
    from unit_converter import UNIT_SYSTEMS, UNIT_CONVERSIONS, UNIT_LABELS, PARAM_UNIT_MAP
    return jsonify(prepare_json({
        'systems': UNIT_SYSTEMS,
        'conversions': UNIT_CONVERSIONS,
        'labels': UNIT_LABELS,
        'param_map': PARAM_UNIT_MAP,
    }))
