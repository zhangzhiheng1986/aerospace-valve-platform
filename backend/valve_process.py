# -*- coding: utf-8 -*-
"""
Aerospace Valve Manufacturing Process Module
Valve Processing - Web API
Standards: HB/Z, GJB, AMS, MIL, QJ series
"""

import math
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
from enum import Enum


# ============================================================
# Process Type Enums
# ============================================================

class ProcessCategory(Enum):
    MACHINING = "machining"
    HEAT_TREATMENT = "heat_treatment"
    SURFACE_TREATMENT = "surface"
    WELDING = "welding"
    ASSEMBLY = "assembly"


class MaterialFamily(Enum):
    ALUMINUM = "aluminum"
    TITANIUM = "titanium"
    STAINLESS_STEEL = "stainless"
    NICKEL_ALLOY = "nickel_alloy"
    COBALT_ALLOY = "cobalt_alloy"
    COPPER_ALLOY = "copper"


# ============================================================
# Machining Process Database
# ============================================================

MACHINING_DB = {
    "aluminum_turning": {
        "name": "Aluminum Alloy Turning",
        "category": ProcessCategory.MACHINING,
        "tool_material": "Carbide (K10-K20, PCD optional)",
        "cutting_speed_m_min": (200, 500),
        "feed_rate_mm_rev": (0.10, 0.40),
        "depth_of_cut_mm": (0.5, 4.0),
        "surface_roughness_ra": (0.8, 3.2),
        "tolerance_grade": "IT7-IT9",
        "coolant": "Emulsion (5-10%) or MQL",
        "tool_life_min": 60,
        "std": "HB/Z 215-92, AMS 4280",
        "applicability": "Rotational valve body/cover/fitting parts"
    },
    "titanium_turning": {
        "name": "Titanium Alloy Turning",
        "category": ProcessCategory.MACHINING,
        "tool_material": "Carbide (M30-M40, uncoated) or PCD",
        "cutting_speed_m_min": (30, 80),
        "feed_rate_mm_rev": (0.08, 0.25),
        "depth_of_cut_mm": (0.3, 2.5),
        "surface_roughness_ra": (0.4, 1.6),
        "tolerance_grade": "IT6-IT8",
        "coolant": "High-pressure high-flow (no chloride, prevent H-embrittlement)",
        "tool_life_min": 30,
        "std": "HB/Z 216-92, AMS 4911, AMS 4928",
        "applicability": "High-pressure body/nozzle/piping (TC4, TA15)"
    },
    "stainless_turning": {
        "name": "Stainless Steel Turning",
        "category": ProcessCategory.MACHINING,
        "tool_material": "Carbide (M20-M30, TiAlN coated)",
        "cutting_speed_m_min": (80, 200),
        "feed_rate_mm_rev": (0.10, 0.30),
        "depth_of_cut_mm": (0.4, 3.0),
        "surface_roughness_ra": (0.8, 1.6),
        "tolerance_grade": "IT7-IT8",
        "coolant": "Sulfurized oil or synthetic fluid",
        "tool_life_min": 45,
        "std": "HB/Z 217-92, AMS 5643 (17-4PH), AMS 5524 (316L)",
        "applicability": "Stem/poppet/fitting (304, 316L, 17-4PH)"
    },
    "nickel_alloy_turning": {
        "name": "Nickel Alloy Turning",
        "category": ProcessCategory.MACHINING,
        "tool_material": "Carbide (M10-M20) or ceramic",
        "cutting_speed_m_min": (20, 50),
        "feed_rate_mm_rev": (0.05, 0.20),
        "depth_of_cut_mm": (0.3, 2.0),
        "surface_roughness_ra": (0.4, 0.8),
        "tolerance_grade": "IT6-IT7",
        "coolant": "High-pressure (7MPa+) synthetic",
        "tool_life_min": 20,
        "std": "HB/Z 218-92, AMS 5663 (Inconel 718), AMS 5645 (Monel 400)",
        "applicability": "High-temp valve/burner (Inconel 718, Waspaloy)"
    },
    "cobalt_alloy_turning": {
        "name": "Cobalt Alloy Turning (Stellite)",
        "category": ProcessCategory.MACHINING,
        "tool_material": "Carbide (K01-K10) or CBN",
        "cutting_speed_m_min": (15, 35),
        "feed_rate_mm_rev": (0.05, 0.15),
        "depth_of_cut_mm": (0.2, 1.5),
        "surface_roughness_ra": (0.2, 0.8),
        "tolerance_grade": "IT5-IT7",
        "coolant": "EP emulsion (high concentration)",
        "tool_life_min": 15,
        "std": "AMS 5387 (Stellite 6B), AMS 5794",
        "applicability": "Seat/seal face after overlay welding"
    },
    "stainless_milling": {
        "name": "Stainless Steel Milling",
        "category": ProcessCategory.MACHINING,
        "tool_material": "Carbide end mill (TiAlN, 4-6 flute)",
        "cutting_speed_m_min": (60, 150),
        "feed_per_tooth_mm": (0.04, 0.12),
        "depth_of_cut_mm": (0.3, 2.0),
        "axial_depth_mm": (5, 25),
        "surface_roughness_ra": (0.8, 1.6),
        "tolerance_grade": "IT8-IT10",
        "coolant": "Mist cooling + oil spray",
        "tool_life_min": 40,
        "std": "HB/Z 219-92",
        "applicability": "Square/irregular valve body faces/slots"
    },
    "titanium_milling": {
        "name": "Titanium Alloy Milling",
        "category": ProcessCategory.MACHINING,
        "tool_material": "Carbide end mill (M30, uncoated)",
        "cutting_speed_m_min": (30, 60),
        "feed_per_tooth_mm": (0.04, 0.10),
        "depth_of_cut_mm": (0.3, 1.5),
        "axial_depth_mm": (5, 20),
        "surface_roughness_ra": (0.4, 1.6),
        "tolerance_grade": "IT7-IT9",
        "coolant": "High-pressure internal cooling",
        "tool_life_min": 25,
        "std": "HB/Z 220-92",
        "applicability": "Ti alloy irregular cavity/flow channel"
    },
    "edm_wire_cutting": {
        "name": "WEDM-LS (Slow Wire EDM)",
        "category": ProcessCategory.MACHINING,
        "tool_material": "Molybdenum/brass wire (D 0.10-0.25mm)",
        "wire_speed_m_s": (0.2, 0.5),
        "pulse_on_us": (1, 8),
        "pulse_off_us": (5, 30),
        "current_a": (1, 5),
        "surface_roughness_ra": (0.2, 0.8),
        "tolerance_grade": "IT5-IT6",
        "cutting_rate_mm2_min": (15, 80),
        "std": "HB/Z 245-90, JB/T 8404",
        "applicability": "Precision poppet/irregular hole (HRC55+)"
    },
}

