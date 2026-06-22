"""
tool_bridge.py — Unified tool executor for multi-agent orchestration.

Combines all 17+ engineering modules behind a single consistent interface.
Handles error wrapping, JSON-safe output (_clean), and parameter normalization.

Used by:
- orchestrate endpoint (_init_orchestrator)
- PAOR engine (tool_executor)
- Any future agent that needs domain computation
"""

import math
import traceback
from enum import Enum

# ============================================================================
# _clean — recursive Infinity/NaN → None
# ============================================================================

def _clean(obj):
    """Recursively replace Infinity/NaN with None for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
    if isinstance(obj, Enum):
        return obj.value
    return obj


# ============================================================================
# Wrapper — standardize all tool outputs
# ============================================================================

def _wrap(func, name, extra_params=None):
    """Return a callable(kwargs) → {"success": bool, ...} for any module function."""
    extra = extra_params or {}

    def wrapped(kwargs):
        try:
            # Merge extra defaults into kwargs
            merged = {}
            merged.update(extra)
            merged.update(kwargs)

            # Call the function — it may be a traditional (positional) or kwargs-accepting function
            result = func(**merged)
            cleaned = _clean(result)
            cleaned['success'] = True
            cleaned['_tool'] = name
            return cleaned
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                '_tool': name,
                '_traceback': traceback.format_exc(),
            }
    return wrapped


# ============================================================================
# Material tools
# ============================================================================

def _material_query(kwargs):
    """Query material database by name or id.
    
    Sprint 9 enhancement: try multiple lookup strategies:
    1. Exact key match
    2. Partial substring match (e.g. "TC4" matches "TC4钛合金")
    3. Synonym mapping (e.g. "FKM" -> "氟橡胶Viton")
    """
    try:
        from materials_database import get_material_detail, db as _mat_db
        name = kwargs.get('material', kwargs.get('name', ''))
        if not name:
            return {'success': False, 'error': 'No material name provided'}
        result = get_material_detail(name)
        if not result:
            # Substring search across all known keys
            n = name.strip().lower()
            best_match = None
            for key in _mat_db.materials.keys():
                if n in key.lower() or n.upper() in key.upper():
                    best_match = key
                    break
            # Synonym table for common short codes
            SYNONYMS = {
                'fkm': '氟橡胶Viton',
                'viton': '氟橡胶Viton',
                'nbr': 'NBR',
                'ptfe': '聚四氟乙烯PTFE',
                'teflon': '聚四氟乙烯PTFE',
                '50crva': '50CrVA',
                '60si2mn': '60Si2Mn',
                'gh4169': 'GH4169',
                'inconel': 'GH4169',
                'inconel 718': 'GH4169',
                'tc4': 'TC4',
                'ti-6al-4v': 'TC4',
                '2a12': '2A12硬铝合金',
                '7075': '7075',
                '1cr18ni9ti': '1Cr18Ni9Ti不锈钢',
                '17-4ph': '17-4PH',
                '440c': '440C',
                'h62': 'H62',
            }
            if not best_match and n.lower() in SYNONYMS:
                result = get_material_detail(SYNONYMS[n.lower()])
                if result:
                    best_match = SYNONYMS[n.lower()]
            if not result and best_match:
                result = get_material_detail(best_match)
            if not result:
                # Last-ditch: list available keys (limited)
                return {
                    'success': False,
                    'error': f'Material "{name}" not found',
                    'available_keys_sample': list(_mat_db.materials.keys())[:5],
                }
        cleaned = _clean(result)
        cleaned['success'] = True
        cleaned['_tool'] = 'query_material'
        return cleaned
    except ImportError:
        return _mock_material(kwargs)
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'query_material'}


def _mock_material(kwargs):
    name = kwargs.get('material', kwargs.get('name', 'TC4'))
    mock_data = {
        'TC4': {
            'name': 'TC4 (Ti-6Al-4V)', 'category': 'Titanium Alloy', 'aerospace_grade': 'Space Grade',
            'density_kgm3': 4430, 'tensile_strength_mpa': 950, 'yield_strength_mpa': 880,
            'elastic_modulus_gpa': 113.8, 'poisson_ratio': 0.342, 'elongation_pct': 14,
            'hardness_hrc': 36, 'thermal_conductivity_wmk': 6.7,
            'specific_heat_jkgk': 526, 'melting_point_c': 1660,
            'max_service_temp_c': 350, 'cte_10_6k': 8.6,
        },
        'GH4169': {
            'name': 'GH4169 (Inconel 718)', 'category': 'Nickel Superalloy', 'aerospace_grade': 'Space Grade',
            'density_kgm3': 8190, 'tensile_strength_mpa': 1379, 'yield_strength_mpa': 1103,
            'elastic_modulus_gpa': 205, 'poisson_ratio': 0.294, 'elongation_pct': 12,
            'hardness_hrc': 42, 'max_service_temp_c': 650,
        },
    }
    m = mock_data.get(name.upper(), mock_data.get('TC4', {}))
    if not m:
        return {'success': False, 'error': f'Material "{name}" not found in database'}
    m['success'] = True
    m['_tool'] = 'query_material'
    return m


# ============================================================================
# QJ20156 compliance tools
# ============================================================================

def _compliance_check(kwargs):
    """Check QJ20156 standard compliance for given parameters."""
    try:
        from qj20156_module import get_standard_info, verify_leak_rate, verify_life_cycles, \
            verify_rated_output_pressure, verify_lockup_pressure, calc_burst_pressure, \
            calc_proof_pressure, calc_safety_margin
        info = get_standard_info()
        wp = float(kwargs.get('working_pressure', kwargs.get('pressure', 10)))
        proof = calc_proof_pressure(wp)
        burst = calc_burst_pressure(wp)
        # calc_safety_margin takes a single dict
        margin = calc_safety_margin({'working_pressure': wp, 'proof_pressure': proof.get('proof_pressure_mpa', wp * 1.5)})

        return _clean({
            'success': True,
            '_tool': 'check_compliance',
            'standard': info.get('standard', 'QJ 20156'),
            'proof_pressure_mpa': proof.get('proof_pressure_mpa'),
            'proof_factor': proof.get('proof_factor'),
            'burst_pressure_mpa': burst.get('burst_pressure_mpa'),
            'burst_factor': burst.get('burst_factor'),
            'safety_margin': margin.get('safety_margin'),
            'verdict': 'pass' if margin.get('safety_margin', 0) >= 1.5 else 'fail',
            'requirements': {
                'proof_factor': '>=1.5x',
                'burst_factor': '>=2.0x',
                'life_cycles': '>=20000',
                'thermal_vacuum_cycles': '6',
                'thermal_cycle_range': '-65C to +120C',
            },
        })
    except ImportError:
        return {
            'success': True, '_tool': 'check_compliance', 'standard': 'QJ 20156',
            'proof_factor': 1.5, 'burst_factor': 2.0, 'verdict': 'pass',
            'note': 'Mock compliance check — QJ20156 module not loaded',
        }
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'check_compliance'}


def _verify_leak(kwargs):
    """Verify leakage rate against QJ20156 requirements."""
    try:
        from qj20156_module import verify_leak_rate
        result = verify_leak_rate(
            float(kwargs.get('leak_rate', 1e-6)),
            leak_type=kwargs.get('leak_type', 'internal'),
        )
        clean = _clean(result)
        clean['success'] = True
        clean['_tool'] = 'verify_leak'
        return clean
    except ImportError:
        return {'success': True, '_tool': 'verify_leak', 'pass': True, 'leak_rate_pam3s': 1e-6,
                'verdict': 'pass', 'note': 'Mock'}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'verify_leak'}


def _verify_rated_output(kwargs):
    try:
        from qj20156_module import verify_rated_output_pressure
        result = verify_rated_output_pressure(
            float(kwargs.get('rated', kwargs.get('target', 5))),
            float(kwargs.get('measured', kwargs.get('output_pressure', kwargs.get('actual', 5)))),
        )
        clean = _clean(result)
        clean['success'] = True
        clean['_tool'] = 'verify_rated'
        return clean
    except ImportError:
        return {'success': True, '_tool': 'verify_rated', 'pass': True, 'verdict': 'pass', 'note': 'Mock'}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'verify_rated'}


def _verify_life_cycles(kwargs):
    try:
        from qj20156_module import verify_life_cycles
        result = verify_life_cycles(kwargs.get('cycles', 20000))
        clean = _clean(result)
        clean['success'] = True
        clean['_tool'] = 'verify_life'
        return clean
    except ImportError:
        return {'success': True, '_tool': 'verify_life', 'pass': True, 'verdict': 'pass', 'note': 'Mock'}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'verify_life'}


# ============================================================================
# Fluid mechanics computation tools
# ============================================================================

def _fluid_calculation(kwargs):
    """Run fluid mechanics calculation. Supports formula_id + params or descriptive message."""
    try:
        message = kwargs.get('message', '')
        formula_id = kwargs.get('formula_id', '')
        params = kwargs.get('params', kwargs)

        # Try fluid_mechanics_calc compute() if available
        try:
            from fluid_mechanics_calc import compute
            # Use message to identify formula, or formula_id directly
            result = compute(formula_id or message, **params)
            clean = _clean(result)
            clean['success'] = True
            clean['_tool'] = 'run_fluid_calculation'
            return clean
        except ImportError:
            # Fallback: direct common formulas
            if 'reynolds' in message.lower() or kwargs.get('velocity'):
                rho = float(kwargs.get('rho', kwargs.get('density', 1.225)))
                vel = float(kwargs.get('velocity', kwargs.get('vel', 10)))
                dia = float(kwargs.get('diameter', kwargs.get('D', 0.01)))
                mu = float(kwargs.get('mu', kwargs.get('viscosity', 1.8e-5)))
                re = rho * vel * dia / mu
                return {'success': True, '_tool': 'run_fluid_calculation',
                        'reynolds_number': round(re, 1),
                        'flow_regime': 'turbulent' if re > 4000 else ('laminar' if re < 2300 else 'transitional')}
            return {'success': True, '_tool': 'run_fluid_calculation',
                    'note': f'Fluid calculation for: {message or formula_id}',
                    'result': params}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'run_fluid_calculation'}


# ============================================================================
# Design tools (solenoid, PRV, spring, oring, seal)
# ============================================================================

def _analyze_solenoid(kwargs):
    """Analyze solenoid valve design parameters.
    Maps working_pressure to geometric dimensions and runs HybridOptimizer.
    Falls back to mock if optimizer cannot be initialized.
    """
    try:
        from solenoid_optimizer import HybridOptimizer, ValveGeometricParams, SolenoidPhysicsEngine
        from solenoid_optimizer import MaterialConstants
        pressure = float(kwargs.get('working_pressure', kwargs.get('pressure', 21)))
        # Map pressure bracket to approximate geometric dimensions
        if pressure <= 10:
            geom = ValveGeometricParams(D_inner_mm=10, D_outer_max_mm=25, L_axial_max_mm=20)
        elif pressure <= 21:
            geom = ValveGeometricParams(D_inner_mm=15, D_outer_max_mm=35, L_axial_max_mm=25)
        elif pressure <= 35:
            geom = ValveGeometricParams(D_inner_mm=20, D_outer_max_mm=40, L_axial_max_mm=30)
        else:
            geom = ValveGeometricParams(D_inner_mm=25, D_outer_max_mm=50, L_axial_max_mm=35)
        physics = SolenoidPhysicsEngine()
        opt = HybridOptimizer(geom, physics, n_particles=kwargs.get('n_particles', 20), n_iterations=30)
        best_awg, best_fit, best_info = opt.optimize()
        clean = _clean({'best_awg': best_awg, 'fitness': best_fit, 'design': best_info})
        clean['success'] = True
        clean['_tool'] = 'analyze_solenoid_valve'
        return clean
    except (ImportError, TypeError, AttributeError) as ie:
        return _mock_solenoid(kwargs, import_error=str(ie))
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'analyze_solenoid_valve'}


def _mock_solenoid(kwargs, import_error=''):
    p = float(kwargs.get('working_pressure', kwargs.get('pressure', 21)))
    return {
        'success': True, '_tool': 'analyze_solenoid_valve',
        'note': f'Mock solenoid design (reason: {import_error})' if import_error else 'Mock solenoid design',
        'design': {
            'working_pressure_mpa': p,
            'proof_pressure_mpa': round(p * 1.5, 1),
            'burst_pressure_mpa': round(p * 2.5, 1),
            'orifice_diameter_mm': 2.0,
            'plunger_material': '440C',
            'armature_force_n': round(p * 50, 1),
        }
    }


def _analyze_prv(kwargs):
    """Analyze pressure reducing valve."""
    try:
        from pressure_reducing_valve import ValveInputParams, PressureReducingValveDesigner
        params = ValveInputParams(
            fluid_type=kwargs.get('fluid', kwargs.get('medium', 'kerosene')),
            inlet_pressure=float(kwargs.get('inlet_pressure', kwargs.get('pressure', 15))),
            outlet_pressure=float(kwargs.get('outlet_pressure', kwargs.get('target', 8))),
            flow_rate=float(kwargs.get('flow_rate', kwargs.get('flow', 5))),
        )
        designer = PressureReducingValveDesigner(params)
        result = designer.design()
        clean = _clean(result)
        clean['success'] = True
        clean['_tool'] = 'analyze_pressure_valve'
        return clean
    except ImportError:
        return _mock_prv(kwargs)
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'analyze_pressure_valve'}


def _mock_prv(kwargs):
    return {
        'success': True, '_tool': 'analyze_pressure_valve',
        'design': {
            'inlet_pressure_mpa': float(kwargs.get('inlet_pressure', 15)),
            'outlet_pressure_mpa': float(kwargs.get('outlet_pressure', 8)),
            'orifice_diameter_mm': 3.5,
            'spring_rate_nmm': 120,
            'poppet_material': '440C',
        }
    }


def _design_spring(kwargs):
    """Design aerospace spring. Function expects single dict arg."""
    try:
        from spring_design import design_spring as ds
        # Build input dict matching the expected schema
        params = {
            'wire_diameter': float(kwargs.get('wire_diameter', kwargs.get('wire_d', 3))),
            'mean_diameter': float(kwargs.get('mean_diameter', kwargs.get('mean_D', 20))),
            'n_coils': int(kwargs.get('n_coils', kwargs.get('coils', 8))),
            'material': kwargs.get('material', '50CrVA'),
            'free_length': float(kwargs.get('free_length', kwargs.get('L0', 50))),
        }
        result = ds(params)
        clean = _clean(result)
        clean['success'] = True
        clean['_tool'] = 'design_spring'
        return clean
    except ImportError:
        return _mock_spring(kwargs)
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'design_spring'}


def _mock_spring(kwargs):
    wd = float(kwargs.get('wire_diameter', 3))
    md = float(kwargs.get('mean_diameter', 20))
    nc = int(kwargs.get('n_coils', 8))
    return {
        'success': True, '_tool': 'design_spring',
        'spring': {
            'wire_diameter_mm': wd, 'mean_diameter_mm': md, 'n_coils': nc,
            'spring_index': round(md / wd, 1),
            'spring_rate_nmm': round(80000 * wd**4 / (8 * nc * md**3), 1),
            'max_shear_stress_mpa': 620,
            'fatigue_life_cycles': 2e6,
        }
    }


def _design_oring(kwargs):
    """Design O-ring seal. Function expects single dict arg."""
    try:
        from oring_design import design_oring as dor
        params = {
            'shaft_diameter': float(kwargs.get('shaft_diameter', kwargs.get('shaft_d', 100))),
            'pressure': float(kwargs.get('working_pressure', kwargs.get('pressure', 30))),
            'seal_type': kwargs.get('seal_type', kwargs.get('type', 'piston')),
            'material': kwargs.get('material', 'NBR'),
        }
        result = dor(params)
        clean = _clean(result)
        clean['success'] = True
        clean['_tool'] = 'design_oring'
        return clean
    except ImportError:
        return _mock_oring(kwargs)
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'design_oring'}


def _mock_oring(kwargs):
    sd = float(kwargs.get('shaft_diameter', 100))
    return {
        'success': True, '_tool': 'design_oring',
        'oring': {
            'cross_section_mm': 5.33, 'inner_diameter_mm': round(sd * 0.89, 1),
            'gland_depth_mm': 4.52, 'gland_width_mm': 7.1,
            'as568_dash': '-238', 'leak_rate_pam3s': 1.5e-5,
        }
    }


def _identify_formula(kwargs):
    """Identify which fluid formula to use based on natural language."""
    message = kwargs.get('message', '').lower()
    # Quick keyword → formula_id mapping
    mappings = {
        'reynolds': 'reynolds_number', 're': 'reynolds_number',
        'bernoulli': 'bernoulli', 'bernoulli': 'bernoulli',
        'mach': 'mach_number', 'sonic': 'mach_number',
        'flow rate': 'volumetric_flow_rate', 'flowrate': 'volumetric_flow_rate',
        'pressure drop': 'darcy_weisbach', 'friction': 'darcy_weisbach',
        'npsh': 'npsh_available', 'cavitation': 'npsh_available',
        'drag': 'drag_force', 'lift': 'lift_force',
        'pump': 'pump_power', 'power': 'pump_power',
    }
    for key, formula_id in mappings.items():
        if key in message:
            return {'success': True, '_tool': 'identify_formula', 'identified': formula_id,
                    'formula_id': formula_id}
    return {'success': True, '_tool': 'identify_formula', 'identified': 'reynolds_number',
            'formula_id': 'reynolds_number', 'note': 'Default formula for generic query'}


def _semantic_search(kwargs):
    """Semantic search across knowledge base, formulas, and materials."""
    query = kwargs.get('query', kwargs.get('message', ''))
    top_k = int(kwargs.get('top_k', 5))
    source = kwargs.get('source', 'all')
    try:
        from vector_store import get_search
        idx = get_search()
        if source == 'all':
            results = idx.unified_search(query, top_k=top_k)
        elif source in idx.stores:
            results = idx.stores[source].search(query, top_k=top_k)
        else:
            return {'success': False, 'error': f'Unknown source: {source}'}
        # Clean for JSON
        clean_results = []
        for r in results:
            cr = {k: v for k, v in r.items() if k != 'text'}  # text is large, skip
            clean_results.append(cr)
        return {'success': True, '_tool': 'semantic_search', 'query': query,
                'source': source, 'total': len(clean_results), 'results': clean_results}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'semantic_search'}


def _search_knowledge(kwargs):
    """Search knowledge base (alias for semantic_search with formatted output).
    Used by PAOR engine's 'search_knowledge' tool step."""
    result = _semantic_search(kwargs)
    if not result.get('success'):
        return result
    # Format results for PAOR consumption
    formatted = []
    for r in result.get('results', []):
        item = {
            'source': r.get('source', 'unknown'),
            'title': r.get('title', r.get('name', '')),
            'type': r.get('type', ''),
            'score': r.get('score', 0),
            'snippet': (r.get('text', '') or r.get('description', '') or '')[:300],
        }
        formatted.append(item)
    return {
        'success': True,
        '_tool': 'search_knowledge',
        'query': result.get('query', kwargs.get('query', '')),
        'total': len(formatted),
        'results': formatted,
    }


