# -*- coding: utf-8 -*-
"""
Pressure Reducing Valve Design Module - Aerospace Valve R&D Platform
Integrated from deepseek_python_20260515_71a7fb.py v3.0
"""

import numpy as np
import math
from dataclasses import dataclass, asdict
from typing import Optional, Tuple, Dict, List
import warnings


@dataclass
class ValveInputParams:
    fluid_type: str = 'kerosene'
    inlet_pressure: float = 25.0
    outlet_pressure: float = 5.0
    min_inlet_pressure: float = 3.0
    flow_rate: float = 500.0
    fluid_temperature: float = 293.0
    regulation_accuracy: float = 0.5
    stability_band: float = 0.1
    leakage_class: str = 'VI'
    response_time: float = 0.05
    vibration_level: float = 20.0
    temperature_range_low: float = 220.0
    temperature_range_high: float = 360.0
    design_life: int = 10000
    reliability_target: float = 0.999
    max_envelope_diameter: float = 100.0
    max_envelope_length: float = 200.0
    inlet_port_size: str = 'DN20'
    outlet_port_size: str = 'DN25'
    mass_limit: float = 1.5


class FluidDatabase:
    FLUID_PROPERTIES = {
        'kerosene': {
            'density': 810, 'dynamic_viscosity': 1.8e-3,
            'bulk_modulus': 1.5e9, 'gas_constant': 0,
            'specific_heat_ratio': 1.0, 'vapor_pressure': 1000,
            'critical_pressure': 2.2e6, 'corrosion_factor': 1.0,
            'cn': 'RP-1/RP-2 \u822a\u7a7a\u7164\u6cb9'
        },
        'nitrogen': {
            'density': 1.16, 'dynamic_viscosity': 1.76e-5,
            'bulk_modulus': 1.0e5, 'gas_constant': 296.8,
            'specific_heat_ratio': 1.4, 'vapor_pressure': 0,
            'critical_pressure': 3.4e6, 'corrosion_factor': 0.5,
            'cn': '\u6c2e\u6c14 (GN2)'
        },
        'helium': {
            'density': 0.166, 'dynamic_viscosity': 1.99e-5,
            'bulk_modulus': 1.0e5, 'gas_constant': 2077,
            'specific_heat_ratio': 1.66, 'vapor_pressure': 0,
            'critical_pressure': 2.27e5, 'corrosion_factor': 0.3,
            'cn': '\u6c26\u6c14 (GHe)'
        },
        'oxygen': {
            'density': 1141, 'dynamic_viscosity': 2.0e-4,
            'bulk_modulus': 1.0e9, 'gas_constant': 259.8,
            'specific_heat_ratio': 1.4, 'vapor_pressure': 1e5,
            'critical_pressure': 5.04e6, 'corrosion_factor': 2.0,
            'cn': '\u6db2\u6c27 (LOX)/\u6c14\u6c27 (GOX)'
        },
        'hydrogen': {
            'density': 70.8, 'dynamic_viscosity': 1.3e-5,
            'bulk_modulus': 1.0e8, 'gas_constant': 4124,
            'specific_heat_ratio': 1.41, 'vapor_pressure': 1.0e5,
            'critical_pressure': 1.3e6, 'corrosion_factor': 0.8,
            'cn': '\u6db2\u6c22 (LH2)/\u6c14\u6c22 (GH2)'
        }
    }

    @classmethod
    def get_property(cls, fluid_name, property_name,
                     pressure=None, temperature=None):
        if fluid_name not in cls.FLUID_PROPERTIES:
            raise ValueError(f"Unsupported fluid: {fluid_name}")
        base_props = cls.FLUID_PROPERTIES[fluid_name]
        base_value = base_props.get(property_name)
        if base_value is None:
            raise ValueError(f"Unsupported property: {property_name}")
        corrected_value = base_value
        if property_name == 'density' and pressure and temperature:
            if base_props['gas_constant'] > 0:
                R = base_props['gas_constant']
                corrected_value = pressure / (R * temperature)
        elif property_name == 'dynamic_viscosity' and temperature:
            if fluid_name in ['nitrogen', 'oxygen']:
                T0 = 293.0
                mu0 = base_value
                corrected_value = mu0 * (temperature / T0)**0.67
        return corrected_value

    @classmethod
    def get_all_fluids(cls):
        result = []
        for name, props in cls.FLUID_PROPERTIES.items():
            result.append({'id': name, 'cn': props.get('cn', name)})
        return result


