"""
航空航天电磁阀线圈高保真优化系统 - 后端计算引擎
从 tkinter 桌面版移植，移除 GUI 依赖，保留核心优化逻辑
"""

import math
import random
import numpy as np
from dataclasses import dataclass, field, fields
from typing import Tuple, List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# 物理模型与优化器（修正版）
# =============================================================================

@dataclass(frozen=True)
class MaterialConstants:
    COPPER_TEMP_COEF: float = 0.00393
    RHO_COPPER_20: float = 0.01724
    MU_0: float = 4e-7 * math.pi
    MU_R_CORE: float = 2000.0
    H_CONV: float = 12.5
    T_AMBIENT: float = 40.0
    T_MAX_HOTSPOT: float = 180.0
    B_SAT: float = 2.35
    COPPER_DENSITY: float = 8960.0

MAT = MaterialConstants()

@dataclass
class ValveGeometricParams:
    D_inner_mm: float = 20.0
    D_outer_max_mm: float = 40.0
    L_axial_max_mm: float = 30.0
    air_gap_main_mm: float = 0.8
    air_gap_secondary_mm: float = 0.1
    armature_length_mm: float = 55.0
    core_rear_angle_deg: float = -40.0
    pole_face_area_mm2: float = 120.0
    V_rated: float = 28.0
    I_current_limit: float = 2.0
    duty_cycle: float = 0.5
    fill_factor_min: float = 0.85
    fill_factor_max: float = 0.96

    def __post_init__(self):
        if self.D_outer_max_mm <= self.D_inner_mm:
            raise ValueError("最大外径必须大于内径")
        if self.L_axial_max_mm <= 0:
            raise ValueError("轴向长度必须为正")
        if self.pole_face_area_mm2 <= 0:
            raise ValueError("极面面积必须为正")
        if self.air_gap_main_mm <= 0:
            raise ValueError("主气隙必须为正")
        if self.air_gap_secondary_mm < 0.02:
            logger.warning("次级气隙过小，可能无法实现")

class AWGDatabase:
    AWG_TABLE = {
        10: (2.588, 2.689, 3.28, 5.26),
        11: (2.305, 2.399, 4.13, 4.17),
        12: (2.053, 2.141, 5.21, 3.31),
        13: (1.828, 1.912, 6.57, 2.62),
        14: (1.628, 1.708, 8.29, 2.08),
        15: (1.450, 1.525, 10.4, 1.65),
        16: (1.291, 1.361, 13.2, 1.31),
        17: (1.150, 1.215, 16.6, 1.04),
        18: (1.024, 1.083, 21.0, 0.823),
        19: (0.912, 0.966, 26.4, 0.653),
        20: (0.812, 0.861, 33.3, 0.518),
        21: (0.723, 0.768, 42.0, 0.410),
        22: (0.644, 0.685, 53.0, 0.326),
        23: (0.573, 0.610, 66.8, 0.258),
        24: (0.511, 0.545, 84.2, 0.205),
        25: (0.455, 0.486, 106.0, 0.163),
        26: (0.405, 0.433, 134.0, 0.129),
        27: (0.361, 0.387, 169.0, 0.102),
        28: (0.321, 0.345, 213.0, 0.0810),
        29: (0.286, 0.308, 268.0, 0.0642),
        30: (0.255, 0.275, 339.0, 0.0509),
        31: (0.227, 0.245, 427.0, 0.0404),
        32: (0.202, 0.219, 538.0, 0.0320),
        33: (0.180, 0.196, 679.0, 0.0254),
        34: (0.160, 0.175, 856.0, 0.0201),
        35: (0.143, 0.156, 1080.0, 0.0160),
        36: (0.127, 0.139, 1360.0, 0.0127),
        37: (0.113, 0.124, 1720.0, 0.0101),
        38: (0.101, 0.111, 2160.0, 0.00799),
        39: (0.090, 0.099, 2730.0, 0.00632),
        40: (0.080, 0.088, 3440.0, 0.00501),
    }

    @classmethod
    def get_awg_list(cls):
        return sorted(cls.AWG_TABLE.keys())

    @classmethod
    def get_awg_params(cls, awg: int):
        return cls.AWG_TABLE[awg]