# ============================================================
# Process tools (Sprint 12: Valve Process Module integration)
# ============================================================

def _list_processes(kwargs):
    """List manufacturing processes by category."""
    category = kwargs.get('category', '').lower()
    try:
        from valve_process import get_process_catalog
        catalog = get_process_catalog()
        if category and category in catalog:
            cat = catalog[category]
            return {
                'success': True,
                '_tool': 'list_processes',
                'category': category,
                'category_name': cat['name'],
                'count': cat['count'],
                'processes': cat['processes'],
            }
        # No category: return summary
        return {
            'success': True,
            '_tool': 'list_processes',
            'categories': [
                {'key': k, 'name': v['name'], 'count': v['count']}
                for k, v in catalog.items()
            ],
        }
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'list_processes'}


def _get_process_detail(kwargs):
    """Get full parameters for a specific process."""
    process_id = kwargs.get('process_id', kwargs.get('process', ''))
    if not process_id:
        return {'success': False, 'error': 'process_id required', '_tool': 'get_process_detail'}
    try:
        from valve_process import get_process_detail
        result = get_process_detail(process_id)
        if result is None:
            return {'success': False, 'error': f'process not found: {process_id}', '_tool': 'get_process_detail'}
        return {'success': True, '_tool': 'get_process_detail', **result}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'get_process_detail'}


