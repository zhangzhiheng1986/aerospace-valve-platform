"""
Parameter Extractor — Sprint 9.1
=================================
Smart parameter extraction from natural language queries for engineering tools.
Replaces the empty "message" passthrough that broke all multi-agent pipelines.

Features:
- Regex + pattern matching for: pressure, flow, temperature, voltage, diameter, material names
- Synonym maps (CN/EN) for: inlet/outlet, fluid types, material codes
- Unit normalization (MPa/Pa/bar/psi, L/min/m^3/s, mm/cm/m)
- Tool-specific parameter resolvers (one per design tool)
- Confidence scoring per extraction

Why this exists:
- Old behavior: orchestrator passed raw "message" to tools that expected structured kwargs
- Tools rejected with "No material name provided" / "missing pressure" etc.
- New behavior: parse user text into a typed kwargs dict, with sensible defaults
"""

import re
import math
from typing import Dict, List, Optional, Tuple, Any


# ============================================================================
# Unit Conversion Tables
# ============================================================================

PRESSURE_UNITS = {
    # canonical: Pa
    'pa': 1.0, 'pascal': 1.0,
    'kpa': 1e3, 'mpa': 1e6, 'gpa': 1e9,
    'bar': 1e5, 'millibar': 100, 'mbar': 100,
    'atm': 101325, 'atmosphere': 101325,
    'psi': 6894.76, 'psia': 6894.76, 'psig': 6894.76,
    'torr': 133.322, 'mmhg': 133.322,
}

FLOW_UNITS = {
    # canonical: L/min
    'l/min': 1.0, 'lpm': 1.0, 'l/m': 1.0,
    'm3/s': 60000, 'm^3/s': 60000,
    'm3/h': 16.667, 'm^3/h': 16.667, 'cmh': 16.667,
    'm3/min': 1000, 'm^3/min': 1000,
    'l/s': 60, 'l/sec': 60,
    'gpm': 3.785, 'gal/min': 3.785,
    'cfm': 28.317,
}

LENGTH_UNITS = {
    # canonical: mm
    'mm': 1.0, 'millimeter': 1.0,
    'cm': 10.0, 'centimeter': 10.0,
    'm': 1000.0, 'meter': 1000.0,
    'in': 25.4, 'inch': 25.4, '"': 25.4,
    'ft': 304.8, 'foot': 304.8,
    'dm': 100.0, 'decimeter': 100.0,
}

TEMP_UNITS = {
    # values stay in C unless suffix is F or K
    'c': 'C', 'celsius': 'C', '℃': 'C',
    'f': 'F', 'fahrenheit': 'F', '℉': 'F',
    'k': 'K', 'kelvin': 'K',
}

VOLTAGE_UNITS = {
    'v': 1.0, 'volt': 1.0,
    'mv': 1e-3, 'kv': 1e3,
}

# ============================================================================
# Synonym Dictionaries
# ============================================================================

# Material synonyms
MATERIAL_SYNONYMS = {
    # Chinese names → canonical codes
    '钛合金': 'TC4', '钛': 'TC4', 'ti-6al-4v': 'TC4', 'ti6al4v': 'TC4',
    '高温合金': 'GH4169', '镍基合金': 'GH4169', 'inconel': 'GH4169', 'inconel 718': 'GH4169',
    '不锈钢': '1Cr18Ni9Ti', '304': '1Cr18Ni9Ti', '321': '1Cr18Ni9Ti',
    '铝合金': '2A12', '7075': '7075', '铝': '2A12',
    '铜合金': 'H62', '黄铜': 'H62',
    '弹簧钢': '50CrVA', '弹簧钢丝': '50CrVA',
    'nbr': 'NBR', '丁腈': 'NBR',
    'fkm': 'FKM', '氟橡胶': 'FKM', 'viton': 'FKM',
    'ffkm': 'FFKM', 'kalrez': 'FFKM',
    'ptfe': 'PTFE', '聚四氟乙烯': 'PTFE', '特氟龙': 'PTFE',
    # English short codes
    'tc4': 'TC4', 'tc6': 'TC6', 'tc11': 'TC11',
    'gh4169': 'GH4169', 'gh605': 'GH605',
    '440c': '440C', '17-4ph': '17-4PH',
    'h62': 'H62', 'hpb59-1': 'HPb59-1',
    '50crva': '50CrVA', '60si2mn': '60Si2Mn',
    '1cr18ni9ti': '1Cr18Ni9Ti', '0cr17ni4cu4nb': '0Cr17Ni4Cu4Nb',
}

