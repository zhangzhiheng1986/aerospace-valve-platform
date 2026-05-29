# -*- coding: utf-8 -*-
"""
QJ 20156-2012 Space System Gas Pressure Reducing Valve General Specification
Compliance & Calculation Module for Aerospace Valve R&D Platform

Covers: Design requirements, material selection, performance specifications,
environmental testing, quality assurance (A/B/C inspection), cleanliness,
life testing, safety margins, pressure strength, burst pressure,
leakage rate verification, and all test profiles.
"""
import math, json
from typing import Dict, List, Any, Optional, Tuple

# ===========================================================================
# CONSTANTS FROM THE STANDARD
# ===========================================================================

# Standard metadata
STANDARD_ID = "QJ 20156-2012"
STANDARD_TITLE_CN = "空间系统气体减压阀通用规范"
STANDARD_TITLE_EN = "General specification for gas pressure reducing valve of space system"
STANDARD_EFFECTIVE = "2013-05-01"
STANDARD_SCOPE = "卫星、航天器、深空探测器、空间站"

# Valve structure types (Section 3.6.2.1)
VALVE_TYPES = [
    {"id": "pilot", "name_cn": "先导式减压阀", "name_en": "Pilot-Operated Pressure Reducing Valve", "desc": "利用先导级实现精密调节"},
    {"id": "direct", "name_cn": "直动式减压阀", "name_en": "Direct-Acting Pressure Reducing Valve", "desc": "结构简单，弹簧驱动"},
    {"id": "load", "name_cn": "负载式减压阀", "name_en": "Load-Type Pressure Reducing Valve", "desc": "利用外部负载进行调节"},
    {"id": "unload", "name_cn": "卸荷式减压阀", "name_en": "Unload-Type Pressure Reducing Valve", "desc": "卸荷机构实现关断"},
]

# Elastic element requirements (Section 3.6.3)
ELASTIC_ELEMENT_REQUIREMENTS = [
    "具有高弹性",
    "具有足够的机械强度",
    "密封性能可靠",
    "对温度影响不敏感",
    "耐腐蚀，与工作介质相容",
    "满足工作寿命要求"
]

# Working temperature range (Section 3.10.1)
TEMP_RANGE_DEFAULT = {"min": -30, "max": 55, "unit": "degC"}

# Performance thresholds
THRESHOLDS = {
    "internal_leak_max": 1e-5,       # Pa*m^3/s (Section 3.8.3.1)
    "external_leak_max": 1e-5,       # Pa*m^3/s (Section 3.8.3.2)
    "rated_pressure_deviation_max": 1.0,  # % of rated value (Section 3.8.4)
    "lockup_pressure_deviation_min": 5.0,  # % of rated (Section 3.8.5.3)
    "lockup_pressure_deviation_max": 20.0,
    "proof_pressure_multiplier": 1.5,  # (Section 3.8.1)
    "burst_pressure_multiplier": 2.0,  # (Section 3.8.2)
    "proof_hold_time_min": 5,          # min (Section 3.8.1)
    "burst_hold_time_min": 5,          # min
    "min_life_cycles": 20000,          # cycles (Section 3.12)
    "elastic_element_overload_min": 2.0,  # multiplier (Section 3.6.3.2.2)
    "elastic_element_overload_cycles_min": 20,  # cycles
    "elastic_element_overload_duration_min": 10,  # seconds per cycle
}

# Cleanliness requirements (Table 2, Section 3.11)
CLEANLINESS_TABLE = [
    {"particle_size_range_um": ">10", "max_count_per_10L": 0},
    {"particle_size_range_um": "6~10", "max_count_per_10L": 200},
    {"particle_size_range_um": "<6", "max_count_per_10L": "not specified"},
]

# Assembly environment (Section 3.7.1)
ASSEMBLY_ENV = {
    "temperature_range": "15~28 degC",
    "humidity_range": "20%~70%",
    "cleanliness_class": "100,000 (QJ 2214-1991)",
    "filter_size_um": 6
}

# Test environment (Section 4.2.1)
TEST_ENV = {
    "temperature_range": "15~28 degC",
    "humidity_range": "15%~70%",
    "pressure": "atmospheric",
    "illuminance": "400 lx",
    "cleanliness": ">=100,000"
}