# ============================================================
# Heat Treatment Database
# ============================================================

HEAT_TREATMENT_DB = {
    "aluminum_t6": {
        "name": "Aluminum T6 (Solution + Aging)",
        "category": ProcessCategory.HEAT_TREATMENT,
        "solution_temp_C": (530, 545),
        "solution_time_h": (1, 4),
        "quench_medium": "Water (RT) or polymer quenchant",
        "aging_temp_C": (175, 195),
        "aging_time_h": (8, 12),
        "target_hardness": "HB 95-150",
        "distortion_mm_m": 0.3,
        "std": "HB 5201-82, AMS 2770, GJB 1694",
        "applicability": "2A12, 6061, 7075 body/bracket"
    },
    "titanium_aging": {
        "name": "Titanium Aging Hardening",
        "category": ProcessCategory.HEAT_TREATMENT,
        "solution_temp_C": (845, 880),
        "solution_time_h": (0.5, 2),
        "quench_medium": "Air (forced)",
        "aging_temp_C": (480, 595),
        "aging_time_h": (4, 8),
        "target_hardness": "HRC 32-40",
        "distortion_mm_m": 0.15,
        "std": "HB 5340-95, AMS 4911, AMS 4965",
        "applicability": "TC4 (Ti-6Al-4V) body/load-bearing"
    },
    "stainless_17_4ph_h900": {
        "name": "17-4PH H900 Aging",
        "category": ProcessCategory.HEAT_TREATMENT,
        "solution_temp_C": (1040, 1065),
        "solution_time_h": (0.5, 1),
        "quench_medium": "Air or oil",
        "aging_temp_C": (480, 490),
        "aging_time_h": (1, 1.5),
        "target_hardness": "HRC 40-44",
        "distortion_mm_m": 0.05,
        "std": "AMS 5643, HB 5341-95",
        "applicability": "High-strength stem/poppet"
    },
    "stainless_316l_annealing": {
        "name": "316L Solution Annealing",
        "category": ProcessCategory.HEAT_TREATMENT,
        "solution_temp_C": (1050, 1100),
        "solution_time_h": (0.5, 1),
        "quench_medium": "Water",
        "aging_temp_C": 0,
        "aging_time_h": 0,
        "target_hardness": "HB 150-180",
        "distortion_mm_m": 0.1,
        "std": "AMS 5524, HB 5350-95",
        "applicability": "316L body/fitting (corrosion priority)"
    },
    "inconel_718_aging": {
        "name": "Inconel 718 Dual Aging",
        "category": ProcessCategory.HEAT_TREATMENT,
        "solution_temp_C": (940, 1010),
        "solution_time_h": (1, 2),
        "quench_medium": "Air",
        "aging_temp_C": (720, 760),
        "aging_time_h": (8, 10),
        "aging_temp_2_C": (620, 650),
        "aging_time_2_h": (8, 10),
        "target_hardness": "HRC 36-44",
        "distortion_mm_m": 0.08,
        "std": "AMS 5663, HB 5353-95",
        "applicability": "Inconel 718 high-temp (burner/regulating)"
    },
    "stellite_overlay": {
        "name": "Stellite 6B Overlay",
        "category": ProcessCategory.HEAT_TREATMENT,
        "process": "Plasma transferred arc / laser cladding",
        "preheat_temp_C": (300, 500),
        "deposition_temp_C": (1050, 1250),
        "post_weld_heat": "Slow cool + 600-650C/2h stress relief",
        "layer_thickness_mm": (1.5, 4.0),
        "target_hardness": "HRC 40-45",
        "std": "AMS 5387, AWS A5.21",
        "applicability": "Seat/ball seal face (wear+corrosion)"
    },
}