# Fluid type synonyms
FLUID_SYNONYMS = {
    '水': 'water', 'water': 'water',
    '空气': 'air', 'air': 'air', '气体': 'air',
    '氮气': 'nitrogen', 'n2': 'nitrogen', 'nitrogen': 'nitrogen',
    '氦气': 'helium', 'he': 'helium', 'helium': 'helium',
    '氧气': 'oxygen', 'o2': 'oxygen', 'oxygen': 'oxygen',
    '煤油': 'kerosene', 'rp-3': 'kerosene', 'rp3': 'kerosene', 'kerosene': 'kerosene',
    '液压油': 'hydraulic_oil', 'hydraulic oil': 'hydraulic_oil', 'hydraulic_oil': 'hydraulic_oil',
    '航空煤油': 'kerosene', 'jet fuel': 'kerosene', 'jet-fuel': 'kerosene',
    '液氧': 'oxygen', 'lox': 'oxygen',
    '液氢': 'hydrogen', 'lh2': 'hydrogen', 'hydrogen': 'hydrogen',
    '氮': 'nitrogen', '液氮': 'nitrogen', 'ln2': 'nitrogen',
    '红烟硝': 'nitrogen_tetroxide', 'n2o4': 'nitrogen_tetroxide', 'nitrogen_tetroxide': 'nitrogen_tetroxide',
}

# Valve type synonyms (for query_material routing)
VALVE_TYPE_SYNONYMS = {
    'solenoid': 'solenoid', 'solenoid valve': 'solenoid', '电磁阀': 'solenoid', '螺线管': 'solenoid',
    'prv': 'pressure_valve', 'pressure reducing': 'pressure_valve', '减压阀': 'pressure_valve',
    'check': 'check_valve', 'check valve': 'check_valve', '单向阀': 'check_valve', '止回阀': 'check_valve',
    'spring': 'spring', '弹簧': 'spring',
    'o-ring': 'o-ring', 'oring': 'o-ring', 'o形圈': 'o-ring', 'o型圈': 'o-ring', '密封圈': 'o-ring',
    'seal': 'seal', '密封副': 'seal', '密封': 'seal',
}

# Property keywords for query_material
MATERIAL_PROPS = ['密度', '弹性模量', '屈服强度', '抗拉强度', '硬度', '熔点', '热导率', '比热',
                  'density', 'modulus', 'yield', 'tensile', 'hardness', 'melting', 'thermal', 'specific heat']


# ============================================================================
# Core Number + Unit Parser
# ============================================================================

def _parse_number_with_unit(text: str, unit_map: Dict[str, float], default_unit: Optional[str] = None) -> Optional[Tuple[float, str]]:
    """
    Find the first number+unit pair in text.
    Returns (value_in_canonical_unit, original_text) or None.
    """
    if not text:
        return None
    # Pattern: (number) [(optional space)] (unit)
    # Number can be: 1, 1.5, 1e3, 1.5E-2, 100,000
    pat = re.compile(
        r'(-?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?)\s*'
        r'([A-Za-zμΩ℃℉°/^0-9\.\-]+)?',
    )
    for m in pat.finditer(text):
        raw = m.group(1).replace(',', '')
        try:
            num = float(raw)
        except ValueError:
            continue
        unit = (m.group(2) or default_unit or '').lower().strip()
        if not unit:
            return num, m.group(0)
        # Try longest match first
        sorted_units = sorted(unit_map.keys(), key=len, reverse=True)
        for u in sorted_units:
            if u in unit or unit == u:
                return num * unit_map[u], m.group(0)
        # Unit not recognized — return raw number
        return num, m.group(0)
    return None