# Storage conditions (Section 5.4)
STORAGE_CONDITIONS = {
    "temperature": "20 +/- 10 degC",
    "humidity": "15%~70%",
    "cleanliness": ">=100,000"
}

# Environmental test parameters (Section 3.10)
ENV_TEST_PROFILES = {
    "thermal_vacuum_qual": {
        "name": "热真空试验 - 鉴定级",
        "pressure": "<=1.3 x 10^-3 Pa",
        "temp_high": "T_max_operating + 10 degC",
        "temp_low": "T_min_operating - 10 degC",
        "cycles_min": 6,
        "dwell_per_extreme_h": 2.0,
        "first_last_cycle_hot_cold": True,
    },
    "thermal_vacuum_accept": {
        "name": "热真空试验 - 验收级",
        "pressure": "<=1.3 x 10^-3 Pa",
        "temp_high": "T_max_operating + 5 degC",
        "temp_low": "T_min_operating - 5 degC",
        "cycles_min": 2,
        "dwell_per_extreme_h": 2.0,
        "first_last_cycle_hot_cold": True,
    },
    "thermal_cycle_qual": {
        "name": "热循环试验 - 鉴定级",
        "pressure": "atmospheric",
        "temp_high": "T_max_operating + 10 degC",
        "temp_low": "T_min_operating - 10 degC",
        "cycles_min": 18,
        "ramp_rate": "3~5 degC/min",
        "dwell_per_extreme_h": 2.0,
    },
    "thermal_cycle_accept": {
        "name": "热循环试验 - 验收级",
        "pressure": "atmospheric",
        "temp_high": "T_max_operating + 5 degC",
        "temp_low": "T_min_operating - 5 degC",
        "cycles_min": 6,
        "ramp_rate": "3~5 degC/min",
        "dwell_per_extreme_h": 2.0,
    },
}

# ===========================================================================
# INSPECTION / TEST MATRIX (Table 3 from the standard)
# ===========================================================================

INSPECTION_ITEMS = [
    {"no": 1, "item": "质量", "chapter": "3.2", "method": "4.5.2", "qual": True, "A": True, "C": True},
    {"no": 2, "item": "外观质量", "chapter": "3.3", "method": "4.5.3", "qual": True, "A": True, "C": True},
    {"no": 3, "item": "标志与代号", "chapter": "3.4", "method": "4.5.4", "qual": True, "A": True, "C": True},
    {"no": 4, "item": "弹性元件鉴定试验", "chapter": "3.6.3.2", "method": "4.5.5", "qual": True, "A": True, "C": True},
    {"no": 5, "item": "减压阀行程限程检查", "chapter": "3.6.4", "method": "4.5.6", "qual": True, "A": True, "C": True},
    {"no": 6, "item": "验证压力试验", "chapter": "3.8.1", "method": "4.5.7", "qual": True, "A": True, "C": True},
    {"no": 7, "item": "最小爆破压力试验", "chapter": "3.8.2", "method": "4.5.8", "qual": True, "A": True, "C": True},
    {"no": 8, "item": "内部泄漏率", "chapter": "3.8.3.1", "method": "4.5.9", "qual": True, "A": True, "C": True},
    {"no": 9, "item": "外部泄漏率", "chapter": "3.8.3.2", "method": "4.5.10", "qual": True, "A": True, "C": True},
    {"no": 10, "item": "额定出口压力", "chapter": "3.8.4", "method": "4.5.11", "qual": True, "A": True, "C": True},
    {"no": 11, "item": "压力特性", "chapter": "3.8.5.1", "method": "4.5.12.1", "qual": True, "A": True, "C": True},
    {"no": 12, "item": "流量特性", "chapter": "3.8.5.2", "method": "4.5.12.2", "qual": True, "A": True, "C": True},
    {"no": 13, "item": "锁紧压力偏差", "chapter": "3.8.5.3", "method": "4.5.13", "qual": True, "A": True, "C": True},
    {"no": 14, "item": "动态特性", "chapter": "3.8.6", "method": "4.5.14", "qual": True, "A": True, "C": True},
    {"no": 15, "item": "出口压力精度", "chapter": "3.8.7", "method": "4.5.15", "qual": True, "A": True, "C": True},
    {"no": 16, "item": "接口检查", "chapter": "3.9", "method": "4.5.16", "qual": True, "A": True, "C": True},
    {"no": 17, "item": "工作温度范围", "chapter": "3.10.1", "method": "4.5.17", "qual": True, "A": True, "C": True},
    {"no": 18, "item": "振动试验 - 鉴定级", "chapter": "3.10.2.1", "method": "4.5.18", "qual": True, "A": False, "C": True},
    {"no": 19, "item": "振动试验 - 验收级", "chapter": "3.10.2.2", "method": "4.5.18", "qual": False, "A": True, "C": False},
    {"no": 20, "item": "冲击试验 - 鉴定级", "chapter": "3.10.3.1", "method": "4.5.19", "qual": True, "A": False, "C": True},
    {"no": 21, "item": "冲击试验 - 验收级", "chapter": "3.10.3.2", "method": "4.5.19", "qual": False, "A": True, "C": False},
    {"no": 22, "item": "热真空试验 - 鉴定级", "chapter": "3.10.4.1", "method": "4.5.20", "qual": True, "A": False, "C": True},
    {"no": 23, "item": "热真空试验 - 验收级", "chapter": "3.10.4.2", "method": "4.5.20", "qual": False, "A": True, "C": False},
    {"no": 24, "item": "热循环试验 - 鉴定级", "chapter": "3.10.5.1", "method": "4.5.21", "qual": True, "A": False, "C": True},
    {"no": 25, "item": "热循环试验 - 验收级", "chapter": "3.10.5.2", "method": "4.5.21", "qual": False, "A": True, "C": False},
    {"no": 26, "item": "爆破压力（环境）", "chapter": "3.10.6.1", "method": "4.5.22", "qual": True, "A": False, "C": True},
    {"no": 27, "item": "验证压力（环境）", "chapter": "3.10.6.2", "method": "4.5.23", "qual": True, "A": False, "C": True},
    {"no": 28, "item": "清洁度", "chapter": "3.11", "method": "4.5.24", "qual": True, "A": True, "C": True},
    {"no": 29, "item": "寿命试验", "chapter": "3.12", "method": "4.5.25", "qual": True, "A": False, "C": True},
    {"no": 30, "item": "安全性", "chapter": "3.13", "method": "4.5.26", "qual": True, "A": False, "C": True},
]

