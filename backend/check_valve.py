# -*- coding: utf-8 -*-
"""
Aerospace Check Valve Design Module - Web API Wrapper
Based on deepseek_python_20260518_dbbe9a.py v2.0
Standards: HB 6456-2014, QJ 1142A-2008
"""

import math
from dataclasses import dataclass, asdict, field
from typing import Dict, Tuple, Optional, List
from enum import Enum


class MediumType(Enum):
    HYDRAULIC_OIL = "hydraulic_oil"
    HYDRAULIC_OIL_5606 = "hydraulic_oil_5606"
    SKYDROL = "skydrol"
    NITROGEN = "nitrogen"
    HELIUM = "helium"
    FUEL_JET_A = "fuel_jet_a"
    UDMH = "udmh"
    N2O4 = "n2o4"

class ValveType(Enum):
    POPPET_CONICAL = "poppet_conical"
    POPPET_BALL = "poppet_ball"
    POPPET_FLAT = "poppet_flat"
    DISC_SPRING = "disc_spring"
    SWING = "swing"

class SealType(Enum):
    METAL_TO_METAL = "metal_to_metal"
    SOFT_SEAT = "soft_seat"
    ELASTOMER_O_RING = "elastomer_o_ring"

class SpringMaterial(Enum):
    STAINLESS_302 = "ss302"
    STAINLESS_316 = "ss316"
    INCONEL_X750 = "inconel_x750"
    INCONEL_718 = "inconel_718"
    MP35N = "mp35n"
    ELGILOY = "elgiloy"


MEDIUM_DB = {
    "hydraulic_oil": {"name":"液压油 (MIL-PRF-83282)","density":840,"viscosity":0.014,"bulk_modulus":1.5e9,"vapor_pressure":1000,"is_gas":False,"sound_speed":1350},
    "hydraulic_oil_5606": {"name":"液压油 (MIL-PRF-5606)","density":860,"viscosity":0.015,"bulk_modulus":1.4e9,"vapor_pressure":800,"is_gas":False,"sound_speed":1300},
    "skydrol": {"name":"磷酸酯液压油 (Skydrol)","density":1000,"viscosity":0.012,"bulk_modulus":2.0e9,"vapor_pressure":500,"is_gas":False,"sound_speed":1400},
    "nitrogen": {"name":"氮气","density":1.138,"viscosity":1.76e-5,"bulk_modulus":1.4,"vapor_pressure":0,"is_gas":True,"sound_speed":353},
    "helium": {"name":"氦气","density":0.164,"viscosity":1.96e-5,"bulk_modulus":1.667,"vapor_pressure":0,"is_gas":True,"sound_speed":1007},
    "fuel_jet_a": {"name":"航空煤油 (Jet A-1)","density":804,"viscosity":0.0016,"bulk_modulus":1.3e9,"vapor_pressure":1000,"is_gas":False,"sound_speed":1280},
    "udmh": {"name":"偏二甲肼 (UDMH)","density":791,"viscosity":0.0005,"bulk_modulus":1.2e9,"vapor_pressure":16000,"is_gas":False,"sound_speed":1200},
    "n2o4": {"name":"四氧化二氮 (N2O4)","density":1443,"viscosity":0.00042,"bulk_modulus":1.8e9,"vapor_pressure":96000,"is_gas":False,"sound_speed":1100},
}

SPRING_MAT_DB = {
    "ss302": {"name":"不锈钢 302","G":69500,"E":193000,"density":7920,"allowable_stress":450,"temp_max":250,"fatigue_limit":240},
    "ss316": {"name":"不锈钢 316","G":69000,"E":193000,"density":8000,"allowable_stress":400,"temp_max":300,"fatigue_limit":200},
    "inconel_x750": {"name":"Inconel X-750","G":76000,"E":214000,"density":8250,"allowable_stress":650,"temp_max":700,"fatigue_limit":350},
    "inconel_718": {"name":"Inconel 718","G":77200,"E":205000,"density":8190,"allowable_stress":720,"temp_max":650,"fatigue_limit":400},
    "mp35n": {"name":"MP35N","G":80000,"E":234000,"density":8430,"allowable_stress":850,"temp_max":400,"fatigue_limit":480},
    "elgiloy": {"name":"Elgiloy","G":78000,"E":206000,"density":8300,"allowable_stress":780,"temp_max":450,"fatigue_limit":420},
}

