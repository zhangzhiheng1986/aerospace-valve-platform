"""
Valve Modules Blueprint: pressure reducing valve, check valve,
spring design, O-ring design, seal design, QJ20156, metrics,
CFD, thermal, structural.
"""

from flask import Blueprint, request, render_template, jsonify
from app.utils.clean import prepare_json
from app.utils.response import error_response

valve_bp = Blueprint('valve_modules', __name__)


# ==================== Page Routes ====================
@valve_bp.route('/pressure_valve')
def pressure_valve_page():
    return render_template('pressure_valve.html')

@valve_bp.route('/check_valve')
def check_valve_page():
    return render_template('check_valve.html')

@valve_bp.route('/spring_design')
@valve_bp.route('/spring')  # alias for backward compat
def spring_page():
    return render_template('spring_design.html')

@valve_bp.route('/oring_design')
@valve_bp.route('/oring')  # alias for backward compat
def oring_page():
    return render_template('oring_design.html')

@valve_bp.route('/seal_design')
@valve_bp.route('/seal')  # alias for backward compat
def seal_page():
    return render_template('seal_design.html')

@valve_bp.route('/qj20156')
def qj20156_page():
    return render_template('qj20156.html')

@valve_bp.route('/valve_metrics')
@valve_bp.route('/metrics')  # alias
def metrics_page():
    return render_template('valve_metrics.html')


# ==================== Pressure Reducing Valve ====================
@valve_bp.route('/api/pressure_valve/fluids')
def pressure_valve_fluids():
    from pressure_reducing_valve import FluidDatabase
    return jsonify(prepare_json(FluidDatabase.get_all_fluids()))

@valve_bp.route('/api/pressure_valve/materials')
def pressure_valve_materials():
    from pressure_reducing_valve import MaterialDatabase
    return jsonify(prepare_json(MaterialDatabase.get_all_materials()))

@valve_bp.route('/api/pressure_valve/presets')
def pressure_valve_presets():
    from pressure_reducing_valve import FluidDatabase, MaterialDatabase
    return jsonify(prepare_json({
        'fluids': FluidDatabase.get_all_fluids(),
        'materials': MaterialDatabase.get_all_materials()
    }))

@valve_bp.route('/api/pressure_valve/design', methods=['POST'])
def pressure_valve_design():
    from pressure_reducing_valve import run_design
    from app.utils.clean import prepare_json as pj
    data = request.get_json() or {}
    return jsonify(prepare_json(run_design(data)))


# ==================== Check Valve ====================
@valve_bp.route('/api/check_valve/presets')
def check_valve_presets():
    import check_valve
    return jsonify(prepare_json({
        'presets': getattr(check_valve, 'PRESET_DESIGNS', [])
    }))

@valve_bp.route('/api/check_valve/design', methods=['POST'])
def check_valve_design():
    import check_valve
    data = request.get_json() or {}
    result = check_valve.run_check_valve_design(data)
    return jsonify(prepare_json(result))


# ==================== Spring Design ====================
@valve_bp.route('/api/spring/materials', methods=['GET'])
def spring_materials():
    from spring_design import get_materials_list
    return jsonify(prepare_json(get_materials_list()))

@valve_bp.route('/api/spring/design', methods=['POST'])
def spring_design():
    from spring_design import design_spring
    data = request.get_json() or {}
    return jsonify(prepare_json(design_spring(data)))


# ==================== O-Ring Design ====================
@valve_bp.route('/api/oring/materials', methods=['GET'])
def oring_materials():
    from oring_design import get_materials_list
    return jsonify(prepare_json(get_materials_list()))

@valve_bp.route('/api/oring/cs_options', methods=['GET'])
def oring_cs_options():
    from oring_design import get_cs_options
    return jsonify(prepare_json(get_cs_options()))

@valve_bp.route('/api/oring/design', methods=['POST'])
def oring_design():
    from oring_design import design_oring
    data = request.get_json() or {}
    return jsonify(prepare_json(design_oring(data)))

@valve_bp.route('/api/oring/diameter-range', methods=['GET'])
def oring_diameter_range():
    from oring_design import get_diameter_range
    is_bore = request.args.get('is_bore_seal', 'true').lower() == 'true'
    cs = request.args.get('cs_preferred_mm', type=float)
    return jsonify(prepare_json(get_diameter_range(is_bore, cs)))


# ==================== Seal Design ====================
@valve_bp.route('/api/seal/catalog')
def seal_catalog():
    import seal_design
    return jsonify(prepare_json(seal_design.get_catalog()))

@valve_bp.route('/api/seal/materials')
def seal_materials():
    from seal_design import MATERIALS
    return jsonify(prepare_json(MATERIALS))

@valve_bp.route('/api/seal/presets')
def seal_presets():
    from seal_design import PRESETS
    return jsonify(prepare_json(PRESETS))

@valve_bp.route('/api/seal/design', methods=['POST'])
def seal_design():
    from seal_design import calculate_seal_design
    data = request.get_json() or {}
    return jsonify(prepare_json(calculate_seal_design(data)))


# ==================== QJ 20156-2012 Standard ====================
@valve_bp.route('/api/qj20156/info')
def qj20156_info():
    from qj20156_module import get_standard_info
    return jsonify(prepare_json(get_standard_info()))

@valve_bp.route('/api/qj20156/design', methods=['POST'])
def qj20156_design_api():
    from qj20156_module import design_assistant
    data = request.get_json() or {}
    return jsonify(prepare_json(design_assistant(data)))

@valve_bp.route('/api/qj20156/thermal_vacuum', methods=['POST'])
def qj20156_thermal_vacuum():
    from qj20156_module import generate_thermal_vacuum_profile
    data = request.get_json() or {}
    return jsonify(prepare_json(generate_thermal_vacuum_profile(data)))