# Chapter structure for the standard browser
CHAPTER_TREE = [
    {"id": "1", "title": "范围", "desc": "适用于卫星、航天器、深空探测器、空间站用气体减压阀"},
    {"id": "2", "title": "规范性引用文件", "desc": "GB、GJB、QJ、SH系列标准"},
    {"id": "3", "title": "要求", "children": [
        {"id": "3.1", "title": "通则", "desc": "减压阀应符合本规范和详细规范的规定"},
        {"id": "3.2", "title": "质量", "desc": "质量要求按详细规范规定"},
        {"id": "3.3", "title": "外观质量", "desc": "无加工缺陷、毛刺、机械损伤；清洁；标识清晰完整"},
        {"id": "3.4", "title": "标志和代号", "desc": "产品代号、批次/日期、流向箭头永久性标识"},
        {"id": "3.5", "title": "材料", "desc": "力学、物理性能、温度范围、介质相容性；按QJ 1386/QJ 977复验"},
        {"id": "3.6", "title": "设计结构", "children": [
            {"id": "3.6.1", "title": "设计输入", "desc": "性能、介质、温度、压力范围、额定值、精度、泄漏、质量、可靠性、接口、包络、清洁度、安装、寿命"},
            {"id": "3.6.2", "title": "结构", "desc": "先导式、直动式、负载式、卸荷式；结构尽量简单"},
            {"id": "3.6.3", "title": "弹性元件", "desc": "6项选型原则；2倍最大工作压力鉴定；≥20次循环，每次≥10s"},
            {"id": "3.6.4", "title": "行程限程", "desc": "一般为2倍最大开度；阀芯行程一般0.3~0.5mm"},
        ]},
        {"id": "3.7", "title": "制造装配", "desc": "洁净间等级10万级；溶剂清洗；乙醇最终冲洗；密封脂涂覆按SH 0449/GJB 941A"},
        {"id": "3.8", "title": "性能", "children": [
            {"id": "3.8.1", "title": "验证压力", "desc": "1.5倍最大腔体工作压力，5min，无泄漏或永久变形"},
            {"id": "3.8.2", "title": "爆破压力", "desc": "2倍最大腔体工作压力，5min，无破裂"},
            {"id": "3.8.3", "title": "泄漏率", "desc": "内部：≤1×10⁻⁵ Pa·m³/s（最高工作温度+工作压力）；外部：同限值（额定出口压力）"},
            {"id": "3.8.4", "title": "额定出口压力", "desc": "偏差<1%额定值（规定入口压力下）"},
            {"id": "3.8.5", "title": "静态特性", "desc": "压力/流量特性偏差+锁紧压力偏差5%~20%"},
            {"id": "3.8.6", "title": "动态特性", "desc": "出口压力稳定；无啸叫或振荡；故障阀拆解复检"},
            {"id": "3.8.7", "title": "出口压力精度", "desc": "考虑入口压力变化、温度、出口流量影响"},
        ]},
        {"id": "3.9", "title": "接口", "desc": "按详细规范规定"},
        {"id": "3.10", "title": "环境适应性", "children": [
            {"id": "3.10.1", "title": "温度范围", "desc": "-30°C ~ 55°C；极限温度测试+浸泡"},
            {"id": "3.10.2", "title": "振动", "desc": "鉴定级+验收级；垂直+平行于安装面方向"},
            {"id": "3.10.3", "title": "冲击", "desc": "鉴定级+验收级；半正弦波；垂直+平行方向"},
            {"id": "3.10.4", "title": "热真空", "desc": "≤1.3×10⁻³ Pa；鉴定级6+循环（T±10°C），验收级2+循环（T±5°C）"},
            {"id": "3.10.5", "title": "热循环", "desc": "常压；鉴定级18+循环（T±10°C），验收级6+循环（T±5°C）；变温率3~5°C/min"},
            {"id": "3.10.6", "title": "耐压", "desc": "爆破2倍、验证1.5倍最大工作压力；试验后性能检查"},
        ]},
        {"id": "3.11", "title": "清洁度", "desc": "表2：>10μm：0颗粒，6~10μm：≤200颗粒/10L"},
        {"id": "3.12", "title": "寿命", "desc": "≥20,000次循环；寿命试验后验证第3.8.3.2~3.8.7条"},
        {"id": "3.13", "title": "安全性", "desc": "结构应防止超压；爆破安全系数≥2倍；验证≥1.5倍"},
    ]},
    {"id": "4", "title": "质量保证规定", "children": [
        {"id": "4.1", "title": "检验分类", "desc": "鉴定检验 + 交收检验（A检查+C检查 或 仅A检查）"},
        {"id": "4.3", "title": "鉴定检验", "desc": "≥2台；全项目测试矩阵；所有项目必须通过（表3）"},
        {"id": "4.4", "title": "交收检验", "desc": "A检查（100%逐台）+ C检查（3台抽样）；按表3"},
    ]},
    {"id": "5", "title": "交货准备", "desc": "真空包装≤5kPa，≤40°C，干燥1~2h；专用运输容器"},
    {"id": "6", "title": "说明事项", "desc": "术语定义：空间系统、减压阀、动态/静态特性、压力/流量特性偏差、锁紧压力偏差"},
]