def _parse_all_pressures(text: str) -> List[Tuple[float, str]]:
    """Find all pressure values in text."""
    results = []
    for m in re.finditer(
        r'(-?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?)\s*'
        r'(MPa|GPa|kPa|bar|psi|atm|Pa|兆帕|百帕|千帕|公斤/平方厘米|kgf/cm²)',
        text, re.IGNORECASE
    ):
        raw = m.group(1).replace(',', '')
        try:
            num = float(raw)
        except ValueError:
            continue
        unit = m.group(2).lower()
        unit_map = {
            'mpa': 'mpa', 'gpa': 'gpa', 'kpa': 'kpa', 'bar': 'bar',
            'psi': 'psi', 'atm': 'atm', 'pa': 'pa',
            '兆帕': 'mpa', '百帕': 'kpa', '千帕': 'kpa',
            '公斤/平方厘米': 'bar', 'kgf/cm²': 'bar',
        }
        canon = unit_map.get(unit, 'mpa')
        results.append((num * PRESSURE_UNITS[canon], m.group(0)))
    return results


def _parse_all_flows(text: str) -> List[Tuple[float, str]]:
    """Find all flow rate values."""
    results = []
    for m in re.finditer(
        r'(-?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?)\s*'
        r'(L/min|LPM|m3/s|m³/s|m3/h|m³/h|L/s|CFM|GPM)',
        text, re.IGNORECASE
    ):
        raw = m.group(1).replace(',', '')
        try:
            num = float(raw)
        except ValueError:
            continue
        unit = m.group(2).lower().replace('³', '3').replace('^3', '3')
        unit_map = {
            'l/min': 'l/min', 'lpm': 'lpm',
            'm3/s': 'm3/s', 'm3/h': 'm3/h',
            'l/s': 'l/s', 'cfm': 'cfm', 'gpm': 'gpm',
        }
        canon = unit_map.get(unit, 'l/min')
        results.append((num * FLOW_UNITS[canon], m.group(0)))
    return results


def _parse_all_temperatures(text: str) -> List[Tuple[float, str]]:
    """Find all temperature values. Returns values in Celsius."""
    results = []
    for m in re.finditer(
        r'(-?\d+(?:[.,]\d+)?)\s*'
        r'(°C|°F|℃|℉|C|F|K)',
        text
    ):
        raw = m.group(1).replace(',', '')
        try:
            num = float(raw)
        except ValueError:
            continue
        unit = m.group(2)
        if unit in ('°C', '℃', 'C'):
            celsius = num
        elif unit in ('°F', '℉', 'F'):
            celsius = (num - 32) * 5 / 9
        elif unit == 'K':
            celsius = num - 273.15
        else:
            celsius = num
        results.append((celsius, m.group(0)))
    return results