# ============================================================
# Surface Treatment Database
# ============================================================

SURFACE_TREATMENT_DB = {
    "aluminum_anodize_hard": {
        "name": "Aluminum Hard Anodizing",
        "category": ProcessCategory.SURFACE_TREATMENT,
        "electrolyte": "Sulfuric acid (200-300 g/L)",
        "temp_C": (-5, 5),
        "current_density_a_dm2": (2.5, 4.0),
        "voltage_v": (40, 80),
        "time_min": (30, 90),
        "coating_thickness_um": (30, 80),
        "hardness_hv": (300, 500),
        "std": "MIL-A-8625 Type III, HB 5475-91",
        "applicability": "2A12/6061/7075 body external"
    },
    "aluminum_chemical_conv": {
        "name": "Aluminum Chem Conversion (Alodine 1200)",
        "category": ProcessCategory.SURFACE_TREATMENT,
        "process": "Dip/spray chromate conversion",
        "coating_thickness_um": (0.5, 4),
        "corrosion_resistance_h": 168,
        "std": "MIL-DTL-5541 Type I, HB 5470-91",
        "applicability": "Inner cavity/complex shape (conductive required)"
    },
    "titanium_nitriding": {
        "name": "Titanium Plasma Nitriding",
        "category": ProcessCategory.SURFACE_TREATMENT,
        "temp_C": (700, 850),
        "time_h": (8, 20),
        "layer_thickness_um": (30, 80),
        "surface_hardness_hv": (800, 1200),
        "std": "AMS 2759, HB 5477-91",
        "applicability": "TC4 stem/poppet (improve wear)"
    },
    "stainless_passivation": {
        "name": "Stainless Passivation",
        "category": ProcessCategory.SURFACE_TREATMENT,
        "process": "Nitric acid (20-50%) dip",
        "temp_C": (40, 70),
        "time_min": (30, 60),
        "post_treatment": "Pure water rinse + dry",
        "std": "ASTM A967, AMS 2700, HB 5473-91",
        "applicability": "316L body inner cavity (corrosion enhancement)"
    },
    "inconel_shot_peening": {
        "name": "Shot Peening (Inconel)",
        "category": ProcessCategory.SURFACE_TREATMENT,
        "media": "Cast steel shot / ceramic (D 0.3-0.8mm)",
        "almen_intensity_mm": (0.2, 0.5),
        "coverage_pct": 100,
        "residual_stress_mpa": (-400, -700),
        "std": "AMS 2430, SAE J2277, HB/Z 26-91",
        "applicability": "Inconel 718 load-bearing area (fatigue life)"
    },
    "ptfe_coating": {
        "name": "PTFE Coating",
        "category": ProcessCategory.SURFACE_TREATMENT,
        "process": "Spray + sintering",
        "thickness_um": (10, 30),
        "sintering_temp_C": (370, 400),
        "friction_coeff": (0.04, 0.10),
        "std": "AMS 2510, HB 5455-91",
        "applicability": "Seat/seal face (low friction sealing)"
    },
}