BODY_MAT_DB = {
    "Ti-6Al-4V": {"yield":880,"ultimate":950,"density":4430,"E":114000,"temp_max":400,"name":"钛合金 Ti-6Al-4V"},
    "15-5PH": {"yield":1000,"ultimate":1070,"density":7800,"E":196000,"temp_max":315,"name":"沉淀硬化钢 15-5PH"},
    "17-4PH": {"yield":1000,"ultimate":1070,"density":7800,"E":196000,"temp_max":315,"name":"沉淀硬化钢 17-4PH"},
    "Inconel718": {"yield":1034,"ultimate":1275,"density":8190,"E":205000,"temp_max":650,"name":"镍基合金 Inconel 718"},
    "304L": {"yield":205,"ultimate":515,"density":8000,"E":193000,"temp_max":300,"name":"奥氏体不锈钢 304L"},
    "Al7075": {"yield":434,"ultimate":503,"density":2810,"E":71700,"temp_max":175,"name":"铝合金 7075-T73"},
}

SEAL_MAT_DB = {
    "metal_to_metal": {"name":"金属-金属硬密封","qb":30.0,"q_allow":400.0,"leak_factor":0.001},
    "soft_seat": {"name":"软阀座密封 (PTFE/PCTFE)","qb":5.0,"q_allow":30.0,"leak_factor":0.0001},
    "elastomer_o_ring": {"name":"弹性体O形圈密封","qb":1.5,"q_allow":10.0,"leak_factor":0.00005},
}

VALVE_TYPE_NAMES = {
    "poppet_conical": "锥阀芯式", "poppet_ball": "球阀芯式",
    "poppet_flat": "平面阀芯式", "disc_spring": "盘式/簧片式", "swing": "旋启式"
}
SEAL_TYPE_NAMES = {
    "metal_to_metal": "金属-金属硬密封", "soft_seat": "软阀座密封 (PTFE/PCTFE)",
    "elastomer_o_ring": "弹性体O形圈密封"
}
SPRING_MAT_NAMES = {k: v["name"] for k, v in SPRING_MAT_DB.items()}


