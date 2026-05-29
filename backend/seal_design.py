# -*- coding: utf-8 -*-
"""
航空航天阀门密封副设计计算 - Web API Module
Based on: Hertz contact theory + Roth molecular flow leak model
"""
import math
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


# ==================== Helper ====================

def _clean(obj):
    """Recursively replace Infinity/NaN with null for JSON serialization."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(x) for x in obj]
    return obj


def _clean_result(result):
    """Convert dataclass result to JSON-safe dict."""
    d = asdict(result)
    return _clean(d)


# ==================== Constants ====================

R_GAS = 8.314
T_STANDARD = 293.15
P_STANDARD = 101325

LEAK_CLASS_COEFFICIENTS = {
    "AA": 0.0, "A": 0.0001, "B": 0.0006, "C": 0.0018,
    "D": 0.006, "E": 0.018, "EE": 0.060, "F": 0.180, "G": 0.600,
}

LEAK_CLASS_INFO = {
    "AA": {"name": "AA 级 - 零泄漏", "desc": "核/航天级零泄漏，最严格等级"},
    "A": {"name": "A 级 - 无可见泄漏", "desc": "无可见泄漏，精密阀门标准"},
    "B": {"name": "B 级 - 0.0006 mm^3/s/mm", "desc": "极低泄漏，高要求工业阀门"},
    "C": {"name": "C 级 - 0.0018 mm^3/s/mm", "desc": "低泄漏，通用精密阀门"},
    "D": {"name": "D 级 - 0.006 mm^3/s/mm", "desc": "默认工业级标准"},
    "E": {"name": "E 级 - 0.018 mm^3/s/mm", "desc": "一般工业阀门"},
    "EE": {"name": "EE 级 - 0.060 mm^3/s/mm", "desc": "较低要求"},
    "F": {"name": "F 级 - 0.180 mm^3/s/mm", "desc": "低要求"},
    "G": {"name": "G 级 - 0.600 mm^3/s/mm", "desc": "最低要求等级"},
}

MATERIALS = {
    "316L_SS": {
        "name": "316L Stainless Steel", "name_cn": "316L 不锈钢",
        "E": 193e9, "nu": 0.30, "sigma_y": 205e6, "sigma_uts": 515e6,
        "hardness": 180, "density": 8000,
        "thermal_expansion": 16.0e-6, "thermal_conductivity": 16.3,
        "category": "metal", "cryo_compatible": True,
        "max_temp": 870, "min_temp": -196,
        "desc": "最常用不锈钢，广泛适用"
    },
    "INCONEL_718": {
        "name": "Inconel 718", "name_cn": "Inconel 718",
        "E": 205e9, "nu": 0.29, "sigma_y": 1034e6, "sigma_uts": 1275e6,
        "hardness": 350, "density": 8190,
        "thermal_expansion": 13.0e-6, "thermal_conductivity": 11.4,
        "category": "metal", "cryo_compatible": True,
        "max_temp": 980, "min_temp": -253,
        "desc": "高温镍基合金，液氢温区兼容"
    },
    "TI_6AL4V": {
        "name": "Ti-6Al-4V", "name_cn": "Ti-6Al-4V 钛合金",
        "E": 114e9, "nu": 0.33, "sigma_y": 880e6, "sigma_uts": 950e6,
        "hardness": 330, "density": 4430,
        "thermal_expansion": 8.6e-6, "thermal_conductivity": 6.7,
        "category": "metal", "cryo_compatible": True,
        "max_temp": 400, "min_temp": -253,
        "desc": "轻质高强度，航天结构首选"
    },
    "17_4PH": {
        "name": "17-4PH", "name_cn": "17-4PH 沉淀硬化不锈钢",
        "E": 196e9, "nu": 0.27, "sigma_y": 1000e6, "sigma_uts": 1070e6,
        "hardness": 340, "density": 7800,
        "thermal_expansion": 10.8e-6, "thermal_conductivity": 18.0,
        "category": "metal", "cryo_compatible": True,
        "max_temp": 480, "min_temp": -196,
        "desc": "高强度不锈钢，高压阀门适用"
    },
    "PTFE": {
        "name": "PTFE (Teflon)", "name_cn": "PTFE 聚四氟乙烯",
        "E": 0.5e9, "nu": 0.46, "sigma_y": 14e6, "sigma_uts": 28e6,
        "hardness": 55, "density": 2200,
        "thermal_expansion": 125e-6, "thermal_conductivity": 0.25,
        "category": "polymer", "cryo_compatible": False,
        "max_temp": 260, "min_temp": -50,
        "leak_factor_m": 0.75, "gasket_factor_a": 3.5, "gasket_factor_b": 0.20,
        "desc": "最常用密封材料，化学稳定性极佳"
    },
    "PCTFE": {
        "name": "PCTFE (Kel-F)", "name_cn": "PCTFE 聚三氟氯乙烯",
        "E": 1.5e9, "nu": 0.44, "sigma_y": 35e6, "sigma_uts": 42e6,
        "hardness": 75, "density": 2130,
        "thermal_expansion": 70e-6, "thermal_conductivity": 0.20,
        "category": "polymer", "cryo_compatible": True,
        "max_temp": 200, "min_temp": -253,
        "leak_factor_m": 0.65, "gasket_factor_a": 3.8, "gasket_factor_b": 0.18,
        "desc": "低温兼容聚合物，液氧/液氮工况首选"
    },
    "PEEK": {
        "name": "PEEK", "name_cn": "PEEK 聚醚醚酮",
        "E": 3.6e9, "nu": 0.40, "sigma_y": 100e6, "sigma_uts": 110e6,
        "hardness": 85, "density": 1320,
        "thermal_expansion": 47e-6, "thermal_conductivity": 0.25,
        "category": "polymer", "cryo_compatible": True,
        "max_temp": 340, "min_temp": -196,
        "leak_factor_m": 0.55, "gasket_factor_a": 4.2, "gasket_factor_b": 0.15,
        "desc": "高性能工程塑料，耐高温高压"
    },
    "FKM": {
        "name": "FKM (Viton)", "name_cn": "FKM 氟橡胶",
        "E": 0.01e9, "nu": 0.49, "sigma_y": 8e6, "sigma_uts": 15e6,
        "hardness": 75, "density": 1850,
        "thermal_expansion": 200e-6, "thermal_conductivity": 0.20,
        "category": "elastomer", "cryo_compatible": False,
        "max_temp": 230, "min_temp": -30,
        "leak_factor_m": 0.40, "gasket_factor_a": 2.5, "gasket_factor_b": 0.35,
        "desc": "常用弹性体密封，O形圈材料"
    },
    "FFKM": {
        "name": "FFKM (Kalrez)", "name_cn": "FFKM 全氟醚橡胶",
        "E": 0.015e9, "nu": 0.49, "sigma_y": 12e6, "sigma_uts": 20e6,
        "hardness": 80, "density": 2000,
        "thermal_expansion": 180e-6, "thermal_conductivity": 0.18,
        "category": "elastomer", "cryo_compatible": True,
        "max_temp": 325, "min_temp": -40,
        "leak_factor_m": 0.35, "gasket_factor_a": 2.8, "gasket_factor_b": 0.30,
        "desc": "顶级弹性体，宽温域高性能"
    },
}

GASES = {
    "N2": {"name": "\u6c2e\u6c14 Nitrogen", "M": 0.028, "viscosity": 17.8e-6, "mean_free_path": 66e-9, "gamma": 1.40, "desc": "\u5e38\u7528\u8bd5\u9a8c\u4ecb\u8d28/\u63a8\u8fdb\u5242"},
    "He": {"name": "\u6c26\u6c14 Helium", "M": 0.004, "viscosity": 19.7e-6, "mean_free_path": 192e-9, "gamma": 1.66, "desc": "\u6c26\u8d28\u8c31\u68c0\u6f0f\u6807\u51c6\u4ecb\u8d28"},
    "H2": {"name": "\u6c22\u6c14 Hydrogen", "M": 0.002, "viscosity": 8.9e-6, "mean_free_path": 124e-9, "gamma": 1.41, "desc": "\u71c3\u6599\u7535\u6c60/\u6db2\u6c22\u5de5\u51b5"},
    "O2": {"name": "\u6c27\u6c14 Oxygen", "M": 0.032, "viscosity": 20.5e-6, "mean_free_path": 70e-9, "gamma": 1.40, "desc": "\u6db2\u6c27\u63a8\u8fdb\u5242\u5de5\u51b5"},
    "Air": {"name": "\u7a7a\u6c14 Air", "M": 0.029, "viscosity": 18.2e-6, "mean_free_path": 68e-9, "gamma": 1.40, "desc": "\u5e38\u89c4\u538b\u7f29\u7a7a\u6c14/\u6c14\u52a8\u7cfb\u7edf"},
    "CH4": {"name": "\u7532\u70f7 Methane", "M": 0.016, "viscosity": 11.0e-6, "mean_free_path": 54e-9, "gamma": 1.32, "desc": "\u5929\u7136\u6c14/\u7532\u70f7\u53d1\u52a8\u673a"},
}

CONTACT_TYPES = {
    "sphere_on_cone": {"name": "\u7403\u5934-\u9525\u9762\u5bc6\u5c01", "desc": "\u6700\u5e38\u89c1\u7684\u822a\u5929\u9600\u95e8\u5bc6\u5c01\u7ed3\u6784\uff0c\u63a8\u8fdb\u5242/\u52a0\u6ce8\u9600\u95e8"},
    "concave_on_cone": {"name": "\u51f9\u9762-\u9525\u9762\u5bc6\u5c01", "desc": "\u65b0\u578b\u8bbe\u8ba1\uff0c\u8d85\u9ad8\u538b\u6c22\u9600\u7b49\u6781\u7aef\u5de5\u51b5"},
    "sphere_on_flat": {"name": "\u7403\u5934-\u5e73\u9762\u5bc6\u5c01", "desc": "\u8f85\u52a9\u5bc6\u5c01\u6216\u7279\u5b9a\u7ed3\u6784"},
    "cylinder_on_flat": {"name": "\u5706\u67f1-\u5e73\u9762\u5bc6\u5c01", "desc": "\u7ebf\u63a5\u89e6\u5f62\u5f0f\uff0c\u8f85\u52a9/\u5bfc\u5411\u5bc6\u5c01"},
}

PRESETS = [
    {
        "id": "lox_valve", "label": "\u6db2\u6c27\u52a0\u6ce8\u9600\u95e8",
        "params": {"seat_diameter_mm": 15.0, "pressure_bar": 10.0, "temperature_C": -183.0,
                   "seat_material": "INCONEL_718", "seal_material": "PCTFE",
                   "contact_type": "sphere_on_cone", "seat_angle_deg": 60.0,
                   "sphere_radius_mm": 7.5, "roughness_Ra_um": 0.2,
                   "gas": "O2", "target_leak_class": "AA"},
        "note": "\u6db2\u6c27\u5de5\u51b5 (-183\u00b0C)\uff0c\u91d1\u5c5e-\u805a\u5408\u7269\u5bc6\u5c01\uff0c\u96f6\u6cc4\u6f0f\u8981\u6c42"
    },
    {
        "id": "hp_helium", "label": "\u9ad8\u538b\u6c26\u6c14\u622a\u6b62\u9600",
        "params": {"seat_diameter_mm": 6.0, "pressure_bar": 350.0, "temperature_C": 20.0,
                   "seat_material": "17_4PH", "seal_material": "316L_SS",
                   "contact_type": "concave_on_cone", "seat_angle_deg": 45.0,
                   "sphere_radius_mm": 5.73, "roughness_Ra_um": 0.1,
                   "gas": "He", "target_leak_class": "B",
                   "seal_force_N": 8000.0},
        "note": "35 MPa\u9ad8\u538b\u6c26\u6c14\uff0c\u91d1\u5c5e-\u91d1\u5c5e\u786c\u5bc6\u5c01\uff0c\u51f9\u9762\u63a5\u89e6\u65b0\u578b\u8bbe\u8ba1"
    },
    {
        "id": "lh2_valve", "label": "\u6db2\u6c22\u71c3\u6599\u9600\u95e8",
        "params": {"seat_diameter_mm": 8.0, "pressure_bar": 20.0, "temperature_C": -253.0,
                   "seat_material": "INCONEL_718", "seal_material": "PCTFE",
                   "contact_type": "sphere_on_cone", "seat_angle_deg": 55.0,
                   "sphere_radius_mm": 4.0, "roughness_Ra_um": 0.15,
                   "gas": "H2", "target_leak_class": "AA"},
        "note": "\u6db2\u6c22\u5de5\u51b5 (-253\u00b0C)\uff0c\u8d85\u4f4e\u6e29\u573a\u5408\uff0c\u96f6\u6cc4\u6f0f\u8981\u6c42"
    },
    {
        "id": "gn2_standard", "label": "\u6c2e\u6c14\u5de5\u4e1a\u9600\u95e8",
        "params": {"seat_diameter_mm": 10.0, "pressure_bar": 5.0, "temperature_C": 20.0,
                   "seat_material": "316L_SS", "seal_material": "PTFE",
                   "contact_type": "sphere_on_cone", "seat_angle_deg": 60.0,
                   "sphere_radius_mm": 5.0, "roughness_Ra_um": 0.4,
                   "gas": "N2", "target_leak_class": "A"},
        "note": "\u5e38\u89c4\u5de5\u4e1a\u5de5\u51b5\uff0c\u91d1\u5c5e-PTFE\u8f6f\u5bc6\u5c01\uff0c\u901a\u7528\u914d\u7f6e"
    },
        {
        "id": "ti_peek", "label": "\u949b\u5408\u91d1-PEEK\u8f7b\u91cf\u5316\u65b9\u6848",
        "params": {"seat_diameter_mm": 12.0, "pressure_bar": 15.0, "temperature_C": -50.0,
                   "seat_material": "TI_6AL4V", "seal_material": "PEEK",
                   "contact_type": "sphere_on_cone", "seat_angle_deg": 60.0,
                   "sphere_radius_mm": 6.0, "roughness_Ra_um": 0.3,
                   "gas": "Air", "target_leak_class": "A"},
        "note": "\u8f7b\u91cf\u5316\u65b9\u6848\uff0c\u949b\u5408\u91d1\u9600\u4f53 + PEEK\u5bc6\u5c01\uff0c\u9002\u5408\u5bf9\u91cd\u91cf\u654f\u611f\u573a\u5408"
    },
]


# ==================== Hertz Contact Mechanics ====================

def _sphere_on_flat(force, R_sphere, E_star):
    a = (3.0 * force * R_sphere / (4.0 * E_star)) ** (1.0 / 3.0)
    p_max = 3.0 * force / (2.0 * math.pi * a ** 2)
    p_avg = force / (math.pi * a ** 2)
    approach = a ** 2 / R_sphere
    return p_max, p_avg, a, approach


def _sphere_on_cone(force, R_sphere, alpha_deg, E_star):
    alpha_rad = math.radians(alpha_deg)
    R_equiv = R_sphere / math.sin(alpha_rad) if alpha_rad > 0.01 else R_sphere
    p_max, p_avg, a, approach = _sphere_on_flat(force, R_equiv, E_star)
    contact_hw = a / math.cos(alpha_rad)
    p_avg_corrected = force / (math.pi * a * contact_hw)
    return p_max, p_avg_corrected, contact_hw, approach


def _concave_on_cone(force, R_plunger, R_seat, e, alpha_deg, E_star):
    alpha_rad = math.radians(alpha_deg)
    R_equiv = 1.0 / abs(1.0 / R_plunger - 1.0 / R_seat)
    if e > 0:
        R_equiv *= (1.0 + e / R_plunger)
    p_max, p_avg, a, approach = _sphere_on_flat(force, R_equiv, E_star)
    contact_hw = a / math.cos(alpha_rad)
    p_avg_corrected = force / (math.pi * a * contact_hw)
    return p_max, p_avg_corrected, contact_hw, approach


def _cylinder_on_flat(force, L_contact, R_cylinder, E_star):
    f_line = force / L_contact
    b = math.sqrt(4.0 * f_line * R_cylinder / (math.pi * E_star))
    p_max = 2.0 * f_line / (math.pi * b)
    p_avg = f_line / (2.0 * b)
    return p_max, p_avg, b


# ==================== Leak Rate (Roth Model) ====================

def _estimate_gap(Ra1, Ra2, contact_stress, hardness_softer):
    sigma_rough = math.sqrt(Ra1 ** 2 + Ra2 ** 2)
    if hardness_softer > 0:
        p_ratio = min(contact_stress / hardness_softer, 0.95)
    else:
        p_ratio = 0.95
    gap = sigma_rough * (1.0 - p_ratio) ** 1.5
    return max(gap, 1e-12)


def _molecular_leak(p_up, p_down, gap, perimeter, contact_width, M, T):
    if gap <= 0 or contact_width <= 0:
        return 0.0
    v_mean = math.sqrt(2.0 * math.pi * R_GAS * T / M)
    Q = (4.0 / 3.0) * v_mean * (gap ** 2 / contact_width) * (p_up - p_down) * perimeter
    return max(Q, 0.0)


def _viscous_leak(p_up, p_down, gap, perimeter, contact_width, viscosity):
    if gap <= 0 or contact_width <= 0:
        return 0.0
    p_avg = (p_up + p_down) / 2.0 if p_up > 0 else p_up
    Q = (math.pi * gap ** 3 / (12.0 * viscosity * contact_width)) * (p_up - p_down) * p_avg * perimeter
    return max(Q, 0.0)


def _transitional_leak(p_up, p_down, gap, perimeter, contact_width, M, viscosity, Kn, T):
    Q_mol = _molecular_leak(p_up, p_down, gap, perimeter, contact_width, M, T)
    Q_vis = _viscous_leak(p_up, p_down, gap, perimeter, contact_width, viscosity)
    if Kn <= 0.01:
        w_mol = 0.0
    elif Kn >= 1.0:
        w_mol = 1.0
    else:
        log_Kn = math.log10(Kn)
        w_mol = (log_Kn - math.log10(0.01)) / (math.log10(1.0) - math.log10(0.01))
    return w_mol * Q_mol + (1.0 - w_mol) * Q_vis


def _convert_leak_units(Q_Pa_m3_s, T=T_STANDARD):
    return {
        "Pa_m3_s": Q_Pa_m3_s,
        "mbar_L_s": Q_Pa_m3_s * 10.0,
        "sccm": Q_Pa_m3_s / P_STANDARD * 60.0 * 1e6,
        "atm_cc_s": Q_Pa_m3_s / P_STANDARD * 1e6,
    }


def _classify_leak(Q_Pa_m3_s, DN=10.0):
    Q_mm3 = Q_Pa_m3_s * 1e6 / 1000.0
    Q_per_DN = Q_mm3 / DN if DN > 0 else float('inf')
    for lc in ["AA", "A", "B", "C", "D", "E", "EE", "F", "G"]:
        if Q_per_DN <= LEAK_CLASS_COEFFICIENTS[lc] * DN:
            return lc
    return "G"


def _find_critical_force(contact_type, geometry, E_star, hardness_softer, dp, min_ratio, max_iter=50, tol=1e-3):
    perimeter = math.pi * geometry["seat_diameter"]
    F_low, F_high = 0.1, 1e6
    F_critical = F_high
    for _ in range(max_iter):
        F_mid = (F_low + F_high) / 2.0
        p_max, p_avg, contact_hw, _ = _calc_hertz(contact_type, geometry, F_mid, E_star)
        ratio = p_avg / dp if dp > 0 else float('inf')
        if ratio >= min_ratio:
            F_critical = F_mid
            F_high = F_mid
        else:
            F_low = F_mid
        if F_low > 0 and (F_high - F_low) / F_low < tol:
            break
    return F_critical


def _calc_hertz(contact_type, geometry, force, E_star):
    ct = contact_type
    if ct == "sphere_on_cone":
        R = geometry.get("sphere_radius", 5e-3)
        return _sphere_on_cone(force, R, geometry["seat_angle"], E_star)
    elif ct == "concave_on_cone":
        R_plunger = geometry.get("sphere_radius", 5e-3)
        R_seat = geometry.get("seat_curvature_radius", 4.5e-3)
        return _concave_on_cone(force, R_plunger, R_seat,
                                geometry.get("eccentricity", 0.0),
                                geometry["seat_angle"], E_star)
    elif ct == "cylinder_on_flat":
        L = math.pi * geometry["seat_diameter"]
        R = geometry.get("sphere_radius", 5e-3)
        p_max, p_avg, b = _cylinder_on_flat(force, L, R, E_star)
        return p_max, p_avg, b, 0.0
    else:  # sphere_on_flat
        R = geometry.get("sphere_radius", 5e-3)
        return _sphere_on_flat(force, R, E_star)


# ==================== Main Design Function ====================

def calculate_seal_design(params: dict) -> dict:
    """
    Main seal pair design calculation.
    Returns JSON-ready result dict.
    """
    # --- Parse inputs ---
    mat_seat = MATERIALS[params["seat_material"]]
    mat_seal = MATERIALS[params["seal_material"]]
    gas = GASES.get(params.get("gas", "N2"), GASES["N2"])
    contact_type = params.get("contact_type", "sphere_on_cone")

    T_K = params.get("temperature_C", 20.0) + 273.15
    P_up = params.get("pressure_bar", 10.0) * 1e5
    P_down = params.get("pressure_downstream_bar", 0.0) * 1e5
    dp = P_up - P_down

    seat_d = params.get("seat_diameter_mm", 10.0) * 1e-3
    seat_angle = params.get("seat_angle_deg", 60.0)
    R_sphere = params.get("sphere_radius_mm", 5.0) * 1e-3
    R_seat_curv = params.get("seat_curvature_radius_mm", 4.5) * 1e-3
    roughness = params.get("roughness_Ra_um", 0.4) * 1e-6
    seat_width = params.get("seat_width_mm", 1.5) * 1e-3
    eccentricity = params.get("eccentricity_mm", 0.0) * 1e-3
    seal_force_input = params.get("seal_force_N")
    preload_force = params.get("preload_force_N", 0.0)
    spring_force = params.get("spring_force_N", 0.0)
    target_lc = params.get("target_leak_class", "A")
    min_sf = params.get("min_safety_factor", 1.5)
    cycle_life_req = params.get("cycle_life_req", 10000)

    # --- Seal type ---
    if mat_seat["category"] == "metal" and mat_seal["category"] == "metal":
        seal_type = "metal-metal"
        min_ratio = 1.8
    elif mat_seal["category"] == "elastomer":
        seal_type = "metal-elastomer"
        min_ratio = 1.2
    else:
        seal_type = "metal-polymer"
        min_ratio = 1.2

    # --- Effective modulus ---
    E_star = 1.0 / ((1.0 - mat_seat["nu"] ** 2) / mat_seat["E"] + (1.0 - mat_seal["nu"] ** 2) / mat_seal["E"])

    # --- Warnings ---
    warnings = []
    T_C = params.get("temperature_C", 20.0)
    if not mat_seat["cryo_compatible"] and T_C < mat_seat["min_temp"]:
        warnings.append(f"阀座材料 {mat_seat['name_cn']} 不适于 {T_C:.0f}°C 低温工况 (最低 {mat_seat['min_temp']}°C)")
    if not mat_seal["cryo_compatible"] and T_C < mat_seal["min_temp"]:
        warnings.append(f"密封材料 {mat_seal['name_cn']} 不适于 {T_C:.0f}°C 低温工况 (最低 {mat_seal['min_temp']}°C)")

    # --- Seal force ---
    geometry = {
        "seat_diameter": seat_d, "seat_angle": seat_angle,
        "sphere_radius": R_sphere, "seat_curvature_radius": R_seat_curv,
        "seat_width": seat_width, "eccentricity": eccentricity,
    }
    hardness_softer = min(mat_seat.get("sigma_y", 205e6), mat_seal.get("sigma_y", 14e6))

    if seal_force_input is None:
        F_critical = _find_critical_force(contact_type, geometry, E_star, hardness_softer, dp, min_ratio)
        F_seal = F_critical * min_sf
        if preload_force:
            F_seal = max(F_seal, preload_force)
        F_seal += spring_force
    else:
        F_seal = seal_force_input
        F_critical = F_seal / min_sf

    # --- Hertz ---
    perimeter = math.pi * seat_d
    if contact_type == "cylinder_on_flat":
        L_contact = perimeter
        p_max, p_avg, contact_hw = _cylinder_on_flat(F_seal, L_contact, R_sphere, E_star)
        approach = 0.0
    else:
        p_max, p_avg, contact_hw, approach = _calc_hertz(contact_type, geometry, F_seal, E_star)

    if "cone" in contact_type:
        contact_area = perimeter * contact_hw * 2.0
    else:
        contact_area = perimeter * contact_hw * 2.0

    # --- Seal state ---
    ratio = p_avg / dp if dp > 0 else float('inf')
    is_sealing = ratio >= min_ratio

    # --- Leak ---
    gap = _estimate_gap(roughness, roughness, p_avg, hardness_softer)
    lambda_gas = gas["mean_free_path"] * (T_K / T_STANDARD) * (P_STANDARD / max(P_up, 1.0))
    Kn = lambda_gas / gap if gap > 0 else float('inf')

    if Kn > 1.0:
        flow_regime = "\u5206\u5b50\u6d41"
        Q_leak = _molecular_leak(P_up, P_down, gap, perimeter, contact_hw * 2.0, gas["M"], T_K)
    elif Kn < 0.01:
        flow_regime = "\u7c98\u6027\u6d41"
        Q_leak = _viscous_leak(P_up, P_down, gap, perimeter, contact_hw * 2.0, gas["viscosity"])
    else:
        flow_regime = "\u8fc7\u6e21\u6d41"
        Q_leak = _transitional_leak(P_up, P_down, gap, perimeter, contact_hw * 2.0,
                                     gas["M"], gas["viscosity"], Kn, T_K)

    Q_units = _convert_leak_units(Q_leak, T_K)
    DN = seat_d * 1000.0
    leak_class = _classify_leak(Q_leak, DN)

    # --- Safety ---
    str_y = p_max / mat_seat["sigma_y"] if mat_seat["sigma_y"] > 0 else float('inf')
    str_u = p_max / mat_seat["sigma_uts"] if mat_seat["sigma_uts"] > 0 else float('inf')
    sf_y = 1.0 / str_y if str_y > 0 else float('inf')
    sf_u = 1.0 / str_u if str_u > 0 else float('inf')
    safety_pass = sf_y >= min_sf and sf_u >= 2.5 and str_y <= 0.85

    # --- Reliability ---
    wear_coeff = 1e-8 if seal_type != "metal-metal" else 1e-5
    wear_depth = wear_coeff * p_max * (cycle_life_req * 0.1e-3) / hardness_softer if hardness_softer > 0 else 0.0
    ratio_fatigue = p_max / mat_seat["sigma_y"] if mat_seat["sigma_y"] > 0 else 1.0
    N_life = 1e6 * ratio_fatigue ** (1.0 / -0.12) if ratio_fatigue < 1.0 else 1e3
    N_life = min(N_life, 1e9)
    beta = (sf_y - 1.0) / (0.15 * sf_y) if sf_y > 0 else 0.0

    est_mass = math.pi * (seat_d / 2) ** 2 * seat_width * mat_seat["density"] * 2.0

    # --- Recommendations ---
    recs = []
    if not is_sealing:
        recs.append(f"密封比压不足 (当前 {ratio:.2f}, 要求 {min_ratio:.2f})。建议增大密封力或减小接触面积。")
    if not safety_pass:
        recs.append(f"安全系数不足 (屈服SF={sf_y:.2f})。建议更换更高强度材料或增大接触面积。")
    if leak_class != "AA" and LEAK_CLASS_COEFFICIENTS.get(leak_class, 0) > LEAK_CLASS_COEFFICIENTS.get(target_lc, 0):
        recs.append(f"泄漏等级未达标 (当前 {leak_class}级, 目标 {target_lc}级)。建议降低表面粗糙度或增大接触应力。")
    if N_life < cycle_life_req:
        recs.append(f"预估寿命不足 (当前 {N_life:.0f}次, 要求 {cycle_life_req}次)。建议降低接触应力或选用更耐磨材料。")

    return _clean({
        "success": True,
        "input": {
            "seal_type": seal_type,
            "contact_type": contact_type,
            "contact_type_cn": CONTACT_TYPES.get(contact_type, {}).get("name", contact_type),
            "seat_material_key": params["seat_material"],
            "seat_material": mat_seat["name_cn"],
            "seal_material_key": params["seal_material"],
            "seal_material": mat_seal["name_cn"],
            "gas": gas["name"],
            "seat_diameter_mm": seat_d * 1000,
            "seat_angle_deg": seat_angle,
            "pressure_bar": params.get("pressure_bar", 10.0),
            "temperature_C": T_C,
            "seal_force_N": F_seal,
            "target_leak_class": target_lc,
            "roughness_Ra_um": roughness * 1e6,
        },
        "contact": {
            "effective_modulus_GPa": E_star / 1e9,
            "p_max_MPa": p_max / 1e6,
            "p_avg_MPa": p_avg / 1e6,
            "contact_width_um": contact_hw * 1e6 * 2.0,
            "contact_area_mm2": contact_area * 1e6,
            "approach_um": approach * 1e6,
        },
        "seal_state": {
            "seal_pressure_MPa": p_avg / 1e6,
            "seal_pressure_ratio": ratio,
            "min_ratio_required": min_ratio,
            "is_sealing": is_sealing,
            "critical_seal_force_N": F_critical,
        },
        "leak": {
            "flow_regime": flow_regime,
            "knudsen_number": Kn,
            "effective_gap_um": gap * 1e6,
            "leak_rate_Pa_m3_s": Q_leak,
            "leak_rate_mbar_L_s": Q_units["mbar_L_s"],
            "leak_rate_sccm": Q_units["sccm"],
            "leak_rate_atm_cc_s": Q_units["atm_cc_s"],
            "leak_class": leak_class,
            "leak_class_info": LEAK_CLASS_INFO.get(leak_class, {}),
            "target_leak_class": target_lc,
        },
        "safety": {
            "p_max_MPa": p_max / 1e6,
            "sigma_y_MPa": mat_seat["sigma_y"] / 1e6,
            "sigma_uts_MPa": mat_seat["sigma_uts"] / 1e6,
            "stress_ratio_yield": str_y,
            "stress_ratio_uts": str_u,
            "safety_factor_yield": sf_y,
            "safety_factor_uts": sf_u,
            "safety_pass": safety_pass,
            "min_sf_required": min_sf,
        },
        "reliability": {
            "predicted_cycle_life": N_life,
            "required_cycle_life": cycle_life_req,
            "wear_depth_um": wear_depth * 1e6,
            "reliability_index": beta,
            "estimated_mass_g": est_mass * 1e3,
        },
        "warnings": warnings,
        "recommendations": recs,
    })


def run_compare(configs: list, gas="N2") -> list:
    """Compare multiple seal designs."""
    results = []
    for cfg in configs:
        r = calculate_seal_design(cfg)
        results.append(r)
    return results


def run_sensitivity(base_config: dict, param_name: str, param_values: list) -> list:
    """Run single-parameter sensitivity analysis."""
    results = []
    for val in param_values:
        cfg = base_config.copy()
        cfg[param_name] = val
        r = calculate_seal_design(cfg)
        results.append({
            "param_value": val,
            "leak_rate_mbar_L_s": r["leak"]["leak_rate_mbar_L_s"],
            "p_max_MPa": r["contact"]["p_max_MPa"],
            "safety_factor_yield": r["safety"]["safety_factor_yield"],
            "safety_pass": r["safety"]["safety_pass"],
            "leak_class": r["leak"]["leak_class"],
            "is_sealing": r["seal_state"]["is_sealing"],
        })
    return results


def get_catalog():
    """Return the full data catalog for the frontend."""
    return {
        "materials": {k: {"key": k, "name_cn": v["name_cn"], "name": v["name"],
                          "category": v["category"], "cryo_compatible": v["cryo_compatible"],
                          "E_GPa": v["E"] / 1e9, "sigma_y_MPa": v["sigma_y"] / 1e6,
                          "density": v["density"], "desc": v["desc"]} for k, v in MATERIALS.items()},
        "gases": {k: {"key": k, "name": v["name"], "M": v["M"],
                      "viscosity": v["viscosity"], "desc": v["desc"]} for k, v in GASES.items()},
        "contact_types": CONTACT_TYPES,
        "leak_classes": LEAK_CLASS_INFO,
        "presets": PRESETS,
        "standards": [
            {"id": "ISO 5208-2015", "desc": "\u5de5\u4e1a\u9600\u95e8\u538b\u529b\u8bd5\u9a8c"},
            {"id": "ANSI/FCI 70-2-2013", "desc": "\u63a7\u5236\u9600\u9600\u5ea7\u6cc4\u6f0f"},
            {"id": "ECSS-E-ST-32-02C", "desc": "\u538b\u529b\u786c\u4ef6\u7ed3\u6784\u8bbe\u8ba1\u4e0e\u9a8c\u8bc1"},
            {"id": "NASA-STD-5012", "desc": "\u822a\u5929\u7ea7\u5bc6\u5c01\u6027\u80fd\u6307\u6807"},
        ],
        "theory": [
            {
                "name": "Hertz\u5f39\u6027\u63a5\u89e6\u7406\u8bba",
                "desc": "\u8ba1\u7b97\u5bc6\u5c01\u9762\u63a5\u89e6\u5e94\u529b\u3001\u63a5\u89e6\u5bbd\u5ea6\u548c\u8d8b\u8fd1\u91cf",
                "limits": "\u5047\u8bbe\u7406\u60f3\u5f39\u6027\u4f53\u3001\u5c0f\u53d8\u5f62\u3001\u65e0\u6469\u64e6\u5149\u6ed1\u8868\u9762\uff0c\u5f53\u63a5\u89e6\u5e94\u529b/\u5c48\u670d\u5f3a\u5ea6>0.7\u65f6\u504f\u4fdd\u5b88"
            },
            {
                "name": "Roth\u5206\u5b50\u6d41\u6cc4\u6f0f\u6a21\u578b",
                "desc": "\u57fa\u4e8e\u514b\u52aa\u68ee\u6570 (Kn) \u8fdb\u884c\u6d41\u6001\u5224\u65ad\uff0c\u5206\u5b50\u6d41/\u7c98\u6027\u6d41\u5206\u754c\u8ba1\u7b97",
                "limits": "\u57fa\u4e8e\u5149\u6ed1\u5e73\u884c\u677f\u95f4\u9699\u5047\u8bbe\uff0c\u8fc7\u6e21\u6d41\u91c7\u7528\u5bf9\u6570\u63d2\u503c\u8fd1\u4f3c"
            },
            {
                "name": "Archard\u78e8\u635f\u6a21\u578b",
                "desc": "\u9884\u4f30\u5bc6\u5c01\u9762\u78e8\u635f\u6df1\u5ea6\u548c\u542f\u95ed\u5bff\u547d",
                "limits": "\u78e8\u635f\u7cfb\u6570\u4e3a\u5178\u578b\u503c\uff0c\u5b9e\u9645\u503c\u9700\u901a\u8fc7\u78e8\u635f\u8bd5\u9a8c\u786e\u5b9a"
            },
        ],
    }