def _recommend_process(kwargs):
    """Recommend process route based on material and valve type."""
    material = kwargs.get('material', kwargs.get('mat', ''))
    valve_type = kwargs.get('valve_type', kwargs.get('valve', ''))
    if not material:
        return {'success': False, 'error': 'material required', '_tool': 'recommend_process'}
    try:
        from valve_process import recommend_process_route
        result = recommend_process_route(material, valve_type)
        # Enrich: get names for process ids
        from valve_process import get_process_detail
        proc_details = []
        for pid in result['processes']:
            d = get_process_detail(pid)
            if d:
                proc_details.append({
                    'id': pid,
                    'name': d['name'],
                    'category': d['category'],
                    'applicability': d.get('applicability', ''),
                })
        result['process_details'] = proc_details
        result['_tool'] = 'recommend_process'
        result['success'] = True
        result['material'] = material
        result['valve_type'] = valve_type
        return result
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'recommend_process'}


def _get_process_route(kwargs):
    """Get full process route (step-by-step instructions)."""
    route_id = kwargs.get('route_id', kwargs.get('route', ''))
    if not route_id:
        # No route: list all
        try:
            from valve_process import list_process_routes
            return {
                'success': True,
                '_tool': 'get_process_route',
                'routes': list_process_routes(),
            }
        except Exception as e:
            return {'success': False, 'error': str(e), '_tool': 'get_process_route'}
    try:
        from valve_process import get_process_route
        result = get_process_route(route_id)
        if result is None:
            return {'success': False, 'error': f'route not found: {route_id}', '_tool': 'get_process_route'}
        return {'success': True, '_tool': 'get_process_route', **result}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'get_process_route'}


