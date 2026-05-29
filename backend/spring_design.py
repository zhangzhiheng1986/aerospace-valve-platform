# -*- coding: utf-8 -*-
"""
Aerospace Helical Compression Spring Design Module - Web API
Based on deepseek_python_20260518_a3d933.py
"""

import math
from typing import Dict, Optional, List

MATERIALS_DB = {
    "SWP-A": {"name": "琴钢丝 (通用级)", "G": 80000, "E": 206000, "rho": 7.85e-9,
              "tau_s": 1500, "tau_0": 450, "temp_max": 120},
    "50CrVA": {"name": "合金弹簧钢 (50CrVA)", "G": 79000, "E": 196000, "rho": 7.85e-9,
               "tau_s": 1200, "tau_0": 400, "temp_max": 200},
    "Inconel718": {"name": "镍基高温合金 Inconel 718", "G": 77000, "E": 200000, "rho": 8.19e-9,
                   "tau_s": 1100, "tau_0": 350, "temp_max": 650},
    "TC4": {"name": "钛合金 Ti-6Al-4V", "G": 44000, "E": 110000, "rho": 4.43e-9,
            "tau_s": 900, "tau_0": 300, "temp_max": 400},
}

SUPPORT_TYPES = {
    "fixed_both": ("两端固定", 5.3),
    "fixed_free": ("一端固定一端自由", 3.7),
    "free_both": ("两端自由", 2.6),
}

SF_STATIC = 1.5


def _clean(v):
    """Replace non-JSON-safe values"""
    if isinstance(v, float):
        if math.isinf(v): return 1e9 if v > 0 else 0
        if math.isnan(v): return 0
        return v
    if isinstance(v, dict):
        return {k: _clean(val) for k, val in v.items()}
    if isinstance(v, list):
        return [_clean(x) for x in v]
    return v