def _parse_all_diameters(text: str) -> List[Tuple[float, str]]:
    """Find all diameter/length values in mm.
    
    Recognizes: mm, cm, m, in, inch, '. Bare 'm' is treated as meter unless
    preceded by a diameter/bore keyword in which case it is interpreted as mm.
    """
    results = []
    text_norm = text
    # Upgrade "diameter X m" / "bore X m" → "X mm" to avoid meter confusion
    for kw in ['diameter', 'bore', 'ø', 'Ø', '内径', '外径', '直径', 'radius', '半径']:
        text_norm = re.sub(
            rf'({re.escape(kw)})\s*(\d+(?:\.\d+)?)\s*m\b',
            rf'\1 \2 mm',
            text_norm,
            flags=re.IGNORECASE,
        )
        # Also reverse: "X m diameter" / "X m bore" → "X mm diameter"
        text_norm = re.sub(
            rf'(\d+(?:\.\d+)?)\s*m\s+({re.escape(kw)})',
            rf'\1 mm \2',
            text_norm,
            flags=re.IGNORECASE,
        )
    # Match unambiguous length units OR (digit + bare 'm' as mm heuristic)
    # Avoid matching 'm/s', 'm^3' etc.
    for m in re.finditer(
        r'(?:[ØΦ直径Dd内径外径半径r])?\s*'
        r'(-?\d+(?:[.,]\d+)?)\s*'
        r'(mm|cm|in|inch|"|mm毫米|cm厘米)\b'
        r'|'
        r'(-?\d+(?:[.,]\d+)?)\s*m\b(?![\^/a-zA-Z])',
        text_norm, re.IGNORECASE
    ):
        if m.group(2):  # explicit unit
            raw = m.group(1)
            unit = m.group(2).lower()
        else:  # bare 'm' (no unit suffix or non-length follows)
            raw = m.group(3)
            unit = 'm'
        try:
            num = float(raw.replace(',', ''))
        except ValueError:
            continue
        unit_map = {
            'mm': 'mm', 'mm毫米': 'mm',
            'cm': 'cm', 'cm厘米': 'cm',
            'm': 'm', 'in': 'in', 'inch': 'in', '"': 'in',
        }
        canon = unit_map.get(unit, 'mm')
        # Heuristic: if num > 100 and unit is 'm', it's probably mm
        if canon == 'm' and num > 100:
            canon = 'mm'
        results.append((num * LENGTH_UNITS[canon], m.group(0)))
    return results


def _parse_voltage(text: str) -> Optional[float]:
    """Find voltage value (returns Volts)."""
    m = re.search(
        r'(\d+(?:[.,]\d+)?)\s*(V|volt|伏)',
        text, re.IGNORECASE
    )
    if m:
        try:
            return float(m.group(1).replace(',', ''))
        except ValueError:
            return None
    return None


# ============================================================================
# Domain-Specific Extractors
# ============================================================================

def extract_material_name(text: str) -> Optional[str]:
    """Extract material name/code from user message."""
    if not text:
        return None
    text_lower = text.lower()
    # Priority 1: explicit material codes
    for code, canon in sorted(MATERIAL_SYNONYMS.items(), key=lambda x: -len(x[0])):
        if code.lower() in text_lower:
            return canon
    # Priority 2: pattern like "TC4", "GH4169"
    m = re.search(r'\b(TC\d+|GH\d{3,4}|1Cr18Ni9Ti|2A\d+|7075|50CrVA|60Si2Mn|440C|17-4PH|H62|HPb59-1|0Cr17Ni4Cu4Nb)\b', text)
    if m:
        return m.group(1)
    return None


def extract_fluid_type(text: str) -> Optional[str]:
    """Extract fluid medium type."""
    if not text:
        return None
    text_lower = text.lower()
    for name, canon in sorted(FLUID_SYNONYMS.items(), key=lambda x: -len(x[0])):
        if name.lower() in text_lower:
            return canon
    return None


def extract_valve_type(text: str) -> Optional[str]:
    """Detect which valve subsystem the user is asking about."""
    if not text:
        return None
    text_lower = text.lower()
    for name, canon in sorted(VALVE_TYPE_SYNONYMS.items(), key=lambda x: -len(x[0])):
        if name.lower() in text_lower:
            return canon
    return None


