#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航空航天电磁阀材料数据库系统
Material Database System for Aerospace Solenoid Valves

设计者：院士级材料科学专家
适用领域：航空航天、国防军工、高端装备制造
"""

import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class MaterialCategory(Enum):
    """材料类别枚举"""
    CONDUCTOR = "导体材料"           # 导线/绕组材料
    MAGNETIC = "磁性材料"           # 铁芯/磁路材料
    INSULATION = "绝缘材料"         # 绝缘包覆材料
    STRUCTURAL = "结构材料"         # 阀体/结构件材料
    SEALING = "密封材料"            # 密封圈/垫片材料
    SPRING = "弹性材料"             # 弹簧/弹性元件
    COATING = "涂层材料"            # 表面防护涂层


@dataclass
class MaterialProperty:
    """材料属性数据结构"""
    name: str                           # 材料名称
    category: MaterialCategory          # 材料类别
    standard: str                       # 执行标准（国标/军标/航标）
    
    # 物理性能
    density: float                      # 密度 (g/cm³)
    melting_point: float                # 熔点 (°C)
    
    # 电学性能（导体材料）
    resistivity: Optional[float] = None     # 电阻率 (Ω·m)
    conductivity: Optional[float] = None    # 电导率 (%IACS)
    temp_coeff_resist: Optional[float] = None  # 电阻温度系数 (1/°C)
    
    # 磁学性能（磁性材料）
    permeability: Optional[float] = None     # 相对磁导率 μr
    saturation_flux: Optional[float] = None  # 饱和磁感应强度 Bs (T)
    coercivity: Optional[float] = None       # 矫顽力 Hc (A/m)
    remanence: Optional[float] = None        # 剩磁 Br (T)
    core_loss: Optional[float] = None        # 铁损 (W/kg @ 1T, 50Hz)
    
    # 力学性能
    tensile_strength: Optional[float] = None  # 抗拉强度 (MPa)
    yield_strength: Optional[float] = None    # 屈服强度 (MPa)
    elongation: Optional[float] = None        # 延伸率 (%)
    hardness: Optional[float] = None          # 硬度 (HB/HRB/HRC)
    elastic_modulus: Optional[float] = None   # 弹性模量 (GPa)
    
    # 热学性能
    thermal_conductivity: Optional[float] = None  # 热导率 (W/m·K)
    thermal_expansion: Optional[float] = None     # 热膨胀系数 (10⁻⁶/°C)
    specific_heat: Optional[float] = None         # 比热容 (J/kg·K)
    
    # 环境适应性
    max_temp: Optional[float] = None      # 最高工作温度 (°C)
    min_temp: Optional[float] = None      # 最低工作温度 (°C)
    corrosion_resistance: Optional[str] = None  # 耐腐蚀等级
    radiation_resistance: Optional[str] = None  # 抗辐射等级
    
    # 工艺性能
    weldability: Optional[str] = None     # 焊接性能
    machinability: Optional[str] = None   # 机加工性能
    
    # 认证与合规
    aerospace_grade: Optional[str] = None  # 航空航天等级认证
    mil_spec: Optional[str] = None         # 军标编号
    notes: Optional[str] = None            # 备注说明


class AerospaceMaterialsDatabase:
    """航空航天材料数据库"""
    
    def __init__(self):
        self.materials: Dict[str, MaterialProperty] = {}
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化专业材料数据库"""
        
        # ==================== 导体材料 ====================
        
        # 1. 航空航天级纯铜
        self.add_material(MaterialProperty(
            name="T2纯铜（航空航天级）",
            category=MaterialCategory.CONDUCTOR,
            standard="GB/T 14957-1994 / AMS 4701",
            density=8.96,
            melting_point=1083.4,
            resistivity=1.7241e-8,
            conductivity=100.0,  # 100% IACS
            temp_coeff_resist=0.00393,
            tensile_strength=220,
            elongation=35,
            hardness=40,  # HB
            elastic_modulus=110,
            thermal_conductivity=401,
            thermal_expansion=16.5,
            max_temp=200,
            min_temp=-269,  # 深冷应用
            corrosion_resistance="优良",
            aerospace_grade="Class A",
            mil_spec="MIL-C-16234",
            notes="高纯度无氧铜，适用于高可靠性电磁阀绕组"
        ))
        
        # 2. 镀银铜线（高频应用）
        self.add_material(MaterialProperty(
            name="镀银铜线TRAg",
            category=MaterialCategory.CONDUCTOR,
            standard="GJB 1934-1994",
            density=8.96,
            melting_point=1083.4,
            resistivity=1.7241e-8,
            conductivity=100.0,
            temp_coeff_resist=0.00393,
            tensile_strength=250,
            elongation=30,
            thermal_conductivity=415,  # 银层提升
            max_temp=200,
            min_temp=-65,
            corrosion_resistance="优良",
            aerospace_grade="Space Grade",
            notes="镀银层厚度≥2μm，高频低损耗，抗高温氧化"
        ))
        
        # 3. 航空航天级铜镍合金（高强度）
        self.add_material(MaterialProperty(
            name="B10铜镍合金",
            category=MaterialCategory.CONDUCTOR,
            standard="GJB 3528-1999",
            density=8.94,
            melting_point=1150,
            resistivity=2.0e-7,
            conductivity=8.6,
            temp_coeff_resist=0.0002,
            tensile_strength=350,
            yield_strength=120,
            elongation=25,
            hardness=80,
            elastic_modulus=135,
            thermal_conductivity=30,
            thermal_expansion=16.0,
            max_temp=300,
            min_temp=-200,
            corrosion_resistance="极佳",  # 海水环境
            aerospace_grade="Naval Grade",
            notes="舰载/海洋环境电磁阀首选，抗海水腐蚀"
        ))
        
        # 4. 高温合金导线
        self.add_material(MaterialProperty(
            name="镍铬合金Cr20Ni80",
            category=MaterialCategory.CONDUCTOR,
            standard="GB/T 1234-2012",
            density=8.4,
            melting_point=1400,
            resistivity=1.09e-6,
            conductivity=1.58,
            temp_coeff_resist=0.00014,
            tensile_strength=650,
            yield_strength=300,
            elongation=20,
            hardness=180,
            elastic_modulus=200,
            thermal_conductivity=15,
            thermal_expansion=14.0,
            max_temp=1100,
            min_temp=-200,
            corrosion_resistance="优良",
            aerospace_grade="High Temp Grade",
            notes="高温电磁阀专用，适用于发动机舱环境"
        ))
        
        # ==================== 磁性材料 ====================
        
        # 5. 航空级电工纯铁
        self.add_material(MaterialProperty(
            name="DT4C电工纯铁",
            category=MaterialCategory.MAGNETIC,
            standard="GB/T 6983-2008",
            density=7.87,
            melting_point=1538,
            permeability=5000,  # 最大磁导率
            saturation_flux=2.15,
            coercivity=32,  # 极低矫顽力
            remanence=0.8,
            core_loss=1.5,
            tensile_strength=280,
            yield_strength=180,
            elongation=25,
            hardness=85,
            elastic_modulus=210,
            thermal_conductivity=80,
            thermal_expansion=11.8,
            max_temp=500,
            min_temp=-60,
            aerospace_grade="Aerospace Grade",
            notes="高磁导率、低矫顽力，直流电磁阀铁芯首选"
        ))
        
        # 6. 硅钢片（低铁损）
        self.add_material(MaterialProperty(
            name="35WW300无取向硅钢",
            category=MaterialCategory.MAGNETIC,
            standard="GB/T 2521-2016",
            density=7.65,
            melting_point=1500,
            permeability=2000,
            saturation_flux=1.89,
            coercivity=50,
            core_loss=3.0,  # W/kg @ 1.7T, 50Hz
            tensile_strength=450,
            hardness=160,
            thermal_conductivity=20,
            thermal_expansion=12.0,
            max_temp=500,
            aerospace_grade="Motor Grade",
            notes="低铁损无取向硅钢，交流电磁阀铁芯"
        ))
        
        # 7. 软磁铁氧体
        self.add_material(MaterialProperty(
            name="MnZn铁氧体R2K",
            category=MaterialCategory.MAGNETIC,
            standard="SJ/T 10218-1994",
            density=4.8,
            melting_point=1390,
            permeability=2000,
            saturation_flux=0.48,
            coercivity=16,
            core_loss=8.0,  # 高频下低损耗
            thermal_conductivity=4,
            thermal_expansion=10.0,
            max_temp=120,
            min_temp=-40,
            aerospace_grade="High Freq Grade",
            notes="高频电磁阀专用，100kHz以上应用"
        ))
        
        # 8. 非晶纳米晶合金
        self.add_material(MaterialProperty(
            name="铁基纳米晶1K107",
            category=MaterialCategory.MAGNETIC,
            standard="GB/T 31952-2015",
            density=7.3,
            melting_point=1400,
            permeability=50000,  # 超高磁导率
            saturation_flux=1.25,
            coercivity=1.2,  # 极低
            core_loss=0.2,  # 极低铁损
            thermal_conductivity=8,
            thermal_expansion=8.0,
            max_temp=120,
            aerospace_grade="Advanced Grade",
            notes="第四代软磁材料，高频高效电磁阀"
        ))
        
        # ==================== 绝缘材料 ====================
        
        # 9. 聚酰亚胺薄膜
        self.add_material(MaterialProperty(
            name="聚酰亚胺薄膜Kapton",
            category=MaterialCategory.INSULATION,
            standard="GJB 975-1990 / AMS 3690",
            density=1.42,
            melting_point=500,  # 分解温度
            thermal_conductivity=0.12,
            thermal_expansion=20,
            max_temp=400,
            min_temp=-269,
            corrosion_resistance="优良",
            radiation_resistance="优良",
            aerospace_grade="Space Grade",
            mil_spec="MIL-P-46174",
            notes="航天级绝缘材料，耐辐射，深冷环境适用"
        ))
        
        # 10. 航空级漆包线
        self.add_material(MaterialProperty(
            name="聚酯亚胺漆包线QZY",
            category=MaterialCategory.INSULATION,
            standard="GB/T 6109.11-2008",
            density=1.35,
            melting_point=300,  # 绝缘层分解温度
            thermal_conductivity=0.15,
            thermal_expansion=25,
            max_temp=180,  # F级绝缘
            min_temp=-60,
            corrosion_resistance="良好",
            aerospace_grade="Class F (155°C)",
            notes="F级绝缘，航空电机电磁阀通用"
        ))
        
        # 11. 聚芳酰胺纸
        self.add_material(MaterialProperty(
            name="Nomex芳纶纸",
            category=MaterialCategory.INSULATION,
            standard="AMS 3691",
            density=0.96,
            melting_point=400,  # 分解温度
            thermal_conductivity=0.05,
            thermal_expansion=15,
            max_temp=220,
            min_temp=-196,
            corrosion_resistance="优良",
            radiation_resistance="良好",
            aerospace_grade="H Class (180°C)",
            notes="H级绝缘，槽绝缘、相间绝缘"
        ))
        
        # ==================== 结构材料 ====================
        
        # 12. 航空铝合金
        self.add_material(MaterialProperty(
            name="2A12硬铝合金",
            category=MaterialCategory.STRUCTURAL,
            standard="GB/T 3190-2008 / AMS 4035",
            density=2.78,
            melting_point=660,
            tensile_strength=420,
            yield_strength=275,
            elongation=12,
            hardness=120,
            elastic_modulus=70,
            thermal_conductivity=130,
            thermal_expansion=23.6,
            max_temp=150,
            min_temp=-196,
            corrosion_resistance="中等",
            weldability="良好",
            machinability="优良",
            aerospace_grade="Aerospace Grade",
            notes="阀体、端盖结构件，轻量化设计"
        ))
        
        # 13. 航空不锈钢
        self.add_material(MaterialProperty(
            name="1Cr18Ni9Ti不锈钢",
            category=MaterialCategory.STRUCTURAL,
            standard="GJB 2294-1995",
            density=7.93,
            melting_point=1400,
            tensile_strength=520,
            yield_strength=205,
            elongation=40,
            hardness=187,  # HB
            elastic_modulus=193,
            thermal_conductivity=16.3,
            thermal_expansion=17.2,
            max_temp=800,
            min_temp=-253,
            corrosion_resistance="优良",
            weldability="良好",
            machinability="中等",
            aerospace_grade="Aerospace Grade",
            notes="高温高压电磁阀阀体，耐腐蚀"
        ))
        
        # 14. 钛合金
        self.add_material(MaterialProperty(
            name="TC4钛合金",
            category=MaterialCategory.STRUCTURAL,
            standard="GJB 2218-1994 / AMS 4911",
            density=4.43,
            melting_point=1660,
            tensile_strength=950,
            yield_strength=880,
            elongation=10,
            hardness=36,  # HRC
            elastic_modulus=110,
            thermal_conductivity=7.3,
            thermal_expansion=8.6,
            max_temp=350,
            min_temp=-196,
            corrosion_resistance="极佳",
            weldability="良好",
            machinability="困难",
            aerospace_grade="Space Grade",
            notes="航天级阀体，高比强度，耐腐蚀"
        ))
        
        # ==================== 密封材料 ====================
        
        # 15. 氟橡胶
        self.add_material(MaterialProperty(
            name="氟橡胶Viton",
            category=MaterialCategory.SEALING,
            standard="AMS 7280",
            density=1.85,
            melting_point=250,  # 分解温度
            thermal_conductivity=0.25,
            thermal_expansion=180,
            max_temp=250,
            min_temp=-20,
            corrosion_resistance="极佳",
            aerospace_grade="Aerospace Grade",
            notes="耐高温燃油、液压油，主密封材料"
        ))
        
        # 16. 聚四氟乙烯
        self.add_material(MaterialProperty(
            name="聚四氟乙烯PTFE",
            category=MaterialCategory.SEALING,
            standard="GB/T 7136-2008",
            density=2.2,
            melting_point=327,  # 熔点
            thermal_conductivity=0.25,
            thermal_expansion=100,
            max_temp=260,
            min_temp=-200,
            corrosion_resistance="极佳",
            aerospace_grade="Chemical Grade",
            notes="化学惰性，静密封、导向环"
        ))
        
        # 17. 航空硅橡胶
        self.add_material(MaterialProperty(
            name="硅橡胶Silastic",
            category=MaterialCategory.SEALING,
            standard="AMS 3303",
            density=1.15,
            melting_point=250,  # 分解温度
            thermal_conductivity=0.2,
            thermal_expansion=250,
            max_temp=250,
            min_temp=-65,
            corrosion_resistance="良好",
            radiation_resistance="良好",
            aerospace_grade="Aerospace Grade",
            notes="宽温域密封，O型圈"
        ))
        
        # ==================== 弹性材料 ====================
        
        # 18. 不锈钢弹簧丝
        self.add_material(MaterialProperty(
            name="1Cr18Ni9弹簧丝",
            category=MaterialCategory.SPRING,
            standard="GB/T 24588-2009",
            density=7.93,
            melting_point=1400,
            tensile_strength=1600,
            yield_strength=1200,
            elongation=8,
            hardness=45,  # HRC
            elastic_modulus=193,
            thermal_conductivity=16.3,
            thermal_expansion=17.2,
            max_temp=300,
            min_temp=-200,
            corrosion_resistance="优良",
            aerospace_grade="Aerospace Grade",
            notes="复位弹簧，抗疲劳"
        ))
        
        # 19. 铍铜合金
        self.add_material(MaterialProperty(
            name="铍铜C17200",
            category=MaterialCategory.SPRING,
            standard="AMS 4535",
            density=8.25,
            melting_point=865,
            tensile_strength=1300,
            yield_strength=1100,
            elongation=5,
            hardness=40,  # HRC
            elastic_modulus=128,
            thermal_conductivity=105,
            thermal_expansion=17.0,
            max_temp=300,
            min_temp=-200,
            corrosion_resistance="优良",
            aerospace_grade="High Perf Grade",
            notes="高弹性极限，精密弹簧"
        ))
        
        # ==================== 涂层材料 ====================
        
        # 20. 等离子喷涂陶瓷
        self.add_material(MaterialProperty(
            name="氧化铝陶瓷涂层",
            category=MaterialCategory.COATING,
            standard="AMS 2434",
            density=3.97,
            melting_point=2050,  # 氧化铝熔点
            thermal_conductivity=25,
            thermal_expansion=8.0,
            max_temp=1000,
            corrosion_resistance="极佳",
            aerospace_grade="Thermal Barrier",
            notes="热障涂层，耐磨耐腐蚀"
        ))
        
        # 21. 镀硬铬
        self.add_material(MaterialProperty(
            name="工程硬铬镀层",
            category=MaterialCategory.COATING,
            standard="AMS 2406",
            density=7.19,
            melting_point=1900,  # 铬熔点
            thermal_conductivity=67,
            thermal_expansion=6.0,
            max_temp=400,
            corrosion_resistance="优良",
            aerospace_grade="Wear Resistant",
            notes="阀芯表面硬化，耐磨"
        ))
    
    def add_material(self, material: MaterialProperty):
        """添加材料到数据库"""
        self.materials[material.name] = material
    
    def get_material(self, name: str) -> Optional[MaterialProperty]:
        """获取材料信息"""
        return self.materials.get(name)
    
    def search_by_category(self, category: MaterialCategory) -> List[MaterialProperty]:
        """按类别搜索材料"""
        return [m for m in self.materials.values() if m.category == category]
    
    def search_by_property(self, 
                          min_temp: Optional[float] = None,
                          max_temp: Optional[float] = None,
                          min_strength: Optional[float] = None,
                          corrosion_resistance: Optional[str] = None) -> List[MaterialProperty]:
        """按属性筛选材料"""
        results = []
        for m in self.materials.values():
            if min_temp is not None and (m.min_temp is None or m.min_temp < min_temp):
                continue
            if max_temp is not None and (m.max_temp is None or m.max_temp < max_temp):
                continue
            if min_strength is not None and (m.tensile_strength is None or m.tensile_strength < min_strength):
                continue
            if corrosion_resistance is not None and m.corrosion_resistance != corrosion_resistance:
                continue
            results.append(m)
        return results
    
    def get_conductor_for_awg(self, awg: int) -> Dict:
        """根据AWG线规获取导线参数"""
        # AWG标准线规表
        awg_table = {
            20: {"diameter_mm": 0.812, "area_mm2": 0.518, "resistance_ohm_per_km": 33.3},
            21: {"diameter_mm": 0.723, "area_mm2": 0.410, "resistance_ohm_per_km": 42.0},
            22: {"diameter_mm": 0.644, "area_mm2": 0.326, "resistance_ohm_per_km": 52.9},
            23: {"diameter_mm": 0.573, "area_mm2": 0.258, "resistance_ohm_per_km": 66.7},
            24: {"diameter_mm": 0.511, "area_mm2": 0.205, "resistance_ohm_per_km": 84.2},
            25: {"diameter_mm": 0.455, "area_mm2": 0.163, "resistance_ohm_per_km": 106.0},
            26: {"diameter_mm": 0.405, "area_mm2": 0.129, "resistance_ohm_per_km": 134.0},
            27: {"diameter_mm": 0.361, "area_mm2": 0.102, "resistance_ohm_per_km": 169.0},
            28: {"diameter_mm": 0.321, "area_mm2": 0.081, "resistance_ohm_per_km": 213.0},
            29: {"diameter_mm": 0.286, "area_mm2": 0.064, "resistance_ohm_per_km": 268.0},
            30: {"diameter_mm": 0.255, "area_mm2": 0.051, "resistance_ohm_per_km": 339.0},
        }
        
        if awg not in awg_table:
            return {"error": f"AWG {awg} 不在标准线规表中"}
        
        return {
            "awg": awg,
            **awg_table[awg],
            "recommended_materials": [
                "T2纯铜（航空航天级）",
                "镀银铜线TRAg",
                "B10铜镍合金"
            ]
        }
    
    def calculate_wire_properties(self, 
                                  material_name: str,
                                  awg: int,
                                  turns: int,
                                  mean_diameter: float) -> Dict:
        """计算绕组性能参数
        
        Args:
            material_name: 材料名称
            awg: 线规号
            turns: 匝数
            mean_diameter: 平均直径 (mm)
        
        Returns:
            包含电阻、质量、热容等参数的字典
        """
        material = self.get_material(material_name)
        if not material:
            return {"error": f"材料 {material_name} 不存在"}
        
        wire_spec = self.get_conductor_for_awg(awg)
        if "error" in wire_spec:
            return wire_spec
        
        # 计算导线长度
        circumference = np.pi * mean_diameter / 1000  # 转换为米
        total_length = turns * circumference
        
        # 计算电阻
        resistance_per_m = wire_spec["resistance_ohm_per_km"] / 1000
        total_resistance = total_length * resistance_per_m
        
        # 计算质量
        cross_section_area = wire_spec["area_mm2"] * 1e-6  # 转换为m²
        volume = total_length * cross_section_area
        mass = volume * material.density * 1000  # 转换为kg
        
        # 计算热容
        if material.specific_heat:
            thermal_capacity = mass * material.specific_heat
        else:
            thermal_capacity = None
        
        return {
            "material": material_name,
            "awg": awg,
            "turns": turns,
            "mean_diameter_mm": mean_diameter,
            "total_length_m": round(total_length, 2),
            "total_resistance_ohm": round(total_resistance, 3),
            "mass_kg": round(mass, 4),
            "thermal_capacity_J_per_K": round(thermal_capacity, 1) if thermal_capacity else None,
            "max_operating_temp": material.max_temp,
            "conductivity_percent_IACS": material.conductivity
        }
    
    def recommend_material(self, 
                          application: str,
                          requirements: Dict) -> List[Dict]:
        """材料推荐引擎
        
        Args:
            application: 应用场景 (solenoid_valve, high_temp, cryogenic, marine, etc.)
            requirements: 性能要求字典
        
        Returns:
            推荐材料列表（按匹配度排序）
        """
        recommendations = []
        
        # 定义应用场景的材料需求
        scenario_requirements = {
            "solenoid_valve": {
                "conductor": {"min_conductivity": 90, "max_temp": 180},
                "magnetic": {"min_permeability": 2000, "max_core_loss": 5},
                "insulation": {"max_temp": 180}
            },
            "high_temp": {
                "conductor": {"max_temp": 500},
                "magnetic": {"max_temp": 500},
                "insulation": {"max_temp": 400}
            },
            "cryogenic": {
                "min_temp": -196,
                "required": ["低温韧性", "尺寸稳定性"]
            },
            "marine": {
                "corrosion_resistance": "极佳",
                "required": ["耐海水腐蚀"]
            },
            "space": {
                "radiation_resistance": "优良",
                "min_temp": -100,
                "max_temp": 150
            }
        }
        
        # 获取场景需求
        scenario = scenario_requirements.get(application, {})
        
        # 评估每种材料
        for material in self.materials.values():
            score = 0
            matched_criteria = []
            
            # 检查温度要求
            if "min_temp" in requirements:
                if material.min_temp and material.min_temp <= requirements["min_temp"]:
                    score += 20
                    matched_criteria.append(f"低温性能: {material.min_temp}°C")
            
            if "max_temp" in requirements:
                if material.max_temp and material.max_temp >= requirements["max_temp"]:
                    score += 20
                    matched_criteria.append(f"高温性能: {material.max_temp}°C")
            
            # 检查强度要求
            if "min_strength" in requirements:
                if material.tensile_strength and material.tensile_strength >= requirements["min_strength"]:
                    score += 15
                    matched_criteria.append(f"抗拉强度: {material.tensile_strength}MPa")
            
            # 检查耐腐蚀性
            if requirements.get("corrosion_resistance") == "极佳":
                if material.corrosion_resistance == "极佳":
                    score += 25
                    matched_criteria.append("耐腐蚀性: 极佳")
            
            # 检查导电性
            if "min_conductivity" in requirements:
                if material.conductivity and material.conductivity >= requirements["min_conductivity"]:
                    score += 20
                    matched_criteria.append(f"电导率: {material.conductivity}%IACS")
            
            # 检查磁性
            if "min_permeability" in requirements:
                if material.permeability and material.permeability >= requirements["min_permeability"]:
                    score += 20
                    matched_criteria.append(f"磁导率: {material.permeability}")
            
            # 航空航天认证加分
            if material.aerospace_grade:
                score += 10
                matched_criteria.append(f"认证等级: {material.aerospace_grade}")
            
            if score > 0:
                recommendations.append({
                    "material": material.name,
                    "category": material.category.value,
                    "score": score,
                    "matched_criteria": matched_criteria,
                    "standard": material.standard
                })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:10]  # 返回前10个推荐
    
    def export_to_json(self) -> str:
        """导出数据库为JSON格式"""
        data = {}
        for name, material in self.materials.items():
            material_dict = asdict(material)
            material_dict["category"] = material.category.value
            data[name] = material_dict
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def get_statistics(self) -> Dict:
        """获取数据库统计信息"""
        stats = {
            "total_materials": len(self.materials),
            "by_category": {},
            "with_aerospace_grade": 0,
            "with_mil_spec": 0
        }
        
        for category in MaterialCategory:
            count = len(self.search_by_category(category))
            stats["by_category"][category.value] = count
        
        for material in self.materials.values():
            if material.aerospace_grade:
                stats["with_aerospace_grade"] += 1
            if material.mil_spec:
                stats["with_mil_spec"] += 1
        
        return stats