def design_spring(data: Dict) -> Dict:
    """Main API entry point"""
    F1 = float(data.get("F1", 50))
    F2 = float(data.get("F2", 150))
    L1_or_Stroke = float(data.get("L1_or_Stroke", 8))
    is_stroke = bool(data.get("is_stroke", True))
    material_name = data.get("material", "Inconel718")
    env_temp = float(data.get("env_temp", 300))
    fatigue_life = float(data.get("fatigue_life", 10000000))
    support_type = data.get("support_type", "fixed_both")
    f_work = float(data.get("f_work", 0))
    iterations = int(data.get("iterations", 15))

    # Validate material
    if material_name not in MATERIALS_DB:
        return {"error": f"Material '{material_name}' not found. Available: {list(MATERIALS_DB.keys())}"}

    mat = MATERIALS_DB[material_name]
    G = mat["G"]
    tau_s = mat["tau_s"]
    tau_0 = mat["tau_0"]

    warnings = []

    # Temperature check
    if env_temp > mat["temp_max"]:
        warnings.append(f"工作温度({env_temp}C)超过材料许用温度({mat['temp_max']}C)")

    # --- Iterative solution ---
    d = 0.5
    D = 8 * d
    n = 5.0
    found = False

    for i in range(iterations):
        C = D / d if d != 0 else 8
        Kw = (4*C - 1) / (4*C - 4) + 0.615 / C
        tau_max_allowed = tau_s / SF_STATIC

        d_new = math.sqrt((8 * Kw * F2 * C) / (math.pi * tau_max_allowed)) if tau_max_allowed > 0 else 1.0
        d = (d + d_new) / 2

        D = 8 * d

        stroke_target = L1_or_Stroke if is_stroke else L1_or_Stroke * 0.2
        k_target = F2 / stroke_target if stroke_target > 0 else F2 / 10
        n_new = (G * d**4) / (8 * D**3 * k_target)
        n = max(3, min(25, round(n_new, 1)))

        if i > 5 and abs(d - d_new) < 0.01:
            found = True
            break

    if not found:
        warnings.append("参数迭代可能未完全收敛，建议人工复核")

    # Store results
    d_val = round(d, 3)
    D_val = round(D, 3)
    n_val = n
    n_total = n_val + 2

    # Geometry
    pitch = D_val / 3.0
    helix_angle = math.atan(pitch / (math.pi * D_val))
    wire_length = math.pi * D_val * n_total / math.cos(helix_angle) if abs(math.cos(helix_angle)) > 1e-6 else 0
    mass_ton = mat["rho"] * (math.pi * d_val**2 / 4) * wire_length
    mass_kg = mass_ton * 1000  # ton -> kg

    # Stiffness & deformation
    k = (G * d_val**4) / (8 * D_val**3 * n_val) if n_val > 0 and D_val > 0 else 0
    delta1 = F1 / k if k > 0 else 0
    delta2 = F2 / k if k > 0 else 0

    # Lengths
    H0 = n_val * pitch + 1.5 * d_val
    H1 = H0 - delta1
    H2 = H0 - delta2
    Hs = n_total * d_val

    # Stress
    C_ratio = D_val / d_val if d_val > 0 else 8
    Kw = (4*C_ratio - 1) / (4*C_ratio - 4) + 0.615 / C_ratio
    tau_max = Kw * (8 * F2 * D_val) / (math.pi * d_val**3) if d_val > 0 else 0
    tau_min = Kw * (8 * F1 * D_val) / (math.pi * d_val**3) if d_val > 0 else 0

    # Safety checks
    sf_static = tau_s / tau_max if tau_max > 0 else 9999

    # Fatigue safety factor
    if tau_max - tau_min <= 0:
        sf_fatigue = 9999
    else:
        sf_fatigue = tau_0 * (1 + tau_min/tau_max) / (tau_max - tau_min)

    # Stability check
    b_ratio = H0 / D_val if D_val > 0 else 0
    limit_b = SUPPORT_TYPES.get(support_type, SUPPORT_TYPES["fixed_both"])[1]
    stability_ok = b_ratio < limit_b
    if not stability_ok:
        warnings.append(f"稳定性不足：高径比b={b_ratio:.2f} > 许用值{limit_b}")

    # Resonance check
    fn = 0.5 * math.sqrt(k / mass_kg) if k > 0 and mass_kg > 0 else 0
    resonance_ok = True
    resonance_info = f"f_n={fn:.1f} Hz"
    if f_work > 0:
        ratio_fn = fn / f_work if fn > 0 else 0
        resonance_info += f", ratio={ratio_fn:.1f}"
        if ratio_fn < 10:
            resonance_ok = False
            warnings.append(f"共振风险：频率比{ratio_fn:.1f} < 10，需调整设计")

    # Static safety check
    if sf_static < SF_STATIC:
        warnings.append(f"静态安全系数{sf_static:.2f} < {SF_STATIC}，强度不足")

    # Solid height check
    if H2 <= Hs:
        warnings.append(f"最大载荷高度H2={H2:.2f}mm接近或低于压并高度Hs={Hs:.2f}mm")

    # Conclusion
    if not warnings:
        conclusion = "设计通过 - 所有指标满足要求"
    elif len([w for w in warnings if "不足" in w or "超限" in w or "风险" in w]) == 0:
        conclusion = "设计通过(有提示信息)"
    else:
        conclusion = f"设计存在{len(warnings)}项问题，需要优化"

    result = {
        "input_summary": {
            "F1": F1, "F2": F2, "stroke_or_L1": L1_or_Stroke,
            "is_stroke": is_stroke, "material": material_name,
            "env_temp_C": env_temp, "fatigue_life": fatigue_life,
            "support_type": support_type, "work_freq_Hz": f_work
        },
        "geometry": {
            "wire_diameter_mm": d_val,
            "mean_diameter_mm": D_val,
            "outer_diameter_mm": round(D_val + d_val, 3),
            "inner_diameter_mm": round(D_val - d_val, 3),
            "spring_index_C": round(C_ratio, 3),
            "active_coils_n": n_val,
            "total_coils_nt": n_total,
            "pitch_p_mm": round(pitch, 3),
            "helix_angle_deg": round(math.degrees(helix_angle), 3),
            "wire_length_mm": round(wire_length, 3),
            "free_height_H0_mm": round(H0, 3),
            "working_height_H1_mm": round(H1, 3),
            "max_load_height_H2_mm": round(H2, 3),
            "solid_height_Hs_mm": round(Hs, 3),
        },
        "mechanics": {
            "stiffness_k_Nmm": round(k, 4),
            "deformation_delta1_mm": round(delta1, 4),
            "deformation_delta2_mm": round(delta2, 4),
            "max_shear_stress_tau_max_MPa": round(tau_max, 3),
            "min_shear_stress_tau_min_MPa": round(tau_min, 3),
            "wahl_factor_Kw": round(Kw, 4),
        },
        "checks": {
            "static_safety_factor": round(sf_static, 3),
            "static_safe": sf_static >= SF_STATIC,
            "static_allowable": SF_STATIC,
            "fatigue_safety_factor": round(sf_fatigue, 3),
            "slenderness_ratio_b": round(b_ratio, 3),
            "stability_limit": limit_b,
            "stability_ok": stability_ok,
            "natural_frequency_Hz": round(fn, 2),
            "resonance_info": resonance_info,
            "resonance_ok": resonance_ok,
        },
        "mass": {
            "mass_kg": round(mass_kg, 6),
            "mass_g": round(mass_kg * 1000, 3),
        },
        "material_info": {
            "key": material_name,
            "name": mat["name"],
            "G_MPa": mat["G"],
            "E_MPa": mat["E"],
            "tau_s_MPa": mat["tau_s"],
            "tau_0_MPa": mat["tau_0"],
            "temp_max_C": mat["temp_max"],
        },
        "warnings": warnings,
        "conclusion": conclusion,
    }

    return _clean(result)


def get_materials_list() -> List[Dict]:
    """Return available materials with properties summary"""
    return [
        {"key": k, "name": v["name"], "tau_s": v["tau_s"], "tau_0": v["tau_0"],
         "temp_max": v["temp_max"], "density_g_cm3": round(v["rho"]*1e6, 2)}
        for k, v in MATERIALS_DB.items()
    ]
