# -*- coding: utf-8 -*-
"""
Aerospace Valve Performance Metrics Database
Systematic, authoritative, comprehensive performance specification library
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict
import json


# ============================================================
# 1. Metric Definitions - Each metric has full metadata
# ============================================================

@dataclass
class MetricDefinition:
    id: str
    name_cn: str
    name_en: str
    symbol: str
    unit: str
    category: str          # pressure/flow/leakage/dynamic/thermal/mechanical/reliability/mass
    definition: str
    test_method: str
    standard_ref: str
    importance: str        # critical/major/secondary
    direction: str         # higher_better/lower_better/range/no_direction


METRICS = [
    # ---- Pressure Metrics ----
    MetricDefinition("P_design", "设计压力", "Design Pressure", "P_d", "MPa",
        "pressure", "阀门在设计工况下长期安全运行的最大压力", "按GB/T 12224或MIL-V-25940进行压力试验验证",
        "GB/T 12224; MIL-V-25940; ECSS-Q-ST-70-38C", "critical", "higher_better"),
    MetricDefinition("P_test", "试验压力", "Test Pressure", "P_t", "MPa",
        "pressure", "验证阀门强度和密封性的压力试验值，通常为设计压力的1.5倍(液压试验)或1.25倍(气压试验)",
        "液压/气压试验，保压时间≥3min(液)或≥2min(气)", "GB/T 12224; ASME B16.34; GJB 3481", "critical", "higher_better"),
    MetricDefinition("P_burst", "爆破压力", "Burst Pressure", "P_b", "MPa",
        "pressure", "阀门壳体发生破裂的最小压力，通常要求≥4倍设计压力", "液压爆破试验，按GJB 3481或MIL-STD-1522A",
        "GJB 3481; MIL-STD-1522A; ECSS-Q-ST-70-38C", "critical", "higher_better"),
    MetricDefinition("P_inlet_max", "最大入口压力", "Maximum Inlet Pressure", "P_in_max", "MPa",
        "pressure", "阀门入口端允许的最高工作压力", "压力传感器+数据采集，按工况谱测量",
        "MIL-V-25940; SAE AS5780; HB 5980", "critical", "higher_better"),
    MetricDefinition("P_outlet_set", "出口设定压力", "Outlet Set Pressure", "P_out_set", "MPa",
        "pressure", "减压阀或调压阀出口端的预定输出压力", "在额定入口压力和流量下测量出口压力",
        "MIL-V-25940; HB 5980; QJ 20028", "major", "range"),
    MetricDefinition("P_differential", "工作压差", "Working Differential Pressure", "dP", "MPa",
        "pressure", "阀门入口与出口之间的压差，是驱动流动和密封设计的核心参数",
        "差压传感器同步测量", "GB/T 12224; SAE AS5780", "critical", "range"),
    MetricDefinition("P_cracking", "开启压力", "Cracking Pressure", "P_cr", "MPa",
        "pressure", "单向阀或安全阀开始产生可测量流量时的入口压力", "以0.1L/min流量对应的入口压力定义",
        "MIL-V-25639; SAE AS5780; GJB 3481", "major", "lower_better"),

    # ---- Flow Metrics ----
    MetricDefinition("Cv", "流量系数", "Flow Coefficient Cv", "C_v", "USGPM",
        "flow", "60F水在1psi压差下通过阀门的流量(US gal/min)，国际通用流通能力指标",
        "按ISA-75.01.01或GB/T 30843测量，取额定行程下的Cv值",
        "ISA-75.01.01; GB/T 30843; IEC 60534-2-1", "critical", "higher_better"),
    MetricDefinition("Kv", "流量系数(公制)", "Flow Coefficient Kv", "K_v", "m3/h",
        "flow", "20C水在0.1MPa压差下通过阀门的流量(m3/h)，Kv≈0.865×Cv",
        "按DIN EN 60534-2-1测量", "DIN EN 60534-2-1; GB/T 30843", "major", "higher_better"),
    MetricDefinition("Q_rated", "额定流量", "Rated Flow", "Q_r", "L/min",
        "flow", "在额定工况(额定压力、额定压差)下阀门允许通过的最大稳定流量",
        "流量计+压力传感器，稳态工况下测量", "MIL-V-25940; HB 5980; QJ 20028", "critical", "higher_better"),
    MetricDefinition("Q_max", "最大流量", "Maximum Flow", "Q_max", "L/min",
        "flow", "阀门在最大开度下能通过的上限流量(此时压力损失显著增大)", "全开工况下测量",
        "SAE AS5780; GJB 3481", "major", "higher_better"),
    MetricDefinition("dP_loss", "压力损失", "Pressure Loss", "dP_loss", "MPa",
        "flow", "额定流量下流体通过阀门产生的不可恢复压力降", "差压法，在额定流量下测量进出口压差",
        "ISA-75.01.01; IEC 60534-2-1; GB/T 30843", "major", "lower_better"),
    MetricDefinition("C_choked", "临界流系数", "Choked Flow Coefficient", "C_f", "-",
        "flow", "可压缩流体达到临界(阻塞)流状态的流量修正系数，取决于比热比和压力比",
        "按ISA-75.01.01计算或实验测定", "ISA-75.01.01; IEC 60534-2-3", "secondary", "no_direction"),
    MetricDefinition("Re_flow", "流动雷诺数", "Flow Reynolds Number", "Re", "-",
        "flow", "表征阀门内流动状态(层流/过渡/湍流)的无量纲数", "Re=ρvD/μ，由实测参数计算",
        "ISO 5167; IEC 60534-2-1", "secondary", "no_direction"),

    # ---- Leakage Metrics ----
    MetricDefinition("L_class", "泄漏等级", "Leakage Class", "Class", "-",
        "leakage", "按ANSI/FCI 70-2(IEC 60534-4)标准定义的阀门密封等级(I~VI级)",
        "关闭阀门后在额定压差下测量泄漏量，对照标准分级",
        "ANSI/FCI 70-2; IEC 60534-4; GB/T 30843", "critical", "lower_better"),
    MetricDefinition("L_internal", "内泄漏量", "Internal Leakage", "L_i", "mL/min",
        "leakage", "阀门关闭状态下流体从入口向出口的泄漏量", "额定压差下，关闭阀门测量出口端泄漏",
        "MIL-V-25940; ANSI/FCI 70-2; GJB 3481", "critical", "lower_better"),
    MetricDefinition("L_external", "外泄漏量", "External Leakage", "L_e", "mL/min",
        "leakage", "流体从阀门壳体、密封面、连接处向环境的泄漏量", "氦质谱检漏(1E-6 Pa·m3/s级)或气泡法",
        "MIL-V-25940; GJB 3481; ECSS-Q-ST-70-38C", "critical", "lower_better"),
    MetricDefinition("L_seat", "阀座泄漏率", "Seat Leakage Rate", "L_s", "bubble/min",
        "leakage", "阀座密封面在规定压差下的泄漏指标，气泡法测定", "水下气泡法或流量计法",
        "ANSI/FCI 70-2; MSS SP-61; GJB 3481", "major", "lower_better"),

    # ---- Dynamic/Response Metrics ----
    MetricDefinition("t_open", "开启响应时间", "Opening Response Time", "t_on", "ms",
        "dynamic", "从驱动信号发出到阀门达到额定开度(通常90%行程)的时间",
        "电信号触发+位移传感器测量，含线圈激励、衔铁运动、阀芯运动全程",
        "MIL-V-25940; SAE AS5780; QJ 20028", "critical", "lower_better"),
    MetricDefinition("t_close", "关闭响应时间", "Closing Response Time", "t_off", "ms",
        "dynamic", "从断电/关阀信号发出到阀门完全关闭(泄漏量达到规定值)的时间",
        "电信号切断+泄漏检测", "MIL-V-25940; SAE AS5780; QJ 20028", "critical", "lower_better"),
    MetricDefinition("t_settle", "稳定时间", "Settling Time", "t_s", "ms",
        "dynamic", "阀门动作后出口压力进入并保持在稳定带宽内的时间",
        "压力传感器+高速采集(≥1kHz)", "SAE AS5780; HB 5980", "major", "lower_better"),
    MetricDefinition("f_natural", "固有频率", "Natural Frequency", "f_n", "Hz",
        "dynamic", "阀门运动组件(阀芯+弹簧系统)的无阻尼固有振动频率",
        "锤击法或频响函数法测量", "GJB 3481; MIL-STD-810", "major", "higher_better"),
    MetricDefinition("zeta", "阻尼比", "Damping Ratio", "zeta", "-",
        "dynamic", "阀门运动系统阻尼与临界阻尼之比，影响响应振荡特性",
        "阶跃响应衰减比法或半功率带宽法", "GJB 3481; HB 5980", "secondary", "range"),
    MetricDefinition("duty_cycle", "工作制", "Duty Cycle", "DC", "%",
        "dynamic", "电磁阀通电时间占周期总时间的百分比(ED%)",
        "持续通电至热稳定后测量线圈温升", "IEC 60034-1; SAE AS5780", "major", "range"),

    # ---- Thermal Metrics ----
    MetricDefinition("T_operating", "工作温度范围", "Operating Temperature Range", "T_op", "K",
        "thermal", "阀门能正常工作的流体和环境温度范围(低温限~高温限)",
        "高低温试验箱，按MIL-STD-810或ECSS方法", "MIL-STD-810; ECSS-Q-ST-70-38C; GJB 3481", "critical", "range"),
    MetricDefinition("T_storage", "储存温度范围", "Storage Temperature Range", "T_st", "K",
        "thermal", "阀门在不工作状态下可安全存放的温度范围", "高低温储存试验",
        "MIL-STD-810; GJB 150; GJB 3481", "major", "range"),
    MetricDefinition("T_coil_max", "线圈最高温度", "Maximum Coil Temperature", "T_c_max", "K",
        "thermal", "电磁阀线圈在最大工作制和最高环境温度下达到的稳态温度",
        "热电偶或红外测温，热稳态下测量", "SAE AS5780; IEC 60034-1; MIL-V-25940", "major", "lower_better"),
    MetricDefinition("dT_thermal_shock", "热冲击耐受", "Thermal Shock Resistance", "dT_shock", "K/s",
        "thermal", "阀门能承受的快速温度变化速率而不失效", "快速切换高低温介质",
        "ECSS-Q-ST-70-38C; GJB 3481", "secondary", "higher_better"),

    # ---- Mechanical/Vibration Metrics ----
    MetricDefinition("vibe_random", "随机振动耐受", "Random Vibration Resistance", "G_rms", "g_rms",
        "mechanical", "阀门在随机振动环境(发射/飞行)中正常工作的最大加速度谱密度",
        "按MIL-STD-810G Method 514.7或ECSS-E-ST-32-08C试验",
        "MIL-STD-810G; ECSS-E-ST-32-08C; GJB 150.16", "critical", "higher_better"),
    MetricDefinition("vibe_sine", "正弦振动耐受", "Sine Vibration Resistance", "G_sin", "g",
        "mechanical", "阀门在正弦扫频振动中不发生共振破坏的加速度量级",
        "正弦扫频试验，5-2000Hz，识别共振点", "MIL-STD-810G; GJB 150.16", "major", "higher_better"),
    MetricDefinition("shock_mech", "机械冲击耐受", "Mechanical Shock Resistance", "G_shock", "g",
        "mechanical", "阀门能承受的半正弦/后峰锯齿脉冲冲击加速度峰值",
        "按MIL-STD-810G Method 516.7或GJB 150.18试验",
        "MIL-STD-810G; GJB 150.18; ECSS-E-ST-32-09C", "critical", "higher_better"),
    MetricDefinition("shock_pyro", "爆炸冲击耐受", "Pyrotechnic Shock Resistance", "G_pyro", "g",
        "mechanical", "阀门在火工品引爆(级间分离等)近场冲击下的耐受能力",
        "近场爆炸冲击试验，SRS分析法", "ECSS-E-ST-32-09C; NASA-STD-7003", "major", "higher_better"),
    MetricDefinition("F_actuation", "驱动力", "Actuation Force", "F_act", "N",
        "mechanical", "驱动阀门完成全行程所需的最小力(电磁力/气动力/手动力)",
        "力传感器+位移传感器同步测量", "MIL-V-25940; SAE AS5780", "major", "higher_better"),
    MetricDefinition("F_flow", "流动力", "Flow Force", "F_flow", "N",
        "mechanical", "流体通过阀口时对阀芯产生的轴向力，影响调节稳定性",
        "CFD仿真+力传感器验证", "SAE AS5780; HB 5980", "major", "lower_better"),
    MetricDefinition("stroke", "额定行程", "Rated Stroke", "L_s", "mm",
        "mechanical", "阀芯从全关到全开的位移量", "位移传感器直接测量",
        "MIL-V-25940; IEC 60534-3", "major", "no_direction"),

    # ---- Reliability/Life Metrics ----
    MetricDefinition("N_cycles", "工作寿命", "Operating Life", "N", "cycles",
        "reliability", "阀门在额定工况下能正常完成开-关循环的次数",
        "寿命试验台自动循环，监测泄漏和响应时间变化",
        "MIL-V-25940; SAE AS5780; QJ 20028", "critical", "higher_better"),
    MetricDefinition("R_target", "可靠性目标", "Reliability Target", "R", "-",
        "reliability", "阀门在规定条件和时间内完成规定功能的概率",
        "由FMEA/FMECA分析和可靠性仿真确定", "ECSS-Q-ST-30C; GJB 899; MIL-HDBK-217", "critical", "higher_better"),
    MetricDefinition("MTBF", "平均故障间隔", "Mean Time Between Failures", "MTBF", "h",
        "reliability", "相邻两次故障间的平均工作时间", "由运行数据统计或MIL-HDBK-217预计",
        "MIL-HDBK-217; GJB 899; ECSS-Q-ST-30C", "major", "higher_better"),
    MetricDefinition("beta_reliability", "可靠性指标", "Reliability Index", "beta", "-",
        "reliability", "基于极限状态函数的Hasofer-Lind可靠性指标，beta>=3.09对应R>=0.999",
        "一阶二次矩法或蒙特卡洛仿真", "ECSS-Q-ST-30C; GJB 899", "major", "higher_better"),
    MetricDefinition("n_safety", "安全系数", "Safety Factor", "n_s", "-",
        "reliability", "材料强度与最大工作应力的比值，航空航天阀门通常要求n>=1.5",
        "由设计计算确定，关键承压件按GJB 3481校核", "GJB 3481; MIL-STD-1522A; ECSS-Q-ST-70-38C", "critical", "higher_better"),
    MetricDefinition("FMEA_class", "失效模式等级", "Failure Mode Class", "SIL", "-",
        "reliability", "基于FMEA/FMECA分析的最严重失效模式严酷度等级(I~IV)",
        "按GJB 1391或ECSS-Q-ST-30C进行FMEA", "GJB 1391; ECSS-Q-ST-30C; MIL-STD-1629A", "major", "lower_better"),

    # ---- Mass/Envelope Metrics ----
    MetricDefinition("m_valve", "阀门质量", "Valve Mass", "m", "kg",
        "mass", "阀门(含驱动机构)的总质量", "称重法",
        "MIL-V-25940; SAE AS5780; HB 5980", "critical", "lower_better"),
    MetricDefinition("V_envelope", "包络体积", "Envelope Volume", "V_env", "cm3",
        "mass", "阀门安装所需的最小包容长方体体积", "三维模型测量",
        "MIL-V-25940; HB 5980", "major", "lower_better"),
    MetricDefinition("D_interface", "接口尺寸", "Interface Size", "DN", "mm",
        "mass", "进出口连接接口的公称尺寸(法兰/螺纹/焊接)", "图纸标注",
        "GB/T 12224; ASME B16.5; MIL-V-25940", "major", "no_direction"),

    # ---- Regulation Accuracy Metrics ----
    MetricDefinition("acc_regulation", "调压精度", "Regulation Accuracy", "dP_acc", "%",
        "pressure", "减压阀出口压力偏离设定值的最大允许百分比", "在流量变化范围内测量出口压力波动",
        "MIL-V-25940; SAE AS5780; QJ 20028", "critical", "lower_better"),
    MetricDefinition("acc_repeatability", "重复性精度", "Repeatability", "dP_rep", "%",
        "pressure", "多次操作同一工况下出口压力的一致性", "重复试验统计分析",
        "SAE AS5780; IEC 60534-2", "major", "lower_better"),
    MetricDefinition("acc_hysteresis", "迟滞误差", "Hysteresis Error", "dP_hys", "%",
        "pressure", "正向行程与反向行程在同一位置的压力差，反映摩擦和弹性迟滞",
        "正反行程慢速扫描测量", "IEC 60534-2; SAE AS5780", "major", "lower_better"),
    MetricDefinition("band_stability", "稳定带宽", "Stability Band", "dP_sb", "MPa",
        "pressure", "减压阀在稳定工况下出口压力的允许波动范围", "稳态工况下长时间监测(≥30min)",
        "SAE AS5780; QJ 20028; HB 5980", "major", "lower_better"),
]


# ============================================================
# 2. Valve Type Specifications - Reference values by type
# ============================================================

VALVE_TYPES = {
    "solenoid_direct": {
        "name_cn": "直动式电磁阀",
        "name_en": "Direct-Acting Solenoid Valve",
        "description": "电磁力直接驱动阀芯，响应快、结构简单，适用于小口径和低压差",
        "applications": ["航空液压", "燃油控制", "环控系统", "推进剂控制"],
        "typical_ranges": {
            "P_design": (0.5, 35), "P_inlet_max": (0.5, 42),
            "Cv": (0.01, 5.0), "Q_rated": (1, 200),
            "t_open": (5, 50), "t_close": (5, 30),
            "L_class": ["IV", "V", "VI"],
            "T_operating": (220, 423), "vibe_random": (5, 30),
            "shock_mech": (30, 100), "N_cycles": (1e4, 1e7),
            "m_valve": (0.05, 3.0), "DN": (3, 25),
            "duty_cycle": (10, 100), "acc_regulation": (0.5, 5.0),
        },
        "key_standards": ["MIL-V-25940", "SAE AS5780", "GJB 3481", "QJ 20028"],
        "critical_metrics": ["t_open", "L_internal", "N_cycles", "vibe_random", "T_operating"],
    },
    "solenoid_pilot": {
        "name_cn": "先导式电磁阀",
        "name_en": "Pilot-Operated Solenoid Valve",
        "description": "先导阀控制主阀芯，适合大口径和大流量，需最低驱动压差",
        "applications": ["火箭推进剂", "卫星推进", "地面供气", "大型液压"],
        "typical_ranges": {
            "P_design": (0.5, 42), "P_inlet_max": (0.5, 50),
            "Cv": (0.5, 50), "Q_rated": (50, 2000),
            "t_open": (20, 200), "t_close": (20, 150),
            "L_class": ["IV", "V", "VI"],
            "T_operating": (220, 423), "vibe_random": (5, 25),
            "shock_mech": (20, 80), "N_cycles": (1e4, 5e6),
            "m_valve": (0.3, 8.0), "DN": (10, 50),
            "dP_differential": (0.05, 0.5), "duty_cycle": (10, 100),
        },
        "key_standards": ["MIL-V-25940", "SAE AS5780", "GJB 3481", "ECSS-Q-ST-70-38C"],
        "critical_metrics": ["t_open", "dP_differential", "L_internal", "N_cycles", "Q_rated"],
    },
    "pressure_reducing": {
        "name_cn": "减压阀",
        "name_en": "Pressure Reducing Valve (Regulator)",
        "description": "将高压入口自动调节至稳定的低压出口，核心调压元件",
        "applications": ["火箭供箱增压", "卫星气路减压", "飞机液压", "地面测试台"],
        "typical_ranges": {
            "P_design": (0.5, 42), "P_inlet_max": (0.5, 70),
            "P_outlet_set": (0.1, 10), "acc_regulation": (0.1, 5.0),
            "Cv": (0.1, 20), "Q_rated": (10, 1000),
            "acc_hysteresis": (0.5, 5.0), "acc_repeatability": (0.1, 2.0),
            "band_stability": (0.01, 0.5),
            "L_class": ["IV", "V", "VI"],
            "T_operating": (80, 423), "vibe_random": (5, 30),
            "shock_mech": (20, 100), "N_cycles": (1e3, 1e6),
            "m_valve": (0.2, 5.0), "DN": (6, 40),
        },
        "key_standards": ["MIL-V-25940", "SAE AS5780", "QJ 20028", "HB 5980", "ECSS-Q-ST-70-38C"],
        "critical_metrics": ["acc_regulation", "band_stability", "acc_hysteresis", "L_internal", "Q_rated"],
    },
    "check_valve": {
        "name_cn": "单向阀(止回阀)",
        "name_en": "Check Valve (Non-Return Valve)",
        "description": "允许流体单向流动，防止逆流，无需外驱动",
        "applications": ["泵出口保护", "管路防逆流", "推进剂隔离", "液压回路"],
        "typical_ranges": {
            "P_design": (0.5, 42), "P_cracking": (0.005, 0.35),
            "Cv": (0.1, 30), "Q_rated": (10, 2000),
            "dP_loss": (0.01, 0.5),
            "L_class": ["IV", "V", "VI"],
            "T_operating": (80, 423), "vibe_random": (5, 30),
            "shock_mech": (20, 100), "N_cycles": (1e4, 1e7),
            "m_valve": (0.05, 3.0), "DN": (4, 50),
            "t_open": (2, 30),
        },
        "key_standards": ["MIL-V-25639", "SAE AS5780", "GJB 3481"],
        "critical_metrics": ["P_cracking", "L_internal", "dP_loss", "t_open", "N_cycles"],
    },
    "relief_safety": {
        "name_cn": "安全阀/溢流阀",
        "name_en": "Relief/Safety Valve",
        "description": "超压保护装置，当系统压力超过设定值时自动开启泄压",
        "applications": ["压力容器保护", "管路超压保护", "推进系统安全", "液压安全"],
        "typical_ranges": {
            "P_design": (0.5, 42), "P_cracking": (0.1, 40),
            "Cv": (1, 100), "Q_rated": (50, 5000),
            "t_open": (5, 50), "L_class": ["III", "IV", "V"],
            "T_operating": (80, 423), "vibe_random": (5, 25),
            "shock_mech": (20, 80), "N_cycles": (1e3, 1e5),
            "m_valve": (0.2, 10.0), "DN": (10, 80),
            "acc_regulation": (1, 10),
        },
        "key_standards": ["ISO 4126", "ASME B16.34", "GJB 3481", "API 526"],
        "critical_metrics": ["P_cracking", "Q_rated", "t_open", "L_internal", "N_cycles"],
    },
    "ball_valve": {
        "name_cn": "球阀",
        "name_en": "Ball Valve",
        "description": "球体旋转90度实现开关，流通能力大、密封性好",
        "applications": ["推进剂加注", "地面供气", "预冷回路", "液氢液氧"],
        "typical_ranges": {
            "P_design": (0.5, 42), "Cv": (5, 200),
            "Q_rated": (100, 10000), "t_open": (50, 5000),
            "L_class": ["IV", "V", "VI"],
            "T_operating": (20, 423), "vibe_random": (3, 20),
            "shock_mech": (15, 60), "N_cycles": (1e3, 1e5),
            "m_valve": (0.5, 30.0), "DN": (10, 100),
            "F_actuation": (5, 500),
        },
        "key_standards": ["MIL-V-25940", "API 6D", "GJB 3481", "ECSS-Q-ST-70-38C"],
        "critical_metrics": ["L_internal", "t_open", "Q_rated", "T_operating", "N_cycles"],
    },
    "butterfly_valve": {
        "name_cn": "蝶阀",
        "name_en": "Butterfly Valve",
        "description": "蝶板旋转实现开关/调节，结构紧凑、质量轻、适合大口径",
        "applications": ["环控风路", "进气调节", "液路切断", "地面设施"],
        "typical_ranges": {
            "P_design": (0.1, 10), "Cv": (10, 500),
            "Q_rated": (200, 20000), "t_open": (100, 10000),
            "L_class": ["III", "IV", "V"],
            "T_operating": (220, 423), "vibe_random": (3, 15),
            "shock_mech": (10, 50), "N_cycles": (1e3, 5e5),
            "m_valve": (0.3, 20.0), "DN": (25, 300),
        },
        "key_standards": ["MIL-V-25940", "API 609", "GB/T 30843"],
        "critical_metrics": ["Q_rated", "L_internal", "t_open", "N_cycles", "m_valve"],
    },
    "proportional_servo": {
        "name_cn": "比例伺服阀",
        "name_en": "Proportional/Servo Valve",
        "description": "连续调节开度实现精确流量/压力控制，高精度电液转换元件",
        "applications": ["发动机推力调节", "姿控推进", "飞行控制", "模拟测试"],
        "typical_ranges": {
            "P_design": (7, 42), "Cv": (0.05, 5),
            "Q_rated": (1, 200), "t_open": (2, 20),
            "acc_regulation": (0.1, 2.0), "acc_hysteresis": (0.1, 3.0),
            "acc_repeatability": (0.05, 1.0), "band_stability": (0.01, 0.2),
            "L_class": ["V", "VI"],
            "T_operating": (220, 423), "vibe_random": (5, 30),
            "shock_mech": (20, 80), "N_cycles": (1e5, 1e8),
            "m_valve": (0.1, 3.0), "DN": (3, 15),
            "f_natural": (50, 500),
        },
        "key_standards": ["SAE AS5780", "MIL-V-25940", "QJ 20028", "ISO 10770"],
        "critical_metrics": ["acc_regulation", "acc_hysteresis", "t_open", "f_natural", "acc_repeatability"],
    },
    "pyrotechnic": {
        "name_cn": "火工品阀门(电爆阀)",
        "name_en": "Pyrotechnic Valve (Squib Valve)",
        "description": "一次性作动阀门，通过火工品爆炸驱动，响应极快、密封极好",
        "applications": ["卫星推进隔离", "火箭级间分离", "安全自毁", "应急切断"],
        "typical_ranges": {
            "P_design": (0.5, 42), "t_open": (1, 10),
            "L_class": ["VI"], "T_operating": (220, 423),
            "N_cycles": 1, "m_valve": (0.05, 1.0),
            "DN": (3, 25), "shock_pyro": (500, 10000),
            "vibe_random": (5, 30), "shock_mech": (50, 200),
            "Q_rated": (5, 500), "Cv": (0.1, 10),
        },
        "key_standards": ["ECSS-E-ST-32-09C", "NASA-STD-7003", "GJB 3481", "MIL-V-25940"],
        "critical_metrics": ["t_open", "L_internal", "shock_pyro", "N_cycles", "reliability"],
    },
}


# ============================================================
# 3. Application Domain Reference Specs
# ============================================================

APPLICATION_DOMAINS = {
    "launch_vehicle_kerosene": {
        "name_cn": "运载火箭煤油路",
        "name_en": "Launch Vehicle Kerosene System",
        "description": "液氧煤油发动机供箱增压、主阀控制、预冷回流等",
        "valve_types_used": ["solenoid_pilot", "pressure_reducing", "check_valve", "ball_valve"],
        "key_requirements": {
            "P_design": "21~35 MPa", "T_operating": "233~350 K",
            "vibe_random": "10~25 g_rms", "N_cycles": "1000~10000",
            "L_internal": "VI级(0.15mL/min)", "m_valve": "1.5~5 kg",
            "Q_rated": "200~800 L/min",
        },
        "standards": ["QJ 20028", "GJB 3481", "HB 5980", "MIL-V-25940"],
        "notes": "煤油润滑性好，对密封材料要求相对宽松；高压化趋势明显(35MPa+)",
    },
    "launch_vehicle_lox": {
        "name_cn": "运载火箭液氧路",
        "name_en": "Launch Vehicle LOX System",
        "description": "液氧发动机主阀、预冷阀、排气阀等，强氧化性介质需特殊材料",
        "valve_types_used": ["solenoid_pilot", "ball_valve", "check_valve"],
        "key_requirements": {
            "P_design": "7~21 MPa", "T_operating": "80~350 K",
            "vibe_random": "10~25 g_rms", "N_cycles": "100~5000",
            "L_internal": "VI级", "m_valve": "0.5~3 kg",
            "Q_rated": "100~500 L/min",
        },
        "standards": ["QJ 20028", "GJB 3481", "NASA-STD-6001", "ECSS-Q-ST-70-38C"],
        "notes": "氧相容性是第一约束：禁用有机油脂，材料需通过ISO 21029燃爆试验",
    },
    "launch_vehicle_lh2": {
        "name_cn": "运载火箭液氢路",
        "name_en": "Launch Vehicle LH2 System",
        "description": "氢氧发动机液氢供应系统，极低温+氢脆风险+极低粘度",
        "valve_types_used": ["solenoid_pilot", "ball_valve", "check_valve", "pressure_reducing"],
        "key_requirements": {
            "P_design": "7~28 MPa", "T_operating": "20~350 K",
            "vibe_random": "10~25 g_rms", "N_cycles": "100~5000",
            "L_internal": "VI级(氦检1E-6 Pa·m3/s)", "m_valve": "0.3~2 kg",
            "Q_rated": "50~300 L/min",
        },
        "standards": ["QJ 20028", "GJB 3481", "NASA-STD-6001", "ECSS-Q-ST-70-38C"],
        "notes": "液氢20K极低温，材料需防氢脆(奥氏体不锈钢/Inconel)；密封极难(粘度极低)",
    },
    "satellite_propulsion": {
        "name_cn": "卫星推进系统",
        "name_en": "Satellite Propulsion System",
        "description": "卫星姿态控制/轨道推进的推进剂供给与控制",
        "valve_types_used": ["solenoid_direct", "pressure_reducing", "check_valve", "pyrotechnic"],
        "key_requirements": {
            "P_design": "0.5~35 MPa", "T_operating": "263~323 K",
            "vibe_random": "5~20 g_rms", "N_cycles": "1e4~1e6",
            "L_internal": "VI级(氦检)", "m_valve": "0.05~0.5 kg",
            "Q_rated": "5~100 L/min", "R_target": "0.999~0.9999",
        },
        "standards": ["ECSS-E-ST-35C", "ECSS-Q-ST-70-38C", "MIL-V-25940", "SAE AS5780"],
        "notes": "质量限制严格(克级优化)；长寿命(10~15年/百万次)；需在轨可靠性极高",
    },
    "aircraft_hydraulic": {
        "name_cn": "飞机液压系统",
        "name_en": "Aircraft Hydraulic System",
        "description": "民用/军用飞机液压动力系统的方向/压力/流量控制",
        "valve_types_used": ["solenoid_direct", "solenoid_pilot", "proportional_servo", "relief_safety"],
        "key_requirements": {
            "P_design": "21~28 MPa", "T_operating": "233~393 K",
            "vibe_random": "5~15 g_rms", "N_cycles": "1e5~1e7",
            "L_internal": "V级", "m_valve": "0.1~5 kg",
            "Q_rated": "10~200 L/min", "t_open": "5~30 ms",
        },
        "standards": ["SAE AS5780", "MIL-V-25940", "RTCA DO-160", "FAR 25.1435"],
        "notes": "磷酸酯液压油(阻燃)需特殊密封材料；需通过DO-160环境试验全套",
    },
    "aircraft_fuel": {
        "name_cn": "飞机燃油系统",
        "name_en": "Aircraft Fuel System",
        "description": "飞机燃油供给、转输、加油/放油的阀门控制",
        "valve_types_used": ["solenoid_pilot", "ball_valve", "check_valve", "butterfly_valve"],
        "key_requirements": {
            "P_design": "0.5~3.5 MPa", "T_operating": "233~353 K",
            "vibe_random": "5~10 g_rms", "N_cycles": "1e4~1e6",
            "L_internal": "V~VI级", "m_valve": "0.2~5 kg",
            "Q_rated": "50~2000 L/min",
        },
        "standards": ["MIL-V-25940", "RTCA DO-160", "FAR 25.957", "SAE AS5780"],
        "notes": "Jet-A/Jet-A1燃油，需防爆设计(防静电/防闪电)；油箱惰化系统关联",
    },
    "ecs_life_support": {
        "name_cn": "环控与生命保障",
        "name_en": "Environmental Control & Life Support",
        "description": "载人航天器/飞机的环控温控、空气再生、水管理",
        "valve_types_used": ["solenoid_direct", "solenoid_pilot", "check_valve", "butterfly_valve"],
        "key_requirements": {
            "P_design": "0.1~2.0 MPa", "T_operating": "270~320 K",
            "vibe_random": "3~10 g_rms", "N_cycles": "1e5~1e7",
            "L_internal": "VI级(毒性介质)", "m_valve": "0.05~1 kg",
            "Q_rated": "5~500 L/min",
        },
        "standards": ["ECSS-E-ST-34C", "NASA-STD-3001", "SSP 50005", "RTCA DO-160"],
        "notes": "毒性零泄漏要求(氨/CO2)；载人安全性要求极高；需微生物控制",
    },
    "ground_test": {
        "name_cn": "地面试验台",
        "name_en": "Ground Test Facility",
        "description": "发动机试车台、组件试验台、推进剂加注系统的阀门",
        "valve_types_used": ["ball_valve", "butterfly_valve", "pressure_reducing", "relief_safety"],
        "key_requirements": {
            "P_design": "0.5~70 MPa", "T_operating": "200~500 K",
            "vibe_random": "2~5 g_rms", "N_cycles": "1e3~1e5",
            "L_internal": "IV~VI级", "m_valve": "1~50 kg",
            "Q_rated": "100~20000 L/min",
        },
        "standards": ["GJB 3481", "QJ 20028", "ASME B16.34", "API 6D"],
        "notes": "非飞行环境，质量和体积限制宽松；但高压大流量工况多；安全冗余要求高",
    },
}


# ============================================================
# 4. Leakage Class Reference Table (ANSI/FCI 70-2)
# ============================================================

LEAKAGE_CLASSES = {
    "I": {
        "name_cn": "I级",
        "description": "不做泄漏测试要求",
        "allowable_leakage": "无限制",
        "test_method": "无需测试",
        "typical_valve": "非关键切断阀",
    },
    "II": {
        "name_cn": "II级",
        "description": "额定Cv的0.5%",
        "allowable_leakage": "0.5% × Cv (水)",
        "test_method": "额定压差下，水介质流量测量",
        "typical_valve": "一般工业调节阀",
    },
    "III": {
        "name_cn": "III级",
        "description": "额定Cv的0.1%",
        "allowable_leakage": "0.1% × Cv (水)",
        "test_method": "额定压差下，水介质流量测量",
        "typical_valve": "一般工业切断阀",
    },
    "IV": {
        "name_cn": "IV级",
        "description": "额定Cv的0.01%",
        "allowable_leakage": "0.01% × Cv (水)",
        "test_method": "额定压差下，水或空气介质测量",
        "typical_valve": "重要切断阀、一般航空航天阀门",
    },
    "V": {
        "name_cn": "V级",
        "description": "5×10⁻⁴ mL/min/in (阀座直径) × psi(压差)",
        "allowable_leakage": "5E-4 mL/(min·in·psi)",
        "test_method": "水介质微流量测量或氦质谱检漏",
        "typical_valve": "航空航天关键阀门、有毒介质",
    },
    "VI": {
        "name_cn": "VI级(气泡级)",
        "description": "极微泄漏，以气泡/分钟计",
        "allowable_leakage_table": {
            "DN6": "0.15 mL/min",
            "DN15": "0.45 mL/min",
            "DN20": "0.60 mL/min",
            "DN25": "0.90 mL/min",
            "DN32": "1.20 mL/min",
            "DN40": "1.50 mL/min",
            "DN50": "2.10 mL/min",
        },
        "test_method": "水下气泡法或氦质谱检漏(1E-6 Pa·m3/s)",
        "typical_valve": "推进剂阀门、氧气阀门、载人航天器阀门",
    },
}


# ============================================================
# 5. Standards Reference
# ============================================================

STANDARDS = [
    {"id": "MIL-V-25940", "title": "Valves, Fluid Flow Control, General Specification", "scope": "军用阀门通用规范", "status": "active"},
    {"id": "MIL-V-25639", "title": "Valve, Check", "scope": "单向阀通用规范", "status": "active"},
    {"id": "MIL-STD-810G", "title": "Environmental Engineering Considerations", "scope": "环境工程考虑与试验", "status": "active"},
    {"id": "MIL-STD-1522A", "title": "Safety Requirements for Pressure Vessels", "scope": "压力容器安全要求", "status": "active"},
    {"id": "MIL-HDBK-217", "title": "Reliability Prediction of Electronic Equipment", "scope": "可靠性预计手册", "status": "inactive(not updated)"},
    {"id": "SAE AS5780", "title": "Solenoid Valves for Aerospace Fluid Systems", "scope": "航空航天流体系统电磁阀", "status": "active"},
    {"id": "ANSI/FCI 70-2", "title": "Control Valve Seat Leakage", "scope": "调节阀阀座泄漏标准", "status": "active"},
    {"id": "ISA-75.01.01", "title": "Flow Equations for Sizing Control Valves", "scope": "调节阀流量计算标准", "status": "active"},
    {"id": "IEC 60534-2-1", "title": "Industrial-Process Control Valves - Flow Capacity", "scope": "工业过程控制阀流量能力", "status": "active"},
    {"id": "ASME B16.34", "title": "Valves - Flanged, Threaded and Welding End", "scope": "法兰/螺纹/焊接端阀门", "status": "active"},
    {"id": "ISO 4126", "title": "Safety Devices for Protection Against Excessive Pressure", "scope": "超压保护安全装置", "status": "active"},
    {"id": "ECSS-Q-ST-70-38C", "title": "High Pressure Valves and Fittings", "scope": "欧洲航天高压阀门与管件", "status": "active"},
    {"id": "ECSS-E-ST-35C", "title": "Space Propulsion - General Requirements", "scope": "航天推进通用要求", "status": "active"},
    {"id": "ECSS-E-ST-32-08C", "title": "Space Engineering - Vibration", "scope": "航天工程-振动试验", "status": "active"},
    {"id": "ECSS-E-ST-32-09C", "title": "Space Engineering - Shock", "scope": "航天工程-冲击试验", "status": "active"},
    {"id": "ECSS-Q-ST-30C", "title": "Space Product Assurance - Dependability", "scope": "航天产品保证-可靠性", "status": "active"},
    {"id": "NASA-STD-6001", "title": "Oxygen Compatibility", "scope": "氧气相容性标准", "status": "active"},
    {"id": "NASA-STD-7003", "title": "Pyrotechnic Shock Test Criteria", "scope": "爆炸冲击试验准则", "status": "active"},
    {"id": "RTCA DO-160", "title": "Environmental Conditions and Test Procedures for Airborne Equipment", "scope": "机载设备环境条件与试验", "status": "active"},
    {"id": "GJB 3481", "title": "航空航天阀门通用规范", "scope": "中国军用航空航天阀门", "status": "active"},
    {"id": "GJB 150", "title": "军用装备实验室环境试验方法", "scope": "中国军用环境试验", "status": "active"},
    {"id": "GJB 1391", "title": "故障模式、影响及危害性分析程序", "scope": "中国FMECA标准", "status": "active"},
    {"id": "GJB 899", "title": "可靠性鉴定和验收试验", "scope": "中国可靠性试验", "status": "active"},
    {"id": "QJ 20028", "title": "航天用电磁阀通用规范", "scope": "中国航天电磁阀", "status": "active"},
    {"id": "HB 5980", "title": "航空减压阀通用规范", "scope": "中国航空减压阀", "status": "active"},
    {"id": "GB/T 12224", "title": "钢制阀门一般要求", "scope": "中国钢制阀门国标", "status": "active"},
    {"id": "GB/T 30843", "title": "工业过程控制阀", "scope": "中国控制阀国标", "status": "active"},
]


# ============================================================
# 6. API Functions
# ============================================================

def get_all_metrics():
    """Return all metric definitions"""
    return [asdict(m) for m in METRICS]

def get_metrics_by_category(category):
    """Filter metrics by category"""
    return [asdict(m) for m in METRICS if m.category == category]

def get_metric_by_id(metric_id):
    """Get a single metric by ID"""
    for m in METRICS:
        if m.id == metric_id:
            return asdict(m)
    return None

def get_all_valve_types():
    """Return all valve type specifications"""
    return VALVE_TYPES

def get_valve_type(type_id):
    """Get a single valve type"""
    return VALVE_TYPES.get(type_id)

def get_all_domains():
    """Return all application domains"""
    return APPLICATION_DOMAINS

def get_domain(domain_id):
    """Get a single domain"""
    return APPLICATION_DOMAINS.get(domain_id)

def get_leakage_classes():
    """Return leakage class reference"""
    return LEAKAGE_CLASSES

def get_all_standards():
    """Return standards list"""
    return STANDARDS

def get_stats():
    """Return database statistics"""
    categories = set()
    for m in METRICS:
        categories.add(m.category)
    return {
        "total_metrics": len(METRICS),
        "categories": sorted(list(categories)),
        "category_counts": {c: len([m for m in METRICS if m.category == c]) for c in sorted(categories)},
        "valve_types": len(VALVE_TYPES),
        "application_domains": len(APPLICATION_DOMAINS),
        "leakage_classes": len(LEAKAGE_CLASSES),
        "standards": len(STANDARDS),
    }

def search_metrics(query):
    """Search metrics by keyword"""
    q = query.lower()
    results = []
    for m in METRICS:
        searchable = f"{m.id} {m.name_cn} {m.name_en} {m.symbol} {m.category} {m.definition} {m.standard_ref}".lower()
        if q in searchable:
            results.append(asdict(m))
    return results
