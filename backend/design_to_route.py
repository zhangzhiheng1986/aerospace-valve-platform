# -*- coding: utf-8 -*-
"""Bridge: convert valve design result -> manufacturing process route.

Sprint 12 follow-up: AI Agent auto-generates process route from design.

Input: design result dict from solenoid_optimizer / pressure_reducing_valve / check_valve
Output: complete process route (operations list + materials + equipment + total time)
"""
import copy
from typing import Dict, List, Optional

from valve_process import (
    PROCESS_ROUTES, get_process_route, get_process_detail, recommend_process_route,
)


def extract_design_meta(design_result: Dict) -> Dict:
    """Pull valve_type / material / dimensions from a design result dict.

    Supports shapes:
      - {'type': 'solenoid',     'best_info': {...}, 'mass_g':...}
      - {'type': 'pressure_valve', 'result': {...}}
      - {'type': 'check',         'result': {...}}
    """
    out = {
        'valve_type': 'unknown',
        'material': 'unknown',
        'pressure_mpa': None,
        'temperature_c': None,
        'nominal_size_mm': None,
        'flow_rate_lpm': None,
        'mass_g': None,
    }
    if not isinstance(design_result, dict):
        return out
    t = design_result.get('type', '')
    out['valve_type'] = t
    if t == 'solenoid':
        bi = design_result.get('best_info', {})
        out['material'] = bi.get('material', 'Iron/Steel core')
        out['mass_g'] = design_result.get('mass_g')
        out['nominal_size_mm'] = bi.get('bore_mm') or bi.get('D_inner_mm')
    elif t in ('pressure_valve', 'prv'):
        sub = design_result.get('result', {})
        out['material'] = sub.get('body_material', 'Stainless Steel')
        out['pressure_mpa'] = sub.get('inlet_pressure_mpa') or sub.get('outlet_pressure_mpa')
        out['temperature_c'] = sub.get('fluid_temperature_c')
        out['flow_rate_lpm'] = sub.get('flow_rate_lpm')
        out['nominal_size_mm'] = sub.get('nominal_size_mm') or sub.get('orifice_mm', 0) * 4
    elif t in ('check', 'check_valve'):
        sub = design_result.get('result', {})
        out['material'] = sub.get('body_material') or sub.get('poppet_material', '17-4PH')
        out['pressure_mpa'] = sub.get('pressure_rating_mpa') or sub.get('rated_pressure_mpa')
        out['nominal_size_mm'] = sub.get('nominal_diameter_mm') or sub.get('dn_mm')
    return out


def _scale_turning_time(ops: List[Dict], size_factor: float = 1.0) -> List[Dict]:
    """Scale turning/grinding/HT times by size factor (size > norm => longer)."""
    new = []
    for op in ops:
        op2 = copy.deepcopy(op)
        op_name = op.get('process', '').lower()
        scaling_ops = ('turn', 'mill', 'grind', 'drill', 'tap')
        if any(s in op_name for s in scaling_ops) and 'heat' not in op_name:
            op2['time_min'] = max(1, int(op.get('time_min', 0) * size_factor))
        new.append(op2)
    return new


def _scale_ht_time(ops: List[Dict], ht_factor: float = 1.0) -> List[Dict]:
    """Scale heat treatment time (bigger/longer parts need longer HT)."""
    new = []
    for op in ops:
        op2 = copy.deepcopy(op)
        op_name = op.get('process', '').lower()
        if any(s in op_name for s in ('heat', 'aging', 'anneal', 'temper', 'solution', 'quench')):
            op2['time_min'] = max(1, int(op.get('time_min', 0) * ht_factor))
        new.append(op2)
    return new


def _renumber(ops: List[Dict]) -> List[Dict]:
    for i, op in enumerate(ops, 1):
        op['step'] = i
    return ops


def _calc_totals(ops: List[Dict]) -> Dict:
    total_min = sum(op.get('time_min', 0) for op in ops)
    return {
        'total_time_min': total_min,
        'total_time_h': round(total_min / 60, 2),
        'steps': len(ops),
    }