class SolenoidPhysicsEngine:
    def __init__(self, mat=MAT):
        self.mat = mat

    def compute_turn_count(self, d_ins_mm: float, geom: ValveGeometricParams, fill_factor: float) -> Tuple[int, float]:
        T_max_mm = (geom.D_outer_max_mm - geom.D_inner_mm) / 2.0
        layers = int(T_max_mm // d_ins_mm)
        if layers <= 0:
            return 0, geom.D_inner_mm
        turns_per_layer = int(geom.L_axial_max_mm // d_ins_mm)
        if turns_per_layer <= 0:
            return 0, geom.D_inner_mm
        N = int(layers * turns_per_layer * fill_factor)
        D_out_actual_mm = geom.D_inner_mm + 2 * layers * d_ins_mm
        D_out_actual_mm = min(D_out_actual_mm, geom.D_outer_max_mm)
        return max(N, 1), D_out_actual_mm

    def thermal_equilibrium(self, R20: float, N: int, d_bare_mm: float,
                            D_out_actual_mm: float, geom: ValveGeometricParams) -> Tuple[float, float, float]:
        L_m = geom.L_axial_max_mm / 1000.0
        D_out_m = D_out_actual_mm / 1000.0
        D_in_m = geom.D_inner_mm / 1000.0
        A_cyl = math.pi * D_out_m * L_m
        A_end = 2 * (math.pi * (D_out_m/2)**2 - math.pi * (D_in_m/2)**2)
        A_heat_m2 = A_cyl + A_end
        if A_heat_m2 <= 0:
            A_heat_m2 = 1e-4
        T_coil = 85.0
        for _ in range(50):
            R_hot = R20 * (1 + self.mat.COPPER_TEMP_COEF * (T_coil - 20.0))
            I = geom.V_rated / R_hot
            if I > geom.I_current_limit:
                return float('inf'), I, R_hot
            P_heat = I**2 * R_hot
            T_new = self.mat.T_AMBIENT + P_heat / (self.mat.H_CONV * A_heat_m2)
            if abs(T_new - T_coil) < 0.5:
                T_coil = T_new
                break
            T_coil = 0.7 * T_coil + 0.3 * T_new
        if T_coil > self.mat.T_MAX_HOTSPOT:
            T_coil = self.mat.T_MAX_HOTSPOT
            R_hot = R20 * (1 + self.mat.COPPER_TEMP_COEF * (T_coil - 20.0))
            I = geom.V_rated / R_hot
        return T_coil, I, R_hot

    def magnetic_circuit_solver(self, N: int, I: float, T_coil: float,
                                geom: ValveGeometricParams,
                                sec_gap_mm: float, armature_factor: float) -> Dict[str, Any]:
        F_mmf = N * I
        lg_main = geom.air_gap_main_mm / 1000.0
        A_pole = geom.pole_face_area_mm2 / 1e6
        R_g_main = lg_main / (self.mat.MU_0 * A_pole)
        lg_sec = sec_gap_mm / 1000.0
        A_sec = A_pole * 0.6
        R_g_sec = lg_sec / (self.mat.MU_0 * A_sec)
        aspect_ratio = geom.L_axial_max_mm / geom.D_outer_max_mm
        f_leak_raw = 1.2 + 0.3 * (1.5 - aspect_ratio)
        f_leak = max(1.2, min(1.8, f_leak_raw))
        R_total_est = R_g_main + R_g_sec
        if R_total_est <= 0:
            return {"B": 0, "Phi": 0, "F_mmf": F_mmf, "F_force_N": 0,
                    "is_saturated": False, "mu_r_core": self.mat.MU_R_CORE,
                    "R_total_H": float('inf'), "f_leak": f_leak}
        Phi_est = F_mmf / R_total_est / f_leak
        B_est = Phi_est / A_pole if A_pole > 0 else 0
        mu_r_core = self.mat.MU_R_CORE
        for _ in range(10):
            l_core = (geom.armature_length_mm * armature_factor * 2) / 1000.0
            A_core = A_pole
            if B_est > 0.1:
                mu_r = self.mat.MU_R_CORE / (1 + B_est / self.mat.B_SAT * 0.8)
                mu_r = max(mu_r, 50)
            else:
                mu_r = self.mat.MU_R_CORE
            R_core = l_core / (mu_r * self.mat.MU_0 * A_core)
            R_total = R_g_main + R_g_sec + R_core
            Phi = F_mmf / R_total / f_leak
            B_new = Phi / A_pole if A_pole > 0 else 0
            if abs(B_new - B_est) < 1e-4:
                B_est = B_new
                mu_r_core = mu_r
                break
            B_est = 0.5 * B_est + 0.5 * B_new
        F_force = (B_est**2 * A_pole) / (2 * self.mat.MU_0) * 0.92
        is_saturated = B_est > (self.mat.B_SAT * 0.8)
        return {
            "B": B_est, "Phi": Phi_est, "F_mmf": F_mmf, "F_force_N": F_force,
            "is_saturated": is_saturated, "mu_r_core": mu_r_core,
            "R_total_H": R_total_est, "f_leak": f_leak
        }

class HybridOptimizer:
    def __init__(self, geom: ValveGeometricParams, physics: SolenoidPhysicsEngine, 
                 n_particles: int = 20, n_iterations: int = 50,
                 log_callback=None):
        self.geom = geom
        self.physics = physics
        self.awg_list = AWGDatabase.get_awg_list()
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.bounds = [
            [0.05, 0.3],
            [geom.fill_factor_min, geom.fill_factor_max],
            [0.8, 1.2]
        ]
        self.dim = len(self.bounds)
        self.log_callback = log_callback

    def _log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def objective(self, x: np.ndarray, awg: int, geom_copy: ValveGeometricParams) -> Tuple[float, Dict]:
        sec_gap, fill_factor, armature_factor = x
        d_bare, d_ins, R_per_km_20, A_cu_mm2 = AWGDatabase.get_awg_params(awg)
        geom_copy.air_gap_secondary_mm = sec_gap
        geom_copy.armature_length_mm = 55.0 * armature_factor
        N, D_out_actual_mm = self.physics.compute_turn_count(d_ins, geom_copy, fill_factor)
        if N < 5:
            return -1e12, {}
        D_avg_mm = (geom_copy.D_inner_mm + D_out_actual_mm) / 2.0
        l_turn_m = D_avg_mm * math.pi / 1000.0
        R20 = R_per_km_20 * (l_turn_m * N) / 1000.0
        T_coil, I, R_hot = self.physics.thermal_equilibrium(R20, N, d_bare, D_out_actual_mm, geom_copy)
        if I > geom_copy.I_current_limit or T_coil > self.physics.mat.T_MAX_HOTSPOT:
            return -1e12, {}
        J = I / A_cu_mm2
        if J > 6.0:
            return -1e12, {}
        mag = self.physics.magnetic_circuit_solver(N, I, T_coil, geom_copy, sec_gap, armature_factor)
        F = mag["F_force_N"]
        penalty = 1.0
        if T_coil > 120:
            penalty *= math.exp(-0.01 * (T_coil - 120))
        if mag["is_saturated"]:
            penalty *= 0.3
        F_final = F * penalty
        info = {
            "awg": awg, "d_bare_mm": d_bare, "d_ins_mm": d_ins, "N": N, "I": I,
            "T_coil": T_coil, "B": mag["B"], "F_raw": F, "F_final": F_final,
            "J": J, "R_hot": R_hot, "saturated": mag["is_saturated"],
            "f_leak": mag["f_leak"], "sec_gap": sec_gap, "fill_factor": fill_factor,
            "armature_factor": armature_factor, "D_out_actual_mm": D_out_actual_mm,
            "A_cu_mm2": A_cu_mm2
        }
        return F_final, info

    def optimize_for_awg(self, awg: int) -> Tuple[float, Dict]:
        w, c1, c2 = 0.7, 1.5, 1.5
        particles = []
        valid_found = False

        # 初始化粒子群
        for _ in range(self.n_particles):
            x = np.array([random.uniform(b[0], b[1]) for b in self.bounds])
            v = np.random.randn(self.dim) * 0.1
            geom_copy = ValveGeometricParams(**{f.name: getattr(self.geom, f.name) for f in fields(self.geom)})
            fit, info = self.objective(x, awg, geom_copy)
            particles.append([x, v, x.copy(), fit, info])
            if fit > -1e10:  # 有效设计
                valid_found = True

        if not valid_found:
            return -1e12, {}

        # 初始化全局最优
        gbest_fit = -1e12
        gbest_x = None
        gbest_info = None
        for p in particles:
            if p[3] > gbest_fit:
                gbest_fit = p[3]
                gbest_x = p[2].copy()
                gbest_info = p[4]

        # 迭代优化
        for it in range(self.n_iterations):
            for p in particles:
                x, v, pbest_x, pbest_fit, pbest_info = p
                geom_copy = ValveGeometricParams(**{f.name: getattr(self.geom, f.name) for f in fields(self.geom)})
                fit, info = self.objective(x, awg, geom_copy)

                # 更新个体最优
                if fit > pbest_fit:
                    pbest_fit, pbest_x, pbest_info = fit, x.copy(), info

                # 更新全局最优
                if fit > gbest_fit:
                    gbest_fit, gbest_x, gbest_info = fit, x.copy(), info

                # 速度与位置更新
                r1, r2 = random.random(), random.random()
                if gbest_x is not None:
                    v = w * v + c1 * r1 * (pbest_x - x) + c2 * r2 * (gbest_x - x)
                else:
                    v = w * v + c1 * r1 * (pbest_x - x)
                x = x + v

                # 边界处理
                for d in range(self.dim):
                    if x[d] < self.bounds[d][0]:
                        x[d] = self.bounds[d][0]
                        v[d] = -v[d] * 0.5
                    if x[d] > self.bounds[d][1]:
                        x[d] = self.bounds[d][1]
                        v[d] = -v[d] * 0.5

                p[0], p[1], p[2], p[3], p[4] = x, v, pbest_x, pbest_fit, pbest_info

            w = max(0.3, w * 0.98)

        if gbest_x is None:
            return -1e12, {}
        return gbest_fit, gbest_info

    def optimize(self, progress_callback=None) -> Tuple[int, float, Dict]:
        best_awg, best_fit, best_info = None, -1e12, None
        total_awg = len(self.awg_list)
        
        for idx, awg in enumerate(self.awg_list):
            self._log(f"优化 AWG {awg} ({idx+1}/{total_awg}) ...")
            if progress_callback:
                progress_callback(idx, total_awg, awg)
            
            fit, info = self.optimize_for_awg(awg)
            if fit > best_fit:
                best_fit, best_awg, best_info = fit, awg, info
                self._log(f"  新最优: AWG {awg}, 电磁力 {fit:.3f} N")
        
        return best_awg, best_fit, best_info


def convert_numpy_types(obj):
    """递归转换NumPy类型为原生Python类型"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return convert_numpy_types(obj.tolist())
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj


def run_optimization(geom_params: Dict, n_particles: int, n_iterations: int, 
                     log_callback=None, progress_callback=None) -> Dict:
    """
    运行优化（供Flask API调用）
    
    Args:
        geom_params: 几何参数字典
        n_particles: 粒子数量
        n_iterations: 迭代次数
        log_callback: 日志回调函数
        progress_callback: 进度回调函数 (current, total, awg)
    
    Returns:
        优化结果字典
    """
    geom = ValveGeometricParams(**geom_params)
    physics = SolenoidPhysicsEngine(MAT)
    optimizer = HybridOptimizer(geom, physics, n_particles, n_iterations, log_callback)
    
    best_awg, best_fit, best_info = optimizer.optimize(progress_callback)
    
    if best_awg is None or best_fit <= -1e10 or best_info is None or not best_info:
        return {
            "success": False,
            "message": "优化失败，未找到可行设计。请检查约束是否过于严格（如最大外径太小、电流限制过严等）。"
        }
    
    # 计算铜线质量
    d_avg_mm = (geom.D_inner_mm + best_info['D_out_actual_mm']) / 2.0
    l_total_m = best_info['N'] * (math.pi * d_avg_mm / 1000.0)
    A_cu_m2 = best_info['A_cu_mm2'] / 1e6
    volume_m3 = l_total_m * A_cu_m2
    mass_g = volume_m3 * MAT.COPPER_DENSITY * 1000
    
    # 构建结果字典
    result = {
        "success": True,
        "best_awg": int(best_awg),
        "best_fit": float(best_fit),
        "best_info": best_info,
        "mass_g": float(mass_g),
        "power_W": float(best_info['I']**2 * best_info['R_hot'])
    }
    
    # 转换所有NumPy类型为原生Python类型
    result = convert_numpy_types(result)
    
    return result


if __name__ == "__main__":
    # 测试代码
    def print_log(msg):
        print(msg)
    
    result = run_optimization(
        geom_params={},
        n_particles=20,
        n_iterations=50,
        log_callback=print_log
    )
    print(result)