# Normative references
REFERENCES = [
    {"code": "GB/T 191", "title": "Packaging - Pictorial marking for handling of goods"},
    {"code": "GB/T 678-2002", "title": "Chemical reagent - Ethanol (absolute ethanol)"},
    {"code": "GB/T 8979-2008", "title": "Pure nitrogen and high purity nitrogen"},
    {"code": "GJB 941A-1996", "title": "Specification for 7804 chemical anti-friction grease"},
    {"code": "GJB 4014", "title": "Safety application criteria for spacecraft"},
    {"code": "QJ 977", "title": "Re-inspection rules for non-metallic materials"},
    {"code": "QJ 1386", "title": "Re-inspection rules for metallic materials"},
    {"code": "QJ 2214-1991", "title": "Cleanliness class and evaluation method for clean rooms"},
    {"code": "QJ 3089-1999", "title": "Helium mass spectrometer leak detection method"},
    {"code": "QJ 3123-2000", "title": "Vacuum leak detection method for spacecraft"},
    {"code": "QJ 3305-2008", "title": "General requirements for spacecraft pressure products testing"},
    {"code": "SH 0004-1990", "title": "Rubber solvent industrial solvent oil"},
    {"code": "SH 0449-1992", "title": "7805 chemical seal grease"},
    {"code": "SH 0456-1992", "title": "Special No.7 precision instrument grease"},
]