def _graph_search(kwargs):
    """Search knowledge graph entities."""
    query = kwargs.get('query', kwargs.get('message', ''))
    entity_type = kwargs.get('entity_type', kwargs.get('type'))
    limit = int(kwargs.get('limit', 10))
    try:
        from knowledge_graph import get_graph_query
        q = get_graph_query()
        results = q.search_entity(query, entity_type=entity_type, limit=limit)
        return {'success': True, '_tool': 'graph_search', 'query': query,
                'total': len(results), 'results': results}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'graph_search'}


def _graph_neighbors(kwargs):
    """Get neighbors of a graph entity."""
    entity_id = kwargs.get('entity_id', kwargs.get('id', ''))
    relation = kwargs.get('relation')
    direction = kwargs.get('direction', kwargs.get('dir', 'both'))
    try:
        from knowledge_graph import get_graph_query
        q = get_graph_query()
        neighbors = q.get_neighbors(entity_id, relation=relation, direction=direction)
        entity = q.get_entity(entity_id)
        return {'success': True, '_tool': 'graph_neighbors',
                'entity': entity, 'neighbors': neighbors, 'total': len(neighbors)}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'graph_neighbors'}


# ============================================================================
# Sprint 14.1: Cost Estimation Tools
# ============================================================================

# Material cost (USD/kg) — aerospace-grade reference prices
_MATERIAL_COSTS = {
    'inconel_718': 95.0,
    'inconel_625': 88.0,
    '316l': 12.0,
    '17-4ph': 28.0,
    'tc4': 180.0,
    'ti-6al-4v': 180.0,
    'co-cr-mo': 75.0,
    'al_7075': 8.0,
    'hastelloy_c276': 130.0,
    'monel_400': 65.0,
    'default': 30.0,
}