@valve_bp.route('/api/qj20156/thermal_cycle', methods=['POST'])
def qj20156_thermal_cycle():
    from qj20156_module import generate_thermal_cycle_profile
    data = request.get_json() or {}
    return jsonify(prepare_json(generate_thermal_cycle_profile(data)))

@valve_bp.route('/api/qj20156/verify_leak', methods=['POST'])
def qj20156_verify_leak():
    from qj20156_module import verify_leak_rate
    data = request.get_json() or {}
    return jsonify(prepare_json(verify_leak_rate(
        data.get('measured_leak', 0),
        data.get('leak_type', 'internal')
    )))

@valve_bp.route('/api/qj20156/verify_rated', methods=['POST'])
def qj20156_verify_rated():
    from qj20156_module import verify_rated_output_pressure
    data = request.get_json() or {}
    return jsonify(prepare_json(verify_rated_output_pressure(
        data.get('rated', 0),
        data.get('measured', 0)
    )))

@valve_bp.route('/api/qj20156/verify_lockup', methods=['POST'])
def qj20156_verify_lockup():
    from qj20156_module import verify_lockup_pressure
    data = request.get_json() or {}
    return jsonify(prepare_json(verify_lockup_pressure(
        data.get('rated_pressure', 0),
        data.get('lockup_pressure', 0)
    )))

@valve_bp.route('/api/qj20156/proof_burst', methods=['POST'])
def qj20156_proof_burst():
    from qj20156_module import calc_proof_pressure, calc_burst_pressure, calc_safety_margin
    data = request.get_json() or {}
    p = data.get('max_working_pressure_MPa', 5)
    proof = calc_proof_pressure(p)
    burst = calc_burst_pressure(p)
    safety = calc_safety_margin({
        'burst_pressure_MPa': p * 2.0,
        'proof_pressure_MPa': p * 1.5,
        'max_working_pressure_MPa': p
    })
    return jsonify(prepare_json({'proof': proof, 'burst': burst, 'safety': safety}))

@valve_bp.route('/api/qj20156/verify_life', methods=['POST'])
def qj20156_verify_life():
    from qj20156_module import verify_life_cycles
    data = request.get_json() or {}
    return jsonify(prepare_json(verify_life_cycles(data.get('cycles', 0))))

@valve_bp.route('/api/qj20156/elastic_element', methods=['POST'])
def qj20156_elastic_element():
    from qj20156_module import calc_elastic_element_overload
    data = request.get_json() or {}
    return jsonify(prepare_json(calc_elastic_element_overload(data.get('working_pressure', 5))))


# ==================== Valve Metrics ====================
@valve_bp.route('/api/metrics/stats')
def metrics_stats():
    from valve_metrics import get_stats
    return jsonify(prepare_json(get_stats()))

@valve_bp.route('/api/metrics/valve_types')
def metrics_valve_types():
    from valve_metrics import get_all_valve_types
    return jsonify(prepare_json(get_all_valve_types()))

@valve_bp.route('/api/metrics/domains')
def metrics_domains():
    from valve_metrics import get_all_domains
    return jsonify(prepare_json(get_all_domains()))

@valve_bp.route('/api/metrics/standards')
def metrics_standards():
    from valve_metrics import get_all_standards
    return jsonify(prepare_json(get_all_standards()))

@valve_bp.route('/api/metrics/leakage_classes')
def metrics_leakage():
    from valve_metrics import get_leakage_classes
    return jsonify(prepare_json(get_leakage_classes()))

@valve_bp.route('/api/metrics/search')
def metrics_search():
    from valve_metrics import search_metrics
    q = request.args.get('q', '')
    return jsonify(prepare_json(search_metrics(q)))

@valve_bp.route('/api/metrics/list')
@valve_bp.route('/api/metrics/all')
def metrics_list():
    from valve_metrics import get_all_metrics, get_metrics_by_category
    cat = request.args.get('category', '')
    if cat:
        return jsonify(prepare_json(get_metrics_by_category(cat)))
    return jsonify(prepare_json(get_all_metrics()))


# ==================== Simulation Tools ====================
@valve_bp.route('/api/cfd/analyze', methods=['POST'])
def cfd_analyze():
    from cfd_analyzer import run_cfd_analysis
    data = request.get_json() or {}
    result = run_cfd_analysis(
        fluid_name=data.get('fluid', 'water_20C'),
        geometry_params=data.get('geometry', {}),
        inlet_pressure=data.get('inlet_pressure', 500000),
        outlet_pressure=data.get('outlet_pressure', 100000),
        opening_ratio=data.get('opening_ratio', 1.0)
    )
    return jsonify(prepare_json(result))

@valve_bp.route('/api/thermal/analyze', methods=['POST'])
def thermal_analyze():
    from thermal_analyzer import run_thermal_analysis
    data = request.get_json() or {}
    result = run_thermal_analysis(
        material_name=data.get('material', 'copper'),
        component_params=data.get('component', {}),
        operating_conditions=data.get('conditions', {})
    )
    return jsonify(prepare_json(result))

@valve_bp.route('/api/structural/analyze', methods=['POST'])
def structural_analyze():
    from structural_analyzer import run_structural_analysis
    data = request.get_json() or {}
    result = run_structural_analysis(
        material_name=data.get('material', 'steel_304'),
        geometry=data.get('geometry', {}),
        loads=data.get('loads', {})
    )
    return jsonify(prepare_json(result))


# Solenoid optimizer lives in its own blueprint: app/blueprints/solenoid.py