# ============================================================
# Welding Database
# ============================================================

WELDING_DB = {
    "inconel_718_ebw": {
        "name": "Inconel 718 Electron Beam Welding",
        "category": ProcessCategory.WELDING,
        "process": "EBW",
        "vacuum_pa": (1, 5),
        "voltage_kv": (50, 80),
        "beam_current_ma": (30, 80),
        "travel_speed_mm_s": (5, 15),
        "preheat_required": False,
        "pwht": "720C/8h + 620C/8h dual aging",
        "std": "AMS 2814, HB/Z 78-91, AWS D17.1",
        "applicability": "Inconel 718 body butt (depth/width 10:1)"
    },
    "stainless_316l_tig": {
        "name": "316L Stainless TIG (GTAW)",
        "category": ProcessCategory.WELDING,
        "process": "TIG/GTAW",
        "filler": "ER316L (D 0.8-1.2mm)",
        "current_a": (60, 150),
        "voltage_v": (10, 16),
        "travel_speed_mm_s": (2, 5),
        "shielding_gas": "Ar 99.99% (backing Ar)",
        "interpass_temp_C": 100,
        "pwht": "Generally not required (or 1050-1100C solution)",
        "std": "AMS 5803, HB/Z 81-91, AWS D17.1",
        "applicability": "316L body/pipe (hermetic weld)"
    },
    "titanium_tc4_lbw": {
        "name": "TC4 Titanium Laser Welding",
        "category": ProcessCategory.WELDING,
        "process": "LBW / Nd:YAG",
        "power_w": (1500, 3000),
        "travel_speed_m_min": (0.6, 2.0),
        "shielding_gas": "Ar trailing shield + back Ar",
        "filler": "TC4 wire (optional)",
        "preheat_required": False,
        "pwht": "Anneal 700-750C/1h (optional)",
        "std": "AMS 4953, HB/Z 79-91",
        "applicability": "Ti body precision welding (low distortion)"
    },
    "stellite_braze": {
        "name": "Stellite Brazing",
        "category": ProcessCategory.WELDING,
        "process": "Vacuum brazing / induction brazing",
        "filler": "BAg series / BCuP series",
        "brazing_temp_C": (650, 900),
        "vacuum_pa": (1, 10),
        "holding_time_min": (10, 30),
        "joint_clearance_mm": (0.03, 0.10),
        "std": "AMS 4770, AWS C3.2",
        "applicability": "Seat ring/seal ring brazing"
    },
}

# ============================================================
# Assembly Process Database
# ============================================================