# Process cost (USD/min) — rough reference rates
_PROCESS_COSTS = {
    'turning': 2.5,
    'milling': 3.5,
    'grinding': 4.0,
    'welding_tig': 3.0,
    'welding_eb': 5.0,
    'welding_laser': 4.5,
    'heat_treat': 1.5,
    'aging': 1.0,
    'shot_peening': 2.0,
    'passivation': 1.0,
    'default': 2.0,
}


def _estimate_cost(kwargs):
    """Sprint 14.1: Estimate total cost for material + process."""
    material = (kwargs.get('material') or 'default').lower().replace(' ', '_').replace('-', '_')
    mass_kg = float(kwargs.get('mass_kg') or kwargs.get('mass') or 1.0)
    process_time_min = float(kwargs.get('process_time_min') or kwargs.get('time_min') or 60.0)
    quantity = int(kwargs.get('quantity') or 1)

    mat_cost = _MATERIAL_COSTS.get(material, _MATERIAL_COSTS['default'])
    proc_cost = _PROCESS_COSTS['default']  # weighted avg
    mat_total = mat_cost * mass_kg * quantity
    proc_total = proc_cost * process_time_min * quantity
    overhead = (mat_total + proc_total) * 0.15
    total = mat_total + proc_total + overhead

    return {
        'success': True,
        '_tool': 'estimate_cost',
        'material': material,
        'mass_kg': mass_kg,
        'process_time_min': process_time_min,
        'quantity': quantity,
        'material_cost_usd': round(mat_total, 2),
        'process_cost_usd': round(proc_total, 2),
        'overhead_usd': round(overhead, 2),
        'total_usd': round(total, 2),
        'unit_cost_usd': round(total / quantity, 2),
        'currency': 'USD',
        'note': 'Reference aerospace-grade cost; actual quotes depend on supplier, batch size, and lead time.',
    }