class SpringDesigner:
    @staticmethod
    def wahl_factor(C):
        return (4*C-1)/(4*C-4) + 0.615/C

    @staticmethod
    def stiffness(d, D2, n, G):
        return G * d**4 / (8.0 * D2**3 * n) if D2 > 0 and n > 0 else 0

    @staticmethod
    def stress(F, d, D2):
        if d <= 0: return 0, 0
        C = D2 / d
        K = SpringDesigner.wahl_factor(C)
        return K * 8.0 * F * D2 / (math.pi * d**3), K

    @staticmethod
    def natural_freq(d, D2, n, G, rho):
        if D2 <= 0 or n <= 0 or rho <= 0: return 0
        return abs(d * math.sqrt(G*1000/(2*rho)) / (2*math.pi*n*D2**2))

    @staticmethod
    def check_buckling(H0, D2, F_max, G, d, n):
        b = H0/D2 if D2 > 0 else 0
        if b <= 2.6: return True, float('inf')
        I = math.pi * d**4 / 64
        F_cr = math.pi**2 * G*1000 * I / (0.7*H0)**2 if H0 > 0 else float('inf')
        return F_max <= F_cr, F_cr

    @classmethod
    def design(cls, spring_force, avail_diam, avail_len, mat_props, sf=1.5, cracking_p=0, cracking_a=0):
        G = mat_props["G"]; tau_allow = mat_props["allowable_stress"]
        std_diams = [0.3,0.4,0.5,0.6,0.7,0.8,1.0,1.2,1.4,1.6,1.8,2.0,2.3,2.5,2.8,3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5,7.0,8.0,9.0,10.0]
        best = None
        for d in std_diams:
            D2 = avail_diam - d - 2.0
            if D2 <= d*3: continue
            C = D2/d
            if C < 3 or C > 16: continue
            K = cls.wahl_factor(C)
            tau_chk = K * 8.0 * spring_force * D2 / (math.pi * d**3)
            if tau_chk > tau_allow/sf: continue
            k_tgt = spring_force / 2.0
            n = G * d**4 / (8.0 * D2**3 * k_tgt) if k_tgt > 0 else 10
            n = max(2.0, min(20.0, n))
            k_act = cls.stiffness(d, D2, n, G)
            lam_max = spring_force*2.0 / k_act if k_act > 0 else 0
            H0 = (n+2)*d + lam_max + 0.1*d*n
            if H0 > avail_len or D2+d > avail_diam: continue
            F_max = spring_force*2.0
            tau_max, _ = cls.stress(F_max, d, D2)
            if tau_max > tau_allow/sf: continue
            buck_ok, F_cr = cls.check_buckling(H0, D2, F_max, G, d, n)
            fn = cls.natural_freq(d, D2, n, G, mat_props.get("density",8000))
            score = abs(C-8) + abs(H0 - avail_len*0.6)
            if best is None or score < best[0]:
                best = (score, d, D2, n, k_act, F_max, tau_max, tau_allow/sf, lam_max, H0, buck_ok, F_cr, fn, C)
        if best is None:
            return None
        _, d, D2, n, k, Fm, tau, tau_a, lam, H0, buck_ok, F_cr, fn, C = best
        n_total = n + 2
        pitch = (H0 - 1.5*d)/n if n > 0 else 0
        helix = math.degrees(math.atan(pitch/(math.pi*D2))) if D2>0 and pitch>0 else 0
        def_crack = cracking_p * cracking_a / k if k > 0 else 0
        return {
            "geometry": {
                "wire_diameter": round(d,2), "mean_coil_diameter": round(D2,2),
                "outer_diameter": round(D2+d,2), "inner_diameter": round(D2-d,2),
                "spring_index": round(C,1), "active_coils": round(n,1),
                "total_coils": round(n_total,1), "free_length": round(H0,2),
                "solid_length": round(n_total*d,2), "pitch": round(pitch,2),
                "helix_angle": round(helix,2), "material_length": round(math.pi*D2*n_total/math.cos(math.radians(helix)),1)
            },
            "performance": {
                "stiffness": round(k,3), "max_load": round(Fm,1),
                "max_stress": round(tau,1), "allowable_stress": round(tau_a,1),
                "max_deformation": round(lam,2), "deformation_at_cracking": round(def_crack,4),
                "natural_frequency": round(fn,1),
                "fatigue_stress_amplitude": round(tau*0.3,1),
                "fatigue_safety_factor": round(mat_props.get("fatigue_limit",tau_allow*0.5)/(tau*0.3),2) if tau>0 else 0,
                "buckling_ratio": round(H0/D2,2) if D2>0 else 0,
                "buckling_critical_load": round(F_cr,1), "is_buckling_safe": buck_ok
            }
        }


class ValveSeatDesigner:
    @staticmethod
    def orifice_diameter(flow_rate, pressure_drop, medium, Cd=0.62):
        Q = flow_rate / 60000.0
        dP = pressure_drop * 1e6
        if dP <= 0 or medium["density"] <= 0: return 2.0
        A = Q / (Cd * math.sqrt(2*dP/medium["density"]))
        d = math.sqrt(4*A/math.pi) * 1000
        return max(d, 2.0)

    @staticmethod
    def seat_geometry(orifice_d, valve_type, seal_type):
        seat_d = orifice_d + 1.0
        if seal_type == "metal_to_metal": sw = 0.5 + 0.02*orifice_d
        elif seal_type == "soft_seat": sw = 0.8 + 0.03*orifice_d
        else: sw = 0.3 + 0.01*orifice_d
        seat_area = math.pi * seat_d * sw
        orifice_area = math.pi * orifice_d**2 / 4
        if valve_type == "poppet_conical": angle = 60.0
        elif valve_type == "poppet_ball": angle = 90.0
        else: angle = 45.0
        ball_d = seat_d * 1.1 if valve_type == "poppet_ball" else 0
        return {
            "seat_diameter": round(seat_d,2), "seat_angle": angle,
            "seat_width": round(sw,3), "seat_area": round(seat_area,2),
            "orifice_diameter": round(orifice_d,2), "orifice_area": round(orifice_area,2),
            "ball_diameter": round(ball_d,2) if ball_d else 0,
            "poppet_cone_angle": angle-1 if valve_type == "poppet_conical" else 0
        }

    @staticmethod
    def seal_performance(seat_geom, op_pressure, crack_p, spring_force, seal_type, medium):
        sp = SEAL_MAT_DB[seal_type]
        pressure_force = op_pressure * 1e6 * seat_geom["orifice_area"] * 1e-6
        total_force = spring_force + pressure_force
        q = total_force / seat_geom["seat_area"] if seat_geom["seat_area"] > 0 else 0
        qb = sp["qb"]; q_allow = sp["q_allow"]
        margin = (q_allow - q)/q_allow*100 if q_allow > 0 else 0
        if q >= qb:
            leakage = sp["leak_factor"] * op_pressure
        else:
            leakage = sp["leak_factor"] * op_pressure * (qb/max(q,0.01))
        return {
            "specific_pressure": round(q,2), "required_qb": qb, "allowable_q": q_allow,
            "spring_force": round(spring_force,2), "pressure_force": round(pressure_force,2),
            "total_force": round(total_force,2), "leakage_estimated": round(leakage,6),
            "margin": round(margin,1), "seal_ok": q >= qb
        }


