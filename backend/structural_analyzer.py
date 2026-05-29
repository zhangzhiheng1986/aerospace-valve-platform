#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航空航天电磁阀研发平台 - 结构强度分析模块
Structural Analysis Module (FEM-based)

功能：
- 应力应变计算
- 变形分析
- 安全系数评估
- 疲劳寿命预测
- 振动特性分析
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math


class StressType(Enum):
    """应力类型"""
    TENSILE = "拉伸"
    COMPRESSIVE = "压缩"
    SHEAR = "剪切"
    VON_MISES = "Von Mises"


class FailureMode(Enum):
    """失效模式"""
    YIELD = "屈服失效"
    FRACTURE = "断裂失效"
    FATIGUE = "疲劳失效"
    BUCKLING = "屈曲失效"


@dataclass
class MaterialMechanical:
    """材料力学性能"""
    name: str                        # 材料名称
    yield_strength: float            # 屈服强度 (Pa)
    ultimate_strength: float         # 抗拉强度 (Pa)
    elastic_modulus: float           # 弹性模量 (Pa)
    poisson_ratio: float             # 泊松比
    shear_modulus: float             # 剪切模量 (Pa)
    density: float                   # 密度 (kg/m³)
    fatigue_limit: Optional[float] = None  # 疲劳极限 (Pa)
    
    @property
    def allowable_stress(self) -> float:
        """许用应力（屈服强度/安全系数1.5）"""
        return self.yield_strength / 1.5


@dataclass
class LoadCondition:
    """载荷条件"""
    force_x: float = 0      # X方向力 (N)
    force_y: float = 0      # Y方向力 (N)
    force_z: float = 0      # Z方向力 (N)
    moment_x: float = 0     # X方向弯矩 (N·m)
    moment_y: float = 0     # Y方向弯矩 (N·m)
    moment_z: float = 0     # Z方向弯矩 (N·m)
    pressure: float = 0     # 压力 (Pa)