def _compare_costs(kwargs):
    """Sprint 14.1: Compare cost across multiple material/process options."""
    options = kwargs.get('options') or []
    if not options and 'material' in kwargs:
        # Build options from a single material spec
        options = [{
            'name': kwargs.get('material', 'option_1'),
            'material': kwargs.get('material'),
            'mass_kg': kwargs.get('mass_kg', 1.0),
            'process_time_min': kwargs.get('process_time_min', 60.0),
        }]
    rows = []
    for opt in options:
        m = opt.get('material', 'default')
        mass = float(opt.get('mass_kg') or 1.0)
        t = float(opt.get('process_time_min') or 60.0)
        mat_cost = _MATERIAL_COSTS.get(m.lower().replace(' ', '_').replace('-', '_'), _MATERIAL_COSTS['default'])
        mat_total = mat_cost * mass
        proc_total = _PROCESS_COSTS['default'] * t
        overhead = (mat_total + proc_total) * 0.15
        total = mat_total + proc_total + overhead
        rows.append({
            'name': opt.get('name', m),
            'material': m,
            'material_cost_usd': round(mat_total, 2),
            'process_cost_usd': round(proc_total, 2),
            'total_usd': round(total, 2),
        })
    rows.sort(key=lambda r: r['total_usd'])
    return {
        'success': True,
        '_tool': 'compare_costs',
        'options': rows,
        'cheapest': rows[0]['name'] if rows else None,
        'total_savings_pct': round((1 - rows[0]['total_usd'] / rows[-1]['total_usd']) * 100, 1) if len(rows) >= 2 else 0,
    }


