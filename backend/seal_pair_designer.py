#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
航空航天阀门密封副设计计算程序
Aerospace Valve Seal Pair Design Calculation Program
===========================================================================
版本: 4.0
日期: 2026-05-17
适用标准: ISO 5208 / ANSI FCI 70-2 / ECSS-E-ST-32-02C
设计依据:
  - Hertz 弹性接触理论 (接触应力/接触宽度计算)
  - Roth 分子流泄漏模型 (Kn数流态判断, 分子流/粘性流分界)
  - 密封状态判定采用二分迭代法确定临界密封压力
  - 泄漏等级评定依据 ISO 5208-2015 (AA ~ G 级)

参考文献:
  [1] Li S, Yin B, Wei C, et al. Structural analysis and multi-objective
      optimization of sealing structure for cryogenic liquid hydrogen
      triple-offset butterfly valve. Scientific Reports, 2025, 15: 36059.
  [2] Choi J, Kim H. Concave Contact Geometry for Enhanced Sealing and
      Structural Integrity in Ultra-High Pressure Hydrogen Solenoid Valves.
      Applied Sciences, 2025, 15(11): 6184.
  [3] ISO 5208:2015 Industrial valves — Pressure testing of metallic valves.
  [4] ANSI/FCI 70-2-2013 Control Valve Seat Leakage.
  [5] ECSS-E-ST-32-02C Rev.2 Structural design and verification of pressurized
      hardware (2025).
  [6] Roth A. Vacuum Sealing Techniques. AIP Press, 1994.

注意: 本程序适用于:
  - 金属-金属 (硬密封)
  - 金属-聚合物 (软密封，如PTFE/PCTFE/PEEK等)