class FlowAnalyzer:
    @staticmethod
    def cv(flow_rate, pd_bar, density):
        if pd_bar <= 0: return 9999
        SG = density / 1000.0
        return flow_rate * math.sqrt(SG / pd_bar)

    @staticmethod
    def pd_from_cv(flow_rate, Cv, density):
        if Cv <= 0: return 9999
        SG = density / 1000.0
        return SG * (flow_rate / Cv)**2

    @staticmethod
    def analyze(inputs_data, seat_geom, medium):
        est_pd = inputs_data["max_pressure_drop"]
        Cv = FlowAnalyzer.cv(inputs_data["nominal_flow_rate"], est_pd*10, medium["density"])
        actual_pd = FlowAnalyzer.pd_from_cv(inputs_data["nominal_flow_rate"], Cv, medium["density"]) / 10
        max_pd = FlowAnalyzer.pd_from_cv(inputs_data["max_flow_rate"], Cv, medium["density"]) / 10
        Q_m3s = inputs_data["nominal_flow_rate"] / 60000.0
        vel_orifice = Q_m3s / (seat_geom["orifice_area"] * 1e-6) if seat_geom["orifice_area"] > 0 else 0
        pipe_area = math.pi * (inputs_data["inlet_port_diameter"]**2) / 4
        vel_pipe = Q_m3s / (pipe_area * 1e-6) if pipe_area > 0 else 0
        kin_visc = medium["viscosity"] / medium["density"] if medium["density"] > 0 else 1e-6
        Re = vel_orifice * (seat_geom["orifice_diameter"]/1000) / kin_visc if kin_visc > 0 else 0
        Cd = 0.35 if Re < 2300 else (0.50 if Re < 10000 else 0.59)
        dP = actual_pd * 1e6
        sigma = (inputs_data["operating_pressure"]*1e6 - medium["vapor_pressure"]) / dP if dP > 0 else 9999
        if sigma > 5: cav = "无气蚀风险"
        elif sigma > 2.5: cav = "轻度气蚀风险"
        elif sigma > 1.5: cav = "中度气蚀风险"
        else: cav = "严重气蚀风险 - 需重新设计"
        return {
            "cv": round(Cv,3), "Cd": round(Cd,3), "Re": round(Re,0),
            "pd_nominal": round(actual_pd,5), "pd_max": round(max_pd,5),
            "vel_orifice": round(vel_orifice,1), "vel_pipe": round(vel_pipe,1),
            "cavitation_index": round(sigma,2), "cavitation_risk": cav
        }