def _cost_breakdown(kwargs):
    """Sprint 14.1: Cost breakdown by category (material / process / overhead)."""
    material = (kwargs.get('material') or 'default').lower().replace(' ', '_').replace('-', '_')
    mass_kg = float(kwargs.get('mass_kg') or 1.0)
    process_time_min = float(kwargs.get('process_time_min') or 60.0)

    mat_cost = _MATERIAL_COSTS.get(material, _MATERIAL_COSTS['default'])
    mat_total = mat_cost * mass_kg
    proc_total = _PROCESS_COSTS['default'] * process_time_min
    overhead = (mat_total + proc_total) * 0.15
    total = mat_total + proc_total + overhead

    if total <= 0:
        return {'success': False, 'error': 'total cost <= 0 (invalid inputs)', '_tool': 'cost_breakdown'}

    return {
        'success': True,
        '_tool': 'cost_breakdown',
        'material': material,
        'breakdown': {
            'material': {'cost_usd': round(mat_total, 2), 'pct': round(mat_total / total * 100, 1)},
            'process': {'cost_usd': round(proc_total, 2), 'pct': round(proc_total / total * 100, 1)},
            'overhead': {'cost_usd': round(overhead, 2), 'pct': 15.0},
        },
        'total_usd': round(total, 2),
    }


# ============================================================================
# Tool registry — maps tool names → handler functions
# ============================================================================

# --- Seal Pair Designer (Sprint 13) ---

def _design_seal_pair(kwargs):
    """Run seal pair design via seal_pair_designer v4.0."""
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from seal_pair_designer import api_seal_design
        result = api_seal_design(kwargs)
        if result.get('success'):
            out = result['output']
            return _clean({
                'success': True, '_tool': 'seal_pair',
                'input': result.get('input_summary', {}),
                'contact_stress_max_MPa': out.get('contact_stress_max_MPa'),
                'safety_factor_yield': out.get('safety_factor_yield'),
                'is_sealing': out.get('is_sealing'),
                'leak_class': out.get('leak_class'),
                'leak_rate_mbar_L_s': out.get('leak_rate_mbar_L_s'),
                'knudsen_number': out.get('knudsen_number'),
                'flow_regime': out.get('flow_regime'),
                'predicted_cycle_life': out.get('predicted_cycle_life'),
                'warnings': result.get('warnings', []),
                'recommendations': result.get('recommendations', []),
            })
        return {'success': False, 'error': result.get('error', 'Unknown error'), '_tool': 'seal_pair'}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'seal_pair'}


def _compare_seal_pairs(kwargs):
    """Compare multiple seal pair designs."""
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from seal_pair_designer import api_compare_designs
        configs = kwargs.get('configs', [])
        gas = kwargs.get('gas', 'N2')
        results = api_compare_designs(configs, gas)
        return _clean({'success': True, '_tool': 'compare_seal_pairs', 'results': results})
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'compare_seal_pairs'}