ASSEMBLY_DB = {
    "thread_lubricant": {
        "name": "Thread Lubrication",
        "category": ProcessCategory.ASSEMBLY,
        "process": "MoS2 / anti-seize on thread",
        "torque_tolerance_pct": 5,
        "std": "HB 5965-95, MIL-T-83420",
        "applicability": "Ti/SS thread anti-seize"
    },
    "torque_control": {
        "name": "Torque-Controlled Fastening",
        "category": ProcessCategory.ASSEMBLY,
        "process": "Torque wrench + angle control",
        "torque_accuracy_pct": (3, 5),
        "angle_tolerance_deg": 5,
        "std": "GJB 3364-98, HB 5362-95",
        "applicability": "Body/cover main seal bolts"
    },
    "cleanliness": {
        "name": "Cleanliness Control",
        "category": ProcessCategory.ASSEMBLY,
        "process": "Ultrasonic + vacuum dry",
        "particle_size_um": (5, 15),
        "cleanliness_grade": "GJB 420B",
        "std": "GJB 420B, HB 6167-89",
        "applicability": "O2/H2/hydraulic system valves"
    },
    "leak_test": {
        "name": "Leak Test",
        "category": ProcessCategory.ASSEMBLY,
        "process": "He mass spec / bubble",
        "test_pressure_factor": 1.5,
        "leak_rate_pa_m3_s": 1e-9,
        "std": "QJ 20156, GJB 2489",
        "applicability": "100% check all sealed valves"
    },
}

# ============================================================
# Process Routes
# ============================================================

PROCESS_ROUTES = {
    "solenoid_valve_body": {
        "name": "Solenoid Valve Body Route",
        "material": "316L Stainless Steel",
        "operations": [
            {"step": 1, "process": "Cut blank", "method": "Bar sawing D30x55", "equipment": "Saw", "time_min": 3},
            {"step": 2, "process": "Rough turning", "method": "Chuck, rough OD/face/ID", "equipment": "CNC lathe", "time_min": 12},
            {"step": 3, "process": "Finish turning", "method": "OD/face/ID finish IT7, Ra 0.8", "equipment": "CNC lathe", "time_min": 8},
            {"step": 4, "process": "Milling", "method": "Hex/square face milling", "equipment": "MC", "time_min": 10},
            {"step": 5, "process": "Drill/tap", "method": "Mounting/threading holes", "equipment": "MC", "time_min": 6},
            {"step": 6, "process": "Deburr", "method": "Manual + power tool", "equipment": "Bench", "time_min": 5},
            {"step": 7, "process": "Solution treat", "method": "1050C/0.5h water quench", "equipment": "Vacuum furnace", "time_min": 90},
            {"step": 8, "process": "Finish grind", "method": "Seal/face finish grind", "equipment": "Surface grinder", "time_min": 8},
            {"step": 9, "process": "Passivation", "method": "HNO3 30% dip 30min", "equipment": "Passivation tank", "time_min": 45},
            {"step": 10, "process": "Cleaning", "method": "Ultrasonic + vacuum dry", "equipment": "Cleaner", "time_min": 20},
            {"step": 11, "process": "Leak test", "method": "He 1.5xWp, leak <1E-9", "equipment": "He detector", "time_min": 15},
            {"step": 12, "process": "Final inspect/pack", "method": "Dim/geometry/visual", "equipment": "CMM/projector", "time_min": 10},
        ],
    },
    "check_valve_poppet": {
        "name": "Check Valve Poppet Route",
        "material": "17-4PH Stainless Steel",
        "operations": [
            {"step": 1, "process": "Cut blank", "method": "Bar D15x30", "equipment": "Saw", "time_min": 2},
            {"step": 2, "process": "Rough turning", "method": "OD/cone/stem rough", "equipment": "CNC lathe", "time_min": 6},
            {"step": 3, "process": "Finish turning", "method": "Finish IT6, cone Ra 0.4", "equipment": "CNC lathe", "time_min": 5},
            {"step": 4, "process": "Aging H900", "method": "480C/1h air cool", "equipment": "Vacuum furnace", "time_min": 75},
            {"step": 5, "process": "Cone lap", "method": "Lapping Ra 0.1", "equipment": "Precision grinder", "time_min": 12},
            {"step": 6, "process": "Matching lap", "method": "Match with seat, check seal line", "equipment": "Lap bench", "time_min": 20},
            {"step": 7, "process": "Clean/leak/pack", "method": "Ultrasonic+dry+leak", "equipment": "Clean/leak station", "time_min": 20},
        ],
    },
    "relief_valve_seat": {
        "name": "Relief Valve Seat (Stellite Overlay) Route",
        "material": "Inconel 718 + Stellite 6B",
        "operations": [
            {"step": 1, "process": "Forging rough", "method": "Rough turn/mill", "equipment": "CNC lathe/mill", "time_min": 25},
            {"step": 2, "process": "Pre-overlay clean", "method": "Acetone wipe + sand blast", "equipment": "Clean bench", "time_min": 10},
            {"step": 3, "process": "Preheat", "method": "300-400C hold", "equipment": "Preheat furnace", "time_min": 60},
            {"step": 4, "process": "Stellite 6B overlay", "method": "PTA, layer 2-3mm", "equipment": "PTA welder", "time_min": 45},
            {"step": 5, "process": "Slow cool + PWHT", "method": "Furnace cool + 620C/2h", "equipment": "HT furnace", "time_min": 180},
            {"step": 6, "process": "Overlay finish turn", "method": "OD/face finish turn", "equipment": "CNC lathe", "time_min": 15},
            {"step": 7, "process": "Overlay lap", "method": "Surface grind + lap Ra 0.05", "equipment": "Precision grinder", "time_min": 25},
            {"step": 8, "process": "718 dual aging", "method": "720/620C dual aging", "equipment": "Vacuum furnace", "time_min": 1080},
            {"step": 9, "process": "Hardness/UT/PT", "method": "HRC + UT + PT", "equipment": "UT/PT device", "time_min": 30},
            {"step": 10, "process": "Match+leak+pack", "method": "Match poppet+He check", "equipment": "Assembly bench", "time_min": 30},
        ],
    },
}


