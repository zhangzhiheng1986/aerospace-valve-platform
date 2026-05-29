#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航空航天电磁阀研发平台 - 流体仿真分析模块
CFD (Computational Fluid Dynamics) Simulation Module

功能：
- 阀门内部流场仿真
- 压力分布计算
- 流速分布计算
- 流量系数计算
- 阻力特性分析
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math


class FlowType(Enum):
    """流动类型"""
    LAMINAR = "层流"
    TURBULENT = "湍流"
    TRANSITIONAL = "过渡流"


class AnalysisType(Enum):
    """分析类型"""
    STEADY = "稳态"
    TRANSIENT = "瞬态"


@dataclass
class FluidProperties:
    """流体属性"""
    name: str                    # 流体名称
    density: float               # 密度 (kg/m³)
    viscosity: float             # 动力粘度 (Pa·s)
    temperature: float           # 温度 (°C)
    pressure: float              # 压力 (Pa)
    
    @property
    def kinematic_viscosity(self) -> float:
        """运动粘度 (m²/s)"""
        return self.viscosity / self.density


@dataclass
class ValveGeometry:
    """阀门几何参数"""
    inlet_diameter: float        # 入口直径 (mm)
    outlet_diameter: float       # 出口直径 (mm)
    orifice_diameter: float      # 阀口直径 (mm)
    stroke: float                # 行程 (mm)
    chamber_length: float        # 阀腔长度 (mm)
    chamber_diameter: float      # 阀腔直径 (mm)
    
    @property
    def inlet_area(self) -> float:
        """入口面积 (m²)"""
        return math.pi * (self.inlet_diameter / 2000) ** 2
    
    @property
    def orifice_area(self) -> float:
        """阀口面积 (m²)"""
        return math.pi * (self.orifice_diameter / 2000) ** 2