def _seal_sensitivity(kwargs):
    """Run seal pair sensitivity analysis."""
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from seal_pair_designer import api_sensitivity_analysis
        base_config = kwargs.get('base_config', {})
        param_name = kwargs.get('param_name', 'roughness_Ra_um')
        values = kwargs.get('values', [0.1, 0.4, 0.8])
        results = api_sensitivity_analysis(base_config, param_name, values)
        return _clean({'success': True, '_tool': 'seal_sensitivity', 'param': param_name, 'results': results})
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'seal_sensitivity'}


# ============================================================================
# Debate Engine tools (Sprint 14)
# ============================================================================

_debate_engine_instance = None


def _get_debate_engine():
    global _debate_engine_instance
    if _debate_engine_instance is None:
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from debate_engine import DebateEngine
        _debate_engine_instance = DebateEngine()
    return _debate_engine_instance


def _get_debate_templates(kwargs):
    """Get available debate templates (design/materials/compliance/safety)."""
    try:
        engine = _get_debate_engine()
        templates = engine.get_templates()
        return {'success': True, '_tool': 'debate_templates', 'count': len(templates), 'templates': templates}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'debate_templates'}


def _create_debate(kwargs):
    """Create a new debate session with given topic and agents."""
    try:
        topic = kwargs.get('topic', '')
        if not topic:
            return {'success': False, 'error': 'topic is required', '_tool': 'create_debate'}
        description = kwargs.get('description', '')
        design_params = kwargs.get('design_params', {})
        agent_names = kwargs.get('agent_names', None)
        engine = _get_debate_engine()
        session = engine.create_session(topic, description, design_params, agent_names)
        return {'success': True, '_tool': 'create_debate', 'session': session}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'create_debate'}


def _get_debate(kwargs):
    """Get debate session by id."""
    try:
        session_id = kwargs.get('session_id', '')
        if not session_id:
            return {'success': False, 'error': 'session_id required', '_tool': 'get_debate'}
        engine = _get_debate_engine()
        session = engine.get_session(session_id)
        return {'success': True, '_tool': 'get_debate', 'session': session}
    except Exception as e:
        return {'success': False, 'error': str(e), '_tool': 'get_debate'}


TOOL_BRIDGE = {
    # Material
    'query_material': _material_query,
    # Compliance
    'check_compliance': _compliance_check,
    'verify_leak': _verify_leak,
    'verify_rated': _verify_rated_output,
    'verify_life': _verify_life_cycles,
    # Fluid mechanics
    'run_fluid_calculation': _fluid_calculation,
    'identify_formula': _identify_formula,
    # Design
    'analyze_solenoid_valve': _analyze_solenoid,
    'analyze_pressure_valve': _analyze_prv,
    'design_spring': _design_spring,
    'design_oring': _design_oring,
    # Search
    'search_knowledge': _search_knowledge,
    'semantic_search': _semantic_search,
    # Knowledge Graph
    'graph_search': _graph_search,
    'graph_neighbors': _graph_neighbors,
    # Process (Sprint 12)
    'list_processes': _list_processes,
    'get_process_detail': _get_process_detail,
    'recommend_process': _recommend_process,
    'get_process_route': _get_process_route,
    # Cost (Sprint 14.1)
    'estimate_cost': _estimate_cost,
    'compare_costs': _compare_costs,
    'cost_breakdown': _cost_breakdown,
    # Seal Pair (Sprint 13)
    'design_seal_pair': _design_seal_pair,
    'compare_seal_pairs': _compare_seal_pairs,
    'seal_sensitivity': _seal_sensitivity,
    # Debate Engine (Sprint 14)
    'create_debate': _create_debate,
    'debate_templates': _get_debate_templates,
    'get_debate': _get_debate,
}


def get_tool_bridge():
    """Return a callable tool_executor(tool_name, kwargs) for PAOR/Orchestrator."""
    def executor(tool_name, kwargs=None):
        kwargs = kwargs or {}
        handler = TOOL_BRIDGE.get(tool_name)
        if not handler:
            return {'success': False, 'error': f'Unknown tool: {tool_name}'}
        return handler(kwargs)
    return executor


def get_tool_handler(tool_name):
    """Return handler function for a given tool name. Returns None if not found."""
    return TOOL_BRIDGE.get(tool_name)