class MaterialDatabase:
    MATERIALS = {
        '17-4PH': {
            'density': 7800, 'yield_strength': 1170,
            'tensile_strength': 1310, 'elastic_modulus': 196e3,
            'poisson_ratio': 0.27, 'thermal_conductivity': 18.3,
            'cte': 10.8e-6, 'fatigue_limit': 550,
            'hardness': 40, 'corrosion_resistance': 0.8,
            'cn': '\u6c89\u6dc0\u786c\u5316\u4e0d\u9508\u94a2'
        },
        'Inconel718': {
            'density': 8190, 'yield_strength': 1100,
            'tensile_strength': 1375, 'elastic_modulus': 200e3,
            'poisson_ratio': 0.29, 'thermal_conductivity': 11.4,
            'cte': 13.0e-6, 'fatigue_limit': 600,
            'hardness': 40, 'corrosion_resistance': 0.9,
            'cn': '\u954d\u57fa\u9ad8\u6e29\u5408\u91d1'
        },
        'Ti-6Al-4V': {
            'density': 4430, 'yield_strength': 880,
            'tensile_strength': 950, 'elastic_modulus': 114e3,
            'poisson_ratio': 0.33, 'thermal_conductivity': 6.7,
            'cte': 8.6e-6, 'fatigue_limit': 500,
            'hardness': 36, 'corrosion_resistance': 0.85,
            'cn': '\u949b\u5408\u91d1'
        },
        'Al-7075-T6': {
            'density': 2810, 'yield_strength': 505,
            'tensile_strength': 570, 'elastic_modulus': 71.7e3,
            'poisson_ratio': 0.33, 'thermal_conductivity': 130,
            'cte': 23.6e-6, 'fatigue_limit': 160,
            'hardness': 150, 'corrosion_resistance': 0.5,
            'cn': '\u94dd\u5408\u91d1'
        },
        'Elgiloy': {
            'density': 8300, 'yield_strength': 1600,
            'tensile_strength': 2000, 'elastic_modulus': 203e3,
            'poisson_ratio': 0.30, 'thermal_conductivity': 13.0,
            'cte': 14.5e-6, 'fatigue_limit': 700,
            'hardness': 55, 'corrosion_resistance': 0.9,
            'cn': '\u94b4\u94ec\u954d\u5408\u91d1(\u5f39\u7c27)'
        }
    }

    @classmethod
    def get_material(cls, name):
        if name not in cls.MATERIALS:
            raise ValueError(f"Unsupported material: {name}")
        return cls.MATERIALS[name].copy()

    @classmethod
    def recommend_body_material(cls, fluid, temperature, pressure):
        if fluid in ['oxygen', 'hydrogen']:
            return 'Inconel718' if temperature < 120 else '17-4PH'
        elif fluid in ['kerosene']:
            return '17-4PH' if pressure > 30 else 'Ti-6Al-4V'
        else:
            return '17-4PH' if pressure > 20 else 'Al-7075-T6'

    @classmethod
    def recommend_spring_material(cls, temperature, cycles):
        if temperature > 500 or cycles > 1e6:
            return 'Inconel718'
        elif temperature > 350:
            return '17-4PH'
        else:
            return 'Elgiloy'

    @classmethod
    def recommend_diaphragm_material(cls, fluid, pressure):
        if fluid in ['oxygen']:
            return 'Inconel718'
        elif pressure > 20:
            return '17-4PH'
        else:
            return 'Elgiloy'

    @classmethod
    def get_all_materials(cls):
        result = []
        for name, props in cls.MATERIALS.items():
            result.append({
                'id': name,
                'cn': props.get('cn', name),
                'yield_strength': props['yield_strength'],
                'density': props['density']
            })
        return result