class BodyDesigner:
    @staticmethod
    def wall_thickness(pressure, inner_d, yield_stress, sf=1.5):
        ri = inner_d/2; sa = yield_stress/sf
        if sa <= pressure: return 999
        return max(ri * (math.sqrt((sa+pressure)/(sa-pressure)) - 1), 1.0)

    @staticmethod
    def stress(pressure, inner_d, outer_d):
        ri=inner_d/2; ro=outer_d/2
        if ro <= ri: return 9999
        return pressure * (ro**2+ri**2)/(ro**2-ri**2)

    @staticmethod
    def design(inputs_data, seat_geom, spring_geom, body_mat_key="15-5PH"):
        mat = BODY_MAT_DB.get(body_mat_key, BODY_MAT_DB["15-5PH"])
        inner_cavity = spring_geom["outer_diameter"] + 3.0
        wt = BodyDesigner.wall_thickness(inputs_data["max_pressure"], inner_cavity, mat["yield"], inputs_data.get("sf_yield",1.5))
        body_od = inner_cavity + 2*wt
        if body_od > inputs_data["max_envelope_diameter"]:
            body_od = inputs_data["max_envelope_diameter"]
            wt = (body_od - inner_cavity)/2
        body_len = spring_geom["free_length"] + 4*wt + 20
        calc_s = BodyDesigner.stress(inputs_data["max_pressure"], inner_cavity, body_od)
        allow_s = mat["yield"] / inputs_data.get("sf_yield",1.5)
        margin = (allow_s - calc_s)/allow_s*100 if allow_s > 0 else 0
        return {
            "material": body_mat_key, "material_name": mat["name"],
            "inlet_d": inputs_data["inlet_port_diameter"],
            "outlet_d": inputs_data["outlet_port_diameter"],
            "outer_diameter": round(body_od,1), "length": round(body_len,1),
            "wall_thickness": round(wt,2), "calc_stress": round(calc_s,1),
            "allowable_stress": round(allow_s,1), "stress_margin": round(margin,1)
        }


class DynamicAnalyzer:
    @staticmethod
    def moving_mass(seat_geom, density=7800):
        d = seat_geom["seat_diameter"]*1.1; L = seat_geom["seat_diameter"]*1.5
        return math.pi*(d/2)**2 * L * 1e-9 * density

    @staticmethod
    def response_time(mass, stiffness, zeta=0.1):
        if stiffness <= 0 or mass <= 0: return 9999
        wn = math.sqrt(stiffness*1000/mass)
        return 4.0/(zeta*wn) * 1000

    @staticmethod
    def natural_freq_valve(mass, stiffness):
        if mass <= 0 or stiffness <= 0: return 0
        return math.sqrt(stiffness*1000/mass) / (2*math.pi)


def _clean(v):
    """Replace non-JSON-safe values (inf, nan) with None/0"""
    import math
    if isinstance(v, float):
        if math.isinf(v): return 1e9 if v > 0 else 0
        if math.isnan(v): return 0
        return v
    if isinstance(v, dict):
        return {k: _clean(val) for k, val in v.items()}
    if isinstance(v, list):
        return [_clean(x) for x in v]
    return v

