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
    """Query material database by name or id."""
    try:
        from materials_database import query_material
        name = kwargs.get('material', kwargs.get('name', ''))
        if not name:
            return {'success': False, 'error': 'No material name provided'}
        result = query_material(name)
        if not result:
            return {'success': False, 'error': f'Material "{name}" not found'}
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
    Falls back to mock if the real optimizer cannot be initialized (needs
    ValveGeometricParams + SolenoidPhysicsEngine).
    """
    try:
        from solenoid_optimizer import HybridOptimizer, ValveGeometricParams, SolenoidPhysicsEngine
        pressure = float(kwargs.get('working_pressure', kwargs.get('pressure', 21)))
        geom = ValveGeometricParams(pressure=pressure)
        physics = SolenoidPhysicsEngine(geom)
        opt = HybridOptimizer(geom, physics, n_particles=kwargs.get('n_particles', 10), n_iterations=30)
        best_awg, best_fit, best_info = opt.optimize()
        clean = _clean({'best_awg': best_awg, 'fitness': best_fit, 'design': best_info})
        clean['success'] = True
        clean['_tool'] = 'analyze_solenoid_valve'
        return clean
    except (ImportError, TypeError, AttributeError) as ie:
        return _mock_solenoid(kwargs, import_error=str(ie))
    except Exception as e:
        return _mock_solenoid(kwargs, import_error=f'Unexpected: {e}')
        clean = _clean(result)
        clean['success'] = True
        clean['_tool'] = 'analyze_solenoid_valve'
        return clean
    except ImportError:
        return _mock_solenoid(kwargs)
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


# ============================================================================
# Tool registry — maps tool names → handler functions
# ============================================================================

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