class CFDAnalyzer:
    """CFD分析器"""
    
    def __init__(self, fluid: FluidProperties, geometry: ValveGeometry):
        self.fluid = fluid
        self.geometry = geometry
        self.results = {}
    
    def calculate_reynolds_number(self, velocity: float, characteristic_length: float) -> float:
        """
        计算雷诺数
        Re = ρvL/μ = vL/ν
        
        Args:
            velocity: 流速 (m/s)
            characteristic_length: 特征长度 (m)
        
        Returns:
            雷诺数
        """
        return (self.fluid.density * velocity * characteristic_length) / self.fluid.viscosity
    
    def determine_flow_type(self, reynolds: float) -> FlowType:
        """
        根据雷诺数判断流动类型
        
        Args:
            reynolds: 雷诺数
        
        Returns:
            流动类型
        """
        if reynolds < 2300:
            return FlowType.LAMINAR
        elif reynolds > 4000:
            return FlowType.TURBULENT
        else:
            return FlowType.TRANSITIONAL
    
    def calculate_pressure_drop(self, flow_rate: float, opening_ratio: float = 1.0) -> float:
        """
        计算压降
        使用简化的伯努利方程和局部阻力损失
        
        Args:
            flow_rate: 体积流量 (m³/s)
            opening_ratio: 开度比 (0-1)
        
        Returns:
            压降 (Pa)
        """
        # 计算流速
        effective_area = self.geometry.orifice_area * opening_ratio
        velocity = flow_rate / effective_area if effective_area > 0 else 0
        
        # 计算雷诺数
        d_orifice = self.geometry.orifice_diameter / 1000  # 转换为m
        reynolds = self.calculate_reynolds_number(velocity, d_orifice)
        
        # 计算摩擦系数（使用Colebrook方程的近似）
        if reynolds < 2300:
            # 层流
            friction_factor = 64 / reynolds if reynolds > 0 else 0
        else:
            # 湍流（Blasius公式）
            friction_factor = 0.316 / (reynolds ** 0.25)
        
        # 局部阻力系数（阀门典型值）
        # 开度越小，阻力系数越大
        if opening_ratio > 0:
            loss_coefficient = (1 - opening_ratio ** 2) / opening_ratio ** 2 + 0.5
        else:
            loss_coefficient = 1000  # 关闭状态
        
        # 压降计算
        # ΔP = K * 0.5 * ρ * v²
        pressure_drop = loss_coefficient * 0.5 * self.fluid.density * velocity ** 2
        
        return pressure_drop
    
    def calculate_flow_coefficient(self, opening_ratio: float = 1.0) -> Dict:
        """
        计算流量系数 Cv
        
        Args:
            opening_ratio: 开度比 (0-1)
        
        Returns:
            流量系数相关参数
        """
        # Cv定义：当压降为1 psi时，通过阀水的流量（US gal/min）
        # 简化计算：Cv = Q / sqrt(ΔP/SG)
        
        # 假设压降 0.1 MPa
        delta_p = 100000  # Pa
        
        # 理论流量（基于孔口公式）
        # Q = Cd * A * sqrt(2 * ΔP / ρ)
        discharge_coefficient = 0.62  # 典型收缩系数
        effective_area = self.geometry.orifice_area * opening_ratio
        
        velocity = math.sqrt(2 * delta_p / self.fluid.density)
        flow_rate = discharge_coefficient * effective_area * velocity
        
        # 转换为 Cv (US gal/min)
        # 1 m³/s = 15850.3 US gal/min
        flow_rate_gpm = flow_rate * 15850.3
        
        # ΔP = 1 psi = 6894.76 Pa
        # Cv = Q / sqrt(ΔP/SG)  对于水 SG=1
        cv = flow_rate_gpm / math.sqrt(delta_p / 6894.76)
        
        return {
            'Cv': cv,
            'Kv': cv * 0.865,  # Kv = 0.865 * Cv
            'discharge_coefficient': discharge_coefficient,
            'effective_area_m2': effective_area,
            'theoretical_velocity_ms': velocity,
            'theoretical_flow_m3s': flow_rate
        }
    
    def simulate_flow_field(self, inlet_pressure: float, outlet_pressure: float,
                           opening_ratio: float = 1.0, grid_resolution: int = 50) -> Dict:
        """
        模拟流场分布（简化模型）
        
        Args:
            inlet_pressure: 入口压力 (Pa)
            outlet_pressure: 出口压力 (Pa)
            opening_ratio: 开度比 (0-1)
            grid_resolution: 网格分辨率
        
        Returns:
            流场数据
        """
        # 压差
        delta_p = inlet_pressure - outlet_pressure
        
        # 创建网格
        x = np.linspace(0, self.geometry.chamber_length, grid_resolution)
        r = np.linspace(-self.geometry.chamber_diameter/2, 
                       self.geometry.chamber_diameter/2, grid_resolution)
        
        # 压力分布（简化：线性分布 + 阀口处压降）
        pressure_field = np.zeros((grid_resolution, grid_resolution))
        for i, xi in enumerate(x):
            # 阀口位置（假设在中间）
            valve_position = self.geometry.chamber_length / 2
            
            if xi < valve_position:
                # 入口段
                pressure_field[i, :] = inlet_pressure - (delta_p * 0.3) * (xi / valve_position)
            else:
                # 出口段
                pressure_field[i, :] = outlet_pressure + (delta_p * 0.7) * (1 - (xi - valve_position) / valve_position)
        
        # 流速分布（基于连续性方程）
        velocity_field = np.zeros((grid_resolution, grid_resolution))
        
        # 入口流速
        inlet_velocity = math.sqrt(2 * delta_p * 0.3 / self.fluid.density)
        
        for i, xi in enumerate(x):
            valve_position = self.geometry.chamber_length / 2
            
            if xi < valve_position:
                # 入口段：流速逐渐加速
                velocity_field[i, :] = inlet_velocity * (1 + 0.5 * xi / valve_position)
            else:
                # 出口段：流速逐渐减速
                velocity_field[i, :] = inlet_velocity * 1.5 * (1 - 0.3 * (xi - valve_position) / valve_position)
        
        # 阀口处流速最大
        valve_idx = grid_resolution // 2
        max_velocity = inlet_velocity / opening_ratio if opening_ratio > 0 else 0
        velocity_field[valve_idx, :] = max_velocity
        
        # 计算雷诺数和流动类型
        d_orifice = self.geometry.orifice_diameter / 1000
        reynolds = self.calculate_reynolds_number(max_velocity, d_orifice)
        flow_type = self.determine_flow_type(reynolds)
        
        return {
            'x_coordinates': x.tolist(),
            'r_coordinates': r.tolist(),
            'pressure_field': pressure_field.tolist(),
            'velocity_field': velocity_field.tolist(),
            'inlet_velocity': inlet_velocity,
            'max_velocity': max_velocity,
            'reynolds_number': reynolds,
            'flow_type': flow_type.value,
            'grid_resolution': grid_resolution
        }
    
    def calculate_cavitation_index(self, inlet_pressure: float, outlet_pressure: float,
                                   vapor_pressure: float = 2339) -> Dict:
        """
        计算空化指数
        
        Args:
            inlet_pressure: 入口压力 (Pa)
            outlet_pressure: 出口压力 (Pa)
            vapor_pressure: 饱和蒸汽压 (Pa)，默认水在20°C
        
        Returns:
            空化相关参数
        """
        delta_p = inlet_pressure - outlet_pressure
        
        # 空化指数 σ = (P_inlet - P_vapor) / (P_inlet - P_outlet)
        if delta_p > 0:
            sigma = (inlet_pressure - vapor_pressure) / delta_p
        else:
            sigma = float('inf')
        
        # 临界空化指数（经验值，通常0.2-0.5）
        sigma_critical = 0.3
        
        # 空化风险
        if sigma > 2.0:
            cavitation_risk = "无空化风险"
        elif sigma > 1.0:
            cavitation_risk = "轻微空化风险"
        elif sigma > sigma_critical:
            cavitation_risk = "中等空化风险"
        else:
            cavitation_risk = "严重空化风险"
        
        return {
            'cavitation_index': sigma,
            'critical_index': sigma_critical,
            'vapor_pressure': vapor_pressure,
            'cavitation_risk': cavitation_risk,
            'safe_operation': sigma > sigma_critical
        }
    
    def run_analysis(self, inlet_pressure: float, outlet_pressure: float,
                    opening_ratio: float = 1.0) -> Dict:
        """
        运行完整CFD分析
        
        Args:
            inlet_pressure: 入口压力 (Pa)
            outlet_pressure: 出口压力 (Pa)
            opening_ratio: 开度比 (0-1)
        
        Returns:
            完整分析结果
        """
        # 流量系数
        flow_coeff = self.calculate_flow_coefficient(opening_ratio)
        
        # 流场仿真
        flow_field = self.simulate_flow_field(inlet_pressure, outlet_pressure, opening_ratio)
        
        # 空化分析
        cavitation = self.calculate_cavitation_index(inlet_pressure, outlet_pressure)
        
        # 压降计算
        delta_p = inlet_pressure - outlet_pressure
        
        # 流量计算
        Q = flow_coeff['Cv'] * math.sqrt(delta_p / 6894.76) / 15850.3  # m³/s
        
        # 功率计算
        power = delta_p * Q  # W
        
        return {
            'success': True,
            'flow_coefficient': flow_coeff,
            'flow_field': flow_field,
            'cavitation': cavitation,
            'performance': {
                'inlet_pressure_Pa': inlet_pressure,
                'outlet_pressure_Pa': outlet_pressure,
                'pressure_drop_Pa': delta_p,
                'pressure_drop_MPa': delta_p / 1e6,
                'opening_ratio': opening_ratio,
                'volumetric_flow_m3s': Q,
                'volumetric_flow_Lmin': Q * 60000,
                'mass_flow_kgs': Q * self.fluid.density,
                'power_W': power,
                'power_kW': power / 1000
            },
            'fluid': {
                'name': self.fluid.name,
                'density': self.fluid.density,
                'viscosity': self.fluid.viscosity,
                'temperature': self.fluid.temperature
            },
            'geometry': {
                'inlet_diameter_mm': self.geometry.inlet_diameter,
                'orifice_diameter_mm': self.geometry.orifice_diameter,
                'stroke_mm': self.geometry.stroke
            }
        }