# ============================================================
# Core Functions
# ============================================================

def get_process_catalog():
    """Return full process catalog for frontend display."""
    return {
        "machining": {
            "name": "Machining",
            "icon": "Wrench",
            "count": len(MACHINING_DB),
            "processes": [
                {"id": k, "name": v["name"], "category": v["category"].value}
                for k, v in MACHINING_DB.items()
            ],
        },
        "heat_treatment": {
            "name": "Heat Treatment",
            "icon": "Flame",
            "count": len(HEAT_TREATMENT_DB),
            "processes": [
                {"id": k, "name": v["name"], "category": v["category"].value}
                for k, v in HEAT_TREATMENT_DB.items()
            ],
        },
        "surface_treatment": {
            "name": "Surface Treatment",
            "icon": "Diamond",
            "count": len(SURFACE_TREATMENT_DB),
            "processes": [
                {"id": k, "name": v["name"], "category": v["category"].value}
                for k, v in SURFACE_TREATMENT_DB.items()
            ],
        },
        "welding": {
            "name": "Welding",
            "icon": "Link",
            "count": len(WELDING_DB),
            "processes": [
                {"id": k, "name": v["name"], "category": v["category"].value}
                for k, v in WELDING_DB.items()
            ],
        },
        "assembly": {
            "name": "Assembly",
            "icon": "List",
            "count": len(ASSEMBLY_DB),
            "processes": [
                {"id": k, "name": v["name"], "category": v["category"].value}
                for k, v in ASSEMBLY_DB.items()
            ],
        },
    }


def get_process_detail(process_id):
    """Get full parameters for a single process."""
    for db in [MACHINING_DB, HEAT_TREATMENT_DB,
               SURFACE_TREATMENT_DB, WELDING_DB, ASSEMBLY_DB]:
        if process_id in db:
            result = dict(db[process_id])
            result["category"] = result["category"].value
            result["id"] = process_id
            return result
    return None


def search_processes(keyword="", category=""):
    """Search processes by keyword and category."""
    results = []
    dbs = {
        "machining": MACHINING_DB,
        "heat_treatment": HEAT_TREATMENT_DB,
        "surface_treatment": SURFACE_TREATMENT_DB,
        "welding": WELDING_DB,
        "assembly": ASSEMBLY_DB,
    }
    for cat_key, db in dbs.items():
        if category and category != cat_key:
            continue
        for pid, pdata in db.items():
            if keyword:
                kw = keyword.lower()
                hay = (pdata["name"] + " " + pdata.get("applicability", "")
                       + " " + pdata.get("std", "")).lower()
                if kw not in hay:
                    continue
            results.append({
                "id": pid,
                "name": pdata["name"],
                "category": cat_key,
                "applicability": pdata.get("applicability", ""),
                "std": pdata.get("std", ""),
            })
    return results