def run_check_valve_design(data):
    """Main API entry: accept dict, return dict"""
    medium_key = data.get("medium", "hydraulic_oil")
    medium = MEDIUM_DB.get(medium_key, MEDIUM_DB["hydraulic_oil"])
    spring_mat_key = data.get("spring_material", "inconel_x750")
    spring_mat = SPRING_MAT_DB[spring_mat_key]
    valve_type = data.get("valve_type", "poppet_conical")
    seal_type = data.get("seal_type", "metal_to_metal")
    sf_yield = data.get("safety_factor_yield", 1.5)
    sf_fatigue = data.get("safety_factor_fatigue", 1.5)

    # Auto-select body material
    max_temp = data.get("max_temperature", 135)
    if max_temp > 300: body_mat = "Inconel718"
    elif max_temp > 175: body_mat = "15-5PH"
    else: body_mat = "Ti-6Al-4V"

    warnings = []

    # Step 1: Orifice & Seat
    orifice_d = ValveSeatDesigner.orifice_diameter(
        data["nominal_flow_rate"], data["max_pressure_drop"], medium)
    orifice_d = min(orifice_d, data["inlet_port_diameter"]*0.8)
    seat = ValveSeatDesigner.seat_geometry(orifice_d, valve_type, seal_type)

    # Step 2: Spring
    cracking_area = seat["orifice_area"]
    spring_preload = data["cracking_pressure"] * 1e6 * cracking_area * 1e-6
    avail_d = data["max_envelope_diameter"] * 0.8
    avail_l = data["max_envelope_length"] * 0.6
    spring_result = SpringDesigner.design(
        spring_preload, avail_d, avail_l, spring_mat, sf_fatigue,
        data["cracking_pressure"], cracking_area)
    if spring_result is None:
        return {"error": "无法找到满足要求的弹簧设计参数，请调整约束条件"}

    spring_geo = spring_result["geometry"]
    spring_perf = spring_result["performance"]

    # Verify cracking pressure
    actual_crack_f = spring_perf["stiffness"] * spring_perf["deformation_at_cracking"]
    actual_crack_p = actual_crack_f / (cracking_area*1e-6) / 1e6 if cracking_area > 0 else 0
    if abs(actual_crack_p - data["cracking_pressure"])/max(data["cracking_pressure"],0.01) > 0.2:
        warnings.append(f"实际开启压力({actual_crack_p:.4f} MPa)与目标({data['cracking_pressure']:.4f} MPa)偏差超过20%")

    # Step 3: Seal
    spring_seal_force = spring_perf["stiffness"] * spring_perf["deformation_at_cracking"]
    seal = ValveSeatDesigner.seal_performance(
        seat, data["operating_pressure"], data["cracking_pressure"],
        spring_seal_force, seal_type, medium)
    if not seal["seal_ok"]:
        warnings.append(f"密封比压({seal['specific_pressure']:.1f} MPa)低于必需({seal['required_qb']:.1f} MPa)")
    if seal["leakage_estimated"] > data.get("max_reverse_leakage", 0.25):
        warnings.append(f"估算泄漏率({seal['leakage_estimated']:.4f} cm3/min)超限")

    # Step 4: Flow
    flow = FlowAnalyzer.analyze(data, seat, medium)
    if flow["pd_nominal"] > data["max_pressure_drop"]:
        warnings.append(f"额定压降({flow['pd_nominal']:.4f} MPa)超限({data['max_pressure_drop']} MPa)")
    if "严重" in flow["cavitation_risk"]:
        warnings.append(f"气蚀风险: {flow['cavitation_risk']}")

    # Step 5: Body
    body = BodyDesigner.design(data, seat, spring_geo, body_mat)
    if body["stress_margin"] < 10:
        warnings.append(f"阀体应力裕度({body['stress_margin']:.1f}%)偏低")

    # Step 6: Dynamic
    mass = DynamicAnalyzer.moving_mass(seat)
    resp_t = DynamicAnalyzer.response_time(mass, spring_perf["stiffness"])
    fn_valve = DynamicAnalyzer.natural_freq_valve(mass, spring_perf["stiffness"])
    if resp_t > data.get("response_time", 10):
        warnings.append(f"响应时间({resp_t:.1f} ms)超限({data['response_time']} ms)")

    # Total mass estimate
    body_vol = math.pi*((body["outer_diameter"]/2)**2 - ((body["outer_diameter"]-2*body["wall_thickness"])/2)**2)*body["length"]
    spring_vol = math.pi*(spring_geo["wire_diameter"]/2)**2 * spring_geo["material_length"]
    total_mass = body_vol*1e-9*7800 + spring_vol*1e-9*spring_mat["density"] + mass

    # Conclusion
    if not warnings:
        conclusion = "设计通过 - 方案满足所有指标要求"
    else:
        conclusion = f"设计通过(有{len(warnings)}条警告) - 建议优化后确认"

    return {
        "input": data,
        "medium_info": {"key": medium_key, "name": medium["name"]},
        "seat": seat,
        "spring": {"geometry": spring_geo, "performance": spring_perf,
                   "material": spring_mat_key, "material_name": spring_mat["name"]},
        "seal": seal,
        "flow": flow,
        "body": body,
        "dynamic": {
            "moving_mass_kg": round(mass,4),
            "response_time_ms": round(resp_t,1),
            "valve_natural_freq": round(fn_valve,1),
            "spring_natural_freq": spring_perf["natural_frequency"],
            "estimated_total_mass_kg": round(total_mass,3)
        },
        "warnings": warnings,
        "conclusion": conclusion
    }

    return _clean(result)