def extract_prv_params(text: str) -> Dict[str, Any]:
    """Extract parameters for analyze_pressure_valve."""
    pressures = _parse_all_pressures(text)
    flows = _parse_all_flows(text)
    fluid = extract_fluid_type(text)

    inlet_pressure_mpa = None
    outlet_pressure_mpa = None

    # If 2+ pressures, assign by context keywords
    if len(pressures) >= 2:
        # Look for "入" (inlet) and "出" (outlet) context near each
        inlet_idx = None
        outlet_idx = None
        for i, (val, raw) in enumerate(pressures):
            pos = text.find(raw)
            if pos < 0:
                continue
            ctx = text[max(0, pos-5):pos+len(raw)+5]
            if '入' in ctx or 'inlet' in ctx.lower() or 'upstream' in ctx.lower():
                inlet_idx = i
            elif '出' in ctx or 'outlet' in ctx.lower() or 'downstream' in ctx.lower() or 'target' in ctx.lower():
                outlet_idx = i
        if inlet_idx is None and outlet_idx is None:
            # Fall back: first = inlet, second = outlet
            inlet_pressure_mpa = pressures[0][0] / 1e6
            outlet_pressure_mpa = pressures[1][0] / 1e6
        else:
            if inlet_idx is not None:
                inlet_pressure_mpa = pressures[inlet_idx][0] / 1e6
            if outlet_idx is not None:
                outlet_pressure_mpa = pressures[outlet_idx][0] / 1e6
            # Fill missing with remaining
            if inlet_pressure_mpa is None or outlet_pressure_mpa is None:
                remaining = [p for i, p in enumerate(pressures) if i not in (inlet_idx, outlet_idx)]
                if inlet_pressure_mpa is None and remaining:
                    inlet_pressure_mpa = remaining[0][0] / 1e6
                if outlet_pressure_mpa is None and len(remaining) > 1:
                    outlet_pressure_mpa = remaining[1][0] / 1e6
    elif len(pressures) == 1:
        # Single pressure = working pressure
        inlet_pressure_mpa = pressures[0][0] / 1e6

    flow_lpm = flows[0][0] if flows else None

    return {
        'fluid_type': fluid,
        'inlet_pressure_mpa': inlet_pressure_mpa,
        'outlet_pressure_mpa': outlet_pressure_mpa,
        'flow_lpm': flow_lpm,
    }


def extract_solenoid_params(text: str) -> Dict[str, Any]:
    """Extract parameters for analyze_solenoid_valve."""
    voltage = _parse_voltage(text)
    strokes = _parse_all_diameters(text)  # stroke is also a length
    pressures = _parse_all_pressures(text)
    material = extract_material_name(text)

    return {
        'voltage': voltage,
        'stroke_mm': strokes[0][0] if strokes else None,
        'working_pressure_mpa': pressures[0][0] / 1e6 if pressures else None,
        'material': material,
    }


def extract_spring_params(text: str) -> Dict[str, Any]:
    """Extract parameters for design_spring."""
    diameters = _parse_all_diameters(text)
    return {
        'outer_diameter_mm': diameters[0][0] if diameters else None,
        'wire_diameter_mm': diameters[1][0] if len(diameters) >= 2 else None,
        'free_length_mm': diameters[2][0] if len(diameters) >= 3 else None,
        'material': extract_material_name(text),
    }


def extract_oring_params(text: str) -> Dict[str, Any]:
    """Extract parameters for design_oring."""
    diameters = _parse_all_diameters(text)
    pressures = _parse_all_pressures(text)
    return {
        'housing_diameter_mm': diameters[0][0] if diameters else None,
        'pressure_mpa': pressures[0][0] / 1e6 if pressures else None,
        'material': extract_material_name(text),
    }


def extract_compliance_params(text: str) -> Dict[str, Any]:
    """Extract parameters for check_compliance."""
    pressures = _parse_all_pressures(text)
    temps = _parse_all_temperatures(text)
    cycles_m = re.search(r'(\d+(?:,\d+)*)\s*(?:cycles|cycle|次|循环)', text, re.IGNORECASE)
    cycles = None
    if cycles_m:
        try:
            cycles = int(cycles_m.group(1).replace(',', ''))
        except ValueError:
            pass
    return {
        'rated_pressure_mpa': pressures[0][0] / 1e6 if pressures else None,
        'rated_temperature_c': temps[0][0] if temps else None,
        'design_life_cycles': cycles,
    }