# 创建全局数据库实例
db = AerospaceMaterialsDatabase()


# API接口函数
def get_all_materials():
    """获取所有材料列表"""
    return [{"name": m.name, "category": m.category.value, "standard": m.standard} 
            for m in db.materials.values()]


def get_material_detail(name: str):
    """获取材料详细信息"""
    material = db.get_material(name)
    if not material:
        return None
    
    result = asdict(material)
    result["category"] = material.category.value
    return result


def search_materials(category: str = None, 
                    min_temp: float = None,
                    max_temp: float = None):
    """搜索材料"""
    if category:
        try:
            cat = MaterialCategory(category)
            materials = db.search_by_category(cat)
        except ValueError:
            materials = []
    else:
        materials = list(db.materials.values())
    
    # 应用温度筛选
    if min_temp is not None:
        materials = [m for m in materials if m.min_temp and m.min_temp <= min_temp]
    if max_temp is not None:
        materials = [m for m in materials if m.max_temp and m.max_temp >= max_temp]
    
    return [{"name": m.name, "category": m.category.value, "standard": m.standard}
            for m in materials]


if __name__ == "__main__":
    # 测试数据库
    print("=" * 60)
    print("航空航天电磁阀材料数据库")
    print("=" * 60)
    
    stats = db.get_statistics()
    print(f"\n数据库统计:")
    print(f"  总材料数: {stats['total_materials']}")
    print(f"  航空航天认证材料: {stats['with_aerospace_grade']}")
    print(f"  军标材料: {stats['with_mil_spec']}")
    print(f"\n按类别统计:")
    for cat, count in stats['by_category'].items():
        print(f"  {cat}: {count}种")
    
    # 测试材料推荐
    print("\n" + "=" * 60)
    print("材料推荐测试 - 电磁阀应用")
    print("=" * 60)
    
    recommendations = db.recommend_material("solenoid_valve", {
        "max_temp": 180,
        "min_conductivity": 90
    })
    
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"\n{i}. {rec['material']}")
        print(f"   类别: {rec['category']}")
        print(f"   匹配度: {rec['score']}分")
        print(f"   标准: {rec['standard']}")