class StructuralAnalyzer:
    """结构强度分析器"""
    
    def __init__(self, material: MaterialMechanical):
        self.material = material
        self.results = {}
    
    def calculate_stress(self, force: float, area: float, 
                        stress_type: StressType = StressType.TENSILE) -> Dict:
        """
        计算应力
        σ = F / A
        
        Args:
            force: 力 (N)
            area: 面积 (m²)
            stress_type: 应力类型
        
        Returns:
            应力结果
        """
        stress = force / area if area > 0 else 0
        
        return {
            'stress_Pa': stress,
            'stress_MPa': stress / 1e6,
            'force_N': force,
            'area_m2': area,
            'stress_type': stress_type.value
        }
    
    def calculate_strain(self, stress: float) -> Dict:
        """
        计算应变
        ε = σ / E
        
        Args:
            stress: 应力 (Pa)
        
        Returns:
            应变结果
        """
        strain = stress / self.material.elastic_modulus
        
        return {
            'strain': strain,
            'stress_Pa': stress,
            'elastic_modulus_GPa': self.material.elastic_modulus / 1e9
        }
    
    def calculate_safety_factor(self, stress: float, 
                               use_ultimate: bool = False) -> Dict:
        """
        计算安全系数
        n = σ_allowable / σ_actual
        
        Args:
            stress: 实际应力 (Pa)
            use_ultimate: 是否使用抗拉强度
        
        Returns:
            安全系数结果
        """
        if use_ultimate:
            reference_strength = self.material.ultimate_strength
            reference_name = "抗拉强度"
        else:
            reference_strength = self.material.yield_strength
            reference_name = "屈服强度"
        
        safety_factor = reference_strength / stress if stress > 0 else float('inf')
        
        # 安全性评估
        if safety_factor >= 3.0:
            assessment = "安全裕度充足"
        elif safety_factor >= 1.5:
            assessment = "安全裕度合格"
        elif safety_factor >= 1.0:
            assessment = "接近临界状态"
        else:
            assessment = "不安全，需要重新设计"
        
        return {
            'safety_factor': safety_factor,
            'reference_strength_MPa': reference_strength / 1e6,
            'reference_name': reference_name,
            'actual_stress_MPa': stress / 1e6,
            'assessment': assessment,
            'safe': safety_factor >= 1.5
        }
    
    def calculate_von_mises_stress(self, sigma_x: float, sigma_y: float, 
                                   sigma_z: float, tau_xy: float = 0,
                                   tau_yz: float = 0, tau_zx: float = 0) -> Dict:
        """
        计算Von Mises等效应力
        σ_vm = sqrt(0.5 * [(σx-σy)² + (σy-σz)² + (σz-σx)² + 6(τxy² + τyz² + τzx²)])
        
        Args:
            sigma_x, sigma_y, sigma_z: 正应力 (Pa)
            tau_xy, tau_yz, tau_zx: 剪应力 (Pa)
        
        Returns:
            Von Mises应力结果
        """
        term1 = (sigma_x - sigma_y)**2
        term2 = (sigma_y - sigma_z)**2
        term3 = (sigma_z - sigma_x)**2
        term4 = 6 * (tau_xy**2 + tau_yz**2 + tau_zx**2)
        
        von_mises = math.sqrt(0.5 * (term1 + term2 + term3 + term4))
        
        return {
            'von_mises_stress_Pa': von_mises,
            'von_mises_stress_MPa': von_mises / 1e6,
            'principal_stresses': {
                'sigma_x_MPa': sigma_x / 1e6,
                'sigma_y_MPa': sigma_y / 1e6,
                'sigma_z_MPa': sigma_z / 1e6
            },
            'shear_stresses': {
                'tau_xy_MPa': tau_xy / 1e6,
                'tau_yz_MPa': tau_yz / 1e6,
                'tau_zx_MPa': tau_zx / 1e6
            }
        }
    
    def calculate_deformation(self, force: float, length: float, 
                             area: float) -> Dict:
        """
        计算变形
        ΔL = F * L / (E * A)
        
        Args:
            force: 力 (N)
            length: 长度 (m)
            area: 截面积 (m²)
        
        Returns:
            变形结果
        """
        deformation = force * length / (self.material.elastic_modulus * area)
        
        # 应变
        strain = deformation / length
        
        return {
            'deformation_m': deformation,
            'deformation_mm': deformation * 1000,
            'strain': strain,
            'force_N': force,
            'length_m': length,
            'area_m2': area
        }
    
    def calculate_bending_stress(self, moment: float, 
                                second_moment: float, 
                                distance: float) -> Dict:
        """
        计算弯曲应力
        σ = M * y / I
        
        Args:
            moment: 弯矩 (N·m)
            second_moment: 截面二次矩 (m⁴)
            distance: 到中性轴距离 (m)
        
        Returns:
            弯曲应力结果
        """
        stress = moment * distance / second_moment
        
        return {
            'bending_stress_Pa': stress,
            'bending_stress_MPa': stress / 1e6,
            'moment_Nm': moment,
            'second_moment_m4': second_moment,
            'distance_m': distance
        }
    
    def calculate_pressure_vessel_stress(self, pressure: float, 
                                        radius: float, 
                                        thickness: float) -> Dict:
        """
        计算压力容器应力（薄壁圆筒）
        环向应力: σ_θ = P * r / t
        轴向应力: σ_z = P * r / (2 * t)
        
        Args:
            pressure: 内压 (Pa)
            radius: 半径 (m)
            thickness: 壁厚 (m)
        
        Returns:
            压力容器应力结果
        """
        # 环向应力（最大）
        hoop_stress = pressure * radius / thickness
        
        # 轴向应力
        axial_stress = pressure * radius / (2 * thickness)
        
        # 径向应力（近似）
        radial_stress = -pressure / 2
        
        # Von Mises应力
        von_mises = math.sqrt(hoop_stress**2 + axial_stress**2 
                             - hoop_stress * axial_stress)
        
        return {
            'hoop_stress_Pa': hoop_stress,
            'hoop_stress_MPa': hoop_stress / 1e6,
            'axial_stress_Pa': axial_stress,
            'axial_stress_MPa': axial_stress / 1e6,
            'radial_stress_Pa': radial_stress,
            'radial_stress_MPa': radial_stress / 1e6,
            'von_mises_Pa': von_mises,
            'von_mises_MPa': von_mises / 1e6,
            'pressure_Pa': pressure,
            'pressure_MPa': pressure / 1e6,
            'radius_mm': radius * 1000,
            'thickness_mm': thickness * 1000
        }
    
    def calculate_fatigue_life(self, stress_amplitude: float,
                               stress_mean: float = 0,
                               method: str = 'goodman') -> Dict:
        """
        计算疲劳寿命（简化S-N曲线法）
        
        Args:
            stress_amplitude: 应力幅 (Pa)
            stress_mean: 平均应力 (Pa)
            method: 平均应力修正方法
        
        Returns:
            疲劳寿命结果
        """
        if not self.material.fatigue_limit:
            return {'error': '材料疲劳极限未定义'}
        
        # 平均应力修正
        if method == 'goodman':
            # Goodman修正
            # σ_a / σ_fl + σ_m / σ_u = 1
            equivalent_stress = stress_amplitude / (1 - stress_mean / self.material.ultimate_strength)
        elif method == 'gerber':
            # Gerber修正
            equivalent_stress = stress_amplitude / (1 - (stress_mean / self.material.ultimate_strength)**2)
        else:
            equivalent_stress = stress_amplitude
        
        # 简化S-N曲线（Basquin方程）
        # σ_a = σ_f' * (2N)^b
        # 假设: σ_f' = 0.9 * σ_u, b = -0.1
        sigma_f = 0.9 * self.material.ultimate_strength
        b = -0.1
        
        if equivalent_stress < self.material.fatigue_limit:
            # 无限寿命
            cycles = float('inf')
            life_category = "无限寿命"
        else:
            # 有限寿命
            cycles = 0.5 * (sigma_f / equivalent_stress) ** (1 / b)
            life_category = "有限寿命"
        
        # 疲劳安全系数
        if equivalent_stress > 0:
            fatigue_safety = self.material.fatigue_limit / equivalent_stress
        else:
            fatigue_safety = float('inf')
        
        return {
            'stress_amplitude_MPa': stress_amplitude / 1e6,
            'stress_mean_MPa': stress_mean / 1e6,
            'equivalent_stress_MPa': equivalent_stress / 1e6,
            'fatigue_limit_MPa': self.material.fatigue_limit / 1e6,
            'cycles_to_failure': cycles,
            'life_category': life_category,
            'fatigue_safety_factor': fatigue_safety,
            'correction_method': method
        }
    
    def calculate_natural_frequency(self, length: float, area: float,
                                   second_moment: float, mode: int = 1) -> Dict:
        """
        计算固有频率（简支梁）
        f_n = (n * π / 2L)² * sqrt(E * I / (ρ * A))
        
        Args:
            length: 长度 (m)
            area: 截面积 (m²)
            second_moment: 截面二次矩 (m⁴)
            mode: 模态阶数
        
        Returns:
            固有频率结果
        """
        # 固有频率
        omega = (mode * math.pi / length)**2 * math.sqrt(
            self.material.elastic_modulus * second_moment / 
            (self.material.density * area)
        )
        
        frequency = omega / (2 * math.pi)
        
        return {
            'natural_frequency_Hz': frequency,
            'natural_frequency_kHz': frequency / 1000,
            'angular_frequency_rads': omega,
            'mode': mode,
            'length_m': length
        }
    
    def run_analysis(self, geometry: Dict, loads: LoadCondition) -> Dict:
        """
        运行完整结构分析
        
        Args:
            geometry: 几何参数
            loads: 载荷条件
        
        Returns:
            完整分析结果
        """
        # 提取几何参数
        diameter = geometry.get('diameter', 0.01)  # m
        thickness = geometry.get('thickness', 0.002)  # m
        length = geometry.get('length', 0.05)  # m
        
        # 计算截面参数
        radius = diameter / 2
        inner_radius = radius - thickness
        area = math.pi * (radius**2 - inner_radius**2)
        second_moment = math.pi / 4 * (radius**4 - inner_radius**4)
        
        # 压力容器应力
        if loads.pressure > 0:
            pressure_stress = self.calculate_pressure_vessel_stress(
                loads.pressure, inner_radius, thickness
            )
        else:
            pressure_stress = None
        
        # 轴向应力
        axial_force = loads.force_x
        axial_stress = self.calculate_stress(axial_force, area)
        
        # 弯曲应力
        bending_moment = math.sqrt(loads.moment_y**2 + loads.moment_z**2)
        if bending_moment > 0:
            bending_stress = self.calculate_bending_stress(
                bending_moment, second_moment, radius
            )
        else:
            bending_stress = None
        
        # 最大应力
        max_stress = axial_stress['stress_Pa']
        if pressure_stress:
            max_stress = max(max_stress, pressure_stress['hoop_stress_Pa'])
        if bending_stress:
            max_stress = max(max_stress, bending_stress['bending_stress_Pa'])
        
        # 安全系数
        safety = self.calculate_safety_factor(max_stress)
        
        # 变形
        deformation = self.calculate_deformation(axial_force, length, area)
        
        # 固有频率
        natural_freq = self.calculate_natural_frequency(length, area, second_moment)
        
        return {
            'success': True,
            'geometry': {
                'diameter_mm': diameter * 1000,
                'thickness_mm': thickness * 1000,
                'length_mm': length * 1000,
                'area_mm2': area * 1e6,
                'second_moment_mm4': second_moment * 1e12
            },
            'loads': {
                'axial_force_N': loads.force_x,
                'pressure_Pa': loads.pressure,
                'pressure_MPa': loads.pressure / 1e6,
                'bending_moment_Nm': bending_moment
            },
            'stress_analysis': {
                'axial_stress': axial_stress,
                'pressure_stress': pressure_stress,
                'bending_stress': bending_stress,
                'max_stress_MPa': max_stress / 1e6
            },
            'safety_factor': safety,
            'deformation': deformation,
            'natural_frequency': natural_freq,
            'material': {
                'name': self.material.name,
                'yield_strength_MPa': self.material.yield_strength / 1e6,
                'ultimate_strength_MPa': self.material.ultimate_strength / 1e6,
                'elastic_modulus_GPa': self.material.elastic_modulus / 1e9
            }
        }