# Key definitions (Section 6)
DEFINITIONS = [
    {"term": "空间系统", "def": "在真空和失重的空间环境中工作的航天器系统，包括卫星、航天器、深空探测器和空间站等航天系统（第6.2.1条）"},
    {"term": "减压阀", "def": "通过阀芯和阀座之间的节流作用，将进口压力降低到所需的出口压力，并在进口压力和流量变化时，自动保持出口压力基本不变的阀门（第6.2.2条）"},
    {"term": "动态特性", "def": "当进口压力或流量突然变化时，减压阀出口压力与时间的函数关系（第6.2.3条）"},
    {"term": "压力特性", "def": "稳定流动状态下，流量不变时，减压阀出口压力随进口压力变化的函数关系（第6.2.4条）"},
    {"term": "流量特性", "def": "稳定流动状态下，进口压力不变时，减压阀出口压力随流量变化的函数关系（第6.2.5条）"},
    {"term": "压力特性偏差", "def": "稳定流动状态下，流量不变时，进口压力变化引起的出口压力相对于额定出口压力的变化量（第6.2.6条）"},
    {"term": "流量特性偏差", "def": "稳定流动状态下，进口压力不变时，流量变化引起的出口压力相对于额定出口压力的变化量（第6.2.7条）"},
    {"term": "锁紧压力偏差", "def": "减压阀关闭时的出口压力相对于额定出口压力的变化量（第6.2.8条）"},
]

# ===========================================================================
# CALCULATION FUNCTIONS
# ===========================================================================