def auto_route_from_design(design_result: Dict, custom_material: Optional[str] = None) -> Dict:
    """Main entry: design_result -> complete process route.

    Strategy:
      1. Extract design meta (valve_type / material / size)
      2. Try exact route match (solenoid -> solenoid_valve_body, etc.)
      3. Use recommend_process_route() to fill in material-specific process cards
      4. Scale times by size factor
      5. Return final route with provenance
    """
    meta = extract_design_meta(design_result)
    if custom_material:
        meta['material'] = custom_material
    vt = meta['valve_type']
    mat = meta['material']
    # Step 1: choose base route
    base_route_id = None
    vt_lower = vt.lower() if vt else ''
    if 'solenoid' in vt_lower:
        base_route_id = 'solenoid_valve_body'
    elif 'pressure' in vt_lower or 'relief' in vt_lower or 'reducing' in vt_lower or vt_lower == 'prv':
        base_route_id = 'relief_valve_seat'
    elif 'check' in vt_lower:
        base_route_id = 'check_valve_poppet'
    provenance = {'strategy': 'auto_route_from_design', 'valve_type': vt, 'material': mat}
    if base_route_id and base_route_id in PROCESS_ROUTES:
        base = get_process_route(base_route_id)
        operations = copy.deepcopy(base['operations'])
        provenance['base_route'] = base_route_id
        # Replace material in notes
        for op in operations:
            op['method'] = op.get('method', '').replace(base.get('material', ''), mat)
    else:
        # No match: generate generic sequence
        operations = _build_generic_route(mat)
        provenance['base_route'] = 'generic'
    # Step 2: size factor scaling
    size_mm = meta.get('nominal_size_mm') or 20
    size_factor = max(0.6, min(2.5, size_mm / 20.0))
    operations = _scale_turning_time(operations, size_factor)
    operations = _scale_ht_time(operations, max(1.0, size_factor * 0.6))
    # Step 3: append material-specific extra processes
    extra = recommend_process_route(mat, vt)
    rec_processes = extra.get('processes', [])
    provenance['recommended_processes'] = rec_processes
    # Step 4: build response
    operations = _renumber(operations)
    totals = _calc_totals(operations)
    return {
        'success': True,
        'valve_type': vt,
        'material': mat,
        'base_route_id': provenance['base_route'],
        'operations': operations,
        'total_time_min': totals['total_time_min'],
        'total_time_h': totals['total_time_h'],
        'steps': totals['steps'],
        'size_factor': round(size_factor, 2),
        'provenance': provenance,
        'recommended_processes': rec_processes,
        'key_points': extra.get('key_points', []),
    }


def _build_generic_route(material: str) -> List[Dict]:
    """Fallback generic sequence for unknown valve type."""
    return [
        {"step": 1, "process": "Cut blank", "method": f"Bar stock cut to size ({material})", "equipment": "Saw", "time_min": 3},
        {"step": 2, "process": "Rough turning", "method": "OD/face rough turn", "equipment": "CNC lathe", "time_min": 10},
        {"step": 3, "process": "Finish turning", "method": "OD/face finish IT7, Ra 0.8", "equipment": "CNC lathe", "time_min": 8},
        {"step": 4, "process": "Milling", "method": "Mating face/key milling", "equipment": "MC", "time_min": 8},
        {"step": 5, "process": "Drill/tap", "method": "Mounting holes drilled/tapped", "equipment": "MC", "time_min": 5},
        {"step": 6, "process": "Deburr", "method": "Manual + power tool", "equipment": "Bench", "time_min": 4},
        {"step": 7, "process": "Heat treatment", "method": f"Per {material} datasheet", "equipment": "Furnace", "time_min": 90},
        {"step": 8, "process": "Finish grind", "method": "Seal/face finish grind", "equipment": "Surface grinder", "time_min": 8},
        {"step": 9, "process": "Surface treat", "method": f"Per {material} corrosion spec", "equipment": "Tank", "time_min": 30},
        {"step": 10, "process": "Cleaning", "method": "Ultrasonic + vacuum dry", "equipment": "Cleaner", "time_min": 15},
        {"step": 11, "process": "Leak test", "method": "He 1.5x Wp, leak <1E-9", "equipment": "He detector", "time_min": 15},
        {"step": 12, "process": "Final inspect/pack", "method": "Dim/geometry/visual", "equipment": "CMM/projector", "time_min": 10},
    ]


# ============================================================
# Test
# ============================================================
if __name__ == '__main__':
    print('=== Test 1: solenoid design -> route ===')
    fake_sol = {
        'success': True,
        'type': 'solenoid',
        'mass_g': 120,
        'best_info': {'material': 'DT4C', 'D_inner_mm': 18, 'bore_mm': 18},
    }
    r = auto_route_from_design(fake_sol)
    print(f"  base={r['base_route_id']}, steps={r['steps']}, total={r['total_time_h']}h")
    print(f"  material={r['material']}, size_factor={r['size_factor']}")
    for op in r['operations'][:5]:
        print(f"    {op['step']}. {op['process']} ({op['time_min']} min)")

    print('\n=== Test 2: pressure_valve design -> route ===')
    fake_prv = {
        'success': True,
        'type': 'pressure_valve',
        'result': {
            'body_material': 'Inconel 718',
            'inlet_pressure_mpa': 35,
            'outlet_pressure_mpa': 5,
            'fluid_temperature_c': 250,
            'flow_rate_lpm': 50,
            'orifice_mm': 12,
        },
    }
    r = auto_route_from_design(fake_prv)
    print(f"  base={r['base_route_id']}, steps={r['steps']}, total={r['total_time_h']}h")
    print(f"  material={r['material']}, size_factor={r['size_factor']}")

    print('\n=== Test 3: check_valve design -> route ===')
    fake_chk = {
        'success': True,
        'type': 'check',
        'result': {
            'body_material': '17-4PH',
            'pressure_rating_mpa': 21,
            'nominal_diameter_mm': 8,
        },
    }
    r = auto_route_from_design(fake_chk)
    print(f"  base={r['base_route_id']}, steps={r['steps']}, total={r['total_time_h']}h")

    print('\n=== Test 4: unknown valve -> generic route ===')
    r = auto_route_from_design({'success': True, 'type': 'unknown_type', 'result': {}})
    print(f"  base={r['base_route_id']}, steps={r['steps']}, total={r['total_time_h']}h")
