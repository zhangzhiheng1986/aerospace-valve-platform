#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航空航天电磁阀研发平台 - 热力学分析模块
Thermal Analysis Module

功能：
- 热传导分析
- 对流换热计算
- 温度场仿真
- 热应力估算
- 热时间常数计算
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math


class HeatTransferMode(Enum):
    """传热模式"""
    CONDUCTION = "热传导"
    CONVECTION = "对流换热"
    RADIATION = "辐射换热"


@dataclass
class Material:
    """材料热物性"""
    name: str                    # 材料名称
    density: float               # 密度 (kg/m³)
    specific_heat: float         # 比热容 (J/kg·K)
    thermal_conductivity: float  # 热导率 (W/m·K)
    
    @property
    def thermal_diffusivity(self) -> float:
        """热扩散率 (m²/s)"""
        return self.thermal_conductivity / (self.density * self.specific_heat)


@dataclass
class BoundaryCondition:
    """边界条件"""
    temperature: Optional[float] = None    # 温度 (K或°C)
    heat_flux: Optional[float] = None      # 热流密度 (W/m²)
    convection_coeff: Optional[float] = None  # 对流换热系数 (W/m²·K)
    ambient_temp: Optional[float] = None   # 环境温度 (K或°C)


class ThermalAnalyzer:
    """热力学分析器"""
    
    def __init__(self, material: Material):
        self.material = material
        self.results = {}
    
    def calculate_conduction_heat(self, area: float, thickness: float,
                                  temp_hot: float, temp_cold: float) -> Dict:
        """
        计算热传导
        Q = k * A * ΔT / d
        
        Args:
            area: 传热面积 (m²)
            thickness: 厚度 (m)
            temp_hot: 高温侧温度 (°C)
            temp_cold: 低温侧温度 (°C)
        
        Returns:
            热传导结果
        """
        delta_T = temp_hot - temp_cold
        Q = self.material.thermal_conductivity * area * delta_T / thickness
        
        # 热流密度
        heat_flux = Q / area
        
        # 热阻
        thermal_resistance = thickness / (self.material.thermal_conductivity * area)
        
        return {
            'heat_rate_W': Q,
            'heat_flux_Wm2': heat_flux,
            'thermal_resistance_KW': thermal_resistance,
            'temperature_difference': delta_T,
            'mode': HeatTransferMode.CONDUCTION.value
        }
    
    def calculate_convection_heat(self, area: float, h: float,
                                  surface_temp: float, fluid_temp: float) -> Dict:
        """
        计算对流换热
        Q = h * A * (T_surface - T_fluid)
        
        Args:
            area: 换热面积 (m²)
            h: 对流换热系数 (W/m²·K)
            surface_temp: 表面温度 (°C)
            fluid_temp: 流体温度 (°C)
        
        Returns:
            对流换热结果
        """
        delta_T = surface_temp - fluid_temp
        Q = h * area * delta_T
        
        # 热流密度
        heat_flux = Q / area
        
        # 热阻
        thermal_resistance = 1 / (h * area)
        
        return {
            'heat_rate_W': Q,
            'heat_flux_Wm2': heat_flux,
            'thermal_resistance_KW': thermal_resistance,
            'temperature_difference': delta_T,
            'convection_coefficient': h,
            'mode': HeatTransferMode.CONVECTION.value
        }
    
    def calculate_radiation_heat(self, area: float, emissivity: float,
                                 surface_temp: float, ambient_temp: float) -> Dict:
        """
        计算辐射换热
        Q = ε * σ * A * (T1⁴ - T2⁴)
        
        Args:
            area: 换热面积 (m²)
            emissivity: 发射率 (0-1)
            surface_temp: 表面温度 (°C)
            ambient_temp: 环境温度 (°C)
        
        Returns:
            辐射换热结果
        """
        # Stefan-Boltzmann常数
        sigma = 5.67e-8  # W/m²·K⁴
        
        # 转换为开尔文
        T1 = surface_temp + 273.15
        T2 = ambient_temp + 273.15
        
        Q = emissivity * sigma * area * (T1**4 - T2**4)
        
        # 热流密度
        heat_flux = Q / area
        
        # 线性化辐射换热系数
        h_rad = emissivity * sigma * (T1 + T2) * (T1**2 + T2**2)
        
        return {
            'heat_rate_W': Q,
            'heat_flux_Wm2': heat_flux,
            'radiation_coefficient': h_rad,
            'emissivity': emissivity,
            'surface_temp_K': T1,
            'ambient_temp_K': T2,
            'mode': HeatTransferMode.RADIATION.value
        }
    
    def calculate_thermal_time_constant(self, mass: float, h: float, 
                                        area: float) -> float:
        """
        计算热时间常数
        τ = m * c / (h * A)
        
        Args:
            mass: 质量 (kg)
            h: 对流换热系数 (W/m²·K)
            area: 换热面积 (m²)
        
        Returns:
            热时间常数 (s)
        """
        return mass * self.material.specific_heat / (h * area)
    
    def simulate_transient_temperature(self, initial_temp: float, ambient_temp: float,
                                       h: float, area: float, mass: float,
                                       time_array: np.ndarray) -> Dict:
        """
        模拟瞬态温度变化（集总参数法）
        T(t) = T_ambient + (T_initial - T_ambient) * exp(-t/τ)
        
        Args:
            initial_temp: 初始温度 (°C)
            ambient_temp: 环境温度 (°C)
            h: 对流换热系数 (W/m²·K)
            area: 换热面积 (m²)
            mass: 质量 (kg)
            time_array: 时间数组 (s)
        
        Returns:
            瞬态温度结果
        """
        # 热时间常数
        tau = self.calculate_thermal_time_constant(mass, h, area)
        
        # 温度变化
        temperature = ambient_temp + (initial_temp - ambient_temp) * np.exp(-time_array / tau)
        
        # 温度变化率
        temp_rate = -(initial_temp - ambient_temp) / tau * np.exp(-time_array / tau)
        
        return {
            'time_s': time_array.tolist(),
            'temperature_C': temperature.tolist(),
            'temperature_rate_Cs': temp_rate.tolist(),
            'thermal_time_constant_s': tau,
            'initial_temp': initial_temp,
            'ambient_temp': ambient_temp,
            'final_temp': ambient_temp
        }
    
    def simulate_2d_temperature_field(self, length: float, width: float,
                                      boundary_conditions: Dict,
                                      heat_source: float = 0,
                                      grid_resolution: int = 50,
                                      time_steps: int = 100) -> Dict:
        """
        模拟2D温度场（有限差分法）
        
        Args:
            length: 长度 (m)
            width: 宽度 (m)
            boundary_conditions: 边界条件
            heat_source: 内热源 (W/m³)
            grid_resolution: 网格分辨率
            time_steps: 时间步数
        
        Returns:
            温度场结果
        """
        # 网格
        dx = length / (grid_resolution - 1)
        dy = width / (grid_resolution - 1)
        
        # 时间步长（稳定性条件）
        alpha = self.material.thermal_diffusivity
        dt = 0.25 * min(dx, dy)**2 / alpha
        
        # 初始温度场
        T = np.ones((grid_resolution, grid_resolution)) * boundary_conditions.get('initial', 20)
        
        # 边界条件
        T_left = boundary_conditions.get('left', 20)
        T_right = boundary_conditions.get('right', 20)
        T_top = boundary_conditions.get('top', 20)
        T_bottom = boundary_conditions.get('bottom', 20)
        
        # 应用边界条件
        T[:, 0] = T_left
        T[:, -1] = T_right
        T[0, :] = T_top
        T[-1, :] = T_bottom
        
        # 时间步进
        for n in range(time_steps):
            T_new = T.copy()
            
            for i in range(1, grid_resolution - 1):
                for j in range(1, grid_resolution - 1):
                    # 二维热传导方程
                    d2T_dx2 = (T[i+1, j] - 2*T[i, j] + T[i-1, j]) / dx**2
                    d2T_dy2 = (T[i, j+1] - 2*T[i, j] + T[i, j-1]) / dy**2
                    
                    # 内热源项
                    source_term = heat_source / (self.material.density * self.material.specific_heat)
                    
                    # 更新温度
                    T_new[i, j] = T[i, j] + dt * (alpha * (d2T_dx2 + d2T_dy2) + source_term)
            
            T = T_new
        
        # 坐标
        x = np.linspace(0, length, grid_resolution)
        y = np.linspace(0, width, grid_resolution)
        
        return {
            'x_coordinates_m': x.tolist(),
            'y_coordinates_m': y.tolist(),
            'temperature_field_C': T.tolist(),
            'max_temperature': float(np.max(T)),
            'min_temperature': float(np.min(T)),
            'avg_temperature': float(np.mean(T)),
            'grid_resolution': grid_resolution,
            'time_steps': time_steps
        }
    
    def calculate_thermal_stress(self, delta_T: float, elastic_modulus: float,
                                 thermal_expansion: float, poisson_ratio: float = 0.3) -> Dict:
        """
        计算热应力
        σ = E * α * ΔT / (1 - ν)
        
        Args:
            delta_T: 温差 (°C)
            elastic_modulus: 弹性模量 (Pa)
            thermal_expansion: 热膨胀系数 (1/K)
            poisson_ratio: 泊松比
        
        Returns:
            热应力结果
        """
        # 热应力
        sigma_thermal = elastic_modulus * thermal_expansion * delta_T / (1 - poisson_ratio)
        
        # 热应变
        strain_thermal = thermal_expansion * delta_T
        
        return {
            'thermal_stress_Pa': sigma_thermal,
            'thermal_stress_MPa': sigma_thermal / 1e6,
            'thermal_strain': strain_thermal,
            'temperature_difference': delta_T,
            'elastic_modulus_GPa': elastic_modulus / 1e9,
            'thermal_expansion': thermal_expansion
        }
    
    def run_analysis(self, component_params: Dict, operating_conditions: Dict) -> Dict:
        """
        运行完整热分析
        
        Args:
            component_params: 组件参数
            operating_conditions: 运行条件
        
        Returns:
            完整分析结果
        """
        # 提取参数
        surface_area = component_params.get('surface_area', 0.01)  # m²
        mass = component_params.get('mass', 0.1)  # kg
        thickness = component_params.get('thickness', 0.005)  # m
        
        initial_temp = operating_conditions.get('initial_temp', 20)
        ambient_temp = operating_conditions.get('ambient_temp', 20)
        fluid_temp = operating_conditions.get('fluid_temp', 80)
        h_convection = operating_conditions.get('convection_coeff', 100)
        emissivity = operating_conditions.get('emissivity', 0.8)
        
        # 稳态热传导
        conduction = self.calculate_conduction_heat(
            surface_area, thickness, fluid_temp, ambient_temp
        )
        
        # 对流换热
        convection = self.calculate_convection_heat(
            surface_area, h_convection, fluid_temp, ambient_temp
        )
        
        # 辐射换热
        radiation = self.calculate_radiation_heat(
            surface_area, emissivity, fluid_temp, ambient_temp
        )
        
        # 热时间常数
        tau = self.calculate_thermal_time_constant(mass, h_convection, surface_area)
        
        # 瞬态温度（10倍时间常数）
        time_array = np.linspace(0, 10 * tau, 100)
        transient = self.simulate_transient_temperature(
            fluid_temp, ambient_temp, h_convection, surface_area, mass, time_array
        )
        
        # 总热损失
        total_heat = conduction['heat_rate_W'] + convection['heat_rate_W'] + radiation['heat_rate_W']
        
        return {
            'success': True,
            'conduction': conduction,
            'convection': convection,
            'radiation': radiation,
            'transient': transient,
            'summary': {
                'total_heat_loss_W': total_heat,
                'thermal_time_constant_s': tau,
                'steady_state_temp_C': ambient_temp,
                'max_temp_C': fluid_temp
            },
            'material': {
                'name': self.material.name,
                'density': self.material.density,
                'specific_heat': self.material.specific_heat,
                'thermal_conductivity': self.material.thermal_conductivity,
                'thermal_diffusivity': self.material.thermal_diffusivity
            }
        }


# 预定义材料
MATERIALS = {
    'copper': Material('纯铜T2', 8960, 385, 401),
    'aluminum': Material('铝合金2A12', 2780, 921, 177),
    'steel': Material('不锈钢304', 7930, 502, 16.3),
    'titanium': Material('钛合金TC4', 4430, 526, 6.7),
    'inconel': Material('Inconel 718', 8190, 435, 11.4),
}


def run_thermal_analysis(material_name: str, component_params: Dict,
                        operating_conditions: Dict) -> Dict:
    """
    运行热分析的便捷函数
    
    Args:
        material_name: 材料名称
        component_params: 组件参数
        operating_conditions: 运行条件
    
    Returns:
        分析结果
    """
    material = MATERIALS.get(material_name)
    if not material:
        return {'success': False, 'error': f'未知材料: {material_name}'}
    
    analyzer = ThermalAnalyzer(material)
    return analyzer.run_analysis(component_params, operating_conditions)