===========================================================================
"""

import math
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum

# ===========================================================================
# JSON serialization cleanup function (handles Infinity/NaN)
# ===========================================================================

def _clean(obj):
    """Recursively clean Infinity/NaN -> None, ensure JSON-serializable"""
    import math as _math
    from enum import Enum as _Enum
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    if isinstance(obj, float):
        if _math.isinf(obj) or _math.isnan(obj):
            return None
    if isinstance(obj, _Enum):
        return obj.value
    return obj



# ===========================================================================
# 一、枚举与常数定义
# ===========================================================================

class SealType(Enum):
    """密封副类型"""
    METAL_METAL = "metal-metal"      # 金属-金属硬密封
    METAL_POLYMER = "metal-polymer"  # 金属-聚合物软密封
    METAL_ELASTOMER = "metal-elastomer"  # 金属-弹性体（O形圈等）


class FlowRegime(Enum):
    """泄漏流态"""
    MOLECULAR = "molecular"    # 分子流 (Kn > 1.0)
    TRANSITIONAL = "transitional"  # 过渡流 (0.01 < Kn < 1.0)
    VISCOUS = "viscous"        # 粘性流 (Kn < 0.01)


class LeakClass(Enum):
    """ISO 5208 泄漏等级"""
    AA = "AA"  # 零泄漏 (核/航天级)
    A = "A"    # 无可见泄漏
    B = "B"    # 0.0006 × DN mm³/s
    C = "C"    # 0.0018 × DN
    D = "D"    # 0.006 × DN (默认工业级)
    E = "E"    # 0.018 × DN
    EE = "EE"  # 0.060 × DN
    F = "F"    # 0.180 × DN
    G = "G"    # 0.600 × DN


class OptimizationGoal(Enum):
    """优化目标"""
    MIN_LEAK_RATE = "min_leak_rate"       # 最小泄漏率
    MIN_CONTACT_STRESS = "min_contact_stress"  # 最小接触应力
    MIN_WEIGHT = "min_weight"             # 最小重量
    BALANCED = "balanced"                 # 综合平衡


# ISO 5208 泄漏等级对应泄漏系数 (单位: mm³/s per mm DN)
# 参照 ISO 5208-2015 标准: AA级为核/航天级零泄漏
LEAK_CLASS_COEFFICIENTS = {
    LeakClass.AA: 0.0,      # 零泄漏
    LeakClass.A:  0.0001,   # 无可见泄漏 (极小值)
    LeakClass.B:  0.0006,
    LeakClass.C:  0.0018,
    LeakClass.D:  0.006,
    LeakClass.E:  0.018,
    LeakClass.EE: 0.060,
    LeakClass.F:  0.180,
    LeakClass.G:  0.600,
}

# 材料数据库: 包含弹性模量、泊松比、屈服强度、密封比压系数等
MATERIAL_DATABASE = {
    # 金属材料
    "316L_SS": {
        "name": "316L Stainless Steel",
        "E": 193e9,          # 弹性模量 [Pa]
        "nu": 0.30,          # 泊松比
        "sigma_y": 205e6,    # 屈服强度 [Pa]
        "sigma_uts": 515e6,  # 抗拉强度 [Pa]
        "hardness": 180,     # 布氏硬度 [HB]
        "density": 8000,     # 密度 [kg/m³]
        "thermal_expansion": 16.0e-6,  # 热膨胀系数 [1/K]
        "thermal_conductivity": 16.3,  # 导热系数 [W/(m·K)]
        "category": "metal",
        "cryo_compatible": True,
        "max_temp": 870,     # 最高使用温度 [°C]
        "min_temp": -196,    # 最低使用温度 [°C]
    },
    "INCONEL_718": {
        "name": "Inconel 718",
        "E": 205e9,
        "nu": 0.29,
        "sigma_y": 1034e6,
        "sigma_uts": 1275e6,
        "hardness": 350,
        "density": 8190,
        "thermal_expansion": 13.0e-6,
        "thermal_conductivity": 11.4,
        "category": "metal",
        "cryo_compatible": True,
        "max_temp": 980,
        "min_temp": -253,    # 液氢温区兼容
    },
    "TI_6AL4V": {
        "name": "Ti-6Al-4V (Grade 5)",
        "E": 114e9,
        "nu": 0.33,
        "sigma_y": 880e6,
        "sigma_uts": 950e6,
        "hardness": 330,
        "density": 4430,
        "thermal_expansion": 8.6e-6,
        "thermal_conductivity": 6.7,
        "category": "metal",
        "cryo_compatible": True,
        "max_temp": 400,
        "min_temp": -253,
    },
    "AL_6061_T6": {
        "name": "Aluminum 6061-T6",
        "E": 69e9,
        "nu": 0.33,
        "sigma_y": 276e6,
        "sigma_uts": 310e6,
        "hardness": 95,
        "density": 2700,
        "thermal_expansion": 23.6e-6,
        "thermal_conductivity": 167,
        "category": "metal",
        "cryo_compatible": True,
        "max_temp": 200,
        "min_temp": -253,
    },
    "17_4PH": {
        "name": "17-4PH Stainless Steel",
        "E": 196e9,
        "nu": 0.27,
        "sigma_y": 1000e6,
        "sigma_uts": 1070e6,
        "hardness": 340,
        "density": 7800,
        "thermal_expansion": 10.8e-6,
        "thermal_conductivity": 18.0,
        "category": "metal",
        "cryo_compatible": True,
        "max_temp": 480,
        "min_temp": -196,
    },
    # 聚合物密封材料
    "PTFE": {
        "name": "PTFE (Teflon)",
        "E": 0.5e9,
        "nu": 0.46,
        "sigma_y": 14e6,
        "sigma_uts": 28e6,
        "hardness": 55,       # Shore D
        "density": 2200,
        "thermal_expansion": 125e-6,
        "thermal_conductivity": 0.25,
        "category": "polymer",
        "cryo_compatible": False,
        "max_temp": 260,
        "min_temp": -50,
        "leak_factor_m": 0.75,  # 泄漏系数 (实验回归)
        "gasket_factor_a": 3.5,  # PVRC垫片系数 a
        "gasket_factor_b": 0.20,  # PVRC垫片系数 b
    },
    "PCTFE": {
        "name": "PCTFE (Kel-F)",
        "E": 1.5e9,
        "nu": 0.44,
        "sigma_y": 35e6,
        "sigma_uts": 42e6,
        "hardness": 75,       # Shore D
        "density": 2130,
        "thermal_expansion": 70e-6,
        "thermal_conductivity": 0.20,
        "category": "polymer",
        "cryo_compatible": True,
        "max_temp": 200,
        "min_temp": -253,
        "leak_factor_m": 0.65,
        "gasket_factor_a": 3.8,
        "gasket_factor_b": 0.18,
    },
    "PEEK": {
        "name": "PEEK",
        "E": 3.6e9,
        "nu": 0.40,
        "sigma_y": 100e6,
        "sigma_uts": 110e6,
        "hardness": 85,       # Shore D
        "density": 1320,
        "thermal_expansion": 47e-6,
        "thermal_conductivity": 0.25,
        "category": "polymer",
        "cryo_compatible": True,
        "max_temp": 340,
        "min_temp": -196,
        "leak_factor_m": 0.55,
        "gasket_factor_a": 4.2,
        "gasket_factor_b": 0.15,
    },
    "FKM": {
        "name": "FKM (Viton)",
        "E": 0.01e9,
        "nu": 0.49,
        "sigma_y": 8e6,
        "sigma_uts": 15e6,
        "hardness": 75,       # Shore A
        "density": 1850,
        "thermal_expansion": 200e-6,
        "thermal_conductivity": 0.20,
        "category": "elastomer",
        "cryo_compatible": False,
        "max_temp": 230,
        "min_temp": -30,
        "leak_factor_m": 0.40,
        "gasket_factor_a": 2.5,
        "gasket_factor_b": 0.35,
    },
    "FFKM": {
        "name": "FFKM (Kalrez / Perfluoroelastomer)",
        "E": 0.015e9,
        "nu": 0.49,
        "sigma_y": 12e6,
        "sigma_uts": 20e6,
        "hardness": 80,       # Shore A
        "density": 2000,
        "thermal_expansion": 180e-6,
        "thermal_conductivity": 0.18,
        "category": "elastomer",
        "cryo_compatible": True,
        "max_temp": 325,
        "min_temp": -40,
        "leak_factor_m": 0.35,
        "gasket_factor_a": 2.8,
        "gasket_factor_b": 0.30,
    },
}

# 气体物性数据库 (用于泄漏率计算)
GAS_PROPERTIES = {
    "N2": {
        "name": "Nitrogen",
        "M": 0.028,           # 摩尔质量 [kg/mol]
        "viscosity": 17.8e-6, # 动力粘度 [Pa·s] @20°C
        "mean_free_path": 66e-9,  # 平均自由程 [m] @1atm,20°C
        "gamma": 1.40,        # 比热比
    },
    "He": {
        "name": "Helium",
        "M": 0.004,
        "viscosity": 19.7e-6,
        "mean_free_path": 192e-9,
        "gamma": 1.66,
    },
    "H2": {
        "name": "Hydrogen",
        "M": 0.002,
        "viscosity": 8.9e-6,
        "mean_free_path": 124e-9,
        "gamma": 1.41,
    },
    "O2": {
        "name": "Oxygen",
        "M": 0.032,
        "viscosity": 20.5e-6,
        "mean_free_path": 70e-9,
        "gamma": 1.40,
    },
    "Air": {
        "name": "Air",
        "M": 0.029,
        "viscosity": 18.2e-6,
        "mean_free_path": 68e-9,
        "gamma": 1.40,
    },
    "CH4": {
        "name": "Methane",
        "M": 0.016,
        "viscosity": 11.0e-6,
        "mean_free_path": 54e-9,
        "gamma": 1.32,
    },
}

# 航天级密封关键性能指标 (参照 NASA-STD-5012 / ECSS)
AEROSPACE_SEAL_SPECS = {
    "leak_rate_he_std": 1e-9,       # 氦检标准漏率 [mbar·L/s]
    "leak_rate_he_max": 1e-7,       # 氦检最大允许漏率
    "max_contact_stress_ratio": 0.9,  # 最大接触应力/屈服强度 比值上限
    "min_safety_factor": 1.50,      # 最小安全系数 (屈服)
    "min_safety_factor_uts": 2.50,  # 最小安全系数 (抗拉)
    "max_surface_roughness_Ra": 0.4e-6,  # 最大表面粗糙度 Ra [m] (金属密封)
    "max_surface_roughness_Ra_polymer": 0.8e-6,  # 聚合物密封
    "min_contact_width_ratio": 1.5,  # 最小接触宽度/等效间隙 比值
    "thermal_cycling_range": (-196, 150),  # 热循环温度范围 [°C]
    "vibration_grms": 20.0,          # 随机振动量级 [Grms]
    "min_cycle_life": 10000,         # 最小启闭寿命 [次]
}

# 通用常数
R_GAS = 8.314           # 通用气体常数 [J/(mol·K)]
T_STANDARD = 293.15     # 标准温度 [K] (20°C)
P_STANDARD = 101325     # 标准大气压 [Pa]


# ===========================================================================
# 二、核心数据结构
# ===========================================================================

@dataclass
class MaterialProperties:
    """材料属性"""
    name: str
    E: float              # 弹性模量 [Pa]
    nu: float             # 泊松比
    sigma_y: float        # 屈服强度 [Pa]
    sigma_uts: float      # 抗拉强度 [Pa]
    hardness: float       # 硬度 [HB or Shore]
    density: float        # 密度 [kg/m³]
    thermal_expansion: float  # 热膨胀系数 [1/K]
    thermal_conductivity: float  # 导热系数 [W/(m·K)]
    category: str         # metal / polymer / elastomer
    cryo_compatible: bool  # 是否兼容低温
    max_temp: float       # 最高使用温度 [°C]
    min_temp: float       # 最低使用温度 [°C]
    leak_factor_m: float = 0.7    # 泄漏系数 (仅聚合物)
    gasket_factor_a: float = 3.5  # PVRC垫片系数 a
    gasket_factor_b: float = 0.2  # PVRC垫片系数 b


@dataclass
class GasProperties:
    """气体物性"""
    name: str
    M: float              # 摩尔质量 [kg/mol]
    viscosity: float      # 动力粘度 [Pa·s]
    mean_free_path: float  # 平均自由程 [m] @1atm,20°C
    gamma: float           # 比热比


@dataclass
class SealGeometryInput:
    """密封副几何输入参数"""
    # 座面/阀瓣接触几何 (按 Hertz 接触分类)
    contact_type: str = "sphere_on_cone"  # 接触类型:
    # sphere_on_cone: 球头-锥面
    # sphere_on_flat: 球头-平面
    # cylinder_on_flat: 圆柱-平面 (线接触)
    # cone_on_cone: 锥面-锥面
    # flat_on_flat: 平面-平面 (垫片密封)
    # concave_on_cone: 凹面-锥面 (新型凹面接触)

    # 关键尺寸
    seat_diameter: float = 10.0e-3       # 阀座密封面公称直径 [m]
    seat_angle: float = 60.0             # 阀座锥角 [°] (半角)
    sphere_radius: Optional[float] = None  # 球头半径 [m]
    seat_curvature_radius: Optional[float] = None  # 阀座曲率半径 [m]
    contact_width_design: float = 1.0e-3  # 设计接触宽度 [m]
    eccentricity: float = 0.0             # 偏心距 [m] (凹面接触)
    seat_width: float = 1.5e-3            # 阀座环带宽度 [m]
    roughness_Ra_seat: float = 0.4e-6     # 阀座表面粗糙度 Ra [m]
    roughness_Ra_seal: float = 0.4e-6     # 密封件表面粗糙度 Ra [m]


@dataclass
class OperatingConditions:
    """工况条件"""
    pressure_upstream: float      # 上游压力 [Pa]
    pressure_downstream: float    # 下游压力 [Pa]
    temperature: float = T_STANDARD  # 工作温度 [K]
    seal_force: Optional[float] = None  # 密封力 [N]
    preload_force: Optional[float] = None  # 预紧力 [N]
    spring_force: float = 0.0     # 弹簧辅助力 [N]
    safety_factor_req: float = 1.5  # 要求安全系数
    cycle_life_req: int = 10000   # 要求启闭寿命 [次]
    vibration_level: float = 0.0  # 振动量级 [Grms]


@dataclass
class SealDesignOutput:
    """密封副设计输出结果"""
    # 接触力学
    contact_stress_max: float = 0.0      # 最大接触应力 [Pa]
    contact_stress_avg: float = 0.0      # 平均接触应力 [Pa]
    contact_width: float = 0.0           # 实际接触宽度 [m]
    contact_area: float = 0.0            # 实际接触面积 [m²]
    hertz_contact_half_width: float = 0.0  # Hertz接触半宽 [m]
    effective_modulus: float = 0.0       # 等效弹性模量 [Pa]

    # 密封状态
    seal_pressure: float = 0.0           # 密封比压 [Pa]
    seal_pressure_ratio: float = 0.0     # 密封比压/介质压力 比值
    is_sealing: bool = False             # 是否满足密封条件
    critical_seal_force: float = 0.0     # 临界密封力 [N]

    # 泄漏
    flow_regime: FlowRegime = FlowRegime.MOLECULAR  # 流态
    knudsen_number: float = 0.0          # 克努森数
    effective_gap_height: float = 0.0    # 等效泄漏间隙 [m]
    leak_rate: float = 0.0               # 泄漏率 [Pa·m³/s]
    leak_rate_mbar_L_s: float = 0.0      # 泄漏率 [mbar·L/s]
    leak_rate_sccm: float = 0.0          # 泄漏率 [sccm]
    leak_class_achieved: LeakClass = LeakClass.G  # 达到的泄漏等级

    # 安全评定
    stress_ratio_yield: float = 0.0      # 应力/屈服强度
    stress_ratio_uts: float = 0.0        # 应力/抗拉强度
    safety_factor_yield: float = 0.0     # 屈服安全系数
    safety_factor_uts: float = 0.0       # 抗拉安全系数
    safety_pass: bool = False            # 安全评定是否通过

    # 可靠性
    predicted_cycle_life: float = 0.0    # 预测启闭寿命 [次]
    wear_depth_estimate: float = 0.0     # 预计磨损深度 [m]
    reliability_index: float = 0.0       # 可靠性指标 β

    # 质量估算
    estimated_mass: float = 0.0          # 密封副估计质量 [kg]


@dataclass
class SealDesignResult:
    """完整设计结果"""
    input_summary: Dict = field(default_factory=dict)
    output: SealDesignOutput = field(default_factory=SealDesignOutput)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    optimization_log: List[Dict] = field(default_factory=list)


# ===========================================================================
# 三、材料与气体工具函数
# ===========================================================================

def get_material(mat_key: str) -> MaterialProperties:
    """从材料数据库获取材料属性"""
    if mat_key not in MATERIAL_DATABASE:
        raise KeyError(f"材料 '{mat_key}' 不在数据库中。可用材料: {list(MATERIAL_DATABASE.keys())}")
    d = MATERIAL_DATABASE[mat_key]
    return MaterialProperties(**{k: d.get(k, 0) for k in MaterialProperties.__dataclass_fields__})


def get_gas(gas_key: str) -> GasProperties:
    """从气体数据库获取气体物性"""
    if gas_key not in GAS_PROPERTIES:
        raise KeyError(f"气体 '{gas_key}' 不在数据库中。可用气体: {list(GAS_PROPERTIES.keys())}")
    d = GAS_PROPERTIES[gas_key]
    return GasProperties(**d)


def calc_effective_modulus(E1: float, nu1: float, E2: float, nu2: float) -> float:
    """
    计算等效弹性模量 (Hertz 接触理论)
    E* = 1 / [(1 - nu1²)/E1 + (1 - nu2²)/E2]
    """
    return 1.0 / ((1.0 - nu1**2) / E1 + (1.0 - nu2**2) / E2)


def calc_effective_radius(R1: float, R2: float) -> float:
    """
    计算等效曲率半径
    1/R* = 1/R1 + 1/R2 (凸面R为正, 凹面R为负)
    用于凹面接触 (R_plunger/R_seat > 1)
    """
    if R1 == 0 or R2 == 0:
        return float('inf')
    return 1.0 / (1.0 / R1 + 1.0 / R2)


# ===========================================================================
# 四、Hertz 接触力学计算模块
# ===========================================================================

class HertzContactAnalysis:
    """
    Hertz 弹性接触理论计算模块
    适用于球-平面、球-锥面、圆柱-平面、凹面-锥面等接触类型
    """

    @staticmethod
    def sphere_on_flat(force: float, R_sphere: float,
                       E_star: float) -> Tuple[float, float, float]:
        """
        球-平面 Hertz 接触
        返回: (max_contact_stress, contact_radius, approach)
        """
        # 接触半径 a = (3FR*/(4E*))^(1/3)
        a = (3.0 * force * R_sphere / (4.0 * E_star)) ** (1.0 / 3.0)
        # 最大接触应力 p0 = 3F/(2πa²)
        p_max = 3.0 * force / (2.0 * math.pi * a**2)
        # 趋近量 δ = a²/R*
        approach = a**2 / R_sphere
        # 平均接触应力
        p_avg = force / (math.pi * a**2)
        return p_max, p_avg, a, approach

    @staticmethod
    def sphere_on_cone(force: float, R_sphere: float, alpha_deg: float,
                       E_star: float) -> Tuple[float, float, float, float]:
        """
        球-锥面 Hertz 接触
        alpha: 锥面半角 [°]
        适用于航天阀门典型的球头-锥面密封结构
        返回: (p_max, p_avg, contact_half_width, approach)
        """
        alpha_rad = math.radians(alpha_deg)
        # 等效半径修正 (锥面接触)
        R_equiv = R_sphere / math.sin(alpha_rad) if alpha_rad > 0.01 else R_sphere
        # 采用球-平面公式的修正形式
        p_max, p_avg, a, approach = HertzContactAnalysis.sphere_on_flat(
            force, R_equiv, E_star
        )
        # 锥面上的实际接触半宽 (投影修正)
        contact_hw = a / math.cos(alpha_rad)
        p_avg_corrected = force / (math.pi * a * contact_hw)
        return p_max, p_avg_corrected, contact_hw, approach

    @staticmethod
    def cylinder_on_flat(force: float, L_contact: float, R_cylinder: float,
                         E_star: float) -> Tuple[float, float, float]:
        """
        圆柱-平面 线接触 Hertz
        返回: (p_max, contact_half_width, approach)
        """
        # 单位长度载荷
        f_line = force / L_contact
        # 接触半宽 b = sqrt(4f_line R* / (π E*))
        b = math.sqrt(4.0 * f_line * R_cylinder / (math.pi * E_star))
        p_max = 2.0 * f_line / (math.pi * b)
        p_avg = f_line / (2.0 * b)
        return p_max, p_avg, b

    @staticmethod
    def concave_on_cone(force: float, R_plunger: float, R_seat: float,
                        e: float, alpha_deg: float, E_star: float
                        ) -> Tuple[float, float, float, float]:
        """
        凹面-锥面 Hertz 接触 (新型设计)
        适用于超高压氢阀等, R_plunger/R_seat > 1
        参考文献: Choi & Kim, Applied Sciences, 2025

        参数:
            force: 密封力 [N]
            R_plunger: 阀瓣(柱塞)曲率半径 [m]
            R_seat: 阀座曲率半径 [m]
            e: 偏心距 [m]
            alpha_deg: 锥面半角 [°]
            E_star: 等效弹性模量 [Pa]
        返回: (p_max, p_avg, contact_half_width, approach)
        """
        alpha_rad = math.radians(alpha_deg)
        # 等效半径 (凹面接触: R_seat取负号)
        R_equiv = 1.0 / abs(1.0 / R_plunger - 1.0 / R_seat)
        # 偏心距修正等效曲率
        if e > 0:
            R_equiv = R_equiv * (1.0 + e / R_plunger)
        # 采用球-平面公式
        p_max, p_avg, a, approach = HertzContactAnalysis.sphere_on_flat(
            force, R_equiv, E_star
        )
        # 锥面投影修正
        contact_hw = a / math.cos(alpha_rad)
        p_avg_corrected = force / (math.pi * a * contact_hw)
        return p_max, p_avg_corrected, contact_hw, approach


# ===========================================================================
# 五、泄漏率计算模块 (Roth 模型 + 流态判断)
# ===========================================================================

class LeakRateCalculator:
    """
    泄漏率计算模块
    基于 Roth 分子流模型，结合 Kn 数进行流态判断
    """

    @staticmethod
    def calc_knudsen_number(mean_free_path: float,
                            characteristic_length: float) -> float:
        """
        计算克努森数
        Kn = λ / L
        其中 λ 为气体平均自由程, L 为特征长度 (等效泄漏间隙)
        """
        if characteristic_length <= 0:
            return float('inf')
        return mean_free_path / characteristic_length

    @staticmethod
    def determine_flow_regime(Kn: float) -> FlowRegime:
        """根据Kn数判断流态"""
        if Kn > 1.0:
            return FlowRegime.MOLECULAR
        elif Kn < 0.01:
            return FlowRegime.VISCOUS
        else:
            return FlowRegime.TRANSITIONAL

    @staticmethod
    def estimate_effective_gap(roughness_Ra1: float, roughness_Ra2: float,
                                contact_stress: float, hardness_softer: float
                                ) -> float:
        """
        估算等效泄漏间隙
        基于 GW (Greenwood-Williamson) 粗糙表面接触模型简化

        参数:
            roughness_Ra1, roughness_Ra2: 两表面粗糙度 [m]
            contact_stress: 接触应力 [Pa]
            hardness_softer: 较软材料的硬度 [Pa]
        返回:
            等效泄漏间隙高度 [m]
        """
        # 复合粗糙度
        sigma_rough = math.sqrt(roughness_Ra1**2 + roughness_Ra2**2)
        # 无量纲接触应力
        if hardness_softer > 0:
            p_ratio = min(contact_stress / hardness_softer, 0.95)
        else:
            p_ratio = 0.95
        # 等效间隙: 随接触应力增大而减小
        gap = sigma_rough * (1.0 - p_ratio) ** 1.5
        return max(gap, 1e-12)  # 最小间隙限制

    @staticmethod
    def calc_molecular_flow_leak_rate(p_up: float, p_down: float,
                                       gap_height: float, perimeter: float,
                                       contact_width: float, M: float,
                                       T: float) -> float:
        """
        Roth 分子流泄漏率模型
        Q = (4/3) * (2πRT/M)^(1/2) * (h²/L_perimeter) * (p_up - p_down) * perimeter

        参数:
            p_up, p_down: 上/下游压力 [Pa]
            gap_height: 等效泄漏间隙高度 [m]
            perimeter: 密封周长 [m]
            contact_width: 接触宽度 [m]
            M: 气体摩尔质量 [kg/mol]
            T: 温度 [K]
        返回:
            泄漏率 [Pa·m³/s]
        """
        if gap_height <= 0 or contact_width <= 0:
            return 0.0
        # 平均分子速度相关的流导系数
        v_mean_factor = math.sqrt(2.0 * math.pi * R_GAS * T / M)
        # 分子流泄漏率 (Roth公式)
        Q = (4.0 / 3.0) * v_mean_factor * (gap_height**2 / contact_width) * \
            (p_up - p_down) * perimeter
        return max(Q, 0.0)

    @staticmethod
    def calc_viscous_flow_leak_rate(p_up: float, p_down: float,
                                     gap_height: float, perimeter: float,
                                     contact_width: float, viscosity: float
                                     ) -> float:
        """
        粘性流泄漏率 (Poiseuille 流)
        Q = (π h³ / (12 η L)) * (p_up² - p_down²) / (2 p_up) * perimeter

        参数:
            p_up, p_down: 上/下游压力 [Pa]
            gap_height: 等效泄漏间隙高度 [m]
            perimeter: 密封周长 [m]
            contact_width: 接触宽度 [m]
            viscosity: 气体动力粘度 [Pa·s]
        返回:
            泄漏率 [Pa·m³/s]
        """
        if gap_height <= 0 or contact_width <= 0:
            return 0.0
        p_avg = (p_up + p_down) / 2.0 if p_up > 0 else p_up
        Q = (math.pi * gap_height**3 / (12.0 * viscosity * contact_width)) * \
            (p_up - p_down) * p_avg * perimeter
        return max(Q, 0.0)

    @staticmethod
    def calc_transitional_flow_leak_rate(p_up: float, p_down: float,
                                          gap_height: float, perimeter: float,
                                          contact_width: float, M: float,
                                          viscosity: float, Kn: float,
                                          T: float) -> float:
        """
        过渡流泄漏率 (分子流+粘性流线性插值)
        基于 Kn 数在分子流和粘性流之间加权
        """
        Q_mol = LeakRateCalculator.calc_molecular_flow_leak_rate(
            p_up, p_down, gap_height, perimeter, contact_width, M, T
        )
        Q_vis = LeakRateCalculator.calc_viscous_flow_leak_rate(
            p_up, p_down, gap_height, perimeter, contact_width, viscosity
        )
        # 对数插值
        if Kn <= 0.01:
            w_mol = 0.0
        elif Kn >= 1.0:
            w_mol = 1.0
        else:
            # 对数域线性插值
            log_Kn = math.log10(Kn)
            log_min = math.log10(0.01)
            log_max = math.log10(1.0)
            w_mol = (log_Kn - log_min) / (log_max - log_min)
        return w_mol * Q_mol + (1.0 - w_mol) * Q_vis

    @staticmethod
    def convert_leak_rate_units(Q_Pa_m3_s: float, T: float = T_STANDARD,
                                 p_ref: float = P_STANDARD) -> Dict[str, float]:
        """
        泄漏率单位转换
        输入: Pa·m³/s
        输出: 多种常用单位

        常用漏率单位换算关系:
          1 Pa·m³/s = 10 mbar·L/s
          1 sccm ≈ 1.689e-3 Pa·m³/s (标准状态)
        """
        Q_mbar_L_s = Q_Pa_m3_s * 10.0  # 1 Pa·m³/s = 10 mbar·L/s
        # sccm: 标准立方厘米每分钟 (1 atm, 0°C 或 20°C)
        # 采用 20°C 标准
        Q_sccm = Q_Pa_m3_s / P_STANDARD * 60.0 * 1e6
        return {
            "Pa_m3_s": Q_Pa_m3_s,
            "mbar_L_s": Q_mbar_L_s,
            "sccm": Q_sccm,
            "atm_cc_s": Q_Pa_m3_s / P_STANDARD * 1e6,  # atm·cc/s
        }

    @staticmethod
    def classify_leak_level(Q_Pa_m3_s: float, DN: float = 10.0) -> LeakClass:
        """
        根据泄漏率评定密封等级 (ISO 5208)
        参照 ISO 5208-2015 等级划分
        """
        # 将泄漏率转换为 mm³/s (水当量)
        # 简化: 1 Pa·m³/s ≈ 10⁶ mm³/s (水) → 换算系数
        Q_mm3_per_s = Q_Pa_m3_s * 1e6 / 1000.0  # 近似换算
        Q_per_DN = Q_mm3_per_s / DN if DN > 0 else float('inf')

        for leak_class in [LeakClass.AA, LeakClass.A, LeakClass.B,
                            LeakClass.C, LeakClass.D, LeakClass.E,
                            LeakClass.EE, LeakClass.F, LeakClass.G]:
            coeff = LEAK_CLASS_COEFFICIENTS[leak_class]
            if Q_per_DN <= coeff * DN:
                return leak_class
        return LeakClass.G


# ===========================================================================
# 六、密封状态判定与临界密封力
# ===========================================================================

class SealStateAnalyzer:
    """
    密封状态分析器
    采用二分迭代法确定临界密封压力
    """

    @staticmethod
    def determine_seal_state(seal_pressure: float, media_pressure: float,
                              seal_pressure_ratio_min: float = 1.2) -> Tuple[bool, float]:
        """
        判定密封状态
        密封条件: 密封比压 >= 最小密封比压系数 × 介质压力
        对于金属密封, 通常要求 m >= 1.5~3.0 倍介质压力
        对于软密封, m >= 1.0~1.5 倍介质压力
        """
        ratio = seal_pressure / media_pressure if media_pressure > 0 else float('inf')
        is_sealing = ratio >= seal_pressure_ratio_min
        return is_sealing, ratio

    @staticmethod
    def find_critical_seal_force(geometry: SealGeometryInput,
                                  materials: Tuple[MaterialProperties, MaterialProperties],
                                  media_pressure: float,
                                  seal_pressure_ratio_min: float = 1.2,
                                  max_iter: int = 50,
                                  tol: float = 1e-3) -> float:
        """
        二分法迭代求解临界密封力

        返回: 临界密封力 [N]
        """
        mat_seat, mat_seal = materials
        E_star = calc_effective_modulus(mat_seat.E, mat_seat.nu,
                                         mat_seal.E, mat_seal.nu)
        # 较软材料硬度 (用于等效间隙估算)
        hardness_softer = min(mat_seat.sigma_y, mat_seal.sigma_y)

        # 密封周长
        perimeter = math.pi * geometry.seat_diameter

        # 二分法搜索范围
        F_low = 0.1  # [N]
        F_high = mat_seat.sigma_y * math.pi * (geometry.seat_diameter / 2)**2
        F_high = min(F_high, 1e6)  # 上限限制

        F_critical = F_high

        for i in range(max_iter):
            F_mid = (F_low + F_high) / 2.0

            # 计算该力下的接触应力和状态
            if geometry.contact_type == "sphere_on_cone":
                p_max, p_avg, contact_hw, _ = HertzContactAnalysis.sphere_on_cone(
                    F_mid, geometry.sphere_radius or 5e-3,
                    geometry.seat_angle, E_star
                )
            elif geometry.contact_type == "concave_on_cone":
                p_max, p_avg, contact_hw, _ = HertzContactAnalysis.concave_on_cone(
                    F_mid, geometry.sphere_radius or 5e-3,
                    geometry.seat_curvature_radius or 4.5e-3,
                    geometry.eccentricity, geometry.seat_angle, E_star
                )
            else:
                p_max, p_avg, contact_hw, _ = HertzContactAnalysis.sphere_on_flat(
                    F_mid, geometry.sphere_radius or 5e-3, E_star
                )

            # 密封比压
            seal_pressure = p_avg

            # 判断密封状态
            is_sealing, ratio = SealStateAnalyzer.determine_seal_state(
                seal_pressure, media_pressure, seal_pressure_ratio_min
            )

            # 二分法调整
            if is_sealing:
                F_critical = F_mid
                F_high = F_mid
            else:
                F_low = F_mid

            if (F_high - F_low) / F_low < tol and i > 5:
                break

        return F_critical


# ===========================================================================
# 七、可靠性评估模块
# ===========================================================================

class ReliabilityAnalyzer:
    """
    密封副可靠性评估
    包括: 寿命预估、磨损分析、可靠性指标计算
    """

    @staticmethod
    def estimate_wear_depth(contact_stress: float, hardness_softer: float,
                             cycle_count: int, wear_coeff: float = 1e-8) -> float:
        """
        Archard 磨损模型预估磨损深度
        h_wear = K * p * L_slide / H

        参数:
            contact_stress: 接触应力 [Pa]
            hardness_softer: 较软材料硬度 [Pa]
            cycle_count: 运行周期数
            wear_coeff: 磨损系数 K (金属-金属 ~1e-5, 金属-聚合物 ~1e-8)
        """
        # 每周期滑动距离估算 (接触宽度的 10%)
        slide_distance_per_cycle = 0.1e-3  # [m] 预估
        total_slide = cycle_count * slide_distance_per_cycle
        h_wear = wear_coeff * contact_stress * total_slide / hardness_softer
        return h_wear

    @staticmethod
    def calc_reliability_index(safety_factor: float, variation_coeff: float = 0.15
                                ) -> float:
        """
        可靠性指标 β 计算 (简化的一次二阶矩法)
        β = (SF - 1) / (variation_coeff * SF)
        """
        if safety_factor <= 0 or variation_coeff <= 0:
            return 0.0
        beta = (safety_factor - 1.0) / (variation_coeff * safety_factor)
        return beta

    @staticmethod
    def estimate_cycle_life(contact_stress: float, sigma_y: float,
                             fatigue_exponent: float = -0.12) -> float:
        """
        预估启闭循环寿命 (基于低周疲劳简化)
        N = (σ_y / σ_contact)^(1/b) * N_ref
        """
        N_ref = 1e6  # 参考循环数
        ratio = contact_stress / sigma_y if sigma_y > 0 else 1.0
        if ratio >= 1.0:
            return 1e3  # 屈服区, 寿命极低
        N = N_ref * ratio ** (1.0 / fatigue_exponent)
        return min(N, 1e9)  # 上限


# ===========================================================================
# 八、密封副设计计算主程序
# ===========================================================================

class AerospaceValveSealDesigner:
    """
    航空航天阀门密封副设计计算主程序
    整合接触力学、泄漏分析、密封状态判定、可靠性评估
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化设计器

        参数:
            config: 可选配置字典, 支持以下键:
                - seal_pressure_ratio_min: 最小密封比压系数 (默认: 金属1.8, 软密封1.2)
                - max_contact_stress_ratio: 最大接触应力/屈服强度比 (默认: 0.85)
                - min_safety_factor: 最小安全系数 (默认: 1.5)
                - iterative_refinement: 是否启用迭代优化 (默认: True)
                - optimization_goal: 优化目标 (默认: balanced)
        """
        self.config = config or {}
        self.seal_pressure_ratio_min = self.config.get(
            'seal_pressure_ratio_min', None)
        self.max_contact_stress_ratio = self.config.get(
            'max_contact_stress_ratio',
            AEROSPACE_SEAL_SPECS['max_contact_stress_ratio'])
        self.min_safety_factor = self.config.get(
            'min_safety_factor',
            AEROSPACE_SEAL_SPECS['min_safety_factor'])
        self.iterative_refinement = self.config.get(
            'iterative_refinement', True)
        self.optimization_goal = self.config.get(
            'optimization_goal', OptimizationGoal.BALANCED)

    def design(self,
               geometry: SealGeometryInput,
               materials: Tuple[str, str],
               operating: OperatingConditions,
               gas: str = "N2",
               target_leak_class: LeakClass = LeakClass.A,
               verbose: bool = True) -> SealDesignResult:
        """
        密封副设计计算主函数

        参数:
            geometry: 几何输入参数
            materials: (阀座材料, 密封件材料) 字符串键
            operating: 工况条件
            gas: 工作介质气体键
            target_leak_class: 目标泄漏等级 (默认 ISO 5208 A级)
            verbose: 是否打印详细输出

        返回:
            SealDesignResult: 完整设计结果
        """
        result = SealDesignResult()
        warnings = []
        recommendations = []

        # ---- 1. 加载材料数据 ----
        try:
            mat_seat = get_material(materials[0])
            mat_seal = get_material(materials[1])
        except KeyError as e:
            raise ValueError(f"材料数据加载失败: {e}")

        # 判断密封类型
        if mat_seat.category == "metal" and mat_seal.category == "metal":
            seal_type = SealType.METAL_METAL
        elif mat_seat.category == "metal" and mat_seal.category in ("polymer", "elastomer"):
            if mat_seal.category == "elastomer":
                seal_type = SealType.METAL_ELASTOMER
            else:
                seal_type = SealType.METAL_POLYMER
        else:
            seal_type = SealType.METAL_METAL

        # 自动确定密封比压系数
        if self.seal_pressure_ratio_min is None:
            if seal_type == SealType.METAL_METAL:
                self.seal_pressure_ratio_min = 1.8
            else:
                self.seal_pressure_ratio_min = 1.2

        # 低温兼容性检查
        T_degC = operating.temperature - 273.15
        if not mat_seat.cryo_compatible and T_degC < mat_seat.min_temp:
            warnings.append(f"阀座材料 {mat_seat.name} 不适于 {T_degC:.0f}°C 低温工况 (最低 {mat_seat.min_temp}°C)")
        if not mat_seal.cryo_compatible and T_degC < mat_seal.min_temp:
            warnings.append(f"密封材料 {mat_seal.name} 不适于 {T_degC:.0f}°C 低温工况 (最低 {mat_seal.min_temp}°C)")

        # ---- 2. 加载气体数据 ----
        try:
            gas_props = get_gas(gas)
        except KeyError:
            gas_props = get_gas("N2")
            warnings.append(f"气体 '{gas}' 不在数据库中, 默认使用 N2")

        # ---- 3. 计算等效弹性模量 ----
        E_star = calc_effective_modulus(mat_seat.E, mat_seat.nu,
                                         mat_seal.E, mat_seal.nu)

        # ---- 4. 确定密封力 ----
        dp = operating.pressure_upstream - operating.pressure_downstream
        if operating.seal_force is None:
            # 迭代求解临界密封力
            F_critical = SealStateAnalyzer.find_critical_seal_force(
                geometry, (mat_seat, mat_seal), dp,
                self.seal_pressure_ratio_min
            )
            # 施加安全裕度
            F_seal = F_critical * self.min_safety_factor
            if operating.preload_force is not None:
                F_seal = max(F_seal, operating.preload_force)
            F_seal += operating.spring_force
        else:
            F_seal = operating.seal_force
            F_critical = F_seal / self.min_safety_factor

        # ---- 5. Hertz 接触力学计算 ----
        p_max = p_avg = contact_hw = approach = 0.0

        if geometry.contact_type == "sphere_on_cone":
            p_max, p_avg, contact_hw, approach = HertzContactAnalysis.sphere_on_cone(
                F_seal, geometry.sphere_radius or 5e-3,
                geometry.seat_angle, E_star
            )
        elif geometry.contact_type == "concave_on_cone":
            p_max, p_avg, contact_hw, approach = HertzContactAnalysis.concave_on_cone(
                F_seal, geometry.sphere_radius or 5e-3,
                geometry.seat_curvature_radius or 4.5e-3,
                geometry.eccentricity, geometry.seat_angle, E_star
            )
        elif geometry.contact_type == "sphere_on_flat":
            p_max, p_avg, contact_hw, approach = HertzContactAnalysis.sphere_on_flat(
                F_seal, geometry.sphere_radius or 5e-3, E_star
            )
        elif geometry.contact_type == "cylinder_on_flat":
            L_contact = math.pi * geometry.seat_diameter
            p_max, p_avg, contact_hw = HertzContactAnalysis.cylinder_on_flat(
                F_seal, L_contact, geometry.sphere_radius or 5e-3, E_star
            )
        else:
            # 平面-平面简化处理
            contact_area = math.pi * geometry.seat_diameter * geometry.seat_width
            p_avg = F_seal / contact_area if contact_area > 0 else 0
            p_max = p_avg * 1.5  # 应力集中系数估算
            contact_hw = geometry.seat_width / 2.0
            approach = 0.0

        # 接触面积
        perimeter = math.pi * geometry.seat_diameter
        if "cone" in geometry.contact_type:
            contact_area = perimeter * contact_hw * 2.0  # 双面锥接触
        else:
            contact_area = perimeter * contact_hw * 2.0

        # ---- 6. 密封状态判定 ----
        is_sealing, seal_ratio = SealStateAnalyzer.determine_seal_state(
            p_avg, dp, self.seal_pressure_ratio_min
        )

        # ---- 7. 泄漏率计算 ----
        # 较软材料硬度 (用于间隙估算)
        hardness_softer = mat_seal.sigma_y if mat_seal.sigma_y < mat_seat.sigma_y else mat_seat.sigma_y
        # 弹性体使用 Shore 硬度换算
        if mat_seal.category == "elastomer":
            hardness_softer = mat_seal.sigma_y * 0.5

        # 等效泄漏间隙
        gap = LeakRateCalculator.estimate_effective_gap(
            geometry.roughness_Ra_seat, geometry.roughness_Ra_seal,
            p_avg, hardness_softer
        )

        # 修正: 气体平均自由程随温度和压力变化
        lambda_gas = gas_props.mean_free_path * (operating.temperature / T_STANDARD) * \
                     (P_STANDARD / max(operating.pressure_upstream, 1.0))

        # Kn 数
        Kn = LeakRateCalculator.calc_knudsen_number(lambda_gas, gap)
        flow_regime = LeakRateCalculator.determine_flow_regime(Kn)

        # 泄漏率计算
        if flow_regime == FlowRegime.MOLECULAR:
            Q_leak = LeakRateCalculator.calc_molecular_flow_leak_rate(
                operating.pressure_upstream, operating.pressure_downstream,
                gap, perimeter, contact_hw * 2.0,  # 有效接触宽度
                gas_props.M, operating.temperature
            )
        elif flow_regime == FlowRegime.VISCOUS:
            Q_leak = LeakRateCalculator.calc_viscous_flow_leak_rate(
                operating.pressure_upstream, operating.pressure_downstream,
                gap, perimeter, contact_hw * 2.0,
                gas_props.viscosity
            )
        else:
            Q_leak = LeakRateCalculator.calc_transitional_flow_leak_rate(
                operating.pressure_upstream, operating.pressure_downstream,
                gap, perimeter, contact_hw * 2.0,
                gas_props.M, gas_props.viscosity, Kn, operating.temperature
            )

        # 泄漏率单位转换
        Q_units = LeakRateCalculator.convert_leak_rate_units(
            Q_leak, operating.temperature
        )

        # 泄漏等级评定
        DN = geometry.seat_diameter * 1000.0  # 转换为 mm
        leak_class = LeakRateCalculator.classify_leak_level(Q_leak, DN)

        # ---- 8. 安全评定 ----
        stress_ratio_yield = p_max / mat_seat.sigma_y if mat_seat.sigma_y > 0 else float('inf')
        stress_ratio_uts = p_max / mat_seat.sigma_uts if mat_seat.sigma_uts > 0 else float('inf')
        sf_yield = 1.0 / stress_ratio_yield if stress_ratio_yield > 0 else float('inf')
        sf_uts = 1.0 / stress_ratio_uts if stress_ratio_uts > 0 else float('inf')

        safety_pass = (sf_yield >= self.min_safety_factor and
                       sf_uts >= AEROSPACE_SEAL_SPECS['min_safety_factor_uts'] and
                       stress_ratio_yield <= self.max_contact_stress_ratio)

        # ---- 9. 可靠性评估 ----
        # 磨损深度
        wear_coeff = 1e-8 if seal_type != SealType.METAL_METAL else 1e-5
        wear_depth = ReliabilityAnalyzer.estimate_wear_depth(
            p_max, hardness_softer, operating.cycle_life_req, wear_coeff
        )

        # 循环寿命
        cycle_life = ReliabilityAnalyzer.estimate_cycle_life(
            p_max, mat_seat.sigma_y
        )

        # 可靠性指标
        beta = ReliabilityAnalyzer.calc_reliability_index(sf_yield)

        # ---- 10. 质量估算 ----
        est_mass = (math.pi * (geometry.seat_diameter / 2)**2 *
                    geometry.seat_width * mat_seat.density * 2.0)

        # ---- 11. 装配输出结果 ----
        output = SealDesignOutput(
            contact_stress_max=p_max,
            contact_stress_avg=p_avg,
            contact_width=contact_hw * 2.0,
            contact_area=contact_area,
            hertz_contact_half_width=contact_hw,
            effective_modulus=E_star,
            seal_pressure=p_avg,
            seal_pressure_ratio=seal_ratio,
            is_sealing=is_sealing,
            critical_seal_force=F_critical,
            flow_regime=flow_regime,
            knudsen_number=Kn,
            effective_gap_height=gap,
            leak_rate=Q_leak,
            leak_rate_mbar_L_s=Q_units['mbar_L_s'],
            leak_rate_sccm=Q_units['sccm'],
            leak_class_achieved=leak_class,
            stress_ratio_yield=stress_ratio_yield,
            stress_ratio_uts=stress_ratio_uts,
            safety_factor_yield=sf_yield,
            safety_factor_uts=sf_uts,
            safety_pass=safety_pass,
            predicted_cycle_life=cycle_life,
            wear_depth_estimate=wear_depth,
            reliability_index=beta,
            estimated_mass=est_mass,
        )

        # ---- 12. 生成建议 ----
        if not is_sealing:
            recommendations.append(
                f"密封比压不足 (当前 {seal_ratio:.2f}, "
                f"要求 {self.seal_pressure_ratio_min:.2f})。"
                f"建议增大密封力或减小接触面积。")
            warnings.append("密封状态: 可能泄漏")

        if not safety_pass:
            recommendations.append(
                f"安全系数不足 (屈服SF={sf_yield:.2f}, "
                f"要求 {self.min_safety_factor:.1f})。"
                f"建议更换更高强度材料或增大接触面积。")
            warnings.append("安全评定: 未通过")

        if leak_class.value > target_leak_class.value and leak_class != LeakClass.AA:
            recommendations.append(
                f"泄漏等级未达标 (当前 {leak_class.value}级, "
                f"目标 {target_leak_class.value}级)。"
                f"建议降低表面粗糙度或增大接触应力。")

        if cycle_life < operating.cycle_life_req:
            recommendations.append(
                f"预估寿命不足 (当前 {cycle_life:.0f}次, "
                f"要求 {operating.cycle_life_req}次)。"
                f"建议降低接触应力或选用更耐磨材料。")

        if (T_degC < -50 and seal_type == SealType.METAL_POLYMER
                and not mat_seal.cryo_compatible):
            recommendations.append(
                f"聚合物密封材料 {mat_seal.name} 不兼容低温工况, "
                f"建议改用 PCTFE 或 PEEK。")

        if wear_depth > geometry.seat_width * 0.1:
            recommendations.append(
                f"磨损深度 ({wear_depth*1e6:.2f} μm) 较大, "
                f"建议增大密封面宽度或选用更耐磨材料。")

        # ---- 13. 迭代优化 (可选) ----
        optimization_log = []
        if self.iterative_refinement and not safety_pass:
            # 尝试调整接触几何
            F_adjusted = F_seal * 1.2
            # 重新计算并记录
            optimization_log.append({
                "action": "increase_seal_force",
                "F_original": F_seal,
                "F_adjusted": F_adjusted,
                "reason": "safety_factor_low"
            })

        # ---- 14. 汇总 ----
        result.input_summary = {
            "seal_type": seal_type.value,
            "contact_type": geometry.contact_type,
            "seat_material": mat_seat.name,
            "seal_material": mat_seal.name,
            "gas_medium": gas_props.name,
            "seat_diameter_mm": geometry.seat_diameter * 1000,
            "seat_angle_deg": geometry.seat_angle,
            "pressure_differential_bar": dp / 1e5,
            "temperature_C": T_degC,
            "seal_force_N": F_seal,
            "target_leak_class": target_leak_class.value,
            "surface_roughness_Ra_um": geometry.roughness_Ra_seat * 1e6,
        }
        result.output = output
        result.warnings = warnings
        result.recommendations = recommendations
        result.optimization_log = optimization_log

        # ---- 15. 详细输出 ----
        if verbose:
            self._print_results(result)

        return result

    def _print_results(self, result: SealDesignResult):
        """格式化打印设计结果"""
        inp = result.input_summary
        out = result.output

        print("\n" + "=" * 70)
        print("  航空航天阀门密封副设计计算结果")
        print("=" * 70)

        print("\n--- 输入参数 ---")
        print(f"  密封类型: {inp['seal_type']}")
        print(f"  接触类型: {inp['contact_type']}")
        print(f"  阀座材料: {inp['seat_material']}")
        print(f"  密封材料: {inp['seal_material']}")
        print(f"  工作介质: {inp['gas_medium']}")
        print(f"  密封面公称直径: {inp['seat_diameter_mm']:.1f} mm")
        print(f"  阀座锥角: {inp['seat_angle_deg']:.1f}°")
        print(f"  压差: {inp['pressure_differential_bar']:.2f} bar")
        print(f"  工作温度: {inp['temperature_C']:.1f}°C")
        print(f"  密封力: {inp['seal_force_N']:.1f} N")
        print(f"  表面粗糙度 Ra: {inp['surface_roughness_Ra_um']:.3f} μm")
        print(f"  目标泄漏等级: ISO 5208 {inp['target_leak_class']}级")

        print("\n--- 接触力学分析 ---")
        print(f"  等效弹性模量 E*: {out.effective_modulus/1e9:.2f} GPa")
        print(f"  最大接触应力 p_max: {out.contact_stress_max/1e6:.1f} MPa")
        print(f"  平均接触应力 p_avg: {out.contact_stress_avg/1e6:.1f} MPa")
        print(f"  接触宽度 (2b): {out.contact_width*1e6:.2f} μm")
        print(f"  接触面积: {out.contact_area*1e6:.3f} mm²")
        print(f"  密封比压: {out.seal_pressure/1e6:.2f} MPa")
        print(f"  密封比压/介质压力: {out.seal_pressure_ratio:.2f}")
        print(f"  临界密封力: {out.critical_seal_force:.1f} N")

        print("\n--- 泄漏分析 ---")
        print(f"  流态: {out.flow_regime.value}")
        print(f"  克努森数 Kn: {out.knudsen_number:.2e}")
        print(f"  等效泄漏间隙: {out.effective_gap_height*1e6:.4f} μm")
        print(f"  泄漏率: {out.leak_rate:.3e} Pa·m³/s")
        print(f"  泄漏率: {out.leak_rate_mbar_L_s:.3e} mbar·L/s")
        print(f"  泄漏率: {out.leak_rate_sccm:.3e} sccm")
        print(f"  达到泄漏等级: ISO 5208 {out.leak_class_achieved.value}级")

        print("\n--- 安全评定 ---")
        print(f"  接触应力/屈服强度: {out.stress_ratio_yield:.3f}")
        print(f"  接触应力/抗拉强度: {out.stress_ratio_uts:.3f}")
        print(f"  屈服安全系数: {out.safety_factor_yield:.2f}")
        print(f"  抗拉安全系数: {out.safety_factor_uts:.2f}")
        print(f"  安全评定: {'[OK] 通过' if out.safety_pass else '[FAIL] 未通过'}")

        print("\n--- 可靠性预估 ---")
        print(f"  预测启闭寿命: {out.predicted_cycle_life:.0f} 次")
        print(f"  预计磨损深度: {out.wear_depth_estimate*1e6:.3f} μm")
        print(f"  可靠性指标 β: {out.reliability_index:.2f}")
        print(f"  密封副估计质量: {out.estimated_mass*1e3:.1f} g")

        # 警告与建议
        if result.warnings:
            print("\n--- [WARN] 警告 ---")
            for w in result.warnings:
                print(f"  [WARN] {w}")

        if result.recommendations:
            print("\n--- [INFO] 设计建议 ---")
            for r in result.recommendations:
                print(f"  → {r}")

        print("\n" + "=" * 70)


# ===========================================================================
# 九、快速接口函数
# ===========================================================================

def quick_design(seat_diameter_mm: float = 10.0,
                 pressure_bar: float = 10.0,
                 temperature_C: float = 20.0,
                 seat_material: str = "316L_SS",
                 seal_material: str = "PTFE",
                 seal_force_N: Optional[float] = None,
                 contact_type: str = "sphere_on_cone",
                 seat_angle_deg: float = 60.0,
                 sphere_radius_mm: float = 5.0,
                 roughness_Ra_um: float = 0.4,
                 gas: str = "N2",
                 target_leak_class: str = "A",
                 verbose: bool = True) -> SealDesignResult:
    """
    密封副快速设计接口函数

    参数:
        seat_diameter_mm: 密封面公称直径 [mm]
        pressure_bar: 介质压差 [bar]
        temperature_C: 工作温度 [°C]
        seat_material: 阀座材料键 (如 "316L_SS", "INCONEL_718")
        seal_material: 密封件材料键 (如 "PTFE", "PCTFE", "PEEK")
        seal_force_N: 密封力 [N] (None=自动计算)
        contact_type: 接触类型
        seat_angle_deg: 阀座锥角 [°]
        sphere_radius_mm: 球头半径 [mm]
        roughness_Ra_um: 表面粗糙度 Ra [μm]
        gas: 工作介质气体键 (如 "N2", "He", "H2")
        target_leak_class: 目标泄漏等级 (如 "AA", "A", "B", "D")
        verbose: 是否打印详细结果

    返回:
        SealDesignResult
    """
    geometry = SealGeometryInput(
        contact_type=contact_type,
        seat_diameter=seat_diameter_mm * 1e-3,
        seat_angle=seat_angle_deg,
        sphere_radius=sphere_radius_mm * 1e-3 if sphere_radius_mm > 0 else None,
        roughness_Ra_seat=roughness_Ra_um * 1e-6,
        roughness_Ra_seal=roughness_Ra_um * 1e-6,
    )

    operating = OperatingConditions(
        pressure_upstream=pressure_bar * 1e5,
        pressure_downstream=0.0,
        temperature=temperature_C + 273.15,
        seal_force=seal_force_N,
    )

    # 目标泄漏等级
    try:
        target_lc = LeakClass(target_leak_class.upper())
    except ValueError:
        target_lc = LeakClass.A
        print(f"警告: 未知泄漏等级 '{target_leak_class}', 默认使用 A 级")

    designer = AerospaceValveSealDesigner()
    result = designer.design(
        geometry=geometry,
        materials=(seat_material, seal_material),
        operating=operating,
        gas=gas,
        target_leak_class=target_lc,
        verbose=verbose,
    )

    return result


# ===========================================================================
# 十、多工况对比分析
# ===========================================================================

def compare_designs(design_configs: List[Dict],
                    gas: str = "N2",
                    verbose: bool = True) -> List[SealDesignResult]:
    """
    多工况/多方案对比分析

    参数:
        design_configs: 设计配置列表, 每项包含:
            - label: 方案标签
            - seat_diameter_mm, pressure_bar, temperature_C, 等 (同 quick_design)
        gas: 工作介质
        verbose: 详细输出

    返回:
        结果列表
    """
    results = []
    print("\n" + "=" * 80)
    print("  多方案密封副设计对比分析")
    print("=" * 80)

    for i, cfg in enumerate(design_configs):
        label = cfg.get("label", f"方案{i+1}")
        print(f"\n{'-'*70}")
        print(f"  >>> {label} <<<")
        print(f"{'-'*70}")

        result = quick_design(
            seat_diameter_mm=cfg.get("seat_diameter_mm", 10.0),
            pressure_bar=cfg.get("pressure_bar", 10.0),
            temperature_C=cfg.get("temperature_C", 20.0),
            seat_material=cfg.get("seat_material", "316L_SS"),
            seal_material=cfg.get("seal_material", "PTFE"),
            seal_force_N=cfg.get("seal_force_N", None),
            contact_type=cfg.get("contact_type", "sphere_on_cone"),
            seat_angle_deg=cfg.get("seat_angle_deg", 60.0),
            sphere_radius_mm=cfg.get("sphere_radius_mm", 5.0),
            roughness_Ra_um=cfg.get("roughness_Ra_um", 0.4),
            gas=gas,
            target_leak_class=cfg.get("target_leak_class", "A"),
            verbose=verbose,
        )
        results.append(result)

    # 汇总对比表
    if verbose and len(results) > 1:
        print("\n" + "=" * 80)
        print("  对比汇总表")
        print("=" * 80)
        header = (f"{'方案':<12} {'接触应力(MPa)':<15} {'安全系数':<10} "
                   f"{'泄漏率(mbar·L/s)':<20} {'泄漏等级':<10} {'安全评定':<10}")
        print(header)
        print("-" * 80)
        for i, (cfg, r) in enumerate(zip(design_configs, results)):
            label = cfg.get("label", f"方案{i+1}")
            row = (f"{label:<12} "
                   f"{r.output.contact_stress_max/1e6:<15.1f} "
                   f"{r.output.safety_factor_yield:<10.2f} "
                   f"{r.output.leak_rate_mbar_L_s:<20.3e} "
                   f"{r.output.leak_class_achieved.value:<10} "
                   f"{'[OK]通过' if r.output.safety_pass else '[FAIL]未通过':<10}")
            print(row)
        print("=" * 80)

    return results


# ===========================================================================
# 十一、敏感性分析
# ===========================================================================

def sensitivity_analysis(base_config: Dict,
                          param_name: str,
                          param_values: List[float],
                          gas: str = "N2") -> List[Dict]:
    """
    单参数敏感性分析

    参数:
        base_config: 基准配置
        param_name: 待分析参数名 (seat_diameter_mm, pressure_bar, roughness_Ra_um, ...)
        param_values: 参数值列表
        gas: 工作介质

    返回:
        分析结果列表 [{param_value, leak_rate, contact_stress, safety_factor, ...}]
    """
    results = []
    for val in param_values:
        cfg = base_config.copy()
        cfg[param_name] = val
        result = quick_design(
            seat_diameter_mm=cfg.get("seat_diameter_mm", 10.0),
            pressure_bar=cfg.get("pressure_bar", 10.0),
            temperature_C=cfg.get("temperature_C", 20.0),
            seat_material=cfg.get("seat_material", "316L_SS"),
            seal_material=cfg.get("seal_material", "PTFE"),
            seal_force_N=cfg.get("seal_force_N", None),
            contact_type=cfg.get("contact_type", "sphere_on_cone"),
            seat_angle_deg=cfg.get("seat_angle_deg", 60.0),
            sphere_radius_mm=cfg.get("sphere_radius_mm", 5.0),
            roughness_Ra_um=cfg.get("roughness_Ra_um", 0.4),
            gas=gas,
            target_leak_class=cfg.get("target_leak_class", "A"),
            verbose=False,
        )
        results.append({
            "param_value": val,
            "leak_rate_mbar_L_s": result.output.leak_rate_mbar_L_s,
            "contact_stress_max_MPa": result.output.contact_stress_max / 1e6,
            "safety_factor_yield": result.output.safety_factor_yield,
            "safety_pass": result.output.safety_pass,
            "leak_class": result.output.leak_class_achieved.value,
        })
    return results


# ===========================================================================
# 十二、主程序入口 (示例与测试)
# ===========================================================================

# ===========================================================================
# Section 13: Flask API Wrapper Functions (Avis Platform Integration)
# ===========================================================================

def api_seal_design(params: dict) -> dict:
    """Flask API wrapper for seal pair design"""
    try:
        result = quick_design(
            seat_diameter_mm=params.get('seat_diameter_mm', 10.0),
            pressure_bar=params.get('pressure_bar', 10.0),
            temperature_C=params.get('temperature_C', 20.0),
            seat_material=params.get('seat_material', '316L_SS'),
            seal_material=params.get('seal_material', 'PTFE'),
            seal_force_N=params.get('seal_force_N'),
            contact_type=params.get('contact_type', 'sphere_on_cone'),
            seat_angle_deg=params.get('seat_angle_deg', 60.0),
            sphere_radius_mm=params.get('sphere_radius_mm', 5.0),
            roughness_Ra_um=params.get('roughness_Ra_um', 0.4),
            gas=params.get('gas', 'N2'),
            target_leak_class=params.get('target_leak_class', 'A'),
            verbose=False,
        )
        output = result.output
        out_dict = {
            'contact_stress_max_MPa': output.contact_stress_max / 1e6,
            'contact_stress_avg_MPa': output.contact_stress_avg / 1e6,
            'contact_width_um': output.contact_width * 1e6,
            'contact_area_mm2': output.contact_area * 1e6,
            'seal_pressure_MPa': output.seal_pressure / 1e6,
            'seal_pressure_ratio': output.seal_pressure_ratio,
            'is_sealing': output.is_sealing,
            'critical_seal_force_N': output.critical_seal_force,
            'flow_regime': output.flow_regime.value,
            'knudsen_number': output.knudsen_number,
            'effective_gap_height_nm': output.effective_gap_height * 1e9,
            'leak_rate_Pa_m3_s': output.leak_rate,
            'leak_rate_mbar_L_s': output.leak_rate_mbar_L_s,
            'leak_rate_sccm': output.leak_rate_sccm,
            'leak_class': output.leak_class_achieved.value,
            'stress_ratio_yield': output.stress_ratio_yield,
            'stress_ratio_uts': output.stress_ratio_uts,
            'safety_factor_yield': output.safety_factor_yield,
            'safety_factor_uts': output.safety_factor_uts,
            'safety_pass': output.safety_pass,
            'predicted_cycle_life': int(output.predicted_cycle_life),
            'wear_depth_um': output.wear_depth_estimate * 1e6,
            'reliability_index': output.reliability_index,
            'estimated_mass_g': output.estimated_mass * 1e3,
        }
        return {
            'success': True,
            'input_summary': result.input_summary,
            'output': _clean(out_dict),
            'warnings': result.warnings,
            'recommendations': result.recommendations,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def api_compare_designs(configs_list: list, gas: str = 'N2') -> list:
    """Flask API wrapper for multi-design comparison"""
    results = compare_designs(configs_list, gas=gas, verbose=False)
    output = []
    for r in results:
        o = r.output
        output.append(_clean({
            'label': configs_list[len(output)].get('label', f'Design {len(output)+1}'),
            'contact_stress_max_MPa': o.contact_stress_max / 1e6,
            'safety_factor_yield': o.safety_factor_yield,
            'leak_rate_mbar_L_s': o.leak_rate_mbar_L_s,
            'leak_class': o.leak_class_achieved.value,
            'safety_pass': o.safety_pass,
            'warnings': r.warnings,
            'recommendations': r.recommendations,
        }))
    return output

def api_sensitivity_analysis(base_config: dict, param_name: str,
                              param_values: list, gas: str = 'N2') -> list:
    """Flask API wrapper for sensitivity analysis"""
    results = sensitivity_analysis(base_config, param_name, param_values, gas)
    return _clean(results)

def get_seal_design_info() -> dict:
    """Return module info: materials, gases, contact types, leak classes"""
    return _clean({
        'materials': {k: {'name': v['name'], 'category': v['category'],
                          'cryo_compatible': v['cryo_compatible'],
                          'max_temp': v['max_temp'], 'min_temp': v['min_temp']}
                     for k, v in MATERIAL_DATABASE.items()},
        'gases': {k: {'name': v['name'], 'M': v['M']} for k, v in GAS_PROPERTIES.items()},
        'contact_types': ['sphere_on_flat', 'sphere_on_cone', 'cylinder_on_flat',
                         'cone_on_cone', 'flat_on_flat', 'concave_on_cone'],
        'leak_classes': [lc.value for lc in LeakClass],
        'version': '4.0',
        'standards': ['ISO 5208-2015', 'ANSI/FCI 70-2-2013', 'ECSS-E-ST-32-02C'],
        'references': ['Li et al. (2025) Scientific Reports 15:36059',
                      'Choi & Kim (2025) Applied Sciences 15(11):6184'],
    })


if __name__ == "__main__":
    print("=" * 70)
    print("航空航天阀门密封副设计计算程序 v4.0")
    print("Aerospace Valve Seal Pair Design Calculator")
    print("=" * 70)
    print("适用标准: ISO 5208 / ANSI FCI 70-2 / ECSS-E-ST-32-02C")
    print("理论依据: Hertz 接触理论 + Roth 分子流泄漏模型")
    print("参考: Li et al. (2025), Choi & Kim (2025)")
    print("=" * 70)

    # ================================================================
    # 示例1: 低温液氧阀门金属-聚合物密封 (航天典型工况)
    # ================================================================
    print("\n" + "[*]" * 70)
    print("[*]  示例1: 液氧加注阀门密封副设计 (LOX, -183°C, 10 bar)")
    print("[*]" * 70)

    result1 = quick_design(
        seat_diameter_mm=15.0,
        pressure_bar=10.0,
        temperature_C=-183.0,      # 液氧温度
        seat_material="INCONEL_718",
        seal_material="PCTFE",     # 低温兼容聚合物
        seal_force_N=None,         # 自动计算
        contact_type="sphere_on_cone",
        seat_angle_deg=60.0,
        sphere_radius_mm=7.5,
        roughness_Ra_um=0.2,       # 航天级粗糙度
        gas="O2",
        target_leak_class="AA",    # 航天零泄漏要求
        verbose=True,
    )

    # ================================================================
    # 示例2: 高压氦气阀门金属-金属密封
    # ================================================================
    print("\n" + "[*]" * 70)
    print("[*]  示例2: 高压氦气截止阀金属-金属密封 (35 MPa, 20°C)")
    print("[*]" * 70)

    result2 = quick_design(
        seat_diameter_mm=6.0,
        pressure_bar=350.0,         # 35 MPa
        temperature_C=20.0,
        seat_material="17_4PH",
        seal_material="316L_SS",    # 金属-金属硬密封
        seal_force_N=8000.0,
        contact_type="concave_on_cone",  # 凹面接触 - 新型设计
        seat_angle_deg=45.0,
        sphere_radius_mm=5.73,     # 优化曲率比
        roughness_Ra_um=0.1,
        gas="He",
        target_leak_class="B",
        verbose=True,
    )

    # ================================================================
    # 示例3: 多方案对比 (材料选型)
    # ================================================================
    print("\n" + "[*]" * 70)
    print("[*]  示例3: 密封材料选型对比 (PTFE vs PCTFE vs PEEK vs 金属)")
    print("[*]" * 70)

    compare_designs([
        {"label": "PTFE软密封", "seat_material": "316L_SS",
         "seal_material": "PTFE", "roughness_Ra_um": 0.4,
         "seat_diameter_mm": 10.0, "pressure_bar": 5.0,
         "temperature_C": 20.0, "target_leak_class": "A"},
        {"label": "PCTFE软密封", "seat_material": "316L_SS",
         "seal_material": "PCTFE", "roughness_Ra_um": 0.3,
         "seat_diameter_mm": 10.0, "pressure_bar": 5.0,
         "temperature_C": 20.0, "target_leak_class": "A"},
        {"label": "PEEK软密封", "seat_material": "316L_SS",
         "seal_material": "PEEK", "roughness_Ra_um": 0.3,
         "seat_diameter_mm": 10.0, "pressure_bar": 5.0,
         "temperature_C": 20.0, "target_leak_class": "A"},
        {"label": "316L硬密封", "seat_material": "316L_SS",
         "seal_material": "316L_SS", "roughness_Ra_um": 0.1,
         "seat_diameter_mm": 10.0, "pressure_bar": 5.0,
         "temperature_C": 20.0, "target_leak_class": "B"},
    ], gas="N2", verbose=True)

    # ================================================================
    # 示例4: 敏感性分析 (表面粗糙度对泄漏率的影响)
    # ================================================================
    print("\n" + "[*]" * 70)
    print("[*]  示例4: 表面粗糙度敏感性分析")
    print("[*]" * 70)

    base_cfg = {
        "seat_diameter_mm": 10.0, "pressure_bar": 5.0, "temperature_C": 20.0,
        "seat_material": "316L_SS", "seal_material": "PTFE",
        "target_leak_class": "A"
    }
    ra_values = [0.1, 0.2, 0.4, 0.8, 1.6]  # μm
    sens_results = sensitivity_analysis(base_cfg, "roughness_Ra_um", ra_values)

    print(f"\n{'Ra (μm)':<10} {'泄漏率 (mbar·L/s)':<22} {'接触应力 (MPa)':<18} "
          f"{'安全系数':<10} {'安全评定':<10}")
    print("-" * 70)
    for r in sens_results:
        print(f"{r['param_value']:<10.1f} "
              f"{r['leak_rate_mbar_L_s']:<22.3e} "
              f"{r['contact_stress_max_MPa']:<18.1f} "
              f"{r['safety_factor_yield']:<10.2f} "
              f"{'[OK]' if r['safety_pass'] else '[FAIL]':<10}")

    print("\n" + "=" * 70)
    print("  程序运行完毕。")
    print("=" * 70)