def get_process_route(route_id):
    """Get process route details."""
    if route_id in PROCESS_ROUTES:
        result = dict(PROCESS_ROUTES[route_id])
        total_time = sum(op["time_min"] for op in result["operations"])
        result["total_time_min"] = total_time
        result["total_time_h"] = round(total_time / 60.0, 2)
        result["steps"] = len(result["operations"])
        result["id"] = route_id
        return result
    return None


def list_process_routes():
    """List all process routes."""
    return [
        {
            "id": rid,
            "name": r["name"],
            "material": r["material"],
            "steps": len(r["operations"]),
            "total_time_min": sum(op["time_min"] for op in r["operations"]),
        }
        for rid, r in PROCESS_ROUTES.items()
    ]


def recommend_process_route(material, valve_type):
    """Recommend process route based on material and valve type."""
    material_lower = material.lower()
    rec = {"processes": [], "route_suggestion": None, "key_points": []}
    # Machining
    if "aluminum" in material_lower or "al" == material_lower.strip():
        rec["processes"].append("aluminum_turning")
    elif "titanium" in material_lower or "tc4" in material_lower or "ti" == material_lower.strip():
        rec["processes"].extend(["titanium_turning", "titanium_milling"])
    elif "inconel" in material_lower:
        rec["processes"].append("nickel_alloy_turning")
    elif "stainless" in material_lower or "316" in material_lower or "17-4" in material_lower or "ss" == material_lower.strip():
        rec["processes"].extend(["stainless_turning", "stainless_milling"])
    # Heat treatment
    if "17-4" in material_lower:
        rec["processes"].append("stainless_17_4ph_h900")
    elif "inconel 718" in material_lower or "inconel718" in material_lower:
        rec["processes"].append("inconel_718_aging")
    elif "titanium" in material_lower or "tc4" in material_lower:
        rec["processes"].append("titanium_aging")
    elif "316l" in material_lower:
        rec["processes"].append("stainless_316l_annealing")
    # Surface treatment
    if "aluminum" in material_lower or "al" == material_lower.strip():
        rec["processes"].extend(["aluminum_anodize_hard", "aluminum_chemical_conv"])
    elif "titanium" in material_lower or "tc4" in material_lower:
        rec["processes"].append("titanium_nitriding")
    elif "stainless" in material_lower or "316" in material_lower:
        rec["processes"].append("stainless_passivation")
    elif "inconel" in material_lower:
        rec["processes"].append("inconel_shot_peening")
    # Route suggestion
    vt = valve_type.lower() if valve_type else ""
    if "solenoid" in vt or "electromagnetic" in vt:
        rec["route_suggestion"] = "solenoid_valve_body"
    elif "check" in vt or "one-way" in vt:
        rec["route_suggestion"] = "check_valve_poppet"
    elif "relief" in vt or "pressure" in vt or "reducing" in vt:
        rec["route_suggestion"] = "relief_valve_seat"
    # Key points
    rec["key_points"] = [
        "Material datasheet must be available before process design",
        "Cleanliness control for O2/H2/hydraulic systems (GJB 420B)",
        "100% leak test per QJ 20156 for sealed valves",
        "NDT (UT/PT/RT) per criticality level",
    ]
    return rec


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    print("=== Process Catalog ===")
    catalog = get_process_catalog()
    for k, v in catalog.items():
        print(f"{v['name']}: {v['count']} processes")
    print("\n=== Recommend for Inconel 718 Relief Valve ===")
    rec = recommend_process_route("Inconel 718", "relief valve")
    print(f"Processes: {rec['processes']}")
    print(f"Route: {rec['route_suggestion']}")
    print("\n=== Route: relief_valve_seat ===")
    route = get_process_route("relief_valve_seat")
    print(f"Total: {route['total_time_min']} min ({route['total_time_h']} h)")