def extract_fluid_calc_params(text: str) -> Dict[str, Any]:
    """Extract parameters for run_fluid_calculation."""
    diameters = _parse_all_diameters(text)
    velocities = re.findall(r'(\d+(?:[.,]\d+)?)\s*(m/s|米/秒|ft/s)', text, re.IGNORECASE)
    densities = re.findall(r'(\d+(?:[.,]\d+)?)\s*(kg/m³|kg/m\^3|g/cm³|g/cm\^3)', text, re.IGNORECASE)
    viscosities = re.findall(r'(\d+(?:[.,]\d+)?[eE][-+]?\d+|\d+(?:[.,]\d+)?)\s*(Pa\.s|Pa·s|cP|cSt|m²/s)', text)

    vel = None
    if velocities:
        try:
            v = float(velocities[0][0].replace(',', ''))
            unit = velocities[0][1].lower().replace('m/s', 'm/s')
            if 'm/s' in unit or '米' in unit:
                vel = v
            elif 'ft/s' in unit:
                vel = v * 0.3048
        except (ValueError, IndexError):
            pass

    rho = None
    if densities:
        try:
            d = float(densities[0][0].replace(',', ''))
            unit = densities[0][1].lower()
            if 'kg/m' in unit or 'kg/m^3' in unit:
                rho = d
            elif 'g/cm' in unit:
                rho = d * 1000
        except (ValueError, IndexError):
            pass

    mu = None
    if viscosities:
        try:
            vis = float(viscosities[0][0].replace(',', ''))
            unit = viscosities[0][1].lower()
            if 'pa' in unit and 's' in unit:
                mu = vis
            elif 'cp' in unit:
                mu = vis * 1e-3
            elif 'cst' in unit:
                # kinematic → need rho; assume water at 1e-6 m²/s = 1e-3 Pa·s
                mu = vis * 1e-6 * (rho if rho else 1000)
        except (ValueError, IndexError):
            pass

    return {
        'velocity_ms': vel,
        'density_kgm3': rho,
        'viscosity_pas': mu,
        'diameter_mm': diameters[0][0] if diameters else None,
    }


# ============================================================================
# Main Router: pick extractor by tool name
# ============================================================================

EXTRACTORS = {
    'analyze_solenoid_valve': extract_solenoid_params,
    'analyze_pressure_valve': extract_prv_params,
    'analyze_check_valve': extract_prv_params,
    'design_spring': extract_spring_params,
    'design_oring': extract_oring_params,
    'check_compliance': extract_compliance_params,
    'run_fluid_calculation': extract_fluid_calc_params,
    'identify_formula': lambda t: {'hint': t},
    'query_material': lambda t: {'material': extract_material_name(t), 'name': extract_material_name(t)},
}