# 预定义流体
FLUIDS = {
    'water_20C': FluidProperties('水(20°C)', 998.2, 0.001002, 20, 101325),
    'water_80C': FluidProperties('水(80°C)', 971.8, 0.000355, 80, 101325),
    'air_20C': FluidProperties('空气(20°C)', 1.205, 1.81e-5, 20, 101325),
    'hydraulic_oil': FluidProperties('液压油', 870, 0.04, 40, 101325),
    'fuel_jet_a': FluidProperties('航空煤油Jet-A', 800, 0.008, 20, 101325),
}


def run_cfd_analysis(fluid_name: str, geometry_params: Dict, 
                    inlet_pressure: float, outlet_pressure: float,
                    opening_ratio: float = 1.0) -> Dict:
    """
    运行CFD分析的便捷函数
    
    Args:
        fluid_name: 流体名称
        geometry_params: 几何参数字典
        inlet_pressure: 入口压力 (Pa)
        outlet_pressure: 出口压力 (Pa)
        opening_ratio: 开度比
    
    Returns:
        分析结果
    """
    # 获取流体
    fluid = FLUIDS.get(fluid_name)
    if not fluid:
        return {'success': False, 'error': f'未知流体: {fluid_name}'}
    
    # 创建几何
    geometry = ValveGeometry(
        inlet_diameter=geometry_params.get('inlet_diameter', 10),
        outlet_diameter=geometry_params.get('outlet_diameter', 10),
        orifice_diameter=geometry_params.get('orifice_diameter', 5),
        stroke=geometry_params.get('stroke', 3),
        chamber_length=geometry_params.get('chamber_length', 30),
        chamber_diameter=geometry_params.get('chamber_diameter', 15)
    )
    
    # 运行分析
    analyzer = CFDAnalyzer(fluid, geometry)
    return analyzer.run_analysis(inlet_pressure, outlet_pressure, opening_ratio)