class PressureReducingValveDesigner:

    def __init__(self, params):
        self.params = params
        self.fluid_props = {}
        self.body_material = ''
        self.spring_material = ''
        self.diaphragm_material = ''
        self._init_fluid_properties()
        self._init_materials()

    def _init_fluid_properties(self):
        props = ['density', 'dynamic_viscosity', 'gas_constant',
                 'specific_heat_ratio', 'vapor_pressure', 'bulk_modulus']
        for prop in props:
            try:
                value = FluidDatabase.get_property(
                    self.params.fluid_type, prop,
                    pressure=self.params.inlet_pressure * 1e6,
                    temperature=self.params.fluid_temperature
                )
                self.fluid_props[prop] = value
            except ValueError:
                self.fluid_props[prop] = 0.0

    def _init_materials(self):
        self.body_material = MaterialDatabase.recommend_body_material(
            self.params.fluid_type,
            self.params.fluid_temperature,
            self.params.inlet_pressure
        )
        self.spring_material = MaterialDatabase.recommend_spring_material(
            self.params.fluid_temperature,
            self.params.design_life
        )
        self.diaphragm_material = MaterialDatabase.recommend_diaphragm_material(
            self.params.fluid_type,
            self.params.inlet_pressure
        )

    def calculate_orifice_diameter(self):
        Q = self.params.flow_rate / 1000 / 60
        rho = self.fluid_props['density']
        delta_p = (self.params.inlet_pressure - self.params.outlet_pressure) * 1e6

        if self.fluid_props['gas_constant'] > 0:
            P1 = self.params.inlet_pressure * 1e6
            P2 = self.params.outlet_pressure * 1e6
            k = self.fluid_props['specific_heat_ratio']
            r_critical = (2 / (k + 1)) ** (k / (k - 1))
            P_critical = P1 * r_critical

            if P2 <= P_critical:
                T = self.params.fluid_temperature
                R = self.fluid_props['gas_constant']
                m_dot = Q * rho
                C = math.sqrt(k / R / T * (2 / (k + 1)) ** ((k + 1) / (k - 1)))
                A_required = m_dot / (C * P1)
            else:
                T = self.params.fluid_temperature
                R = self.fluid_props['gas_constant']
                ratio = P2 / P1
                flow_func = math.sqrt(
                    (2 * k / (k - 1)) *
                    (ratio ** (2 / k) - ratio ** ((k + 1) / k))
                )
                A_required = Q * rho / (P1 * flow_func * math.sqrt(2 / (R * T)))
        else:
            Cd = 0.65
            A_required = Q / (Cd * math.sqrt(2 * delta_p / rho))

        d_orifice = math.sqrt(4 * A_required / math.pi) * 1000
        d_orifice *= 1.15
        d_orifice = round(d_orifice * 2) / 2

        max_d = self.params.max_envelope_diameter * 0.7
        if d_orifice > max_d:
            d_orifice = max_d

        return d_orifice

    def calculate_max_lift(self, orifice_diameter):
        h_optimized = orifice_diameter / 4 * 1.1
        return round(h_optimized, 2)

    def calculate_sensor_diameter(self, orifice_diameter):
        P_out = self.params.outlet_pressure * 1e6
        spring_force_ratio = 0.7
        force_factor = 1.2
        A_sensor_required = (
            spring_force_ratio * math.pi * (orifice_diameter / 1000)**2 / 4 *
            self.params.inlet_pressure * 1e6 * force_factor
        ) / P_out
        d_sensor = math.sqrt(4 * A_sensor_required / math.pi) * 1000
        d_sensor = math.sqrt(d_sensor**2 / 0.8)
        d_sensor = round(d_sensor * 2) / 2
        return d_sensor

    def calculate_spring_design(self, orifice_diameter, sensor_diameter, max_lift):
        P_out = self.params.outlet_pressure * 1e6
        A_sensor_geo = math.pi * (sensor_diameter / 1000)**2 / 4
        A_sensor_eff = A_sensor_geo * 0.8
        F_out = P_out * A_sensor_eff

        d_m = orifice_diameter / 1000
        h_m = max_lift / 1000
        delta_P = (self.params.inlet_pressure - self.params.outlet_pressure) * 1e6
        F_flow = 0.43 * d_m * delta_P * h_m

        F_friction = 0.05 * F_out

        A_valve = math.pi * (orifice_diameter / 1000)**2 / 4
        F_inlet_on_valve = self.params.inlet_pressure * 1e6 * A_valve
        F_preload = F_inlet_on_valve + F_friction

        k_spring = (F_out - F_preload - F_flow) / h_m if h_m > 0 else 1e6
        k_spring_N_mm = abs(k_spring) / 1000

        spring_mat = MaterialDatabase.get_material(self.spring_material)
        C = 8
        F_max = F_out
        K_w = (4 * C - 1) / (4 * C - 4) + 0.615 / C
        tau_allowable = spring_mat['yield_strength'] * 0.5

        d_wire = math.sqrt(
            K_w * 8 * F_max * C / (math.pi * tau_allowable * 1e6)
        ) * 1000
        d_wire = round(d_wire * 2) / 2
        if d_wire < 0.5:
            d_wire = 0.5

        D_coil = C * d_wire
        G = spring_mat['elastic_modulus'] / (2 * (1 + spring_mat['poisson_ratio']))
        N_active = (G * (d_wire / 1000)**4) / (8 * (D_coil / 1000)**3 * abs(k_spring))
        N_active = max(3, round(N_active))
        N_total = N_active + 2

        L_free = (F_max / abs(k_spring)) * 1.2 * 1000

        return {
            'stiffness': k_spring_N_mm,
            'preload': F_preload,
            'wire_diameter': d_wire,
            'coil_diameter': D_coil,
            'active_coils': N_active,
            'total_coils': N_total,
            'free_length': L_free,
            'material': self.spring_material,
            'max_force': F_max,
            'shear_stress': K_w * 8 * F_max * C / (math.pi * (d_wire / 1000)**2) / 1e6,
            'allowable_stress': tau_allowable
        }

    def calculate_flow_coefficient(self, orifice_diameter, max_lift):
        d_inch = orifice_diameter / 25.4
        h_inch = max_lift / 25.4
        Cv = 30 * d_inch * h_inch
        return round(Cv, 2)

    def calculate_natural_frequency(self, spring_stiffness, sensor_diameter):
        m_estimate = 0.1 * (sensor_diameter / 50)**2
        k = spring_stiffness * 1000
        f_n = 1 / (2 * math.pi) * math.sqrt(k / m_estimate)
        return round(f_n, 1)

    def calculate_flow_force(self, orifice_diameter, max_lift):
        d_m = orifice_diameter / 1000
        h_m = max_lift / 1000
        delta_P = (self.params.inlet_pressure - self.params.outlet_pressure) * 1e6
        F_flow_base = 0.43 * d_m * delta_P * h_m
        return F_flow_base * 0.7

    def check_strength(self, orifice_diameter, sensor_diameter, spring_design):
        body_mat = MaterialDatabase.get_material(self.body_material)
        R_o = self.params.max_envelope_diameter / 2
        R_i = sensor_diameter * 0.6
        P = self.params.inlet_pressure

        if R_o > R_i:
            sigma_hoop = P * (R_o**2 + R_i**2) / (R_o**2 - R_i**2)
        else:
            sigma_hoop = P * 10

        sigma_max = sigma_hoop * 1.5
        safety_factor = body_mat['yield_strength'] / sigma_max if sigma_max > 0 else 99
        return sigma_max, safety_factor

    def estimate_mass(self, orifice_diameter, sensor_diameter, spring_design):
        body_mat = MaterialDatabase.get_material(self.body_material)
        spring_mat = MaterialDatabase.get_material(self.spring_material)

        L_body = self.params.max_envelope_length
        D_body = self.params.max_envelope_diameter
        t_wall = 2.5

        V_body = math.pi * D_body * L_body * t_wall
        m_body = V_body * 1e-9 * body_mat['density']

        V_spool = math.pi * (sensor_diameter / 2)**2 * 10
        m_spool = V_spool * 1e-9 * body_mat['density']

        d_wire = spring_design['wire_diameter']
        D_coil = spring_design['coil_diameter']
        N_total = spring_design['total_coils']
        V_spring = math.pi * (d_wire / 2)**2 * math.pi * D_coil * N_total
        m_spring = V_spring * 1e-9 * spring_mat['density']

        m_misc = 0.1
        return m_body + m_spool + m_spring + m_misc

    def reliability_analysis(self):
        uncertainties = {
            'inlet_pressure': 0.05,
            'spring_stiffness': 0.03,
            'orifice_diameter': 0.01,
            'flow_force': 0.10,
            'material_strength': 0.08,
            'seat_wear': 0.02
        }
        sigma_p_out = 0.1 * self.params.outlet_pressure * 0.03
        beta = self.params.stability_band / sigma_p_out if sigma_p_out > 0 else 99
        sensitivities = {}
        total = sum(uncertainties.values())
        for param, cov in uncertainties.items():
            sensitivities[param] = round(cov * 100 / total, 1)
        return beta, sensitivities

    def optimize_valve_design(self):
        suggestions = []
        if self.params.flow_rate > 600:
            suggestions.append("\u91c7\u7528\u7a7a\u5fc3\u9600\u82af\u7ed3\u6784\u4ee5\u964d\u4f4e\u975e\u7ebf\u6027\u6d41\u52a8\u529b")
            suggestions.append("\u5efa\u8bae\u4f7f\u7528\u591a\u76ee\u6807\u4f18\u5316\u6846\u67b6(NSGA-II)\u4f18\u5316\u9600\u53e3\u5f62\u72b6")
            suggestions.append("\u8003\u8651\u589e\u52a0\u6d41\u52a8\u529b\u8865\u507f\u7ed3\u6784(\u5982\u538b\u529b\u5e73\u8861\u69fd)")
        if self.fluid_props.get('dynamic_viscosity', 0) > 0.001:
            suggestions.append("\u91c7\u7528U\u578b\u6216C\u578b\u8282\u6d41\u69fd\u964d\u4f4e\u7c98\u6027\u52a0\u70ed\u548c\u70ed\u53d8\u5f62\u98ce\u9669")
        if self.params.reliability_target > 0.999:
            suggestions.append("\u5efa\u8bae\u5f00\u5c55\u53ef\u9760\u6027\u4eff\u771f\u5206\u6790\uff0c\u8003\u8651\u51e0\u4f55\u3001\u8f7d\u8377\u548c\u6750\u6599\u53c2\u6570\u7684\u4e0d\u786e\u5b9a\u6027")
        temp_range = self.params.temperature_range_high - self.params.temperature_range_low
        if temp_range > 200:
            suggestions.append("\u8003\u8651\u70ed\u53d8\u5f62\u8865\u507f\u8bbe\u8ba1\uff0c\u9009\u62e9\u70ed\u81a8\u80c0\u7cfb\u6570\u5339\u914d\u7684\u6750\u6599\u5bf9")
        if self.params.mass_limit < 0.8:
            suggestions.append("\u91c7\u7528\u949b\u5408\u91d1\u6216\u590d\u5408\u6750\u6599\u58f3\u4f53\u51cf\u91cd")
        return suggestions

    def design(self):
        d_orifice = self.calculate_orifice_diameter()
        h_max = self.calculate_max_lift(d_orifice)
        d_sensor = self.calculate_sensor_diameter(d_orifice)
        spring = self.calculate_spring_design(d_orifice, d_sensor, h_max)
        Cv = self.calculate_flow_coefficient(d_orifice, h_max)
        pressure_loss = 0.05 * self.params.inlet_pressure
        internal_leakage = 0.15 * (d_orifice / 25.4) / 1000
        f_n = self.calculate_natural_frequency(spring['stiffness'], d_sensor)
        F_flow = self.calculate_flow_force(d_orifice, h_max)
        max_stress, safety_factor = self.check_strength(d_orifice, d_sensor, spring)
        mass = self.estimate_mass(d_orifice, d_sensor, spring)
        reliability_index, sensitivities = self.reliability_analysis()
        suggestions = self.optimize_valve_design()

        flow_area = math.pi * d_orifice * h_max * math.sin(math.radians(45))

        warnings_list = []
        if mass > self.params.mass_limit:
            warnings_list.append(
                f"\u4f30\u7b97\u8d28\u91cf {mass:.3f}kg \u8d85\u8fc7\u9650\u5236 {self.params.mass_limit}kg"
            )
        if safety_factor < 1.5:
            warnings_list.append(
                f"\u5b89\u5168\u7cfb\u6570 {safety_factor:.2f} < 1.5\uff0c\u9700\u52a0\u5f3a"
            )

        return {
            'input': asdict(self.params),
            'materials': {
                'body': self.body_material,
                'spring': self.spring_material,
                'diaphragm': self.diaphragm_material,
                'body_cn': MaterialDatabase.MATERIALS.get(self.body_material, {}).get('cn', ''),
                'spring_cn': MaterialDatabase.MATERIALS.get(self.spring_material, {}).get('cn', ''),
                'diaphragm_cn': MaterialDatabase.MATERIALS.get(self.diaphragm_material, {}).get('cn', '')
            },
            'geometry': {
                'orifice_diameter': round(d_orifice, 2),
                'max_lift': round(h_max, 2),
                'seat_width': 1.5,
                'seat_angle': 45.0,
                'flow_area': round(flow_area, 2),
                'sensor_type': 'diaphragm',
                'sensor_diameter': round(d_sensor, 2),
                'sensor_effective_area': round(math.pi * (d_sensor / 2)**2 * 0.8, 2),
                'sensor_thickness': 0.3
            },
            'spring': {
                'stiffness': round(spring['stiffness'], 2),
                'preload': round(spring['preload'], 2),
                'wire_diameter': round(spring['wire_diameter'], 2),
                'coil_diameter': round(spring['coil_diameter'], 2),
                'active_coils': spring['active_coils'],
                'total_coils': spring['total_coils'],
                'free_length': round(spring['free_length'], 2),
                'material': spring['material'],
                'material_cn': MaterialDatabase.MATERIALS.get(spring['material'], {}).get('cn', ''),
                'shear_stress': round(spring['shear_stress'], 2),
                'allowable_stress': round(spring['allowable_stress'], 2)
            },
            'performance': {
                'flow_coefficient_Cv': Cv,
                'pressure_drop': round(pressure_loss, 3),
                'internal_leakage': round(internal_leakage, 5),
                'natural_frequency': f_n,
                'flow_force': round(F_flow, 2),
                'response_time': self.params.response_time
            },
            'strength': {
                'max_stress': round(max_stress, 2),
                'safety_factor': round(safety_factor, 2),
                'fatigue_life': self.params.design_life,
                'mass': round(mass, 3)
            },
            'reliability': {
                'reliability_index': round(reliability_index, 3),
                'sensitivity_factors': sensitivities
            },
            'suggestions': suggestions,
            'warnings': warnings_list
        }


def run_design(input_data):
    """API entry point: accepts dict, returns dict"""
    # Input validation: guard against non-physical values
    inlet_p = float(input_data.get('inlet_pressure', 0))
    outlet_p = float(input_data.get('outlet_pressure', 0))
    if inlet_p <= 0:
        return {'error': f'Inlet pressure must be positive, got {inlet_p}'}
    if outlet_p <= 0:
        return {'error': f'Outlet pressure must be positive, got {outlet_p}'}
    if inlet_p <= outlet_p:
        return {'error': f'Inlet pressure must exceed outlet pressure (in={inlet_p}, out={outlet_p})'}
    params = ValveInputParams()
    for key, value in input_data.items():
        if hasattr(params, key):
            if key == 'temperature_range':
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    params.temperature_range_low = value[0]
                    params.temperature_range_high = value[1]
            else:
                setattr(params, key, value)

    designer = PressureReducingValveDesigner(params)
    return designer.design()