def extract_for_tool(tool_name: str, user_message: str) -> Dict[str, Any]:
    """
    Route a user message to the right extractor and return structured kwargs.
    Always includes 'message' as fallback and 'user_message' for downstream tools.
    
    Field-name mapping aligns with tool_bridge expectations:
    - analyze_pressure_valve: inlet_pressure, outlet_pressure, flow_rate, fluid_type/fluid
    - analyze_solenoid_valve: voltage, stroke, force_required, working_pressure/pressure
    - design_spring: wire_diameter, mean_diameter/outer_diameter, n_coils, free_length
    - design_oring: shaft_diameter, pressure, seal_type
    - check_compliance: working_pressure, pressure, rated
    - query_material: material, name
    """
    extractor = EXTRACTORS.get(tool_name)
    if not extractor:
        return {'message': user_message}
    extracted = extractor(user_message)
    # Align with tool_bridge expected kwargs
    if tool_name == 'analyze_pressure_valve' or tool_name == 'analyze_check_valve':
        if 'inlet_pressure_mpa' in extracted and extracted['inlet_pressure_mpa'] is not None:
            extracted['inlet_pressure'] = extracted['inlet_pressure_mpa']
        if 'outlet_pressure_mpa' in extracted and extracted['outlet_pressure_mpa'] is not None:
            extracted['outlet_pressure'] = extracted['outlet_pressure_mpa']
        if 'flow_lpm' in extracted and extracted['flow_lpm'] is not None:
            extracted['flow_rate'] = extracted['flow_lpm']
        if 'fluid_type' in extracted and extracted['fluid_type'] is not None:
            extracted['fluid'] = extracted['fluid_type']
            extracted['medium'] = extracted['fluid_type']
    if tool_name == 'analyze_solenoid_valve':
        if 'working_pressure_mpa' in extracted and extracted['working_pressure_mpa'] is not None:
            extracted['pressure'] = extracted['working_pressure_mpa']
            extracted['working_pressure'] = extracted['working_pressure_mpa']
    if tool_name == 'check_compliance':
        if 'rated_pressure_mpa' in extracted and extracted['rated_pressure_mpa'] is not None:
            extracted['pressure'] = extracted['rated_pressure_mpa']
            extracted['working_pressure'] = extracted['rated_pressure_mpa']
        if 'design_life_cycles' in extracted and extracted['design_life_cycles'] is not None:
            extracted['cycles'] = extracted['design_life_cycles']
    if tool_name == 'design_oring':
        if 'housing_diameter_mm' in extracted and extracted['housing_diameter_mm'] is not None:
            extracted['shaft_diameter'] = extracted['housing_diameter_mm']
        if 'pressure_mpa' in extracted and extracted['pressure_mpa'] is not None:
            extracted['pressure'] = extracted['pressure_mpa']
            extracted['working_pressure'] = extracted['pressure_mpa']
    # Sprint 9.1 enhancement: if query_material got no name, infer from context
    if tool_name == 'query_material' and not extracted.get('material'):
        # Use extracted conditions (pressure, temperature) to recommend
        pressures = _parse_all_pressures(user_message)
        temps = _parse_all_temperatures(user_message)
        if temps and temps[0][0] > 400:
            extracted['material'] = 'TC4'  # High-temp titanium
        elif pressures and pressures[0][0] / 1e6 > 10:
            extracted['material'] = '1Cr18Ni9Ti'
        else:
            extracted['material'] = '2A12'  # Common aerospace aluminum
        extracted['_auto_selected'] = True
    # Final: duplicate material -> name for tool_bridge compatibility
    if 'material' in extracted and 'name' not in extracted:
        extracted['name'] = extracted['material']
    extracted['message'] = user_message
    extracted['user_message'] = user_message
    # Compute confidence: fraction of non-null extracted fields
    if extracted:
        non_null = sum(1 for k, v in extracted.items()
                       if v is not None and v != '' and not k.startswith('_'))
        confidence = min(1.0, non_null / 4.0)  # 4 fields = full confidence
        extracted['_extraction_confidence'] = round(confidence, 2)
    return extracted


# ============================================================================
# Self-Test
# ============================================================================

if __name__ == '__main__':
    test_cases = [
        ('Help me design a pressure reducing valve, inlet 15 MPa, outlet 2 MPa, flow 100 L/min, medium is RP-3 kerosene',
         'analyze_pressure_valve'),
        ('设计减压阀, 入口15MPa, 出口2MPa, 流量100L/min, 介质煤油', 'analyze_pressure_valve'),
        ('Design a solenoid for 28V, 2mm stroke, 10N force', 'analyze_solenoid_valve'),
        ('What material should I use for a valve operating at 500C and 20 MPa in rocket engine?',
         'query_material'),
        ('Compute Reynolds number for water at 5 m/s in a 50mm diameter pipe',
         'run_fluid_calculation'),
        ('Spring for 50mm OD, wire 2mm, free length 30mm, 50CrVA material',
         'design_spring'),
        ('O-ring for 100mm bore, 30MPa pressure, FKM material',
         'design_oring'),
    ]
    for text, tool in test_cases:
        print(f'>>> Tool: {tool}')
        print(f'    Text: {text}')
        result = extract_for_tool(tool, text)
        print(f'    Extracted: {result}')
        print()