def _clean(obj):
    """Recursively replace NaN/Infinity with None for JSON compatibility."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, list):
        return [_clean(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    return obj


def calc_proof_pressure(max_working_pressure: float) -> Dict:
    """Calculate proof pressure requirements (Section 3.8.1)"""
    proof_p = max_working_pressure * THRESHOLDS["proof_pressure_multiplier"]
    return _clean({
        "max_working_pressure_MPa": max_working_pressure,
        "proof_pressure_MPa": proof_p,
        "hold_time_min": THRESHOLDS["proof_hold_time_min"],
        "acceptance_criteria": "无泄漏、无破裂、无永久变形",
        "multiplier": THRESHOLDS["proof_pressure_multiplier"],
        "pass": True
    })


def calc_burst_pressure(max_working_pressure: float) -> Dict:
    """Calculate burst pressure requirements (Section 3.8.2)"""
    burst_p = max_working_pressure * THRESHOLDS["burst_pressure_multiplier"]
    return _clean({
        "max_working_pressure_MPa": max_working_pressure,
        "burst_pressure_MPa": burst_p,
        "hold_time_min": THRESHOLDS["burst_hold_time_min"],
        "acceptance_criteria": "无破裂",
        "multiplier": THRESHOLDS["burst_pressure_multiplier"],
        "pass": True
    })


def verify_leak_rate(measured_leak: float, leak_type: str = "internal") -> Dict:
    """Verify leak rate against standard (Section 3.8.3)"""
    limit = THRESHOLDS["internal_leak_max"]
    return _clean({
        "measured_Pa_m3_s": measured_leak,
        "limit_Pa_m3_s": limit,
        "pass": measured_leak <= limit,
        "type": leak_type,
        "margin_db": round(20 * math.log10(limit / max(measured_leak, 1e-20)), 2)
    })


def verify_rated_output_pressure(rated: float, measured: float) -> Dict:
    """Verify rated output pressure deviation (Section 3.8.4)"""
    deviation_pct = abs(measured - rated) / rated * 100.0
    return _clean({
        "rated_MPa": rated,
        "measured_MPa": measured,
        "deviation_pct": round(deviation_pct, 3),
        "limit_pct": THRESHOLDS["rated_pressure_deviation_max"],
        "pass": deviation_pct <= THRESHOLDS["rated_pressure_deviation_max"]
    })


def verify_lockup_pressure(rated_pressure: float, lockup_pressure: float) -> Dict:
    """Verify lock-up pressure deviation (Section 3.8.5.3)"""
    deviation_pct = abs(lockup_pressure - rated_pressure) / rated_pressure * 100.0
    pass_result = (THRESHOLDS["lockup_pressure_deviation_min"]
                   <= deviation_pct
                   <= THRESHOLDS["lockup_pressure_deviation_max"])
    return _clean({
        "rated_MPa": rated_pressure,
        "lockup_MPa": lockup_pressure,
        "deviation_pct": round(deviation_pct, 3),
        "limit_min_pct": THRESHOLDS["lockup_pressure_deviation_min"],
        "limit_max_pct": THRESHOLDS["lockup_pressure_deviation_max"],
        "pass": pass_result
    })


def calc_elastic_element_overload(working_pressure: float) -> Dict:
    """Calculate elastic element overload test requirements (Section 3.6.3.2.2)"""
    overload_p = working_pressure * THRESHOLDS["elastic_element_overload_min"]
    return _clean({
        "overload_pressure_MPa": overload_p,
        "min_cycles": THRESHOLDS["elastic_element_overload_cycles_min"],
        "min_duration_per_cycle_s": THRESHOLDS["elastic_element_overload_duration_min"],
        "total_min_duration_s": (THRESHOLDS["elastic_element_overload_cycles_min"]
                                 * THRESHOLDS["elastic_element_overload_duration_min"]),
        "requirements": [
            "承受不小于2倍最大工作压力，不少于20次，每次不少于10s",
            "在最低工作温度下，施加不小于2倍最大工作压力，浸泡2h后进行泄漏检查",
            "通过极端力学环境试验后进行泄漏检查"
        ]
    })


def generate_thermal_vacuum_profile(params: Dict) -> Dict:
    """Generate thermal vacuum test profile (Section 3.10.4)"""
    level = params.get("level", "qual")  # qual or accept
    t_max = params.get("t_max_operating", 55)
    t_min = params.get("t_min_operating", -30)
    cycles = params.get("cycles_override", None)

    if level == "qual":
        profile = dict(ENV_TEST_PROFILES["thermal_vacuum_qual"])
        cycles = cycles if cycles else profile["cycles_min"]
        t_high = t_max + 10
        t_low = t_min - 10
    else:
        profile = dict(ENV_TEST_PROFILES["thermal_vacuum_accept"])
        cycles = cycles if cycles else profile["cycles_min"]
        t_high = t_max + 5
        t_low = t_min - 5

    dwell_h = profile["dwell_per_extreme_h"]
    total_h = cycles * (2 * dwell_h + 2)

    profile_points = []
    current_temp = 20  # start at room temp
    for cycle in range(1, int(cycles) + 1):
        profile_points.append({"cycle": cycle, "phase": "ramp to hot", "temp_C": t_high, "cumulative_h": round((cycle-1)*(2*dwell_h+2) + 1, 1)})
        profile_points.append({"cycle": cycle, "phase": "hot dwell", "temp_C": t_high, "cumulative_h": round((cycle-1)*(2*dwell_h+2) + 1 + dwell_h, 1)})
        profile_points.append({"cycle": cycle, "phase": "ramp to cold", "temp_C": t_low, "cumulative_h": round((cycle-1)*(2*dwell_h+2) + 1 + dwell_h + 1, 1)})
        profile_points.append({"cycle": cycle, "phase": "cold dwell", "temp_C": t_low, "cumulative_h": round((cycle)*(2*dwell_h+2), 1)})

    return _clean({
        "level": level,
        "min_pressure_Pa": 1.3e-3,
        "t_max_operating_C": t_max,
        "t_min_operating_C": t_min,
        "t_high_C": t_high,
        "t_low_C": t_low,
        "cycles": cycles,
        "dwell_per_extreme_h": dwell_h,
        "total_duration_est_h": round(total_h, 1),
        "first_last_cycle_hot_cold": True,
        "profile_points": profile_points,
        "post_test_checks": [
            "内部泄漏率（第3.8.3.2条）",
            "额定出口压力（第3.8.4条）",
            "压力特性（第3.8.5条）",
            "动态特性（第3.8.6条）",
            "出口压力精度（第3.8.7条）"
        ],
        "notes": [
            "测温传感器应安装在减压阀本体上（非试验箱壁）",
            "温度变化率<1°C/h时可认为温度已稳定",
            "第一个和最后一个循环须进行高温启动+低温启动性能测试",
            f"最后一个循环应从高温回归室温"
        ]
    })


def generate_thermal_cycle_profile(params: Dict) -> Dict:
    """Generate thermal cycling test profile (Section 3.10.5)"""
    level = params.get("level", "qual")
    t_max = params.get("t_max_operating", 55)
    t_min = params.get("t_min_operating", -30)
    cycles = params.get("cycles_override", None)

    if level == "qual":
        profile = dict(ENV_TEST_PROFILES["thermal_cycle_qual"])
        cycles = cycles if cycles else profile["cycles_min"]
        t_high = t_max + 10
        t_low = t_min - 10
    else:
        profile = dict(ENV_TEST_PROFILES["thermal_cycle_accept"])
        cycles = cycles if cycles else profile["cycles_min"]
        t_high = t_max + 5
        t_low = t_min - 5

    dwell_h = profile["dwell_per_extreme_h"]
    total_h = cycles * (2 * dwell_h + 2)

    return _clean({
        "level": level,
        "pressure": "atmospheric",
        "t_max_operating_C": t_max,
        "t_min_operating_C": t_min,
        "t_high_C": t_high,
        "t_low_C": t_low,
        "cycles": cycles,
        "ramp_rate": profile["ramp_rate"],
        "dwell_per_extreme_h": dwell_h,
        "total_duration_est_h": round(total_h, 1),
        "post_test_checks": [
            "外部泄漏率（第3.8.3.2条）",
            "额定出口压力（第3.8.4条）",
            "压力特性（第3.8.5条）",
            "动态特性（第3.8.6条）",
            "出口压力精度（第3.8.7条）"
        ]
    })


def verify_cleanliness(particles: List[Dict]) -> Dict:
    """Verify cleanliness per Table 2 (Section 3.11)"""
    results = []
    for size_range, table_row in [
        (">10 um", CLEANLINESS_TABLE[0]),
        ("6~10 um", CLEANLINESS_TABLE[1])
    ]:
        entry = next((p for p in particles if p.get("size_range") == size_range), None)
        count = entry["count"] if entry else 0
        results.append({
            "size_range": size_range,
            "count": count,
            "limit": table_row["max_count_per_10L"],
            "pass": count <= table_row["max_count_per_10L"]
        })
    return _clean({"results": results, "overall_pass": all(r["pass"] for r in results)})


def generate_compliance_checklist(params: Dict) -> Dict:
    """Generate a compliance checklist based on valve configuration"""
    valve_type = params.get("valve_type", "direct")
    maturity = params.get("maturity", "new")  # new / mature
    use_case = params.get("use_case", "qualification")

    items = []
    total = 0
    passed = 0

    for item in INSPECTION_ITEMS:
        applicable = True
        # Only mature designs may skip C inspection
        if maturity == "mature" and item["C"] and not item["A"]:
            applicable = item["qual"]  # qual always required
        if use_case == "delivery_acceptance":
            applicable = item["A"]
        elif use_case == "qualification":
            applicable = item["qual"]

        items.append(_clean({
            "no": item["no"],
            "item": item["item"],
            "chapter": item["chapter"],
            "method": item["method"],
            "applicable": applicable,
            "status": "待检验",
            "result": "未测试",
            "notes": ""
        }))
        if applicable:
            total += 1

    return _clean({
        "valve_type": valve_type,
        "maturity": maturity,
        "use_case": use_case,
        "total_items": total,
        "passed": passed,
        "items": items,
        "reference_standard": STANDARD_ID
    })


def calc_safety_margin(params: Dict) -> Dict:
    """Calculate safety margins per Section 3.13"""
    burst_p = params.get("burst_pressure_MPa", 0)
    proof_p = params.get("proof_pressure_MPa", 0)
    max_working_p = params.get("max_working_pressure_MPa", 0)
    design_p = params.get("design_burst_MPa", 0) or burst_p

    margins = {
        "burst_vs_working": round(design_p / max_working_p, 2) if max_working_p > 0 else None,
        "burst_required": THRESHOLDS["burst_pressure_multiplier"],
        "proof_vs_working": round(proof_p / max_working_p, 2) if max_working_p > 0 else None,
        "proof_required": THRESHOLDS["proof_pressure_multiplier"],
        "burst_pass": (design_p / max_working_p >= THRESHOLDS["burst_pressure_multiplier"]) if max_working_p > 0 else False,
        "proof_pass": (proof_p / max_working_p >= THRESHOLDS["proof_pressure_multiplier"]) if max_working_p > 0 else False,
    }
    return _clean(margins)


def verify_life_cycles(cycles: int) -> Dict:
    """Verify life cycles (Section 3.12)"""
    return _clean({
        "cycles": cycles,
        "min_required": THRESHOLDS["min_life_cycles"],
        "pass": cycles >= THRESHOLDS["min_life_cycles"],
        "margin_pct": round((cycles - THRESHOLDS["min_life_cycles"]) / THRESHOLDS["min_life_cycles"] * 100, 1)
    })


# ===========================================================================
# COMPREHENSIVE DESIGN ASSISTANT
# ===========================================================================

def design_assistant(params: Dict) -> Dict:
    """Comprehensive PRV design/verification against QJ 20156-2012"""
    max_wp = params.get("max_working_pressure_MPa", 5.0)
    rated_op = params.get("rated_output_pressure_MPa", 1.0)
    t_max = params.get("t_max_operating_C", 55)
    t_min = params.get("t_min_operating_C", -30)
    valve_type = params.get("valve_type", "direct")
    maturity = params.get("maturity", "new")

    return _clean({
        "standard": {"id": STANDARD_ID, "title": STANDARD_TITLE_CN, "effective": STANDARD_EFFECTIVE},
        "proof_pressure": calc_proof_pressure(max_wp),
        "burst_pressure": calc_burst_pressure(max_wp),
        "safety_margin": calc_safety_margin({
            "burst_pressure_MPa": max_wp * THRESHOLDS["burst_pressure_multiplier"],
            "proof_pressure_MPa": max_wp * THRESHOLDS["proof_pressure_multiplier"],
            "max_working_pressure_MPa": max_wp
        }),
        "elastic_element_overload": calc_elastic_element_overload(max_wp),
        "thermal_vacuum_qual": generate_thermal_vacuum_profile({"level": "qual", "t_max_operating": t_max, "t_min_operating": t_min}),
        "thermal_vacuum_accept": generate_thermal_vacuum_profile({"level": "accept", "t_max_operating": t_max, "t_min_operating": t_min}),
        "thermal_cycle_qual": generate_thermal_cycle_profile({"level": "qual", "t_max_operating": t_max, "t_min_operating": t_min}),
        "thermal_cycle_accept": generate_thermal_cycle_profile({"level": "accept", "t_max_operating": t_max, "t_min_operating": t_min}),
        "life_requirement": verify_life_cycles(THRESHOLDS["min_life_cycles"]),
        "leak_limit_internal": THRESHOLDS["internal_leak_max"],
        "leak_limit_external": THRESHOLDS["external_leak_max"],
        "rated_output_tolerance_pct": THRESHOLDS["rated_pressure_deviation_max"],
        "lockup_range_pct": f"{THRESHOLDS['lockup_pressure_deviation_min']}~{THRESHOLDS['lockup_pressure_deviation_max']}",
        "inspection_matrix": generate_compliance_checklist({"valve_type": valve_type, "maturity": maturity, "use_case": "qualification"}),
        "operating_temp_range": {"min_C": t_min, "max_C": t_max},
        "cleanliness_limits": CLEANLINESS_TABLE,
        "thresholds": THRESHOLDS
    })


def get_standard_info() -> Dict:
    """Get all standard information for the frontend browser"""
    return {
        "standard_id": STANDARD_ID,
        "title_cn": STANDARD_TITLE_CN,
        "title_en": STANDARD_TITLE_EN,
        "effective": STANDARD_EFFECTIVE,
        "scope": STANDARD_SCOPE,
        "chapter_tree": CHAPTER_TREE,
        "references": REFERENCES,
        "definitions": DEFINITIONS,
        "inspection_items": INSPECTION_ITEMS,
        "inspection_total": len(INSPECTION_ITEMS),
        "valve_types": VALVE_TYPES,
        "cleanliness_table": CLEANLINESS_TABLE,
        "assembly_env": ASSEMBLY_ENV,
        "test_env": TEST_ENV,
        "storage_conditions": STORAGE_CONDITIONS,
        "thresholds": THRESHOLDS,
        "env_test_profiles": ENV_TEST_PROFILES,
        "elastic_element_reqs": ELASTIC_ELEMENT_REQUIREMENTS,
        "temp_range_default": TEMP_RANGE_DEFAULT,
    }