# 预定义材料
MATERIALS = {
    'steel_304': MaterialMechanical(
        '不锈钢304', 205e6, 515e6, 193e9, 0.29, 75e9, 7930, 240e6
    ),
    'steel_316': MaterialMechanical(
        '不锈钢316', 290e6, 580e6, 193e9, 0.29, 75e9, 8000, 290e6
    ),
    'titanium_tc4': MaterialMechanical(
        '钛合金TC4', 880e6, 950e6, 110e9, 0.34, 41e9, 4430, 510e6
    ),
    'inconel_718': MaterialMechanical(
        'Inconel 718', 1035e6, 1240e6, 200e9, 0.29, 77e9, 8190, 550e6
    ),
    'aluminum_7075': MaterialMechanical(
        '铝合金7075-T6', 503e6, 572e6, 71.7e9, 0.33, 26.9e9, 2810, 160e6
    ),
}


def run_structural_analysis(material_name: str, geometry: Dict, 
                           loads: Dict) -> Dict:
    """
    运行结构分析的便捷函数
    
    Args:
        material_name: 材料名称
        geometry: 几何参数
        loads: 载荷参数
    
    Returns:
        分析结果
    """
    material = MATERIALS.get(material_name)
    if not material:
        return {'success': False, 'error': f'未知材料: {material_name}'}
    
    load_condition = LoadCondition(**loads)
    analyzer = StructuralAnalyzer(material)
    return analyzer.run_analysis(geometry, load_condition)
