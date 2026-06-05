"""
Fluid Mechanics Super Calculator - Backend Formula Engine
==========================================================
130+ formulas across 12 categories for aerospace valve R&D.
"""

import math

# Sprint 5: Pumps, Flow Measurement, Aerodynamics, Turbulence, CFD
from fluid_mechanics_sprint5 import (
    pump_hydraulic_power, pump_shaft_power, pump_efficiency,
    specific_speed_metric, specific_speed_imperial, affinity_law_Q, affinity_law_H,
    npsh_available, suction_specific_speed,
    venturi_flow_rate, venturi_mass_flow, orifice_flow_rate,
    pitot_velocity, weir_rectangular, weir_vnotch, nozzle_flow_rate, rotameter_flow,
    lift_force, drag_force, lift_drag_ratio, induced_drag,
    skin_friction_drag, wave_drag, bluff_body_drag,
    stall_speed, aspect_ratio_fx,
    turbulence_intensity, turbulent_kinetic_energy,
    kolmogorov_length_scale, kolmogorov_time_scale, kolmogorov_velocity_scale,
    eddy_viscosity_mixing_length, reynolds_stress_uv,
    viscous_sublayer_thickness, friction_velocity, logarithmic_law,
    cfl_condition, grid_reynolds_number, peclet_number,
    courant_number_wave, numerical_diffusion_coeff,
    mesh_reynolds_requirement, taylor_microscale,
    turbulent_viscosity_ratio, dissipation_rate_estimate, y_plus_estimate,
)

# Sprint 5: Pumps, Flow Measurement, Aerodynamics, Turbulence, CFD
from fluid_mechanics_sprint5 import (
    pump_hydraulic_power, pump_shaft_power, pump_efficiency,
    specific_speed_metric, specific_speed_imperial, affinity_law_Q, affinity_law_H,
    npsh_available, suction_specific_speed,
    venturi_flow_rate, venturi_mass_flow, orifice_flow_rate,
    pitot_velocity, weir_rectangular, weir_vnotch, nozzle_flow_rate, rotameter_flow,
    lift_force, drag_force, lift_drag_ratio, induced_drag,
    skin_friction_drag, wave_drag, bluff_body_drag,
    stall_speed, aspect_ratio_fx,
    turbulence_intensity, turbulent_kinetic_energy,
    kolmogorov_length_scale, kolmogorov_time_scale, kolmogorov_velocity_scale,
    eddy_viscosity_mixing_length, reynolds_stress_uv,
    viscous_sublayer_thickness, friction_velocity, logarithmic_law,
    cfl_condition, grid_reynolds_number, peclet_number,
    courant_number_wave, numerical_diffusion_coeff,
    mesh_reynolds_requirement, taylor_microscale,
    turbulent_viscosity_ratio, dissipation_rate_estimate, y_plus_estimate,
)

# Sprint 5: Pumps, Flow Measurement, Aerodynamics, Turbulence, CFD
from fluid_mechanics_sprint5 import (
    pump_hydraulic_power, pump_shaft_power, pump_efficiency,
    specific_speed_metric, specific_speed_imperial, affinity_law_Q, affinity_law_H,
    npsh_available, suction_specific_speed,
    venturi_flow_rate, venturi_mass_flow, orifice_flow_rate,
    pitot_velocity, weir_rectangular, weir_vnotch, nozzle_flow_rate, rotameter_flow,
    lift_force, drag_force, lift_drag_ratio, induced_drag,
    skin_friction_drag, wave_drag, bluff_body_drag,
    stall_speed, aspect_ratio_fx,
    turbulence_intensity, turbulent_kinetic_energy,
    kolmogorov_length_scale, kolmogorov_time_scale, kolmogorov_velocity_scale,
    eddy_viscosity_mixing_length, reynolds_stress_uv,
    viscous_sublayer_thickness, friction_velocity, logarithmic_law,
    cfl_condition, grid_reynolds_number, peclet_number,
    courant_number_wave, numerical_diffusion_coeff,
    mesh_reynolds_requirement, taylor_microscale,
    turbulent_viscosity_ratio, dissipation_rate_estimate, y_plus_estimate,
)

# Sprint 4: Non-Newtonian, Multi-Phase, Cavitation
from fluid_mechanics_sprint4 import (
    bingham_shear_stress, bingham_pipe_flow_rate,
    power_law_apparent_viscosity, power_law_pipe_flow_velocity,
    generalized_reynolds_number_power_law, dodge_metzner_friction_factor,
    herschel_bulkley_shear_stress, casson_shear_stress,
    homogeneous_void_fraction, homogeneous_two_phase_density,
    mcadams_viscosity, lockhart_martinelli_X, chisholm_two_phase_multiplier,
    drift_flux_void_fraction, baker_flow_pattern_map,
    taitel_dukler_transition, slug_frequency,
    cavitation_number, thoma_cavitation_parameter,
    npsh_available, npsh_required_by_suction_specific_speed,
    rayleigh_plesset_radius, bubble_natural_frequency,
    cavitation_erosion_power, critical_cavitation_factor,
)

# =============================================================================
# Safe division & JSON cleaning
# =============================================================================

def safe_div(a, b, default=None):
    try:
        if b == 0: return default
        return a / b
    except (ZeroDivisionError, TypeError):
        return default

def _clean(obj):
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
    return obj

# =============================================================================
# Fluid Property Database (14 aerospace fluids)
# =============================================================================

FLUID_PROPERTIES = {
    'water_20C': {'name': 'Water (20C)', 'rho': 998.0, 'mu': 0.001002, 'nu': 1.004e-6, 'sigma': 0.0728, 'K_bulk': 2.15e9, 'P_v': 2340.0, 'Cp': 4182.0, 'k_thermal': 0.598, 'gamma': 1.33},
    'water_50C': {'name': 'Water (50C)', 'rho': 988.0, 'mu': 0.000547, 'nu': 5.53e-7, 'sigma': 0.0679, 'K_bulk': 2.2e9, 'P_v': 12350.0, 'Cp': 4181.0, 'k_thermal': 0.644, 'gamma': 1.33},
    'air_20C': {'name': 'Air (20C,1atm)', 'rho': 1.204, 'mu': 1.825e-5, 'nu': 1.516e-5, 'sigma': 0.0, 'K_bulk': 1.42e5, 'P_v': 0.0, 'Cp': 1005.0, 'k_thermal': 0.0257, 'gamma': 1.4, 'R_gas': 287.0},
    'helium_20C': {'name': 'He (20C,1atm)', 'rho': 0.166, 'mu': 1.99e-5, 'nu': 1.2e-4, 'K_bulk': 1.05e5, 'gamma': 1.66, 'R_gas': 2077.0},
    'nitrogen_20C': {'name': 'N2 (20C,1atm)', 'rho': 1.165, 'mu': 1.76e-5, 'nu': 1.51e-5, 'K_bulk': 1.39e5, 'gamma': 1.4, 'R_gas': 296.8},
    'oxygen_20C': {'name': 'O2 (20C,1atm)', 'rho': 1.331, 'mu': 2.04e-5, 'nu': 1.53e-5, 'K_bulk': 1.05e5, 'gamma': 1.4, 'R_gas': 259.8},
    'kerosene': {'name': 'RP-1 Kerosene', 'rho': 810.0, 'mu': 0.00164, 'nu': 2.02e-6, 'sigma': 0.028, 'K_bulk': 1.3e9, 'P_v': 4000.0},
    'hydrazine': {'name': 'N2H4', 'rho': 1021.0, 'mu': 0.00097, 'nu': 9.5e-7, 'sigma': 0.0675, 'K_bulk': 2.0e9, 'P_v': 1700.0},
    'hydraulic_oil': {'name': 'Hydraulic Oil VG32', 'rho': 870.0, 'mu': 0.02784, 'nu': 3.2e-5, 'sigma': 0.032, 'K_bulk': 1.5e9},
    'lh2': {'name': 'LH2', 'rho': 70.8, 'mu': 1.3e-5, 'nu': 1.84e-7, 'K_bulk': 5.0e7, 'gamma': 1.4, 'R_gas': 4157.0},
    'lox': {'name': 'LOX', 'rho': 1141.0, 'mu': 1.9e-4, 'nu': 1.67e-7, 'K_bulk': 8.0e8, 'gamma': 1.2},
    'diesel': {'name': 'Diesel Fuel', 'rho': 850.0, 'mu': 0.003, 'nu': 3.53e-6, 'sigma': 0.028, 'K_bulk': 1.4e9},
    'sea_water': {'name': 'Sea Water (20C)', 'rho': 1025.0, 'mu': 0.00107, 'nu': 1.04e-6, 'sigma': 0.073, 'K_bulk': 2.34e9},
    'ethanol': {'name': 'Ethanol (20C)', 'rho': 789.0, 'mu': 0.0012, 'nu': 1.52e-6, 'sigma': 0.0223, 'K_bulk': 1.1e9, 'P_v': 5950.0},
}

PIPE_ROUGHNESS = {
    'drawn_tube': 0.0015, 'steel_commercial': 0.046, 'steel_riveted': 0.9,
    'cast_iron': 0.26, 'galvanized_iron': 0.15, 'concrete': 0.3,
    'smooth_plastic': 0.005, 'brass': 0.0015, 'copper': 0.0015,
}

# =============================================================================
# Category 1: Basic Fluid Properties
# =============================================================================

def density_from_mass_volume(mass, volume):
    return safe_div(mass, volume)

def specific_weight(rho, g=9.81):
    return rho * g

def specific_gravity(rho, rho_ref=1000.0):
    return safe_div(rho, rho_ref)

def dynamic_from_kinematic_viscosity(nu, rho):
    return nu * rho

def kinematic_from_dynamic_viscosity(mu, rho):
    return safe_div(mu, rho)

def bulk_modulus(dp, dV, V):
    return safe_div(-V * dp, dV)

def surface_tension_force(sigma, L):
    return sigma * L

def vapor_pressure_antoine(A, B, C, T):
    return 10 ** (A - safe_div(B, C + T))

# =============================================================================
# Category 2: Hydrostatics
# =============================================================================

def hydrostatic_pressure(rho, g, h, P0=101325.0):
    return P0 + rho * g * h

def manometer_pressure(rho_fluid, g, h_diff):
    return rho_fluid * g * h_diff

def hydrostatic_force_plane(rho, g, h_c, A):
    return rho * g * h_c * A

def center_of_pressure(h_c, I_xx_c, A, theta=90.0):
    y_c = safe_div(h_c, math.sin(math.radians(theta)))
    return safe_div(h_c + I_xx_c, y_c * A) if y_c and A else None

def buoyancy_force(rho_fluid, g, V_displaced):
    return rho_fluid * g * V_displaced

def metacenter_height(I_waterline, V_displaced, BG=0.0):
    return safe_div(I_waterline, V_displaced) - BG

def fluid_height_in_tank(mass, rho, area):
    return safe_div(mass, rho * area)

def capillary_rise(sigma, theta, rho, g, R):
    return safe_div(2.0 * sigma * math.cos(math.radians(theta)), rho * g * R)

# =============================================================================
# Category 3: Continuity & Bernoulli
# =============================================================================

def continuity_eq(A1, V1, A2):
    return safe_div(A1 * V1, A2)

def bernoulli_total_pressure(P, rho, V, z=0.0, g=9.81):
    return P + 0.5 * rho * V**2 + rho * g * z

def bernoulli_velocity(P1, P2, rho, z1=0.0, z2=0.0, V1=0.0, g=9.81):
    delta = 2.0 * (P1 - P2) / rho + 2.0 * g * (z1 - z2) + V1**2
    return math.sqrt(delta) if delta >= 0 else None

def bernoulli_pressure_drop_ideal(rho, V1, V2, z1=0.0, z2=0.0, g=9.81):
    return 0.5 * rho * (V2**2 - V1**2) + rho * g * (z2 - z1)

def energy_eq_head(h_pump, h_turbine, h_loss, z1, z2, V1, V2, P1, P2, rho, g=9.81):
    head = (z2 - z1) + (V2**2 - V1**2)/(2.0*g) + (P2 - P1)/(rho * g)
    return h_pump - h_turbine - h_loss - head

def momentum_force(rho, Q, V_out, V_in, beta=1.0):
    return rho * Q * (beta * V_out - beta * V_in)

def cavitation_number(P, P_v, rho, V):
    return safe_div(P - P_v, 0.5 * rho * V**2)

def stagnation_pressure(P_static, rho, V):
    return P_static + 0.5 * rho * V**2

def flow_rate_from_area_velocity(A, V):
    return A * V

def mass_flow_rate(rho, Q):
    return rho * Q

# =============================================================================
# Category 4: Pipe Flow
# =============================================================================

def reynolds_number(rho, V, D, mu):
    return safe_div(rho * V * D, mu)

def reynolds_number_nu(V, D, nu):
    return safe_div(V * D, nu)

def friction_factor_laminar(Re):
    return safe_div(64.0, Re)

def friction_factor_blasius(Re):
    if Re > 0: return 0.316 * Re ** (-0.25)
    return None

def friction_factor_colebrook(Re, epsilon, D):
    if Re <= 0 or D <= 0: return None
    rr = epsilon / D
    if Re < 2300: return friction_factor_laminar(Re)
    f = safe_div(0.25, (math.log10(safe_div(rr, 3.7) + safe_div(5.74, Re**0.9)))**2)
    for _ in range(30):
        try:
            rhs = -2.0 * math.log10(rr/3.7 + 2.51/(Re * math.sqrt(f)))
            f_new = 1.0 / (rhs**2)
            if abs(f_new - f) < 1e-10: return f_new
            f = f_new
        except (ValueError, ZeroDivisionError): break
    return f

def friction_factor_swamee_jain(Re, epsilon, D):
    if Re <= 0 or D <= 0: return None
    rr = safe_div(epsilon, D)
    denom = math.log10(rr/3.7 + 5.74/(Re**0.9))
    return safe_div(0.25, denom**2)

def darcy_weisbach_hf(f, L, D, V, g=9.81):
    return safe_div(f * L * V**2, D * 2.0 * g)

def darcy_weisbach_dP(f, L, D, rho, V):
    return f * safe_div(L, D) * 0.5 * rho * V**2

def hazen_williams_velocity(C, R_h, S):
    return 0.849 * C * (R_h ** 0.63) * (S ** 0.54)

def hydraulic_radius(A, P_wetted):
    return safe_div(A, P_wetted)

def hydraulic_diameter(A, P_wetted):
    return safe_div(4.0 * A, P_wetted)

def minor_loss_head(K, V, g=9.81):
    return safe_div(K * V**2, 2.0 * g)

def minor_loss_pressure(K, rho, V):
    return K * 0.5 * rho * V**2

def sudden_expansion_loss(A1, A2, V1, rho):
    K = (1.0 - safe_div(A1, A2)) ** 2
    return K * 0.5 * rho * V1**2

def sudden_contraction_loss(A1, A2, V2, rho):
    ratio = safe_div(A2, A1)
    if ratio is None: return None
    K = 0.5 * (1.0 - ratio) ** 2.5 if ratio <= 0.76 else 0.42 * (1.0 - ratio)
    return K * 0.5 * rho * V2**2

def pipe_series_equivalent_length(K_total, D, f):
    return safe_div(K_total * D, f)

def pipe_exit_loss(V, rho, K=1.0):
    return K * 0.5 * rho * V**2

def pipe_entrance_loss(V, rho, r_D=0.0):
    if r_D <= 0: K = 0.5
    elif r_D < 0.1: K = 0.25
    elif r_D < 0.2: K = 0.1
    else: K = 0.03
    return K * 0.5 * rho * V**2

def pipe_bend_loss(V, rho, R_bend, D, theta_deg=90.0):
    theta_rad = math.radians(theta_deg)
    R_D = safe_div(R_bend, D) or 0.0
    if R_D == 0: K = 1.1 * theta_rad
    else: K = (0.131 + 0.163 * (safe_div(D, R_bend, 1)**3.5)) * (theta_rad / (math.pi/2))
    return K * 0.5 * rho * V**2

# =============================================================================
# Category 5: Open Channel Flow
# =============================================================================

def froude_number(V, g, y_h):
    return safe_div(V, math.sqrt(g * y_h))

def manning_velocity(n, R_h, S):
    return safe_div(R_h**(2.0/3.0) * S**0.5, n)

def manning_discharge(n, A, R_h, S):
    return safe_div(A * R_h**(2.0/3.0) * S**0.5, n)

def chezy_velocity(C, R_h, S):
    return C * math.sqrt(R_h * S)

def critical_depth_rectangular(Q, b, g=9.81):
    return (Q**2 / (g * b**2)) ** (1.0/3.0)

def specific_energy(y, Q, A_flow, g=9.81):
    return y + safe_div(Q**2, 2.0 * g * A_flow**2)

def hydraulic_jump_ratio(Fr1):
    return 0.5 * (math.sqrt(1.0 + 8.0 * Fr1**2) - 1.0)

def hydraulic_jump_energy_loss(y1, y2):
    return safe_div((y2 - y1)**3, 4.0 * y1 * y2)

def weir_discharge_rectangular(C_d, b, H, g=9.81):
    return (2.0/3.0) * C_d * b * math.sqrt(2.0 * g) * H**1.5

# =============================================================================
# Category 6: Compressible Flow
# =============================================================================

def speed_of_sound(k, R, T):
    return math.sqrt(k * R * T)

def mach_number(V, a):
    return safe_div(V, a)

def isentropic_T_ratio(M, k=1.4):
    return 1.0 / (1.0 + 0.5 * (k - 1.0) * M**2)

def isentropic_P_ratio(M, k=1.4):
    return (1.0 + 0.5 * (k - 1.0) * M**2) ** (-k/(k - 1.0))

def isentropic_rho_ratio(M, k=1.4):
    return (1.0 + 0.5 * (k - 1.0) * M**2) ** (-1.0/(k - 1.0))

def isentropic_area_ratio(M, k=1.4):
    term = (2.0/(k+1.0)) * (1.0 + (k-1.0)/2.0 * M**2)
    return safe_div(term**((k+1.0)/(2.0*(k-1.0))), M)

def normal_shock_P_ratio(M1, k=1.4):
    return 1.0 + (2.0 * k/(k + 1.0)) * (M1**2 - 1.0)

def normal_shock_rho_ratio(M1, k=1.4):
    return (k + 1.0) * M1**2 / ((k - 1.0) * M1**2 + 2.0)

def normal_shock_M2(M1, k=1.4):
    num = (k - 1.0) * M1**2 + 2.0
    den = 2.0 * k * M1**2 - (k - 1.0)
    return math.sqrt(safe_div(num, den))

def prandtl_meyer_angle(M, k=1.4):
    t1 = math.sqrt((k + 1.0)/(k - 1.0))
    t2 = math.sqrt(M**2 - 1.0) if M > 1 else 0
    return t1 * math.atan(safe_div(t2, t1, 0)) - math.atan(t2)

def nozzle_mass_flow(P0, T0, A_t, k=1.4, R=287.0):
    factor = math.sqrt(k/R * (2.0/(k+1.0))**((k+1.0)/(k-1.0)))
    return safe_div(P0 * A_t * factor, math.sqrt(T0))

def expansion_velocity(P0, P_exit, T0, k=1.4, R=287.0):
    ratio = safe_div(P_exit, P0)
    if ratio is None or ratio <= 0: return None
    return math.sqrt(2.0 * k/(k-1.0) * R * T0 * (1.0 - ratio**((k-1.0)/k)))

# =============================================================================
# Category 7: Orifices & Valves
# =============================================================================

def orifice_flow(C_d, A_o, rho, dP):
    return C_d * A_o * math.sqrt(safe_div(2.0 * abs(dP), rho))

def valve_Cv(Q_gpm, dP_psi, SG=1.0):
    return Q_gpm * math.sqrt(safe_div(SG, dP_psi))

def flow_from_Cv(Cv, dP_psi, SG=1.0):
    return Cv * math.sqrt(safe_div(dP_psi, SG))

def Kv_to_Cv(Kv):
    return 1.156 * Kv

def Cv_to_Kv(Cv):
    return 0.865 * Cv

def valve_dp_from_Cv(Q_gpm, Cv, SG=1.0):
    return SG * (safe_div(Q_gpm, Cv))**2

def choked_flow_dP(P1, P_v, FL=0.85):
    return FL**2 * (P1 - 0.96 * P_v)

def cavitation_index_valve(P_d, P_v, rho, V):
    return safe_div(P_d - P_v, 0.5 * rho * V**2)

def valve_authority(dP_valve, dP_total):
    return safe_div(dP_valve, dP_total)

def torricelli_velocity(h, g=9.81):
    return math.sqrt(2.0 * g * h)

def nozzle_velocity_incompressible(dP, rho):
    return math.sqrt(2.0 * safe_div(dP, rho))

def flow_coefficient_Cd_via_Re(Re, beta):
    if Re <= 0: return None
    return 0.5959 + 0.0312*beta**2.1 - 0.184*beta**8 + 91.71*beta**2.5/(Re**0.75)

def expansion_factor_compressible(k, beta, dP, P1):
    ratio = safe_div(dP, P1)
    if ratio is None: return None
    return 1.0 - (0.41 + 0.35*beta**4) * ratio / k

def pipe_to_orifice_velocity(D, d, V_pipe):
    return V_pipe * (safe_div(D, d))**2

def venturi_discharge(C_d, A_t, rho, dP, beta):
    return C_d * A_t / math.sqrt(1.0 - beta**4) * math.sqrt(2.0 * safe_div(dP, rho))

def vena_contracta_area(A_o, C_c=0.62):
    return C_c * A_o

def flow_resistance_coefficient(dP, Q, rho):
    return safe_div(dP, Q**2)

# =============================================================================
# Category 8: Boundary Layer & Drag
# =============================================================================

def bl_thickness_laminar(x, Re_x):
    return safe_div(5.0 * x, math.sqrt(Re_x))

def bl_thickness_turbulent(x, Re_x):
    return safe_div(0.37 * x, Re_x**0.2)

def skin_friction_coef_laminar(Re_L):
    return safe_div(1.328, math.sqrt(Re_L))

def skin_friction_coef_turbulent(Re_L):
    return safe_div(0.074, Re_L**0.2)

def drag_force(C_d, rho, V, A_ref):
    return 0.5 * C_d * rho * V**2 * A_ref

def lift_force(C_l, rho, V, A):
    return 0.5 * C_l * rho * V**2 * A

def drag_force_stokes(mu, R, V):
    return 6.0 * math.pi * mu * R * V

def drag_coef_sphere(Re):
    if Re <= 0: return None
    if Re < 1: return safe_div(24.0, Re)
    if Re < 1000: return safe_div(24.0, Re) * (1.0 + 0.15 * Re**0.687)
    return 0.44

def terminal_velocity_sphere(rho_p, rho_f, R, mu, g=9.81):
    return safe_div(2.0 * R**2 * (rho_p - rho_f) * g, 9.0 * mu)

def flat_plate_reynolds(V, L, nu):
    return safe_div(V * L, nu)

# =============================================================================
# Category 9: Fluid Power / Hydraulics
# =============================================================================

def pump_power(Q, dP, eta=0.85):
    return safe_div(Q * dP, eta)

def hydraulic_power(Q, dP):
    return Q * dP

def cylinder_force(P, A_piston, A_rod=0):
    return P * (A_piston - A_rod)

def cylinder_velocity(Q, A):
    return safe_div(Q, A)

def motor_torque(q_displacement, dP, eta_m=0.92):
    return safe_div(q_displacement * dP * eta_m, 2.0 * math.pi)

def motor_speed(Q, q_displacement, eta_v=0.95):
    return safe_div(Q * eta_v, q_displacement)

def accumulator_size(V0, P0, P1, n=1.4):
    return V0 * (1.0 - (safe_div(P0, P1))**(1.0/n))

def pump_efficiency_overall(eta_v, eta_m):
    return eta_v * eta_m

def pressure_intensifier_ratio(A_large, A_small):
    return safe_div(A_large, A_small)

def fluid_spring_stiffness(K_bulk, A, V):
    return safe_div(K_bulk * A**2, V)

def hydraulic_time_constant(V, Q):
    return safe_div(V, Q)

# =============================================================================
# Category 10: Water Hammer & Surge
# =============================================================================

def joukowsky_pressure(rho, a, dV):
    return rho * a * abs(dV)

def wave_speed_fluid(K, rho, D=0.0, e=0.0, E_pipe=2.1e11, C=1.0):
    a0 = math.sqrt(safe_div(K, rho))
    if D <= 0 or e <= 0: return a0
    return safe_div(a0, math.sqrt(1.0 + C * K * D / (E_pipe * e)))

def surge_pressure_instant_valve(rho, a, V0):
    return rho * a * V0

def pipe_period(L, a):
    return safe_div(2.0 * L, a)

def critical_closure_time(L, a):
    return safe_div(2.0 * L, a)

# =============================================================================
# Category 11: Dimensional Analysis
# =============================================================================

def dimensionless_reynolds(V, L, nu):
    return safe_div(V * L, nu)

def dimensionless_froude(V, g, L):
    return safe_div(V, math.sqrt(g * L))

def dimensionless_mach(V, a):
    return safe_div(V, a)

def dimensionless_weber(rho, V, L, sigma):
    return safe_div(rho * V**2 * L, sigma)

def dimensionless_euler(dP, rho, V):
    return safe_div(dP, rho * V**2)

def dimensionless_strouhal(f, L, V):
    return safe_div(f * L, V)

def buckingham_pi_count(n_vars, n_dims):
    return n_vars - n_dims

# =============================================================================
# Category 12: Fluid-Structure Interaction
# =============================================================================

def natural_frequency_fluid_column(K, rho, L, A):
    return safe_div(math.sqrt(safe_div(K * A, rho * L)), 2.0 * math.pi)

def added_mass_coefficient(C_m, V_fluid, rho_fluid):
    return C_m * V_fluid * rho_fluid

def vortex_shedding_frequency(St, V, D):
    return safe_div(St * V, D)

def reduced_velocity_viv(U, f_n, D):
    return safe_div(U, f_n * D)

def fluid_elastic_instability(f_n, D, m, rho, zeta=0.01):
    K_c = 2.0 * math.pi * zeta * m / (rho * D**2)
    return K_c * f_n * D


# =============================================================================
# Category 13: Gas Flow Calculations
# =============================================================================

def gas_density_ideal(P, T, R=287.0):
    """Ideal gas density: rho = P/(R*T)"""
    return safe_div(P, R * T)

def gas_density_real(P, T, Z, R=287.0):
    """Real gas density with compressibility factor"""
    return safe_div(P, Z * R * T)

def compressibility_factor_Papay(P_pr, T_pr):
    """Z-factor using Papay correlation (valid 0.2<P_pr<15, 1.0<T_pr<3.0)"""
    if P_pr <= 0 or T_pr <= 0: return None
    return 1.0 - 3.52 * P_pr / (10.0 ** (0.9813 * T_pr)) + 0.274 * P_pr**2 / (10.0 ** (0.8157 * T_pr))

def gas_viscosity_LGE(rho_g, T, Mw, T_pc=None):
    """Gas viscosity via Lee-Gonzalez-Eakin correlation (micropoise -> Pa-s)"""
    if T <= 0 or Mw <= 0: return None
    rho_g_m = rho_g * 1e-3  # kg/m3 -> g/cm3 approx
    K = (9.4 + 0.02 * Mw) * T**1.5 / (209.0 + 19.0 * Mw + T)
    X = 3.5 + 986.0 / T + 0.01 * Mw
    Y = 2.4 - 0.2 * X
    mu_g_cp = K * math.exp(X * rho_g_m**Y) * 1e-4  # micropoise -> cP -> Pa-s
    return mu_g_cp * 0.001  # cP -> Pa-s

def gas_mass_flow_isothermal(P1, P2, T, L, D, f, R=287.0):
    """Isothermal compressible pipe mass flow rate"""
    if P1 <= 0 or P2 <= 0 or T <= 0 or L <= 0 or D <= 0 or f <= 0: return None
    A = math.pi * D**2 / 4.0
    P_m = (P1 + P2) / 2.0  # mean pressure
    rho_m = safe_div(P_m, R * T)
    dP = P1 - P2
    if dP <= 0: return None
    V_m = math.sqrt(safe_div(2.0 * dP * D, f * L * rho_m))
    if V_m is None: return None
    return rho_m * A * V_m

def gas_weymouth_flow(P1_psi, P2_psi, T_R, L_mi, D_in, SG, Z=1.0, E=1.0):
    """Weymouth equation for gas pipeline flow (USCS -> SCF/day)
    P1,P2: psia; T: deg Rankine; L: miles; D: inches; SG: specific gravity
    Returns: Q in SCF/day"""
    if P1_psi <= P2_psi or T_R <= 0 or L_mi <= 0 or D_in <= 0: return None
    Ts = 520.0  # standard temp R
    Ps = 14.7   # standard pressure psia
    const = 433.49 * E * (Ts / Ps)
    numer = (P1_psi**2 - P2_psi**2) * D_in**(16.0/3.0)
    denom = SG * T_R * L_mi * Z
    return const * math.sqrt(safe_div(numer, denom))

def gas_panhandle_a_flow(P1_psi, P2_psi, T_R, L_mi, D_in, SG, Z=1.0, E=1.0):
    """Panhandle A equation (high Re, large diameter pipelines)
    Returns: Q in SCF/day"""
    if P1_psi <= P2_psi or T_R <= 0 or L_mi <= 0 or D_in <= 0: return None
    Ts = 520.0; Ps = 14.7
    K = 435.87 * E * (Ts / Ps)**1.0788
    numer = (P1_psi**2 - P2_psi**2)**0.5394 * D_in**2.6182
    denom = (SG**0.8539 * T_R * L_mi * Z)**0.5394
    return safe_div(K * numer, denom)

def gas_panhandle_b_flow(P1_psi, P2_psi, T_R, L_mi, D_in, SG, Z=1.0, E=1.0):
    """Panhandle B equation (lower Re, medium pipelines)
    Returns: Q in SCF/day"""
    if P1_psi <= P2_psi or T_R <= 0 or L_mi <= 0 or D_in <= 0: return None
    Ts = 520.0; Ps = 14.7
    K = 737.0 * E * (Ts / Ps)**1.02
    numer = (P1_psi**2 - P2_psi**2)**0.51 * D_in**2.53
    denom = (SG**0.961 * T_R * L_mi * Z)**0.51
    return safe_div(K * numer, denom)

def gas_critical_pressure_ratio(k=1.4):
    """Critical pressure ratio for choked flow: r_c = (2/(k+1))^(k/(k-1))"""
    if k <= 1.0: return None
    return (2.0 / (k + 1.0)) ** (k / (k - 1.0))

def gas_orifice_mass_flow(C_d, A_o, P1, T1, P2, k=1.4, R=287.0, Y=None):
    """Compressible gas flow through orifice (non-choked or with expansion factor Y)
    Uses expansion factor Y for non-choked flow"""
    if P1 <= 0 or T1 <= 0 or A_o <= 0: return None
    rho1 = safe_div(P1, R * T1)
    if rho1 is None: return None
    dP = P1 - P2
    if dP <= 0: return None
    # Calculate expansion factor if not provided
    r_c = gas_critical_pressure_ratio(k)
    ratio = safe_div(P2, P1)
    if Y is None:
        if ratio is not None and ratio > (r_c or 0.528):
            Y = 1.0 - 0.333 * safe_div(P1 - P2, k * P1)
        else:
            Y = 0.85  # choked approximate
    return C_d * A_o * Y * math.sqrt(2.0 * rho1 * dP)

def gas_choked_mass_flow(C_d, A_t, P0, T0, k=1.4, R=287.0):
    """Choked (sonic) gas mass flow through nozzle/orifice
    m_dot = C_d * A_t * P0 / sqrt(T0) * sqrt(k/R * (2/(k+1))^((k+1)/(k-1)))"""
    if P0 <= 0 or T0 <= 0 or A_t <= 0: return None
    r_c = (2.0 / (k + 1.0)) ** ((k + 1.0) / (k - 1.0))
    return C_d * A_t * P0 * math.sqrt(safe_div(k, R * T0) * r_c)

def gas_nozzle_flow_efficiency(C_d, A_t, P0, T0, P_b, k=1.4, R=287.0, eta_n=0.95):
    """Real nozzle flow with efficiency factor
    Checks if choked or non-choked based on back pressure"""
    if P0 <= 0 or T0 <= 0 or A_t <= 0: return None
    r_c = gas_critical_pressure_ratio(k)
    ratio = safe_div(P_b, P0)
    if ratio is None: return None
    if ratio <= (r_c or 0.528):
        # Choked
        return eta_n * gas_choked_mass_flow(C_d, A_t, P0, T0, k, R)
    else:
        # Non-choked
        T2 = T0 * ratio ** ((k - 1.0) / k)
        V_exit = math.sqrt(2.0 * k * R * T0 / (k - 1.0) * (1.0 - ratio ** ((k - 1.0) / k)))
        rho_exit = safe_div(P_b, R * T2)
        if rho_exit is None or V_exit is None: return None
        return eta_n * rho_exit * A_t * V_exit

def gas_erosional_velocity(rho, C=100.0):
    """API RP 14E erosional velocity limit: V_e = C / sqrt(rho)
    C=100 for continuous, 125-150 for intermittent, 150-200 for non-corrosive"""
    if rho <= 0: return None
    return safe_div(C, math.sqrt(rho))

def gas_pipeline_linepack(V_pipe, P_avg, T_avg, Z=1.0, R=287.0):
    """Pipeline storage (line pack) capacity in standard m3
    Gas stored = V_pipe * P_avg / (Z * R * T_avg) * (T_s / T_avg)"""
    if T_avg <= 0: return None
    T_s = 288.7  # standard temp K (15C)
    P_s = 101325.0  # standard pressure Pa
    n_gas = safe_div(P_avg * V_pipe, Z * R * T_avg)
    if n_gas is None: return None
    return n_gas * R * T_s / P_s  # standard m3


# =============================================================================
# Formula Registry - All 130+ formulas organized by category
# =============================================================================

def get_all_formulas():
    """Return complete formula catalog organized by 12 categories."""
    return {
        '1_basic_properties': {
            'name': 'Basic Fluid Properties', 'icon': 'flask', 'count': 8,
            'desc': 'Density, viscosity, bulk modulus, surface tension, vapor pressure',
            'formulas': [
                {'id': 'density', 'name': 'Density', 'eq': 'rho = m / V', 'inputs': ['mass', 'volume'], 'output': 'density'},
                {'id': 'specific_weight', 'name': 'Specific Weight', 'eq': 'gamma = rho * g', 'inputs': ['rho', 'g'], 'output': 'gamma'},
                {'id': 'specific_gravity', 'name': 'Specific Gravity', 'eq': 'SG = rho / rho_ref', 'inputs': ['rho', 'rho_ref'], 'output': 'SG'},
                {'id': 'dynamic_viscosity', 'name': 'Dynamic Viscosity', 'eq': 'mu = nu * rho', 'inputs': ['nu', 'rho'], 'output': 'mu'},
                {'id': 'kinematic_viscosity', 'name': 'Kinematic Viscosity', 'eq': 'nu = mu / rho', 'inputs': ['mu', 'rho'], 'output': 'nu'},
                {'id': 'bulk_modulus', 'name': 'Bulk Modulus', 'eq': 'K = -V * dP/dV', 'inputs': ['dp', 'dV', 'V'], 'output': 'K'},
                {'id': 'surface_tension', 'name': 'Surface Tension Force', 'eq': 'F = sigma * L', 'inputs': ['sigma', 'L'], 'output': 'F'},
                {'id': 'vapor_pressure', 'name': 'Vapor Pressure (Antoine)', 'eq': 'log10(Pv) = A-B/(C+T)', 'inputs': ['A', 'B', 'C', 'T'], 'output': 'P_v'},
            ]
        },
        '2_hydrostatics': {
            'name': 'Hydrostatics', 'icon': 'water', 'count': 8,
            'desc': 'Pressure at depth, manometer, buoyancy, capillary rise',
            'formulas': [
                {'id': 'hydrostatic_pressure', 'name': 'Pressure at Depth', 'eq': 'P = P0 + rho*g*h', 'inputs': ['rho', 'h', 'P0', 'g'], 'output': 'P'},
                {'id': 'manometer', 'name': 'Manometer Equation', 'eq': 'dP = rho_f * g * h', 'inputs': ['rho_fluid', 'h_diff', 'g'], 'output': 'dP'},
                {'id': 'hydrostatic_force_plane', 'name': 'Force on Plane Surface', 'eq': 'F = rho*g*h_c*A', 'inputs': ['rho', 'h_c', 'A', 'g'], 'output': 'F'},
                {'id': 'center_of_pressure', 'name': 'Center of Pressure', 'eq': 'y_cp = y_c+I_xx/(y_c*A)', 'inputs': ['h_c', 'I_xx_c', 'A', 'theta'], 'output': 'y_cp'},
                {'id': 'buoyancy', 'name': 'Buoyancy (Archimedes)', 'eq': 'F_b = rho*g*V_d', 'inputs': ['rho_fluid', 'V_displaced', 'g'], 'output': 'F_b'},
                {'id': 'metacenter', 'name': 'Metacentric Height', 'eq': 'GM = I/V - BG', 'inputs': ['I_waterline', 'V_displaced', 'BG'], 'output': 'GM'},
                {'id': 'tank_height', 'name': 'Tank Fluid Height', 'eq': 'h = m/(rho*A)', 'inputs': ['mass', 'rho', 'area'], 'output': 'h'},
                {'id': 'capillary_rise', 'name': 'Capillary Rise', 'eq': 'h = 2*sigma*cos(theta)/(rho*g*R)', 'inputs': ['sigma', 'theta', 'rho', 'R', 'g'], 'output': 'h'},
            ]
        },
        '3_bernoulli': {
            'name': 'Continuity & Bernoulli', 'icon': 'chart-line', 'count': 10,
            'desc': 'Bernoulli equation, continuity, energy, momentum, cavitation',
            'formulas': [
                {'id': 'continuity', 'name': 'Continuity Equation', 'eq': 'V2 = A1*V1/A2', 'inputs': ['A1', 'V1', 'A2'], 'output': 'V2'},
                {'id': 'bernoulli_total_pressure', 'name': 'Bernoulli Total Pressure', 'eq': 'P_t = P+0.5*rho*V^2+rho*g*z', 'inputs': ['P', 'rho', 'V', 'z', 'g'], 'output': 'P_t'},
                {'id': 'bernoulli_velocity', 'name': 'Bernoulli Velocity', 'eq': 'V2 = sqrt(delta_P)', 'inputs': ['P1', 'P2', 'rho', 'z1', 'z2', 'V1', 'g'], 'output': 'V2'},
                {'id': 'bernoulli_dp', 'name': 'Bernoulli Pressure Drop', 'eq': 'dP = 0.5*rho*(V2^2-V1^2)+rho*g*dz', 'inputs': ['rho', 'V1', 'V2', 'z1', 'z2', 'g'], 'output': 'dP'},
                {'id': 'energy_eq', 'name': 'Energy Equation', 'eq': 'Head balance', 'inputs': ['h_pump', 'h_turbine', 'h_loss', 'P1', 'P2', 'V1', 'V2', 'z1', 'z2', 'rho', 'g'], 'output': 'E_balance'},
                {'id': 'momentum_force', 'name': 'Momentum Force', 'eq': 'F = rho*Q*(V_out-V_in)', 'inputs': ['rho', 'Q', 'V_out', 'V_in'], 'output': 'F'},
                {'id': 'cavitation_number', 'name': 'Cavitation Number', 'eq': 'sigma = (P-Pv)/(0.5*rho*V^2)', 'inputs': ['P', 'P_v', 'rho', 'V'], 'output': 'sigma'},
                {'id': 'stagnation', 'name': 'Stagnation Pressure', 'eq': 'P0 = P+0.5*rho*V^2', 'inputs': ['P_static', 'rho', 'V'], 'output': 'P0'},
                {'id': 'volume_flow', 'name': 'Volumetric Flow Rate', 'eq': 'Q = A * V', 'inputs': ['A', 'V'], 'output': 'Q'},
                {'id': 'mass_flow', 'name': 'Mass Flow Rate', 'eq': 'm_dot = rho * Q', 'inputs': ['rho', 'Q'], 'output': 'm_dot'},
            ]
        },
        '4_pipe_flow': {
            'name': 'Pipe Flow & Friction', 'icon': 'pipe', 'count': 20,
            'desc': 'Reynolds, Darcy-Weisbach, friction factors, minor losses',
            'formulas': [
                {'id': 'reynolds', 'name': 'Reynolds Number', 'eq': 'Re = rho*V*D/mu', 'inputs': ['rho', 'V', 'D', 'mu'], 'output': 'Re'},
                {'id': 'reynolds_nu', 'name': 'Re (Kinematic)', 'eq': 'Re = V*D/nu', 'inputs': ['V', 'D', 'nu'], 'output': 'Re'},
                {'id': 'f_laminar', 'name': 'f (Laminar)', 'eq': 'f = 64/Re', 'inputs': ['Re'], 'output': 'f'},
                {'id': 'f_blasius', 'name': 'f (Blasius)', 'eq': 'f = 0.316*Re^(-0.25)', 'inputs': ['Re'], 'output': 'f'},
                {'id': 'f_colebrook', 'name': 'f (Colebrook)', 'eq': '1/sqrt(f)=-2log(rr/3.7+2.51/(Re*sqrt(f)))', 'inputs': ['Re', 'epsilon', 'D'], 'output': 'f'},
                {'id': 'f_swamee_jain', 'name': 'f (Swamee-Jain)', 'eq': 'f = 0.25/[log(rr/3.7+5.74/Re^0.9)]^2', 'inputs': ['Re', 'epsilon', 'D'], 'output': 'f'},
                {'id': 'darcy_hf', 'name': 'Darcy-Weisbach h_f', 'eq': 'h_f = f*L/D*V^2/(2g)', 'inputs': ['f', 'L', 'D', 'V', 'g'], 'output': 'h_f'},
                {'id': 'darcy_dp', 'name': 'Darcy-Weisbach dP', 'eq': 'dP = f*L/D*0.5*rho*V^2', 'inputs': ['f', 'L', 'D', 'rho', 'V'], 'output': 'dP'},
                {'id': 'hazen_williams', 'name': 'Hazen-Williams V', 'eq': 'V = 0.849*C*R_h^0.63*S^0.54', 'inputs': ['C', 'R_h', 'S'], 'output': 'V'},
                {'id': 'hydraulic_radius', 'name': 'Hydraulic Radius', 'eq': 'R_h = A/P_w', 'inputs': ['A', 'P_wetted'], 'output': 'R_h'},
                {'id': 'hydraulic_diameter', 'name': 'Hydraulic Diameter', 'eq': 'D_h = 4*A/P_w', 'inputs': ['A', 'P_wetted'], 'output': 'D_h'},
                {'id': 'minor_loss_head', 'name': 'Minor Loss Head', 'eq': 'h_m = K*V^2/(2g)', 'inputs': ['K', 'V', 'g'], 'output': 'h_m'},
                {'id': 'minor_loss_dp', 'name': 'Minor Loss dP', 'eq': 'dP_m = K*0.5*rho*V^2', 'inputs': ['K', 'rho', 'V'], 'output': 'dP_m'},
                {'id': 'sudden_expansion', 'name': 'Sudden Expansion', 'eq': 'K = (1-A1/A2)^2', 'inputs': ['A1', 'A2', 'V1', 'rho'], 'output': 'dP_sudden'},
                {'id': 'sudden_contraction', 'name': 'Sudden Contraction', 'eq': 'dP = K*0.5*rho*V2^2', 'inputs': ['A1', 'A2', 'V2', 'rho'], 'output': 'dP_contraction'},
                {'id': 'equiv_length', 'name': 'Equivalent Length', 'eq': 'L_eq = K_tot*D/f', 'inputs': ['K_total', 'D', 'f'], 'output': 'L_eq'},
                {'id': 'pipe_exit', 'name': 'Pipe Exit Loss', 'eq': 'dP = 1.0*0.5*rho*V^2', 'inputs': ['V', 'rho'], 'output': 'dP_exit'},
                {'id': 'pipe_entrance', 'name': 'Pipe Entrance Loss', 'eq': 'K varies with r/D', 'inputs': ['V', 'rho', 'r_D'], 'output': 'dP_entrance'},
                {'id': 'pipe_bend', 'name': 'Pipe Bend Loss', 'eq': 'K = f(R/D, theta)', 'inputs': ['V', 'rho', 'R_bend', 'D', 'theta_deg'], 'output': 'dP_bend'},
            ]
        },
        '5_open_channel': {
            'name': 'Open Channel Flow', 'icon': 'river', 'count': 9,
            'desc': 'Manning, Chezy, Froude, critical depth, hydraulic jump, weirs',
            'formulas': [
                {'id': 'froude', 'name': 'Froude Number', 'eq': 'Fr = V/sqrt(g*y_h)', 'inputs': ['V', 'y_h', 'g'], 'output': 'Fr'},
                {'id': 'manning_v', 'name': 'Manning Velocity', 'eq': 'V = (1/n)*R_h^(2/3)*S^(1/2)', 'inputs': ['n', 'R_h', 'S'], 'output': 'V'},
                {'id': 'manning_q', 'name': 'Manning Discharge', 'eq': 'Q = (1/n)*A*R_h^(2/3)*S^(1/2)', 'inputs': ['n', 'A', 'R_h', 'S'], 'output': 'Q'},
                {'id': 'chezy_v', 'name': 'Chezy Velocity', 'eq': 'V = C*sqrt(R_h*S)', 'inputs': ['C', 'R_h', 'S'], 'output': 'V'},
                {'id': 'critical_depth_rect', 'name': 'Critical Depth (Rect.)', 'eq': 'y_c = (q^2/g)^(1/3)', 'inputs': ['Q', 'b', 'g'], 'output': 'y_c'},
                {'id': 'specific_energy', 'name': 'Specific Energy', 'eq': 'E = y+Q^2/(2g*A^2)', 'inputs': ['y', 'Q', 'A_flow', 'g'], 'output': 'E'},
                {'id': 'hydraulic_jump_ratio', 'name': 'Hydraulic Jump Ratio', 'eq': 'y2/y1=0.5*(sqrt(1+8Fr1^2)-1)', 'inputs': ['Fr1'], 'output': 'y_ratio'},
                {'id': 'hydraulic_jump_energy', 'name': 'Jump Energy Loss', 'eq': 'dE = (y2-y1)^3/(4*y1*y2)', 'inputs': ['y1', 'y2'], 'output': 'dE'},
                {'id': 'weir_rect', 'name': 'Rectangular Weir', 'eq': 'Q = (2/3)*C_d*b*sqrt(2g)*H^1.5', 'inputs': ['C_d', 'b', 'H', 'g'], 'output': 'Q'},
            ]
        },
        '6_compressible': {
            'name': 'Compressible Flow', 'icon': 'rocket', 'count': 12,
            'desc': 'Mach, isentropic flow, normal shock, Prandtl-Meyer, nozzle flow',
            'formulas': [
                {'id': 'speed_of_sound', 'name': 'Speed of Sound', 'eq': 'a = sqrt(k*R*T)', 'inputs': ['k', 'R', 'T'], 'output': 'a'},
                {'id': 'mach', 'name': 'Mach Number', 'eq': 'M = V/a', 'inputs': ['V', 'a'], 'output': 'M'},
                {'id': 'isentropic_T', 'name': 'Isentropic T/T0', 'eq': 'T/T0=(1+(k-1)/2*M^2)^(-1)', 'inputs': ['M', 'k'], 'output': 'T_ratio'},
                {'id': 'isentropic_P', 'name': 'Isentropic P/P0', 'eq': 'P/P0=(1+(k-1)/2*M^2)^(-k/(k-1))', 'inputs': ['M', 'k'], 'output': 'P_ratio'},
                {'id': 'isentropic_rho', 'name': 'Isentropic rho/rho0', 'eq': 'rho/rho0=(1+(k-1)/2*M^2)^(-1/(k-1))', 'inputs': ['M', 'k'], 'output': 'rho_ratio'},
                {'id': 'area_ratio', 'name': 'A/A* Ratio', 'eq': 'A/A*=f(M,k)', 'inputs': ['M', 'k'], 'output': 'A_ratio'},
                {'id': 'normal_shock_P', 'name': 'Normal Shock P2/P1', 'eq': 'P2/P1=1+2k/(k+1)*(M1^2-1)', 'inputs': ['M1', 'k'], 'output': 'P_ratio'},
                {'id': 'normal_shock_rho', 'name': 'Normal Shock rho2/rho1', 'eq': '(k+1)M1^2/((k-1)M1^2+2)', 'inputs': ['M1', 'k'], 'output': 'rho_ratio'},
                {'id': 'normal_shock_M2', 'name': 'Normal Shock M2', 'eq': 'M2 from Rankine-Hugoniot', 'inputs': ['M1', 'k'], 'output': 'M2'},
                {'id': 'pm_angle', 'name': 'Prandtl-Meyer Angle', 'eq': 'nu(M)', 'inputs': ['M', 'k'], 'output': 'nu'},
                {'id': 'nozzle_mass_flow', 'name': 'Choked Nozzle m_dot', 'eq': 'm_dot=P0*A_t/sqrt(T0)*factor', 'inputs': ['P0', 'T0', 'A_t', 'k', 'R'], 'output': 'm_dot'},
                {'id': 'expansion_velocity', 'name': 'Expansion Velocity', 'eq': 'V=sqrt(2kRT0/(k-1)*(1-(Pe/P0)^((k-1)/k)))', 'inputs': ['P0', 'P_exit', 'T0', 'k', 'R'], 'output': 'V_exit'},
            ]
        },
        '7_orifice_valve': {
            'name': 'Orifices & Valves', 'icon': 'valve', 'count': 17,
            'desc': 'Cv/Kv coefficients, pressure drop, choked flow, cavitation, venturi',
            'formulas': [
                {'id': 'orifice_flow', 'name': 'Orifice Flow', 'eq': 'Q=C_d*A*sqrt(2*dP/rho)', 'inputs': ['C_d', 'A_o', 'rho', 'dP'], 'output': 'Q'},
                {'id': 'valve_Cv', 'name': 'Flow Coefficient Cv', 'eq': 'Cv=Q*sqrt(SG/dP)', 'inputs': ['Q_gpm', 'dP_psi', 'SG'], 'output': 'Cv'},
                {'id': 'flow_from_Cv', 'name': 'Flow from Cv', 'eq': 'Q=Cv*sqrt(dP/SG)', 'inputs': ['Cv', 'dP_psi', 'SG'], 'output': 'Q_gpm'},
                {'id': 'Kv_to_Cv', 'name': 'Kv to Cv', 'eq': 'Cv=1.156*Kv', 'inputs': ['Kv'], 'output': 'Cv'},
                {'id': 'Cv_to_Kv', 'name': 'Cv to Kv', 'eq': 'Kv=0.865*Cv', 'inputs': ['Cv'], 'output': 'Kv'},
                {'id': 'valve_dp_from_Cv', 'name': 'dP from Cv', 'eq': 'dP=SG*(Q/Cv)^2', 'inputs': ['Q_gpm', 'Cv', 'SG'], 'output': 'dP'},
                {'id': 'choked_dP', 'name': 'Choked Flow dP', 'eq': 'dP_c=FL^2*(P1-F_F*P_v)', 'inputs': ['P1', 'P_v', 'FL'], 'output': 'dP_choked'},
                {'id': 'cavitation_index', 'name': 'Cavitation Index', 'eq': 'K=(P_d-P_v)/(0.5*rho*V^2)', 'inputs': ['P_d', 'P_v', 'rho', 'V'], 'output': 'K_cav'},
                {'id': 'valve_authority', 'name': 'Valve Authority', 'eq': 'N=dP_valve/dP_total', 'inputs': ['dP_valve', 'dP_total'], 'output': 'N'},
                {'id': 'torricelli', 'name': 'Torricelli Velocity', 'eq': 'V=sqrt(2*g*h)', 'inputs': ['h', 'g'], 'output': 'V'},
                {'id': 'nozzle_v', 'name': 'Nozzle Velocity (Incomp.)', 'eq': 'V=sqrt(2*dP/rho)', 'inputs': ['dP', 'rho'], 'output': 'V'},
                {'id': 'Cd_via_Re', 'name': 'C_d via Re', 'eq': 'Reader-Harris/Gallagher', 'inputs': ['Re', 'beta'], 'output': 'C_d'},
                {'id': 'expansion_factor', 'name': 'Expansion Factor Y', 'eq': 'Y=1-(0.41+0.35*b^4)*dP/(P1*k)', 'inputs': ['k', 'beta', 'dP', 'P1'], 'output': 'Y'},
                {'id': 'orifice_velocity', 'name': 'Orifice Velocity', 'eq': 'V_o=V_pipe*(D/d)^2', 'inputs': ['D', 'd', 'V_pipe'], 'output': 'V_o'},
                {'id': 'venturi_q', 'name': 'Venturi Discharge', 'eq': 'Q=C_d*A_t/sqrt(1-b^4)*sqrt(2*dP/rho)', 'inputs': ['C_d', 'A_t', 'rho', 'dP', 'beta'], 'output': 'Q'},
                {'id': 'vena_contracta', 'name': 'Vena Contracta Area', 'eq': 'A_vc=C_c*A_o', 'inputs': ['A_o', 'C_c'], 'output': 'A_vc'},
                {'id': 'flow_resistance', 'name': 'Flow Resistance', 'eq': 'R_f=dP/Q^2', 'inputs': ['dP', 'Q'], 'output': 'R_f'},
            ]
        },
        '8_boundary_layer': {
            'name': 'Boundary Layer & Drag', 'icon': 'wave', 'count': 10,
            'desc': 'BL thickness, drag/lift, Stokes drag, terminal velocity',
            'formulas': [
                {'id': 'bl_laminar', 'name': 'BL Thickness (Laminar)', 'eq': 'delta=5*x/sqrt(Re_x)', 'inputs': ['x', 'Re_x'], 'output': 'delta'},
                {'id': 'bl_turbulent', 'name': 'BL Thickness (Turbulent)', 'eq': 'delta=0.37*x/Re_x^(1/5)', 'inputs': ['x', 'Re_x'], 'output': 'delta'},
                {'id': 'cf_laminar', 'name': 'Skin Friction (Laminar)', 'eq': 'C_f=1.328/sqrt(Re_L)', 'inputs': ['Re_L'], 'output': 'C_f'},
                {'id': 'cf_turbulent', 'name': 'Skin Friction (Turbulent)', 'eq': 'C_f=0.074/Re_L^(1/5)', 'inputs': ['Re_L'], 'output': 'C_f'},
                {'id': 'drag_force', 'name': 'Drag Force', 'eq': 'F_D=0.5*C_D*rho*V^2*A', 'inputs': ['C_d', 'rho', 'V', 'A_ref'], 'output': 'F_D'},
                {'id': 'lift_force', 'name': 'Lift Force', 'eq': 'F_L=0.5*C_L*rho*V^2*A', 'inputs': ['C_l', 'rho', 'V', 'A'], 'output': 'F_L'},
                {'id': 'stokes_drag', 'name': 'Stokes Drag (Sphere)', 'eq': 'F_d=6*pi*mu*R*V', 'inputs': ['mu', 'R', 'V'], 'output': 'F_d'},
                {'id': 'cd_sphere', 'name': 'C_D for Sphere', 'eq': 'C_D=f(Re)', 'inputs': ['Re'], 'output': 'C_D'},
                {'id': 'terminal_v', 'name': 'Terminal Velocity (Stokes)', 'eq': 'V_t=2*R^2*(rho_p-rho_f)*g/(9*mu)', 'inputs': ['rho_p', 'rho_f', 'R', 'mu', 'g'], 'output': 'V_t'},
                {'id': 're_flat_plate', 'name': 'Flat Plate Reynolds', 'eq': 'Re_L=V*L/nu', 'inputs': ['V', 'L', 'nu'], 'output': 'Re_L'},
            ]
        },
        '9_fluid_power': {
            'name': 'Fluid Power / Hydraulics', 'icon': 'gear', 'count': 11,
            'desc': 'Pump/motor power, cylinder forces, accumulator, fluid spring',
            'formulas': [
                {'id': 'pump_power', 'name': 'Pump Power', 'eq': 'P=Q*dP/eta', 'inputs': ['Q', 'dP', 'eta'], 'output': 'P_pump'},
                {'id': 'hydraulic_power', 'name': 'Hydraulic Power', 'eq': 'P_h=Q*dP', 'inputs': ['Q', 'dP'], 'output': 'P_h'},
                {'id': 'cylinder_force', 'name': 'Cylinder Force', 'eq': 'F=P*A', 'inputs': ['P', 'A_piston', 'A_rod'], 'output': 'F'},
                {'id': 'cylinder_velocity', 'name': 'Cylinder Velocity', 'eq': 'V=Q/A', 'inputs': ['Q', 'A'], 'output': 'V'},
                {'id': 'motor_torque', 'name': 'Motor Torque', 'eq': 'T=q*dP*eta_m/(2*pi)', 'inputs': ['q_displacement', 'dP', 'eta_m'], 'output': 'T'},
                {'id': 'motor_speed', 'name': 'Motor Speed', 'eq': 'n=Q*eta_v/q', 'inputs': ['Q', 'q_displacement', 'eta_v'], 'output': 'n'},
                {'id': 'accumulator', 'name': 'Accumulator Sizing', 'eq': 'V_gas=V0*(P0/P1)^(1/n)', 'inputs': ['V0', 'P0', 'P1', 'n'], 'output': 'V_gas'},
                {'id': 'pressure_intensifier', 'name': 'Pressure Intensifier', 'eq': 'Ratio=A_large/A_small', 'inputs': ['A_large', 'A_small'], 'output': 'ratio'},
                {'id': 'fluid_spring', 'name': 'Fluid Spring Stiffness', 'eq': 'k_f=K*A^2/V', 'inputs': ['K_bulk', 'A', 'V'], 'output': 'k_f'},
                {'id': 'time_constant', 'name': 'Hydraulic Time Constant', 'eq': 'tau=V/Q', 'inputs': ['V', 'Q'], 'output': 'tau'},
                {'id': 'pump_eff', 'name': 'Overall Pump Eff.', 'eq': 'eta=eta_v*eta_m', 'inputs': ['eta_v', 'eta_m'], 'output': 'eta'},
            ]
        },
        '10_water_hammer': {
            'name': 'Water Hammer & Surge', 'icon': 'bolt', 'count': 5,
            'desc': 'Joukowsky pressure, wave speed, surge, reflection time',
            'formulas': [
                {'id': 'joukowsky', 'name': 'Joukowsky dP', 'eq': 'dP=rho*a*dV', 'inputs': ['rho', 'a', 'dV'], 'output': 'dP'},
                {'id': 'wave_speed', 'name': 'Wave Speed', 'eq': 'a=a0/sqrt(1+C*K*D/(E*e))', 'inputs': ['K', 'rho', 'D', 'e', 'E_pipe'], 'output': 'a'},
                {'id': 'instant_surge', 'name': 'Instant Closure Surge', 'eq': 'dP=rho*a*V0', 'inputs': ['rho', 'a', 'V0'], 'output': 'dP_surge'},
                {'id': 'pipe_period', 'name': 'Pipe Period', 'eq': 'T_r=2*L/a', 'inputs': ['L', 'a'], 'output': 'T_r'},
                {'id': 'critical_tc', 'name': 'Critical Closure Time', 'eq': 't_c=2*L/a', 'inputs': ['L', 'a'], 'output': 't_c'},
            ]
        },
        '11_dimensional': {
            'name': 'Dimensional Analysis', 'icon': 'scale', 'count': 7,
            'desc': 'Re, Fr, Ma, We, Eu, St numbers, Buckingham Pi',
            'formulas': [
                {'id': 're_number', 'name': 'Reynolds Number', 'eq': 'Re=V*L/nu', 'inputs': ['V', 'L', 'nu'], 'output': 'Re'},
                {'id': 'fr_number', 'name': 'Froude Number', 'eq': 'Fr=V/sqrt(g*L)', 'inputs': ['V', 'L', 'g'], 'output': 'Fr'},
                {'id': 'ma_number', 'name': 'Mach Number', 'eq': 'Ma=V/a', 'inputs': ['V', 'a'], 'output': 'Ma'},
                {'id': 'we_number', 'name': 'Weber Number', 'eq': 'We=rho*V^2*L/sigma', 'inputs': ['rho', 'V', 'L', 'sigma'], 'output': 'We'},
                {'id': 'eu_number', 'name': 'Euler Number', 'eq': 'Eu=dP/(rho*V^2)', 'inputs': ['dP', 'rho', 'V'], 'output': 'Eu'},
                {'id': 'st_number', 'name': 'Strouhal Number', 'eq': 'St=f*L/V', 'inputs': ['f', 'L', 'V'], 'output': 'St'},
                {'id': 'buckingham_pi', 'name': 'Buckingham Pi Count', 'eq': 'n_pi=n_vars-n_dims', 'inputs': ['n_vars', 'n_dims'], 'output': 'n_pi'},
            ]
        },
        '12_fsi': {
            'name': 'Fluid-Structure Interaction', 'icon': 'sync', 'count': 5,
            'desc': 'Natural frequency, added mass, vortex shedding, VIV',
            'formulas': [
                {'id': 'fn_fluid_column', 'name': 'Fluid Column Nat. Freq.', 'eq': 'f_n=sqrt(KA/(rho*L))/(2pi)', 'inputs': ['K', 'rho', 'L', 'A'], 'output': 'f_n'},
                {'id': 'added_mass', 'name': 'Added Mass', 'eq': 'm_a=C_m*V_f*rho_f', 'inputs': ['C_m', 'V_fluid', 'rho_fluid'], 'output': 'm_a'},
                {'id': 'vortex_shedding', 'name': 'Vortex Shedding Freq.', 'eq': 'f_vs=St*V/D', 'inputs': ['St', 'V', 'D'], 'output': 'f_vs'},
                {'id': 'reduced_velocity', 'name': 'Reduced Velocity (VIV)', 'eq': 'V_r=U/(f_n*D)', 'inputs': ['U', 'f_n', 'D'], 'output': 'V_r'},
                {'id': 'fluid_elastic', 'name': 'Fluid-Elastic Instability', 'eq': 'U_c=K_c*f_n*D', 'inputs': ['f_n', 'D', 'm', 'rho', 'zeta'], 'output': 'U_crit'},
            ]
        },
        '13_gas_flow': {
            'name': 'Gas Flow Calculations', 'icon': 'rocket', 'count': 14,
            'desc': 'Compressible pipe flow, Weymouth/Panhandle, choked orifice, line pack',
            'formulas': [
                {'id': 'gas_density_ideal', 'name': 'Ideal Gas Density', 'eq': 'rho=P/(R*T)', 'inputs': ['P', 'T', 'R'], 'output': 'rho'},
                {'id': 'gas_density_real', 'name': 'Real Gas Density (Z)', 'eq': 'rho=P/(Z*R*T)', 'inputs': ['P', 'T', 'Z', 'R'], 'output': 'rho'},
                {'id': 'z_factor_papay', 'name': 'Z-Factor (Papay)', 'eq': 'Z=1-3.52*P_pr/10^(0.98T_pr)+0.274*P_pr^2/10^(0.82T_pr)', 'inputs': ['P_pr', 'T_pr'], 'output': 'Z'},
                {'id': 'gas_viscosity', 'name': 'Gas Viscosity (LGE)', 'eq': 'mu=K*exp(X*rho_g^Y)', 'inputs': ['rho_g', 'T', 'Mw'], 'output': 'mu'},
                {'id': 'isothermal_flow', 'name': 'Isothermal Pipe Gas Flow', 'eq': 'm_dot=rho_m*A*V_m', 'inputs': ['P1', 'P2', 'T', 'L', 'D', 'f', 'R'], 'output': 'm_dot'},
                {'id': 'weymouth', 'name': 'Weymouth Equation', 'eq': 'Q=433.49*E*(Ts/Ps)*sqrt((P1^2-P2^2)*D^(16/3)/(SG*T*L*Z))', 'inputs': ['P1_psi', 'P2_psi', 'T_R', 'L_mi', 'D_in', 'SG', 'Z', 'E'], 'output': 'Q_scfd'},
                {'id': 'panhandle_a', 'name': 'Panhandle A', 'eq': 'Q=435.87*E*(Ts/Ps)^1.0788*(dP^2^0.5394*D^2.6182/(SG^0.8539*T*L*Z)^0.5394)', 'inputs': ['P1_psi', 'P2_psi', 'T_R', 'L_mi', 'D_in', 'SG', 'Z', 'E'], 'output': 'Q_scfd'},
                {'id': 'panhandle_b', 'name': 'Panhandle B', 'eq': 'Q=737*E*(Ts/Ps)^1.02*(dP^2^0.51*D^2.53/(SG^0.961*T*L*Z)^0.51)', 'inputs': ['P1_psi', 'P2_psi', 'T_R', 'L_mi', 'D_in', 'SG', 'Z', 'E'], 'output': 'Q_scfd'},
                {'id': 'gas_critical_ratio', 'name': 'Critical Pressure Ratio', 'eq': 'r_c=(2/(k+1))^(k/(k-1))', 'inputs': ['k'], 'output': 'r_c'},
                {'id': 'gas_orifice_flow', 'name': 'Gas Orifice Flow', 'eq': 'm_dot=C_d*A*Y*sqrt(2*rho*dP)', 'inputs': ['C_d', 'A_o', 'P1', 'T1', 'P2', 'k', 'R'], 'output': 'm_dot'},
                {'id': 'gas_choked_flow', 'name': 'Choked Gas Flow', 'eq': 'm_dot=C_d*A_t*P0/sqrt(T0)*sqrt(k/R*(2/(k+1))^((k+1)/(k-1)))', 'inputs': ['C_d', 'A_t', 'P0', 'T0', 'k', 'R'], 'output': 'm_dot_choked'},
                {'id': 'gas_nozzle_eff', 'name': 'Nozzle Flow w/ Efficiency', 'eq': 'm_dot=C_d*A*eta*check_choked(P_b/P0)', 'inputs': ['C_d', 'A_t', 'P0', 'T0', 'P_b', 'k', 'R', 'eta_n'], 'output': 'm_dot'},
                {'id': 'erosional_velocity', 'name': 'Erosional Velocity (API RP 14E)', 'eq': 'V_e=C/sqrt(rho)', 'inputs': ['rho', 'C'], 'output': 'V_e'},
                {'id': 'line_pack', 'name': 'Pipeline Line Pack', 'eq': 'V_std=V_pipe*P_avg/(Z*R*T_avg)*Ts/T_avg_to_std', 'inputs': ['V_pipe', 'P_avg', 'T_avg', 'Z', 'R'], 'output': 'V_scm'},
            ]
        },
        '13_gas_flow': {
            'name': 'Gas Flow Calculations', 'icon': 'rocket', 'count': 14,
            'desc': 'Compressible pipe flow, Weymouth/Panhandle, choked orifice, line pack',
            'formulas': [
                {'id': 'gas_density_ideal', 'name': 'Ideal Gas Density', 'eq': 'rho=P/(R*T)', 'inputs': ['P', 'T', 'R'], 'output': 'rho'},
                {'id': 'gas_density_real', 'name': 'Real Gas Density (Z)', 'eq': 'rho=P/(Z*R*T)', 'inputs': ['P', 'T', 'Z', 'R'], 'output': 'rho'},
                {'id': 'z_factor_papay', 'name': 'Z-Factor (Papay)', 'eq': 'Z=1-3.52*P_pr/10^(0.98T_pr)+0.274*P_pr^2/10^(0.82T_pr)', 'inputs': ['P_pr', 'T_pr'], 'output': 'Z'},
                {'id': 'gas_viscosity', 'name': 'Gas Viscosity (LGE)', 'eq': 'mu=K*exp(X*rho_g^Y)', 'inputs': ['rho_g', 'T', 'Mw'], 'output': 'mu'},
                {'id': 'isothermal_flow', 'name': 'Isothermal Pipe Gas Flow', 'eq': 'm_dot=rho_m*A*V_m', 'inputs': ['P1', 'P2', 'T', 'L', 'D', 'f', 'R'], 'output': 'm_dot'},
                {'id': 'weymouth', 'name': 'Weymouth Equation', 'eq': 'Q=433.49*E*(Ts/Ps)*sqrt((P1^2-P2^2)*D^(16/3)/(SG*T*L*Z))', 'inputs': ['P1_psi', 'P2_psi', 'T_R', 'L_mi', 'D_in', 'SG', 'Z', 'E'], 'output': 'Q_scfd'},
                {'id': 'panhandle_a', 'name': 'Panhandle A', 'eq': 'Q=435.87*E*(Ts/Ps)^1.08*(dP^2^0.54*D^2.62/(...))', 'inputs': ['P1_psi', 'P2_psi', 'T_R', 'L_mi', 'D_in', 'SG', 'Z', 'E'], 'output': 'Q_scfd'},
                {'id': 'panhandle_b', 'name': 'Panhandle B', 'eq': 'Q=737*E*(Ts/Ps)^1.02*(dP^2^0.51*D^2.53/(...))', 'inputs': ['P1_psi', 'P2_psi', 'T_R', 'L_mi', 'D_in', 'SG', 'Z', 'E'], 'output': 'Q_scfd'},
                {'id': 'gas_critical_ratio', 'name': 'Critical Pressure Ratio', 'eq': 'r_c=(2/(k+1))^(k/(k-1))', 'inputs': ['k'], 'output': 'r_c'},
                {'id': 'gas_orifice_flow', 'name': 'Gas Orifice Flow', 'eq': 'm_dot=C_d*A*Y*sqrt(2*rho*dP)', 'inputs': ['C_d', 'A_o', 'P1', 'T1', 'P2', 'k', 'R'], 'output': 'm_dot'},
                {'id': 'gas_choked_flow', 'name': 'Choked Gas Flow', 'eq': 'm_dot=C_d*A_t*P0/sqrt(T0)*sqrt(k/R*(2/(k+1))^((k+1)/(k-1)))', 'inputs': ['C_d', 'A_t', 'P0', 'T0', 'k', 'R'], 'output': 'm_dot_choked'},
                {'id': 'gas_nozzle_eff', 'name': 'Nozzle Flow w/ Efficiency', 'eq': 'm_dot=C_d*A*eta*check_choked(P_b/P0)', 'inputs': ['C_d', 'A_t', 'P0', 'T0', 'P_b', 'k', 'R', 'eta_n'], 'output': 'm_dot'},
                {'id': 'erosional_velocity', 'name': 'Erosional Velocity (API RP 14E)', 'eq': 'V_e=C/sqrt(rho)', 'inputs': ['rho', 'C'], 'output': 'V_e'},
                {'id': 'line_pack', 'name': 'Pipeline Line Pack', 'eq': 'V_std=V_pipe*P_avg/(Z*R*T_avg)', 'inputs': ['V_pipe', 'P_avg', 'T_avg', 'Z', 'R'], 'output': 'V_scm'},
            ]
        },


        '14_non_newtonian': {
            'name': 'Non-Newtonian Fluids', 'icon': 'chart-line', 'count': 8,
            'desc': 'Bingham, Power-law, Herschel-Bulkley, Casson models',
            'formulas': [
                {'id': 'bingham_shear', 'name': 'Bingham Shear Stress', 'eq': 'tau = tau_y + mu_p * gamma_dot', 'inputs': ['tau_y', 'mu_p', 'gamma_dot'], 'output': 'tau'},
                {'id': 'bingham_pipe_Q', 'name': 'Bingham Pipe Flow Rate', 'eq': 'Q = pi*R^4*dP/(8*mu_p*L) * (1 - 4/3*phi + phi^4/3)', 'inputs': ['tau_y', 'mu_p', 'dP', 'L', 'R_pipe'], 'output': 'Q'},
                {'id': 'power_law_mu_app', 'name': 'Power-Law Apparent Viscosity', 'eq': 'mu_app = K * gamma_dot^(n-1)', 'inputs': ['K', 'n', 'gamma_dot'], 'output': 'mu_app'},
                {'id': 'power_law_pipe_V', 'name': 'Power-Law Pipe Velocity', 'eq': 'V = (dP/(2*K*L))^(1/n) * n/(3n+1) * R^((n+1)/n)', 'inputs': ['K', 'n', 'dP', 'L', 'R_pipe'], 'output': 'V'},
                {'id': 're_gen_power_law', 'name': 'Gen. Reynolds (Power-Law)', 'eq': 'Re_MR = rho*V^(2-n)*D^n/(K*8^(n-1)*((3n+1)/(4n))^n)', 'inputs': ['rho', 'V', 'D', 'K', 'n'], 'output': 'Re_MR'},
                {'id': 'dodge_metzner_f', 'name': 'Dodge-Metzner Friction Factor', 'eq': '1/sqrt(f) = 4/n^0.75*log10(Re*f^(1-n/2)) - 0.4/n^1.2', 'inputs': ['Re_MR', 'n'], 'output': 'f'},
                {'id': 'hb_shear', 'name': 'Herschel-Bulkley Shear', 'eq': 'tau = tau_y + K * gamma_dot^n', 'inputs': ['tau_y', 'K', 'n', 'gamma_dot'], 'output': 'tau'},
                {'id': 'casson_shear', 'name': 'Casson Shear Stress', 'eq': 'sqrt(tau) = sqrt(tau_y) + sqrt(mu_c * gamma_dot)', 'inputs': ['tau_y', 'mu_c', 'gamma_dot'], 'output': 'tau'},
            ]
        },
        '15_multiphase': {
            'name': 'Multi-Phase Flow', 'icon': 'water', 'count': 9,
            'desc': 'Void fraction, two-phase density/viscosity, flow regimes',
            'formulas': [
                {'id': 'hom_void_frac', 'name': 'Homogeneous Void Fraction', 'eq': 'alpha = 1/(1 + (1-x)/x * rho_g/rho_l)', 'inputs': ['x', 'rho_g', 'rho_l'], 'output': 'alpha'},
                {'id': 'hom_tp_density', 'name': 'Two-Phase Density', 'eq': 'rho_tp = 1/(x/rho_g + (1-x)/rho_l)', 'inputs': ['x', 'rho_g', 'rho_l'], 'output': 'rho_tp'},
                {'id': 'mcadams_visc', 'name': 'McAdams Viscosity', 'eq': '1/mu_tp = x/mu_g + (1-x)/mu_l', 'inputs': ['x', 'mu_g', 'mu_l'], 'output': 'mu_tp'},
                {'id': 'LM_X', 'name': 'Lockhart-Martinelli X', 'eq': 'X = ((1-x)/x)^0.9*(rho_g/rho_l)^0.5*(mu_l/mu_g)^0.1', 'inputs': ['x', 'rho_g', 'rho_l', 'mu_g', 'mu_l'], 'output': 'X'},
                {'id': 'chisholm_phi2', 'name': 'Chisholm Multiplier', 'eq': 'phi_l^2 = 1 + C/X + 1/X^2', 'inputs': ['X', 'C'], 'output': 'phi_l2'},
                {'id': 'drift_flux_alpha', 'name': 'Drift Flux Void Fraction', 'eq': 'alpha = j_g/(C0*(j_g+j_l) + V_gj)', 'inputs': ['j_g', 'j_l', 'C0'], 'output': 'alpha_df'},
                {'id': 'baker_map', 'name': 'Baker Flow Map', 'eq': 'lambda=(rho_g/rho_air*rho_l/rho_w)^0.5; psi=sigma_w/sigma_st*...', 'inputs': ['G_g', 'G_l', 'lmbda', 'psi'], 'output': 'x_baker'},
                {'id': 'taitel_dukler', 'name': 'Taitel-Dukler Transition', 'eq': 'v_sg_crit = 0.25*(g*(rho_l-rho_g)*sigma/rho_l^2)^0.25', 'inputs': ['v_sg', 'D', 'rho_g', 'rho_l', 'sigma'], 'output': 'v_sg_crit'},
                {'id': 'slug_freq', 'name': 'Slug Frequency', 'eq': 'f_s = 0.0226*(v_sl/g/D*(19.75+v_m^2/g/D))^1.2', 'inputs': ['v_sl', 'v_sg', 'D'], 'output': 'f_s'},
            ]
        },
        '17_pumps_turbo': {
            'name': 'Pumps & Turbomachinery',
            'name_zh': '泵与叶轮机械',
            'formulas': [
                'pump_hydraulic_power', 'pump_shaft_power', 'pump_efficiency',
                'specific_speed_metric', 'specific_speed_imperial',
                'affinity_law_Q', 'affinity_law_H',
                'npsh_available', 'suction_specific_speed',
            ],
        },
        '18_flow_measurement': {
            'name': 'Flow Measurement',
            'name_zh': '流量测量',
            'formulas': [
                'venturi_flow_rate', 'venturi_mass_flow', 'orifice_flow_rate',
                'pitot_velocity', 'weir_rectangular', 'weir_vnotch',
                'nozzle_flow_rate', 'rotameter_flow',
            ],
        },
        '19_aerodynamics': {
            'name': 'External Aerodynamics',
            'name_zh': '外部空气动力学',
            'formulas': [
                'lift_force', 'drag_force', 'lift_drag_ratio', 'induced_drag',
                'skin_friction_drag', 'wave_drag', 'bluff_body_drag',
                'stall_speed', 'aspect_ratio_fx',
            ],
        },
        '20_turbulence': {
            'name': 'Turbulence',
            'name_zh': '湍流',
            'formulas': [
                'turbulence_intensity', 'turbulent_kinetic_energy',
                'kolmogorov_length_scale', 'kolmogorov_time_scale', 'kolmogorov_velocity_scale',
                'eddy_viscosity_mixing_length', 'reynolds_stress_uv',
                'viscous_sublayer_thickness', 'friction_velocity', 'logarithmic_law',
            ],
        },
        '21_cfd_basics': {
            'name': 'CFD Fundamentals',
            'name_zh': '计算流体力学基础',
            'formulas': [
                'cfl_condition', 'grid_reynolds_number', 'peclet_number',
                'courant_number_wave', 'numerical_diffusion_coeff',
                'mesh_reynolds_requirement', 'taylor_microscale',
                'turbulent_viscosity_ratio', 'dissipation_rate_estimate', 'y_plus_estimate',
            ],
        },
        '16_cavitation': {
            'name': 'Cavitation', 'icon': 'bolt', 'count': 8,
            'desc': 'Cavitation number, NPSH, bubble dynamics, erosion',
            'formulas': [
                {'id': 'cav_number', 'name': 'Cavitation Number', 'eq': 'sigma = (P_ref - P_v)/(0.5*rho*V^2)', 'inputs': ['P_ref', 'P_v', 'rho', 'V'], 'output': 'sigma_c'},
                {'id': 'thoma_param', 'name': 'Thoma Parameter', 'eq': 'sigma_T = (H_atm - H_v - H_s)/H', 'inputs': ['H_atm', 'H_v', 'H_s'], 'output': 'sigma_T'},
                {'id': 'npsh_a', 'name': 'NPSH Available', 'eq': 'NPSH_a = (P_atm-P_v)/(rho*g) + h_s - h_f', 'inputs': ['P_atm', 'P_v', 'h_s', 'h_f', 'rho'], 'output': 'NPSH_a'},
                {'id': 'npsh_r', 'name': 'NPSH Required (S)', 'eq': 'NPSH_r = (N*sqrt(Q)/S)^(4/3)', 'inputs': ['N', 'Q', 'S'], 'output': 'NPSH_r'},
                {'id': 'rayleigh_plesset', 'name': 'Rayleigh-Plesset Radius', 'eq': 'R = R0 + sqrt(2*(P_v-P_inf)/(3*rho))*t', 'inputs': ['R0', 'P_v', 'P_inf', 'rho', 't'], 'output': 'R_max'},
                {'id': 'bubble_freq', 'name': 'Bubble Natural Frequency', 'eq': 'f_n = 1/(2*pi*R0)*sqrt(3*k*P_inf/rho)', 'inputs': ['P_inf', 'rho', 'R0', 'k'], 'output': 'f_n'},
                {'id': 'cav_erosion', 'name': 'Cavitation Erosion Power', 'eq': 'P_eros = sigma_f*rho*V^3*A/2', 'inputs': ['rho', 'V', 'A', 'sigma_f'], 'output': 'P_eros'},
                {'id': 'crit_cav_factor', 'name': 'Critical Cavitation Factor', 'eq': 'sigma_cr = sigma_st/(0.5*rho*V^2*D)', 'inputs': ['V', 'D', 'sigma_st', 'rho'], 'output': 'sigma_cr'},
            ]
        },
        '17_pumps_turbo': {
            'name': 'Pumps & Turbomachinery', 'icon': 'gear', 'count': 9,
            'desc': 'Centrifugal/axial pump power, specific speed, affinity laws, NPSH',
            'formulas': [
                {'id': 'pump_hydraulic_power', 'name': 'Pump Hydraulic Power', 'eq': 'P_h = rho*g*Q*H', 'inputs': ['rho', 'Q', 'H', 'g'], 'output': 'P_h'},
                {'id': 'pump_shaft_power', 'name': 'Pump Shaft Power', 'eq': 'P_s = P_h/eta', 'inputs': ['P_h', 'eta'], 'output': 'P_s'},
                {'id': 'pump_efficiency', 'name': 'Pump Efficiency', 'eq': 'eta = P_h/P_s', 'inputs': ['P_h', 'P_s'], 'output': 'eta'},
                {'id': 'specific_speed_metric', 'name': 'Specific Speed (Metric)', 'eq': 'N_s = N*sqrt(Q)/H^(3/4)', 'inputs': ['N', 'Q', 'H'], 'output': 'N_s'},
                {'id': 'specific_speed_imperial', 'name': 'Specific Speed (US)', 'eq': 'N_s = N*sqrt(Q)/H^(3/4)', 'inputs': ['N_rpm', 'Q_gpm', 'H_ft'], 'output': 'N_s_us'},
                {'id': 'affinity_law_Q', 'name': 'Affinity Law - Flow', 'eq': 'Q2/Q1 = (D2/D1)^3*(N2/N1)', 'inputs': ['D1', 'D2', 'N1', 'N2'], 'output': 'Q_ratio'},
                {'id': 'affinity_law_H', 'name': 'Affinity Law - Head', 'eq': 'H2/H1 = (D2/D1)^2*(N2/N1)^2', 'inputs': ['D1', 'D2', 'N1', 'N2'], 'output': 'H_ratio'},
                {'id': 'npsh_available', 'name': 'NPSH Available', 'eq': 'NPSHa=(P_atm-P_v)/(rho*g)+h_s-h_f', 'inputs': ['P_atm', 'P_v', 'h_s', 'h_f', 'rho', 'g'], 'output': 'NPSHa'},
                {'id': 'suction_specific_speed', 'name': 'Suction Specific Speed', 'eq': 'N_ss=N*sqrt(Q)/NPSHr^(3/4)', 'inputs': ['N', 'Q', 'NPSHr'], 'output': 'N_ss'},
            ]
        },
        '18_flow_measurement': {
            'name': 'Flow Measurement', 'icon': 'chart-line', 'count': 8,
            'desc': 'Venturi, orifice, pitot tube, rotameter, weir, nozzle flow metering',
            'formulas': [
                {'id': 'venturi_flow_rate', 'name': 'Venturi Volumetric Flow', 'eq': 'Q=Cd*A2*sqrt(2*dp/(rho*(1-beta^4)))', 'inputs': ['Cd', 'A2', 'rho', 'dp', 'beta'], 'output': 'Q'},
                {'id': 'venturi_mass_flow', 'name': 'Venturi Mass Flow', 'eq': 'm_dot=Cd*A2*sqrt(2*rho*dp/(1-beta^4))', 'inputs': ['Cd', 'A2', 'rho', 'dp', 'beta'], 'output': 'm_dot'},
                {'id': 'orifice_flow_rate', 'name': 'Orifice Flow', 'eq': 'Q=Cd*A0*sqrt(2*dp/(rho*(1-beta^4)))', 'inputs': ['Cd', 'A0', 'rho', 'dp', 'beta'], 'output': 'Q'},
                {'id': 'pitot_velocity', 'name': 'Pitot Tube Velocity', 'eq': 'V=sqrt(2*dp/rho)', 'inputs': ['dp', 'rho'], 'output': 'V'},
                {'id': 'weir_rectangular', 'name': 'Weir (Rectangular)', 'eq': 'Q=Cd*2/3*b*sqrt(2g)*H^(3/2)', 'inputs': ['Cd', 'b', 'H'], 'output': 'Q'},
                {'id': 'weir_vnotch', 'name': 'Weir (V-Notch)', 'eq': 'Q=Cd*8/15*tan(theta/2)*sqrt(2g)*H^(5/2)', 'inputs': ['Cd', 'theta_deg', 'H'], 'output': 'Q'},
                {'id': 'nozzle_flow_rate', 'name': 'Nozzle Flow', 'eq': 'Q=Cd*A_n*sqrt(2*dp/rho)', 'inputs': ['Cd', 'A_n', 'rho', 'dp'], 'output': 'Q'},
                {'id': 'rotameter_flow', 'name': 'Rotameter Flow', 'eq': 'Q=Cd*A_a*sqrt(2g*V_f*(rho_f-rho)/(rho*A_f))', 'inputs': ['Cd', 'A_annulus', 'V_float', 'rho_f', 'rho'], 'output': 'Q'},
            ]
        },
        '19_aerodynamics': {
            'name': 'External Aerodynamics', 'icon': 'rocket', 'count': 9,
            'desc': 'Lift, drag, L/D, induced drag, skin friction, wave drag, stall speed',
            'formulas': [
                {'id': 'lift_force', 'name': 'Lift Force', 'eq': 'F_L=0.5*CL*rho*V^2*A', 'inputs': ['CL', 'rho', 'V', 'A'], 'output': 'F_L'},
                {'id': 'drag_force', 'name': 'Drag Force', 'eq': 'F_D=0.5*CD*rho*V^2*A', 'inputs': ['CD', 'rho', 'V', 'A'], 'output': 'F_D'},
                {'id': 'lift_drag_ratio', 'name': 'L/D Ratio', 'eq': 'L/D=CL/CD', 'inputs': ['CL', 'CD'], 'output': 'LD'},
                {'id': 'induced_drag', 'name': 'Induced Drag Coeff', 'eq': 'C_Di=CL^2/(pi*AR*e)', 'inputs': ['CL', 'AR', 'e'], 'output': 'CDi'},
                {'id': 'skin_friction_drag', 'name': 'Skin Friction Drag', 'eq': 'F_Df=0.5*Cf*rho*V^2*A_wet', 'inputs': ['Cf', 'rho', 'V', 'A_wet'], 'output': 'F_Df'},
                {'id': 'wave_drag', 'name': 'Wave Drag', 'eq': 'C_dw=10*(M-0.8)^3*(t/c)^2', 'inputs': ['M', 't_c'], 'output': 'Cdw'},
                {'id': 'bluff_body_drag', 'name': 'Bluff Body Drag', 'eq': 'F_D=0.5*CD*rho*V^2*A_front', 'inputs': ['CD', 'rho', 'V', 'A_front'], 'output': 'F_D'},
                {'id': 'stall_speed', 'name': 'Stall Speed', 'eq': 'V_stall=sqrt(2W/(rho*S*CL_max))', 'inputs': ['W', 'rho', 'S', 'CL_max'], 'output': 'V_stall'},
                {'id': 'aspect_ratio_fx', 'name': 'Aspect Ratio', 'eq': 'AR=b^2/S', 'inputs': ['b', 'S'], 'output': 'AR'},
            ]
        },
        '20_turbulence': {
            'name': 'Turbulence', 'icon': 'wave', 'count': 10,
            'desc': 'Intensity, TKE, Kolmogorov scales, eddy viscosity, Reynolds stress, wall laws',
            'formulas': [
                {'id': 'turbulence_intensity', 'name': 'Turbulence Intensity', 'eq': 'Tu = u_rms / U_mean', 'inputs': ['u_rms', 'U_mean'], 'output': 'Tu'},
                {'id': 'turbulent_kinetic_energy', 'name': 'Turbulent Kinetic Energy', 'eq': 'k = 0.5*(u_rms^2+v_rms^2+w_rms^2)', 'inputs': ['u_rms', 'v_rms', 'w_rms'], 'output': 'k'},
                {'id': 'kolmogorov_length_scale', 'name': 'Kolmogorov Length Scale', 'eq': 'eta = (nu^3/epsilon)^(1/4)', 'inputs': ['epsilon', 'nu'], 'output': 'eta'},
                {'id': 'kolmogorov_time_scale', 'name': 'Kolmogorov Time Scale', 'eq': 'tau_eta = sqrt(nu/epsilon)', 'inputs': ['epsilon', 'nu'], 'output': 'tau_eta'},
                {'id': 'kolmogorov_velocity_scale', 'name': 'Kolmogorov Velocity Scale', 'eq': 'u_eta = (nu*epsilon)^(1/4)', 'inputs': ['epsilon', 'nu'], 'output': 'u_eta'},
                {'id': 'eddy_viscosity_mixing_length', 'name': 'Mixing-Length Eddy Viscosity', 'eq': 'nu_t = l_m^2 * |dU/dy|', 'inputs': ['l_m', 'dU_dy'], 'output': 'nu_t'},
                {'id': 'reynolds_stress_uv', 'name': 'Reynolds Shear Stress', 'eq': 'tau_t = -rho * nu_t * dU/dy', 'inputs': ['rho', 'nu_t', 'dU_dy'], 'output': 'tau_t'},
                {'id': 'viscous_sublayer_thickness', 'name': 'Viscous Sublayer Thickness', 'eq': 'y_vs = 5*nu/u_tau (y+=5)', 'inputs': ['nu', 'u_tau'], 'output': 'y_vs'},
                {'id': 'friction_velocity', 'name': 'Friction Velocity', 'eq': 'u_tau = sqrt(tau_w/rho)', 'inputs': ['tau_w', 'rho'], 'output': 'u_tau'},
                {'id': 'logarithmic_law', 'name': 'Logarithmic Law', 'eq': 'u+ = (1/kappa)*ln(y+) + B', 'inputs': ['y_plus', 'kappa', 'B'], 'output': 'u_plus'},
            ]
        },
        '21_cfd_basics': {
            'name': 'CFD Fundamentals', 'icon': 'scale', 'count': 10,
            'desc': 'CFL, grid Reynolds, Peclet, y+, dissipation, numerical diffusion',
            'formulas': [
                {'id': 'cfl_condition', 'name': 'CFL Condition', 'eq': 'CFL = U*dt/dx', 'inputs': ['U', 'dt', 'dx'], 'output': 'CFL'},
                {'id': 'grid_reynolds_number', 'name': 'Grid Reynolds Number', 'eq': 'Re_dx = U*dx/nu', 'inputs': ['U', 'dx', 'nu'], 'output': 'Re_dx'},
                {'id': 'peclet_number', 'name': 'Peclet Number', 'eq': 'Pe = U*L/alpha', 'inputs': ['U', 'L', 'alpha'], 'output': 'Pe'},
                {'id': 'courant_number_wave', 'name': 'Wave Courant Number', 'eq': 'Co = c*dt/dx', 'inputs': ['c', 'dt', 'dx'], 'output': 'Co'},
                {'id': 'numerical_diffusion_coeff', 'name': 'Numerical Diffusion Coeff', 'eq': 'D_num ~ 0.5*U*dx', 'inputs': ['U', 'dx'], 'output': 'D_num'},
                {'id': 'mesh_reynolds_requirement', 'name': 'Mesh Reynolds Requirement', 'eq': 'dx_max < 2*nu/U', 'inputs': ['U', 'nu'], 'output': 'dx_max'},
                {'id': 'taylor_microscale', 'name': 'Taylor Microscale', 'eq': 'lambda = sqrt(15*nu*U/grid)', 'inputs': ['lambda_g', 'U', 'nu'], 'output': 'lambda_mu'},
                {'id': 'turbulent_viscosity_ratio', 'name': 'Turbulent Viscosity Ratio', 'eq': 'nu_t_ratio = nu_t / nu', 'inputs': ['nu_t', 'nu'], 'output': 'nu_t_ratio'},
                {'id': 'dissipation_rate_estimate', 'name': 'Dissipation Rate Estimate', 'eq': 'epsilon = Cmu^(3/4)*k^(3/2)/L', 'inputs': ['k', 'L_integral'], 'output': 'epsilon'},
                {'id': 'y_plus_estimate', 'name': 'y+ Estimate', 'eq': 'y+ = y*u_tau/nu', 'inputs': ['y', 'u_tau', 'nu'], 'output': 'y_plus'},
            ]
        },
    }


# =============================================================================
# Default inputs for each formula
# =============================================================================

DEFAULT_INPUTS = {
    'density': {'mass': 1.0, 'volume': 0.001},
    'specific_weight': {'rho': 1000, 'g': 9.81},
    'specific_gravity': {'rho': 850, 'rho_ref': 1000},
    'dynamic_viscosity': {'nu': 1e-6, 'rho': 1000},
    'kinematic_viscosity': {'mu': 0.001, 'rho': 1000},
    'bulk_modulus': {'dp': 1e6, 'dV': -1e-6, 'V': 0.001},
    'surface_tension': {'sigma': 0.0728, 'L': 0.1},
    'vapor_pressure': {'A': 8.07131, 'B': 1730.63, 'C': 233.426, 'T': 20},
    'hydrostatic_pressure': {'rho': 1000, 'h': 10, 'P0': 101325, 'g': 9.81},
    'manometer': {'rho_fluid': 1000, 'h_diff': 0.5, 'g': 9.81},
    'hydrostatic_force_plane': {'rho': 1000, 'h_c': 5, 'A': 2, 'g': 9.81},
    'center_of_pressure': {'h_c': 5, 'I_xx_c': 0.667, 'A': 2, 'theta': 90},
    'buoyancy': {'rho_fluid': 1000, 'V_displaced': 0.5, 'g': 9.81},
    'metacenter': {'I_waterline': 100, 'V_displaced': 50, 'BG': 0},
    'tank_height': {'mass': 1000, 'rho': 1000, 'area': 2},
    'capillary_rise': {'sigma': 0.0728, 'theta': 0, 'rho': 1000, 'R': 0.001, 'g': 9.81},
    'continuity': {'A1': 0.01, 'V1': 2, 'A2': 0.005},
    'bernoulli_total_pressure': {'P': 101325, 'rho': 1.2, 'V': 30, 'z': 0, 'g': 9.81},
    'bernoulli_velocity': {'P1': 200000, 'P2': 101325, 'rho': 1.2, 'z1': 0, 'z2': 0, 'V1': 10, 'g': 9.81},
    'bernoulli_dp': {'rho': 1.2, 'V1': 10, 'V2': 30, 'z1': 0, 'z2': 0, 'g': 9.81},
    'energy_eq': {'h_pump': 50, 'h_turbine': 0, 'h_loss': 5, 'P1': 101325, 'P2': 200000, 'V1': 2, 'V2': 1, 'z1': 0, 'z2': 10, 'rho': 1000, 'g': 9.81},
    'momentum_force': {'rho': 1000, 'Q': 0.1, 'V_out': 5, 'V_in': 2},
    'cavitation_number': {'P': 200000, 'P_v': 2340, 'rho': 1000, 'V': 20},
    'stagnation': {'P_static': 101325, 'rho': 1.2, 'V': 50},
    'volume_flow': {'A': 0.01, 'V': 5},
    'mass_flow': {'rho': 1.2, 'Q': 0.05},
    'reynolds': {'rho': 1000, 'V': 2, 'D': 0.05, 'mu': 0.001},
    'reynolds_nu': {'V': 2, 'D': 0.05, 'nu': 1e-6},
    'f_laminar': {'Re': 1000},
    'f_blasius': {'Re': 50000},
    'f_colebrook': {'Re': 100000, 'epsilon': 0.046, 'D': 50},
    'f_swamee_jain': {'Re': 100000, 'epsilon': 0.046, 'D': 50},
    'darcy_hf': {'f': 0.02, 'L': 100, 'D': 0.1, 'V': 3, 'g': 9.81},
    'darcy_dp': {'f': 0.02, 'L': 100, 'D': 0.1, 'rho': 1000, 'V': 3},
    'hazen_williams': {'C': 130, 'R_h': 0.05, 'S': 0.001},
    'hydraulic_radius': {'A': 0.2, 'P_wetted': 1.0},
    'hydraulic_diameter': {'A': 0.2, 'P_wetted': 1.0},
    'minor_loss_head': {'K': 2.5, 'V': 3, 'g': 9.81},
    'minor_loss_dp': {'K': 2.5, 'rho': 1000, 'V': 3},
    'sudden_expansion': {'A1': 0.01, 'A2': 0.02, 'V1': 5, 'rho': 1000},
    'sudden_contraction': {'A1': 0.02, 'A2': 0.01, 'V2': 5, 'rho': 1000},
    'equiv_length': {'K_total': 5, 'D': 0.1, 'f': 0.02},
    'pipe_exit': {'V': 3, 'rho': 1000},
    'pipe_entrance': {'V': 3, 'rho': 1000, 'r_D': 0},
    'pipe_bend': {'V': 3, 'rho': 1000, 'R_bend': 0.1, 'D': 0.05, 'theta_deg': 90},
    'froude': {'V': 3, 'y_h': 1.5, 'g': 9.81},
    'manning_v': {'n': 0.013, 'R_h': 0.5, 'S': 0.001},
    'manning_q': {'n': 0.013, 'A': 2, 'R_h': 0.5, 'S': 0.001},
    'chezy_v': {'C': 60, 'R_h': 0.5, 'S': 0.001},
    'critical_depth_rect': {'Q': 5, 'b': 3, 'g': 9.81},
    'specific_energy': {'y': 1.5, 'Q': 5, 'A_flow': 4.5, 'g': 9.81},
    'hydraulic_jump_ratio': {'Fr1': 3.5},
    'hydraulic_jump_energy': {'y1': 0.3, 'y2': 1.5},
    'weir_rect': {'C_d': 0.62, 'b': 2, 'H': 0.5, 'g': 9.81},
    'speed_of_sound': {'k': 1.4, 'R': 287, 'T': 293},
    'mach': {'V': 340, 'a': 340},
    'isentropic_T': {'M': 2, 'k': 1.4},
    'isentropic_P': {'M': 2, 'k': 1.4},
    'isentropic_rho': {'M': 2, 'k': 1.4},
    'area_ratio': {'M': 2, 'k': 1.4},
    'normal_shock_P': {'M1': 2, 'k': 1.4},
    'normal_shock_rho': {'M1': 2, 'k': 1.4},
    'normal_shock_M2': {'M1': 2, 'k': 1.4},
    'pm_angle': {'M': 2, 'k': 1.4},
    'nozzle_mass_flow': {'P0': 1e6, 'T0': 500, 'A_t': 0.001, 'k': 1.4, 'R': 287},
    'expansion_velocity': {'P0': 1e6, 'P_exit': 50000, 'T0': 500, 'k': 1.4, 'R': 287},
    'orifice_flow': {'C_d': 0.62, 'A_o': 0.0001, 'rho': 1000, 'dP': 50000},
    'valve_Cv': {'Q_gpm': 50, 'dP_psi': 5, 'SG': 1.0},
    'flow_from_Cv': {'Cv': 10, 'dP_psi': 5, 'SG': 1.0},
    'Kv_to_Cv': {'Kv': 10},
    'Cv_to_Kv': {'Cv': 10},
    'valve_dp_from_Cv': {'Q_gpm': 50, 'Cv': 10, 'SG': 1.0},
    'choked_dP': {'P1': 500000, 'P_v': 2340, 'FL': 0.85},
    'cavitation_index': {'P_d': 200000, 'P_v': 2340, 'rho': 1000, 'V': 15},
    'valve_authority': {'dP_valve': 50000, 'dP_total': 100000},
    'torricelli': {'h': 5, 'g': 9.81},
    'nozzle_v': {'dP': 100000, 'rho': 1000},
    'Cd_via_Re': {'Re': 100000, 'beta': 0.5},
    'expansion_factor': {'k': 1.4, 'beta': 0.5, 'dP': 5000, 'P1': 200000},
    'orifice_velocity': {'D': 0.05, 'd': 0.025, 'V_pipe': 2},
    'venturi_q': {'C_d': 0.98, 'A_t': 0.0005, 'rho': 1000, 'dP': 30000, 'beta': 0.5},
    'vena_contracta': {'A_o': 0.0001, 'C_c': 0.62},
    'flow_resistance': {'dP': 50000, 'Q': 0.01},
    'bl_laminar': {'x': 1.0, 'Re_x': 50000},
    'bl_turbulent': {'x': 1.0, 'Re_x': 5000000},
    'cf_laminar': {'Re_L': 50000},
    'cf_turbulent': {'Re_L': 5000000},
    'drag_force': {'C_d': 0.5, 'rho': 1.2, 'V': 20, 'A_ref': 2},
    'lift_force': {'C_l': 1.5, 'rho': 1.2, 'V': 50, 'A': 30},
    'stokes_drag': {'mu': 0.001, 'R': 0.001, 'V': 0.01},
    'cd_sphere': {'Re': 100},
    'terminal_v': {'rho_p': 2500, 'rho_f': 1000, 'R': 0.001, 'mu': 0.001, 'g': 9.81},
    're_flat_plate': {'V': 10, 'L': 2, 'nu': 1.5e-5},
    'pump_power': {'Q': 0.01, 'dP': 1e6, 'eta': 0.85},
    'hydraulic_power': {'Q': 0.01, 'dP': 1e6},
    'cylinder_force': {'P': 1e6, 'A_piston': 0.005, 'A_rod': 0.001},
    'cylinder_velocity': {'Q': 0.005, 'A': 0.005},
    'motor_torque': {'q_displacement': 1e-5, 'dP': 1e6, 'eta_m': 0.92},
    'motor_speed': {'Q': 0.005, 'q_displacement': 1e-5, 'eta_v': 0.95},
    'accumulator': {'V0': 0.01, 'P0': 1e6, 'P1': 5e6, 'n': 1.4},
    'pressure_intensifier': {'A_large': 0.01, 'A_small': 0.001},
    'fluid_spring': {'K_bulk': 1.5e9, 'A': 0.005, 'V': 0.001},
    'time_constant': {'V': 0.001, 'Q': 0.0001},
    'pump_eff': {'eta_v': 0.95, 'eta_m': 0.92},
    'joukowsky': {'rho': 1000, 'a': 1200, 'dV': 2},
    'wave_speed': {'K': 2.15e9, 'rho': 1000, 'D': 0.1, 'e': 0.005, 'E_pipe': 2.1e11},
    'instant_surge': {'rho': 1000, 'a': 1200, 'V0': 3},
    'pipe_period': {'L': 500, 'a': 1200},
    'critical_tc': {'L': 500, 'a': 1200},
    're_number': {'V': 10, 'L': 2, 'nu': 1.5e-5},
    'fr_number': {'V': 5, 'L': 10, 'g': 9.81},
    'ma_number': {'V': 300, 'a': 340},
    'we_number': {'rho': 1000, 'V': 5, 'L': 0.01, 'sigma': 0.0728},
    'eu_number': {'dP': 50000, 'rho': 1000, 'V': 10},
    'st_number': {'f': 50, 'L': 0.1, 'V': 10},
    'buckingham_pi': {'n_vars': 5, 'n_dims': 3},
    'fn_fluid_column': {'K': 2.15e9, 'rho': 1000, 'L': 2, 'A': 0.001},
    'added_mass': {'C_m': 1.0, 'V_fluid': 0.01, 'rho_fluid': 1000},
    'vortex_shedding': {'St': 0.21, 'V': 2, 'D': 0.05},
    'reduced_velocity': {'U': 5, 'f_n': 10, 'D': 0.05},
    'fluid_elastic': {'f_n': 10, 'D': 0.05, 'm': 5, 'rho': 1000, 'zeta': 0.01},
    'gas_density_ideal': {'P': 101325, 'T': 293, 'R': 287},
    'gas_density_real': {'P': 1e6, 'T': 300, 'Z': 0.92, 'R': 287},
    'z_factor_papay': {'P_pr': 3.0, 'T_pr': 1.5},
    'gas_viscosity': {'rho_g': 1.2, 'T': 300, 'Mw': 28.97},
    'isothermal_flow': {'P1': 2e6, 'P2': 1.8e6, 'T': 300, 'L': 1000, 'D': 0.3, 'f': 0.015, 'R': 287},
    'weymouth': {'P1_psi': 500, 'P2_psi': 400, 'T_R': 520, 'L_mi': 50, 'D_in': 12, 'SG': 0.6, 'Z': 0.92, 'E': 1.0},
    'panhandle_a': {'P1_psi': 500, 'P2_psi': 400, 'T_R': 520, 'L_mi': 50, 'D_in': 12, 'SG': 0.6, 'Z': 0.92, 'E': 1.0},
    'panhandle_b': {'P1_psi': 500, 'P2_psi': 400, 'T_R': 520, 'L_mi': 50, 'D_in': 12, 'SG': 0.6, 'Z': 0.92, 'E': 1.0},
    'gas_critical_ratio': {'k': 1.4},
    'gas_orifice_flow': {'C_d': 0.62, 'A_o': 0.0005, 'P1': 500000, 'T1': 300, 'P2': 400000, 'k': 1.4, 'R': 287},
    'gas_choked_flow': {'C_d': 0.95, 'A_t': 0.0001, 'P0': 1e6, 'T0': 300, 'k': 1.4, 'R': 287},
    'gas_nozzle_eff': {'C_d': 0.95, 'A_t': 0.0001, 'P0': 1e6, 'T0': 300, 'P_b': 500000, 'k': 1.4, 'R': 287, 'eta_n': 0.95},
    'erosional_velocity': {'rho': 50, 'C': 100},
    'line_pack': {'V_pipe': 5000, 'P_avg': 2e6, 'T_avg': 300, 'Z': 0.92, 'R': 287},
}


# =============================================================================
# Compute Engine - dispatch by formula_id
# =============================================================================

def compute_formula(formula_id, inputs):
    """Compute a formula given its ID and input parameters. Returns {results: {}, error: null}."""
    result = {'formula_id': formula_id, 'error': None, 'results': {}}
    try:
        if formula_id == 'density':
            result['results']['density'] = density_from_mass_volume(float(inputs.get('mass', 1)), float(inputs.get('volume', 0.001))) or 0
        elif formula_id == 'specific_weight':
            result['results']['gamma'] = specific_weight(float(inputs.get('rho', 1000)), float(inputs.get('g', 9.81)))
        elif formula_id == 'specific_gravity':
            result['results']['SG'] = specific_gravity(float(inputs.get('rho', 850)), float(inputs.get('rho_ref', 1000))) or 0
        elif formula_id == 'dynamic_viscosity':
            result['results']['mu'] = dynamic_from_kinematic_viscosity(float(inputs.get('nu', 1e-6)), float(inputs.get('rho', 1000))) or 0
        elif formula_id == 'kinematic_viscosity':
            result['results']['nu'] = kinematic_from_dynamic_viscosity(float(inputs.get('mu', 0.001)), float(inputs.get('rho', 1000))) or 0
        elif formula_id == 'bulk_modulus':
            result['results']['K'] = bulk_modulus(float(inputs.get('dp', 1e6)), float(inputs.get('dV', -1e-6)), float(inputs.get('V', 0.001))) or 0
        elif formula_id == 'surface_tension':
            result['results']['F'] = surface_tension_force(float(inputs.get('sigma', 0.0728)), float(inputs.get('L', 0.1))) or 0
        elif formula_id == 'vapor_pressure':
            result['results']['P_v'] = vapor_pressure_antoine(float(inputs.get('A', 8.07)), float(inputs.get('B', 1730.6)), float(inputs.get('C', 233.4)), float(inputs.get('T', 20)))

        elif formula_id == 'hydrostatic_pressure':
            result['results']['P'] = hydrostatic_pressure(float(inputs.get('rho', 1000)), float(inputs.get('g', 9.81)), float(inputs.get('h', 10)), float(inputs.get('P0', 101325)))
        elif formula_id == 'manometer':
            result['results']['dP'] = manometer_pressure(float(inputs.get('rho_fluid', 1000)), float(inputs.get('g', 9.81)), float(inputs.get('h_diff', 0.5)))
        elif formula_id == 'hydrostatic_force_plane':
            result['results']['F'] = hydrostatic_force_plane(float(inputs.get('rho', 1000)), float(inputs.get('g', 9.81)), float(inputs.get('h_c', 5)), float(inputs.get('A', 2)))
        elif formula_id == 'center_of_pressure':
            result['results']['y_cp'] = center_of_pressure(float(inputs.get('h_c', 5)), float(inputs.get('I_xx_c', 0.667)), float(inputs.get('A', 2)), float(inputs.get('theta', 90))) or 0
        elif formula_id == 'buoyancy':
            result['results']['F_b'] = buoyancy_force(float(inputs.get('rho_fluid', 1000)), float(inputs.get('g', 9.81)), float(inputs.get('V_displaced', 0.5)))
        elif formula_id == 'metacenter':
            result['results']['GM'] = metacenter_height(float(inputs.get('I_waterline', 100)), float(inputs.get('V_displaced', 50)), float(inputs.get('BG', 0))) or 0
        elif formula_id == 'tank_height':
            result['results']['h'] = fluid_height_in_tank(float(inputs.get('mass', 1000)), float(inputs.get('rho', 1000)), float(inputs.get('area', 2))) or 0
        elif formula_id == 'capillary_rise':
            result['results']['h'] = capillary_rise(float(inputs.get('sigma', 0.0728)), float(inputs.get('theta', 0)), float(inputs.get('rho', 1000)), float(inputs.get('g', 9.81)), float(inputs.get('R', 0.001))) or 0

        elif formula_id == 'continuity':
            result['results']['V2'] = continuity_eq(float(inputs.get('A1', 0.01)), float(inputs.get('V1', 2)), float(inputs.get('A2', 0.005))) or 0
        elif formula_id == 'bernoulli_total_pressure':
            result['results']['P_t'] = bernoulli_total_pressure(float(inputs.get('P', 101325)), float(inputs.get('rho', 1.2)), float(inputs.get('V', 30)), float(inputs.get('z', 0)), float(inputs.get('g', 9.81)))
        elif formula_id == 'bernoulli_velocity':
            result['results']['V2'] = bernoulli_velocity(float(inputs.get('P1', 200000)), float(inputs.get('P2', 101325)), float(inputs.get('rho', 1.2)), float(inputs.get('z1', 0)), float(inputs.get('z2', 0)), float(inputs.get('V1', 10)), float(inputs.get('g', 9.81))) or 0
        elif formula_id == 'bernoulli_dp':
            result['results']['dP'] = bernoulli_pressure_drop_ideal(float(inputs.get('rho', 1.2)), float(inputs.get('V1', 10)), float(inputs.get('V2', 30)), float(inputs.get('z1', 0)), float(inputs.get('z2', 0)), float(inputs.get('g', 9.81)))
        elif formula_id == 'energy_eq':
            result['results']['E_balance'] = energy_eq_head(float(inputs.get('h_pump', 50)), float(inputs.get('h_turbine', 0)), float(inputs.get('h_loss', 5)), float(inputs.get('z1', 0)), float(inputs.get('z2', 10)), float(inputs.get('V1', 2)), float(inputs.get('V2', 1)), float(inputs.get('P1', 101325)), float(inputs.get('P2', 200000)), float(inputs.get('rho', 1000)), float(inputs.get('g', 9.81))) or 0
        elif formula_id == 'momentum_force':
            result['results']['F'] = momentum_force(float(inputs.get('rho', 1000)), float(inputs.get('Q', 0.1)), float(inputs.get('V_out', 5)), float(inputs.get('V_in', 2)))
        elif formula_id == 'cavitation_number':
            result['results']['sigma'] = cavitation_number(float(inputs.get('P', 200000)), float(inputs.get('P_v', 2340)), float(inputs.get('rho', 1000)), float(inputs.get('V', 20))) or 0
        elif formula_id == 'stagnation':
            result['results']['P0'] = stagnation_pressure(float(inputs.get('P_static', 101325)), float(inputs.get('rho', 1.2)), float(inputs.get('V', 50)))
        elif formula_id == 'volume_flow':
            result['results']['Q'] = flow_rate_from_area_velocity(float(inputs.get('A', 0.01)), float(inputs.get('V', 5))) or 0
        elif formula_id == 'mass_flow':
            result['results']['m_dot'] = mass_flow_rate(float(inputs.get('rho', 1.2)), float(inputs.get('Q', 0.05))) or 0

        elif formula_id == 'reynolds':
            result['results']['Re'] = reynolds_number(float(inputs.get('rho', 1000)), float(inputs.get('V', 2)), float(inputs.get('D', 0.05)), float(inputs.get('mu', 0.001))) or 0
        elif formula_id == 'reynolds_nu':
            result['results']['Re'] = reynolds_number_nu(float(inputs.get('V', 2)), float(inputs.get('D', 0.05)), float(inputs.get('nu', 1e-6))) or 0
        elif formula_id == 'f_laminar':
            result['results']['f'] = friction_factor_laminar(float(inputs.get('Re', 1000))) or 0
        elif formula_id == 'f_blasius':
            result['results']['f'] = friction_factor_blasius(float(inputs.get('Re', 50000))) or 0
        elif formula_id == 'f_colebrook':
            eps = float(inputs.get('epsilon', 0.046)) * 0.001
            D_m = float(inputs.get('D', 50.0)) * 0.001
            result['results']['f'] = friction_factor_colebrook(float(inputs.get('Re', 100000)), eps, D_m) or 0
        elif formula_id == 'f_swamee_jain':
            eps = float(inputs.get('epsilon', 0.046)) * 0.001
            D_m = float(inputs.get('D', 50.0)) * 0.001
            result['results']['f'] = friction_factor_swamee_jain(float(inputs.get('Re', 100000)), eps, D_m) or 0
        elif formula_id == 'darcy_hf':
            result['results']['h_f'] = darcy_weisbach_hf(float(inputs.get('f', 0.02)), float(inputs.get('L', 100)), float(inputs.get('D', 0.1)), float(inputs.get('V', 3)), float(inputs.get('g', 9.81))) or 0
        elif formula_id == 'darcy_dp':
            result['results']['dP'] = darcy_weisbach_dP(float(inputs.get('f', 0.02)), float(inputs.get('L', 100)), float(inputs.get('D', 0.1)), float(inputs.get('rho', 1000)), float(inputs.get('V', 3))) or 0
        elif formula_id == 'hazen_williams':
            result['results']['V'] = hazen_williams_velocity(float(inputs.get('C', 130)), float(inputs.get('R_h', 0.05)), float(inputs.get('S', 0.001))) or 0
        elif formula_id == 'hydraulic_radius':
            result['results']['R_h'] = hydraulic_radius(float(inputs.get('A', 0.2)), float(inputs.get('P_wetted', 1.0))) or 0
        elif formula_id == 'hydraulic_diameter':
            result['results']['D_h'] = hydraulic_diameter(float(inputs.get('A', 0.2)), float(inputs.get('P_wetted', 1.0))) or 0
        elif formula_id == 'minor_loss_head':
            result['results']['h_m'] = minor_loss_head(float(inputs.get('K', 2.5)), float(inputs.get('V', 3)), float(inputs.get('g', 9.81))) or 0
        elif formula_id == 'minor_loss_dp':
            result['results']['dP_m'] = minor_loss_pressure(float(inputs.get('K', 2.5)), float(inputs.get('rho', 1000)), float(inputs.get('V', 3))) or 0
        elif formula_id == 'sudden_expansion':
            dP = sudden_expansion_loss(float(inputs.get('A1', 0.01)), float(inputs.get('A2', 0.02)), float(inputs.get('V1', 5)), float(inputs.get('rho', 1000))) or 0
            result['results']['dP_sudden'] = dP
        elif formula_id == 'sudden_contraction':
            result['results']['dP_contraction'] = sudden_contraction_loss(float(inputs.get('A1', 0.02)), float(inputs.get('A2', 0.01)), float(inputs.get('V2', 5)), float(inputs.get('rho', 1000))) or 0
        elif formula_id == 'equiv_length':
            result['results']['L_eq'] = pipe_series_equivalent_length(float(inputs.get('K_total', 5)), float(inputs.get('D', 0.1)), float(inputs.get('f', 0.02))) or 0
        elif formula_id == 'pipe_exit':
            result['results']['dP_exit'] = pipe_exit_loss(float(inputs.get('V', 3)), float(inputs.get('rho', 1000))) or 0
        elif formula_id == 'pipe_entrance':
            result['results']['dP_entrance'] = pipe_entrance_loss(float(inputs.get('V', 3)), float(inputs.get('rho', 1000)), float(inputs.get('r_D', 0))) or 0
        elif formula_id == 'pipe_bend':
            result['results']['dP_bend'] = pipe_bend_loss(float(inputs.get('V', 3)), float(inputs.get('rho', 1000)), float(inputs.get('R_bend', 0.1)), float(inputs.get('D', 0.05)), float(inputs.get('theta_deg', 90))) or 0

        elif formula_id == 'froude':
            result['results']['Fr'] = froude_number(float(inputs.get('V', 3)), float(inputs.get('g', 9.81)), float(inputs.get('y_h', 1.5))) or 0
        elif formula_id == 'manning_v':
            result['results']['V'] = manning_velocity(float(inputs.get('n', 0.013)), float(inputs.get('R_h', 0.5)), float(inputs.get('S', 0.001))) or 0
        elif formula_id == 'manning_q':
            result['results']['Q'] = manning_discharge(float(inputs.get('n', 0.013)), float(inputs.get('A', 2)), float(inputs.get('R_h', 0.5)), float(inputs.get('S', 0.001))) or 0
        elif formula_id == 'chezy_v':
            result['results']['V'] = chezy_velocity(float(inputs.get('C', 60)), float(inputs.get('R_h', 0.5)), float(inputs.get('S', 0.001))) or 0
        elif formula_id == 'critical_depth_rect':
            result['results']['y_c'] = critical_depth_rectangular(float(inputs.get('Q', 5)), float(inputs.get('b', 3)), float(inputs.get('g', 9.81))) or 0
        elif formula_id == 'specific_energy':
            E = float(inputs.get('y', 1.5)) + safe_div(float(inputs.get('Q', 5))**2, 2.0 * float(inputs.get('g', 9.81)) * float(inputs.get('A_flow', 4.5))**2)
            result['results']['E'] = E or 0
        elif formula_id == 'hydraulic_jump_ratio':
            r = hydraulic_jump_ratio(float(inputs.get('Fr1', 3.5)))
            result['results']['y_ratio'] = r
        elif formula_id == 'hydraulic_jump_energy':
            result['results']['dE'] = hydraulic_jump_energy_loss(float(inputs.get('y1', 0.3)), float(inputs.get('y2', 1.5))) or 0
        elif formula_id == 'weir_rect':
            result['results']['Q'] = weir_discharge_rectangular(float(inputs.get('C_d', 0.62)), float(inputs.get('b', 2)), float(inputs.get('H', 0.5)), float(inputs.get('g', 9.81))) or 0

        elif formula_id == 'speed_of_sound':
            result['results']['a'] = speed_of_sound(float(inputs.get('k', 1.4)), float(inputs.get('R', 287)), float(inputs.get('T', 293)))
        elif formula_id == 'mach':
            result['results']['M'] = mach_number(float(inputs.get('V', 340)), float(inputs.get('a', 340))) or 0
        elif formula_id == 'isentropic_T':
            result['results']['T_ratio'] = isentropic_T_ratio(float(inputs.get('M', 2)), float(inputs.get('k', 1.4)))
        elif formula_id == 'isentropic_P':
            result['results']['P_ratio'] = isentropic_P_ratio(float(inputs.get('M', 2)), float(inputs.get('k', 1.4)))
        elif formula_id == 'isentropic_rho':
            result['results']['rho_ratio'] = isentropic_rho_ratio(float(inputs.get('M', 2)), float(inputs.get('k', 1.4)))
        elif formula_id == 'area_ratio':
            result['results']['A_ratio'] = isentropic_area_ratio(float(inputs.get('M', 2)), float(inputs.get('k', 1.4))) or 0
        elif formula_id == 'normal_shock_P':
            result['results']['P_ratio'] = normal_shock_P_ratio(float(inputs.get('M1', 2)), float(inputs.get('k', 1.4)))
        elif formula_id == 'normal_shock_rho':
            result['results']['rho_ratio'] = normal_shock_rho_ratio(float(inputs.get('M1', 2)), float(inputs.get('k', 1.4))) or 0
        elif formula_id == 'normal_shock_M2':
            result['results']['M2'] = normal_shock_M2(float(inputs.get('M1', 2)), float(inputs.get('k', 1.4)))
        elif formula_id == 'pm_angle':
            result['results']['nu'] = math.degrees(prandtl_meyer_angle(float(inputs.get('M', 2)), float(inputs.get('k', 1.4))))
        elif formula_id == 'nozzle_mass_flow':
            result['results']['m_dot'] = nozzle_mass_flow(float(inputs.get('P0', 1e6)), float(inputs.get('T0', 500)), float(inputs.get('A_t', 0.001)), float(inputs.get('k', 1.4)), float(inputs.get('R', 287))) or 0
        elif formula_id == 'expansion_velocity':
            result['results']['V_exit'] = expansion_velocity(float(inputs.get('P0', 1e6)), float(inputs.get('P_exit', 50000)), float(inputs.get('T0', 500)), float(inputs.get('k', 1.4)), float(inputs.get('R', 287))) or 0

        elif formula_id == 'orifice_flow':
            result['results']['Q'] = orifice_flow(float(inputs.get('C_d', 0.62)), float(inputs.get('A_o', 0.0001)), float(inputs.get('rho', 1000)), float(inputs.get('dP', 50000))) or 0
        elif formula_id == 'valve_Cv':
            result['results']['Cv'] = valve_Cv(float(inputs.get('Q_gpm', 50)), float(inputs.get('dP_psi', 5)), float(inputs.get('SG', 1.0))) or 0
        elif formula_id == 'flow_from_Cv':
            result['results']['Q_gpm'] = flow_from_Cv(float(inputs.get('Cv', 10)), float(inputs.get('dP_psi', 5)), float(inputs.get('SG', 1.0))) or 0
        elif formula_id == 'Kv_to_Cv':
            result['results']['Cv'] = Kv_to_Cv(float(inputs.get('Kv', 10)))
        elif formula_id == 'Cv_to_Kv':
            result['results']['Kv'] = Cv_to_Kv(float(inputs.get('Cv', 10)))
        elif formula_id == 'valve_dp_from_Cv':
            result['results']['dP'] = valve_dp_from_Cv(float(inputs.get('Q_gpm', 50)), float(inputs.get('Cv', 10)), float(inputs.get('SG', 1.0))) or 0
        elif formula_id == 'choked_dP':
            result['results']['dP_choked'] = choked_flow_dP(float(inputs.get('P1', 500000)), float(inputs.get('P_v', 2340)), float(inputs.get('FL', 0.85)))
        elif formula_id == 'cavitation_index':
            result['results']['K_cav'] = cavitation_index_valve(float(inputs.get('P_d', 200000)), float(inputs.get('P_v', 2340)), float(inputs.get('rho', 1000)), float(inputs.get('V', 15))) or 0
        elif formula_id == 'valve_authority':
            result['results']['N'] = valve_authority(float(inputs.get('dP_valve', 50000)), float(inputs.get('dP_total', 100000))) or 0
        elif formula_id == 'torricelli':
            result['results']['V'] = torricelli_velocity(float(inputs.get('h', 5)), float(inputs.get('g', 9.81)))
        elif formula_id == 'nozzle_v':
            result['results']['V'] = nozzle_velocity_incompressible(float(inputs.get('dP', 100000)), float(inputs.get('rho', 1000))) or 0
        elif formula_id == 'Cd_via_Re':
            result['results']['C_d'] = flow_coefficient_Cd_via_Re(float(inputs.get('Re', 100000)), float(inputs.get('beta', 0.5))) or 0
        elif formula_id == 'expansion_factor':
            result['results']['Y'] = expansion_factor_compressible(float(inputs.get('k', 1.4)), float(inputs.get('beta', 0.5)), float(inputs.get('dP', 5000)), float(inputs.get('P1', 200000))) or 1.0
        elif formula_id == 'orifice_velocity':
            result['results']['V_o'] = pipe_to_orifice_velocity(float(inputs.get('D', 0.05)), float(inputs.get('d', 0.025)), float(inputs.get('V_pipe', 2))) or 0
        elif formula_id == 'venturi_q':
            result['results']['Q'] = venturi_discharge(float(inputs.get('C_d', 0.98)), float(inputs.get('A_t', 0.0005)), float(inputs.get('rho', 1000)), float(inputs.get('dP', 30000)), float(inputs.get('beta', 0.5))) or 0
        elif formula_id == 'vena_contracta':
            result['results']['A_vc'] = vena_contracta_area(float(inputs.get('A_o', 0.0001)), float(inputs.get('C_c', 0.62)))
        elif formula_id == 'flow_resistance':
            result['results']['R_f'] = flow_resistance_coefficient(float(inputs.get('dP', 50000)), float(inputs.get('Q', 0.01)), float(inputs.get('rho', 1000))) or 0

        elif formula_id == 'bl_laminar':
            result['results']['delta'] = bl_thickness_laminar(float(inputs.get('x', 1.0)), float(inputs.get('Re_x', 50000))) or 0
        elif formula_id == 'bl_turbulent':
            result['results']['delta'] = bl_thickness_turbulent(float(inputs.get('x', 1.0)), float(inputs.get('Re_x', 5000000))) or 0
        elif formula_id == 'cf_laminar':
            result['results']['C_f'] = skin_friction_coef_laminar(float(inputs.get('Re_L', 50000))) or 0
        elif formula_id == 'cf_turbulent':
            result['results']['C_f'] = skin_friction_coef_turbulent(float(inputs.get('Re_L', 5000000))) or 0
        elif formula_id == 'drag_force':
            result['results']['F_D'] = drag_force(float(inputs.get('CD', float(inputs.get('C_d', 0.03)))), float(inputs.get('rho', 1.225)), float(inputs.get('V', 50)), float(inputs.get('A', float(inputs.get('A_ref', 20)))))
        elif formula_id == 'lift_force':
            result['results']['F_L'] = lift_force(float(inputs.get('CL', float(inputs.get('C_l', 1.2)))), float(inputs.get('rho', 1.225)), float(inputs.get('V', 50)), float(inputs.get('A', 20)))
        elif formula_id == 'stokes_drag':
            result['results']['F_d'] = drag_force_stokes(float(inputs.get('mu', 0.001)), float(inputs.get('R', 0.001)), float(inputs.get('V', 0.01)))
        elif formula_id == 'cd_sphere':
            result['results']['C_D'] = drag_coef_sphere(float(inputs.get('Re', 100))) or 0
        elif formula_id == 'terminal_v':
            result['results']['V_t'] = terminal_velocity_sphere(float(inputs.get('rho_p', 2500)), float(inputs.get('rho_f', 1000)), float(inputs.get('R', 0.001)), float(inputs.get('mu', 0.001)), float(inputs.get('g', 9.81))) or 0
        elif formula_id == 're_flat_plate':
            result['results']['Re_L'] = flat_plate_reynolds(float(inputs.get('V', 10)), float(inputs.get('L', 2)), float(inputs.get('nu', 1.5e-5))) or 0

        elif formula_id == 'pump_power':
            result['results']['P_pump'] = pump_power(float(inputs.get('Q', 0.01)), float(inputs.get('dP', 1e6)), float(inputs.get('eta', 0.85))) or 0
        elif formula_id == 'hydraulic_power':
            result['results']['P_h'] = hydraulic_power(float(inputs.get('Q', 0.01)), float(inputs.get('dP', 1e6)))
        elif formula_id == 'cylinder_force':
            result['results']['F'] = cylinder_force(float(inputs.get('P', 1e6)), float(inputs.get('A_piston', 0.005)), float(inputs.get('A_rod', 0.001)))
        elif formula_id == 'cylinder_velocity':
            result['results']['V'] = cylinder_velocity(float(inputs.get('Q', 0.005)), float(inputs.get('A', 0.005))) or 0
        elif formula_id == 'motor_torque':
            result['results']['T'] = motor_torque(float(inputs.get('q_displacement', 1e-5)), float(inputs.get('dP', 1e6)), float(inputs.get('eta_m', 0.92))) or 0
        elif formula_id == 'motor_speed':
            result['results']['n'] = motor_speed(float(inputs.get('Q', 0.005)), float(inputs.get('q_displacement', 1e-5)), float(inputs.get('eta_v', 0.95))) or 0
        elif formula_id == 'accumulator':
            result['results']['V_gas'] = accumulator_size(float(inputs.get('V0', 0.01)), float(inputs.get('P0', 1e6)), float(inputs.get('P1', 5e6)), float(inputs.get('n', 1.4)))
        elif formula_id == 'pressure_intensifier':
            result['results']['ratio'] = pressure_intensifier_ratio(float(inputs.get('A_large', 0.01)), float(inputs.get('A_small', 0.001))) or 0
        elif formula_id == 'fluid_spring':
            result['results']['k_f'] = fluid_spring_stiffness(float(inputs.get('K_bulk', 1.5e9)), float(inputs.get('A', 0.005)), float(inputs.get('V', 0.001))) or 0
        elif formula_id == 'time_constant':
            result['results']['tau'] = hydraulic_time_constant(float(inputs.get('V', 0.001)), float(inputs.get('Q', 0.0001))) or 0
        elif formula_id == 'pump_eff':
            result['results']['eta'] = pump_efficiency_overall(float(inputs.get('eta_v', 0.95)), float(inputs.get('eta_m', 0.92)))

        elif formula_id == 'joukowsky':
            result['results']['dP'] = joukowsky_pressure(float(inputs.get('rho', 1000)), float(inputs.get('a', 1200)), float(inputs.get('dV', 2)))
        elif formula_id == 'wave_speed':
            result['results']['a'] = wave_speed_fluid(float(inputs.get('K', 2.15e9)), float(inputs.get('rho', 1000)), float(inputs.get('D', 0.1)), float(inputs.get('e', 0.005)), float(inputs.get('E_pipe', 2.1e11)))
        elif formula_id == 'instant_surge':
            result['results']['dP_surge'] = surge_pressure_instant_valve(float(inputs.get('rho', 1000)), float(inputs.get('a', 1200)), float(inputs.get('V0', 3)))
        elif formula_id == 'pipe_period':
            result['results']['T_r'] = pipe_period(float(inputs.get('L', 500)), float(inputs.get('a', 1200))) or 0
        elif formula_id == 'critical_tc':
            result['results']['t_c'] = critical_closure_time(float(inputs.get('L', 500)), float(inputs.get('a', 1200))) or 0

        elif formula_id == 're_number':
            result['results']['Re'] = dimensionless_reynolds(float(inputs.get('V', 10)), float(inputs.get('L', 2)), float(inputs.get('nu', 1.5e-5))) or 0
        elif formula_id == 'fr_number':
            result['results']['Fr'] = dimensionless_froude(float(inputs.get('V', 5)), float(inputs.get('g', 9.81)), float(inputs.get('L', 10))) or 0
        elif formula_id == 'ma_number':
            result['results']['Ma'] = dimensionless_mach(float(inputs.get('V', 300)), float(inputs.get('a', 340))) or 0
        elif formula_id == 'we_number':
            result['results']['We'] = dimensionless_weber(float(inputs.get('rho', 1000)), float(inputs.get('V', 5)), float(inputs.get('L', 0.01)), float(inputs.get('sigma', 0.0728))) or 0
        elif formula_id == 'eu_number':
            result['results']['Eu'] = dimensionless_euler(float(inputs.get('dP', 50000)), float(inputs.get('rho', 1000)), float(inputs.get('V', 10))) or 0
        elif formula_id == 'st_number':
            result['results']['St'] = dimensionless_strouhal(float(inputs.get('f', 50)), float(inputs.get('L', 0.1)), float(inputs.get('V', 10))) or 0
        elif formula_id == 'buckingham_pi':
            result['results']['n_pi'] = buckingham_pi_count(int(inputs.get('n_vars', 5)), int(inputs.get('n_dims', 3)))

        elif formula_id == 'fn_fluid_column':
            result['results']['f_n'] = natural_frequency_fluid_column(float(inputs.get('K', 2.15e9)), float(inputs.get('rho', 1000)), float(inputs.get('L', 2)), float(inputs.get('A', 0.001))) or 0
        elif formula_id == 'added_mass':
            result['results']['m_a'] = added_mass_coefficient(float(inputs.get('C_m', 1.0)), float(inputs.get('V_fluid', 0.01)), float(inputs.get('rho_fluid', 1000)))
        elif formula_id == 'vortex_shedding':
            result['results']['f_vs'] = vortex_shedding_frequency(float(inputs.get('St', 0.21)), float(inputs.get('V', 2)), float(inputs.get('D', 0.05))) or 0
        elif formula_id == 'reduced_velocity':
            result['results']['V_r'] = reduced_velocity_viv(float(inputs.get('U', 5)), float(inputs.get('f_n', 10)), float(inputs.get('D', 0.05))) or 0
        elif formula_id == 'fluid_elastic':
            result['results']['U_crit'] = fluid_elastic_instability(float(inputs.get('f_n', 10)), float(inputs.get('D', 0.05)), float(inputs.get('m', 5)), float(inputs.get('rho', 1000)), float(inputs.get('zeta', 0.01)))

        elif formula_id == 'gas_density_ideal':
            result['results']['rho'] = gas_density_ideal(float(inputs.get('P', 101325)), float(inputs.get('T', 293)), float(inputs.get('R', 287))) or 0
        elif formula_id == 'gas_density_real':
            result['results']['rho'] = gas_density_real(float(inputs.get('P', 1e6)), float(inputs.get('T', 300)), float(inputs.get('Z', 0.92)), float(inputs.get('R', 287))) or 0
        elif formula_id == 'z_factor_papay':
            result['results']['Z'] = compressibility_factor_Papay(float(inputs.get('P_pr', 3.0)), float(inputs.get('T_pr', 1.5))) or 0
        elif formula_id == 'gas_viscosity':
            result['results']['mu'] = gas_viscosity_LGE(float(inputs.get('rho_g', 1.2)), float(inputs.get('T', 300)), float(inputs.get('Mw', 28.97))) or 0
        elif formula_id == 'isothermal_flow':
            result['results']['m_dot'] = gas_mass_flow_isothermal(float(inputs.get('P1', 2e6)), float(inputs.get('P2', 1.8e6)), float(inputs.get('T', 300)), float(inputs.get('L', 1000)), float(inputs.get('D', 0.3)), float(inputs.get('f', 0.015)), float(inputs.get('R', 287))) or 0
        elif formula_id == 'weymouth':
            result['results']['Q_scfd'] = gas_weymouth_flow(float(inputs.get('P1_psi', 500)), float(inputs.get('P2_psi', 400)), float(inputs.get('T_R', 520)), float(inputs.get('L_mi', 50)), float(inputs.get('D_in', 12)), float(inputs.get('SG', 0.6)), float(inputs.get('Z', 0.92)), float(inputs.get('E', 1.0))) or 0
        elif formula_id == 'panhandle_a':
            result['results']['Q_scfd'] = gas_panhandle_a_flow(float(inputs.get('P1_psi', 500)), float(inputs.get('P2_psi', 400)), float(inputs.get('T_R', 520)), float(inputs.get('L_mi', 50)), float(inputs.get('D_in', 12)), float(inputs.get('SG', 0.6)), float(inputs.get('Z', 0.92)), float(inputs.get('E', 1.0))) or 0
        elif formula_id == 'panhandle_b':
            result['results']['Q_scfd'] = gas_panhandle_b_flow(float(inputs.get('P1_psi', 500)), float(inputs.get('P2_psi', 400)), float(inputs.get('T_R', 520)), float(inputs.get('L_mi', 50)), float(inputs.get('D_in', 12)), float(inputs.get('SG', 0.6)), float(inputs.get('Z', 0.92)), float(inputs.get('E', 1.0))) or 0
        elif formula_id == 'gas_critical_ratio':
            result['results']['r_c'] = gas_critical_pressure_ratio(float(inputs.get('k', 1.4))) or 0
        elif formula_id == 'gas_orifice_flow':
            result['results']['m_dot'] = gas_orifice_mass_flow(float(inputs.get('C_d', 0.62)), float(inputs.get('A_o', 0.0005)), float(inputs.get('P1', 500000)), float(inputs.get('T1', 300)), float(inputs.get('P2', 400000)), float(inputs.get('k', 1.4)), float(inputs.get('R', 287))) or 0
        elif formula_id == 'gas_choked_flow':
            result['results']['m_dot_choked'] = gas_choked_mass_flow(float(inputs.get('C_d', 0.95)), float(inputs.get('A_t', 0.0001)), float(inputs.get('P0', 1e6)), float(inputs.get('T0', 300)), float(inputs.get('k', 1.4)), float(inputs.get('R', 287))) or 0
        elif formula_id == 'gas_nozzle_eff':
            result['results']['m_dot'] = gas_nozzle_flow_efficiency(float(inputs.get('C_d', 0.95)), float(inputs.get('A_t', 0.0001)), float(inputs.get('P0', 1e6)), float(inputs.get('T0', 300)), float(inputs.get('P_b', 200000)), float(inputs.get('k', 1.4)), float(inputs.get('R', 287)), float(inputs.get('eta_n', 0.95))) or 0
        elif formula_id == 'erosional_velocity':
            result['results']['V_e'] = gas_erosional_velocity(float(inputs.get('rho', 50)), float(inputs.get('C', 100))) or 0
        elif formula_id == 'line_pack':
            result['results']['V_scm'] = gas_pipeline_linepack(float(inputs.get('V_pipe', 5000)), float(inputs.get('P_avg', 2e6)), float(inputs.get('T_avg', 300)), float(inputs.get('Z', 0.92)), float(inputs.get('R', 287))) or 0


        # Sprint 4: Non-Newtonian
        elif formula_id == 'bingham_shear':
            result['results']['tau'] = bingham_shear_stress(float(inputs.get('tau_y', 0)), float(inputs.get('mu_p', 0)), float(inputs.get('gamma_dot', 0))) or 0
        elif formula_id == 'bingham_pipe_Q':
            result['results']['Q'] = bingham_pipe_flow_rate(float(inputs.get('tau_y', 0)), float(inputs.get('mu_p', 1)), float(inputs.get('dP', 100000)), float(inputs.get('L', 1)), float(inputs.get('R_pipe', 0.025))) or 0
        elif formula_id == 'power_law_mu_app':
            result['results']['mu_app'] = power_law_apparent_viscosity(float(inputs.get('K', 1)), float(inputs.get('n', 0.5)), float(inputs.get('gamma_dot', 100))) or 0
        elif formula_id == 'power_law_pipe_V':
            result['results']['V'] = power_law_pipe_flow_velocity(float(inputs.get('K', 1)), float(inputs.get('n', 0.5)), float(inputs.get('dP', 100000)), float(inputs.get('L', 1)), float(inputs.get('R_pipe', 0.025))) or 0
        elif formula_id == 're_gen_power_law':
            result['results']['Re_MR'] = generalized_reynolds_number_power_law(float(inputs.get('rho', 1000)), float(inputs.get('V', 1)), float(inputs.get('D', 0.05)), float(inputs.get('K', 1)), float(inputs.get('n', 0.5))) or 0
        elif formula_id == 'dodge_metzner_f':
            result['results']['f'] = dodge_metzner_friction_factor(float(inputs.get('Re_MR', 5000)), float(inputs.get('n', 0.7))) or 0
        elif formula_id == 'hb_shear':
            result['results']['tau'] = herschel_bulkley_shear_stress(float(inputs.get('tau_y', 10)), float(inputs.get('K', 1)), float(inputs.get('n', 0.6)), float(inputs.get('gamma_dot', 100))) or 0
        elif formula_id == 'casson_shear':
            result['results']['tau'] = casson_shear_stress(float(inputs.get('tau_y', 5)), float(inputs.get('mu_c', 0.01)), float(inputs.get('gamma_dot', 100))) or 0

        # Sprint 4: Multi-Phase
        elif formula_id == 'hom_void_frac':
            result['results']['alpha'] = homogeneous_void_fraction(float(inputs.get('x', 0.5)), float(inputs.get('rho_g', 1.2)), float(inputs.get('rho_l', 1000))) or 0
        elif formula_id == 'hom_tp_density':
            result['results']['rho_tp'] = homogeneous_two_phase_density(float(inputs.get('x', 0.5)), float(inputs.get('rho_g', 1.2)), float(inputs.get('rho_l', 1000))) or 0
        elif formula_id == 'mcadams_visc':
            result['results']['mu_tp'] = mcadams_viscosity(float(inputs.get('x', 0.5)), float(inputs.get('mu_g', 1.8e-5)), float(inputs.get('mu_l', 0.001))) or 0
        elif formula_id == 'LM_X':
            result['results']['X'] = lockhart_martinelli_X(float(inputs.get('x', 0.3)), float(inputs.get('rho_g', 1.2)), float(inputs.get('rho_l', 1000)), float(inputs.get('mu_g', 1.8e-5)), float(inputs.get('mu_l', 0.001))) or 0
        elif formula_id == 'chisholm_phi2':
            result['results']['phi_l2'] = chisholm_two_phase_multiplier(float(inputs.get('X', 1)), float(inputs.get('C', 20))) or 0
        elif formula_id == 'drift_flux_alpha':
            result['results']['alpha_df'] = drift_flux_void_fraction(float(inputs.get('j_g', 0.5)), float(inputs.get('j_l', 1.0)), float(inputs.get('C0', 1.2))) or 0
        elif formula_id == 'baker_map':
            bm = baker_flow_pattern_map(float(inputs.get('G_g', 100)), float(inputs.get('G_l', 500)), float(inputs.get('lmbda', 1)), float(inputs.get('psi', 1)))
            if bm:
                result['results'].update(bm)
            else:
                result['results']['error'] = 'Invalid input'
        elif formula_id == 'taitel_dukler':
            result['results']['v_sg_crit'] = taitel_dukler_transition(float(inputs.get('v_sg', 1)), float(inputs.get('D', 0.05)), float(inputs.get('rho_g', 1.2)), float(inputs.get('rho_l', 1000)), float(inputs.get('sigma', 0.073))) or 0
        elif formula_id == 'slug_freq':
            result['results']['f_s'] = slug_frequency(float(inputs.get('v_sl', 1)), float(inputs.get('v_sg', 2)), float(inputs.get('D', 0.05))) or 0

        # Sprint 4: Cavitation
        elif formula_id == 'cav_number':
            result['results']['sigma_c'] = cavitation_number(float(inputs.get('P_ref', 101325)), float(inputs.get('P_v', 2340)), float(inputs.get('rho', 998)), float(inputs.get('V', 10))) or 0
        elif formula_id == 'thoma_param':
            result['results']['sigma_T'] = thoma_cavitation_parameter(float(inputs.get('H_atm', 10.33)), float(inputs.get('H_v', 0.24)), float(inputs.get('H_s', 3))) or 0
        elif formula_id == 'npsh_available':
            result['results']['NPSHa'] = npsh_available(float(inputs.get('P_atm', 101325)), float(inputs.get('P_v', 2339)), float(inputs.get('h_s', 2)), float(inputs.get('h_f', 1.5)), float(inputs.get('rho', 998)))
        elif formula_id == 'npsh_r':
            result['results']['NPSH_r'] = npsh_required_by_suction_specific_speed(float(inputs.get('N', 1750)), float(inputs.get('Q', 0.1)), float(inputs.get('S', 8000))) or 0
        elif formula_id == 'rayleigh_plesset':
            result['results']['R_max'] = rayleigh_plesset_radius(float(inputs.get('R0', 1e-5)), float(inputs.get('P_v', 2340)), float(inputs.get('P_inf', 101325)), float(inputs.get('rho', 998)), float(inputs.get('t', 1e-6))) or 0
        elif formula_id == 'bubble_freq':
            result['results']['f_n'] = bubble_natural_frequency(float(inputs.get('P_inf', 101325)), float(inputs.get('rho', 998)), float(inputs.get('R0', 1e-5)), float(inputs.get('k', 1.4))) or 0
        elif formula_id == 'cav_erosion':
            result['results']['P_eros'] = cavitation_erosion_power(float(inputs.get('rho', 998)), float(inputs.get('V', 30)), float(inputs.get('A', 0.01)), float(inputs.get('sigma_f', 0.1))) or 0
        elif formula_id == 'pump_hydraulic_power':
            result['results']['P_h'] = pump_hydraulic_power(float(inputs.get('Q', 0.01)), float(inputs.get('rho', 998)), float(inputs.get('H', 20)))
        elif formula_id == 'pump_shaft_power':
            result['results']['P_s'] = pump_shaft_power(float(inputs.get('P_h', 1960)), float(inputs.get('eta', 0.75)))
        elif formula_id == 'pump_efficiency':
            result['results']['eta'] = pump_efficiency(float(inputs.get('P_h', 1960)), float(inputs.get('P_s', 2613)))
        elif formula_id == 'specific_speed_metric':
            result['results']['N_s'] = specific_speed_metric(float(inputs.get('Q', 0.01)), float(inputs.get('H', 20)), float(inputs.get('N', 2900)))
        elif formula_id == 'specific_speed_imperial':
            result['results']['N_s_us'] = specific_speed_imperial(float(inputs.get('Q_gpm', 100)), float(inputs.get('H_ft', 50)), float(inputs.get('N_rpm', 3500)))
        elif formula_id == 'affinity_law_Q':
            result['results']['Q_ratio'] = affinity_law_Q(float(inputs.get('D1', 0.2)), float(inputs.get('D2', 0.25)), float(inputs.get('N1', 2900)), float(inputs.get('N2', 2900)))
        elif formula_id == 'affinity_law_H':
            result['results']['H_ratio'] = affinity_law_H(float(inputs.get('D1', 0.2)), float(inputs.get('D2', 0.25)), float(inputs.get('N1', 2900)), float(inputs.get('N2', 2900)))
        elif formula_id == 'suction_specific_speed':
            result['results']['N_ss'] = suction_specific_speed(float(inputs.get('Q', 0.01)), float(inputs.get('NPSHr', 3)), float(inputs.get('N', 2900)))
        elif formula_id == 'venturi_flow_rate':
            result['results']['Q'] = venturi_flow_rate(float(inputs.get('Cd', 0.98)), float(inputs.get('A2', 0.0003)), float(inputs.get('rho', 998)), float(inputs.get('dp', 10000)), float(inputs.get('beta', 0.5)))
        elif formula_id == 'venturi_mass_flow':
            result['results']['m_dot'] = venturi_mass_flow(float(inputs.get('Cd', 0.98)), float(inputs.get('A2', 0.0003)), float(inputs.get('rho', 998)), float(inputs.get('dp', 10000)), float(inputs.get('beta', 0.5)))
        elif formula_id == 'orifice_flow_rate':
            result['results']['Q'] = orifice_flow_rate(float(inputs.get('Cd', 0.61)), float(inputs.get('A0', 0.0002)), float(inputs.get('rho', 998)), float(inputs.get('dp', 10000)), float(inputs.get('beta', 0.5)))
        elif formula_id == 'pitot_velocity':
            result['results']['V'] = pitot_velocity(float(inputs.get('dp', 1000)), float(inputs.get('rho', 1.225)))
        elif formula_id == 'weir_rectangular':
            result['results']['Q'] = weir_rectangular(float(inputs.get('Cd', 0.62)), float(inputs.get('b', 2)), float(inputs.get('H', 0.3)))
        elif formula_id == 'weir_vnotch':
            result['results']['Q'] = weir_vnotch(float(inputs.get('Cd', 0.58)), float(inputs.get('theta_deg', 90)), float(inputs.get('H', 0.3)))
        elif formula_id == 'nozzle_flow_rate':
            result['results']['Q'] = nozzle_flow_rate(float(inputs.get('Cd', 0.96)), float(inputs.get('A_n', 0.0001)), float(inputs.get('rho', 998)), float(inputs.get('dp', 10000)))
        elif formula_id == 'rotameter_flow':
            result['results']['Q'] = rotameter_flow(float(inputs.get('Cd', 0.98)), float(inputs.get('A_annulus', 0.0001)), float(inputs.get('V_float', 2e-5)), float(inputs.get('rho_f', 7800)), float(inputs.get('rho', 998)))
        elif formula_id == 'lift_force':
            result['results']['F_L'] = lift_force(float(inputs.get('CL', 1.2)), float(inputs.get('rho', 1.225)), float(inputs.get('V', 50)), float(inputs.get('A', 20)))
        elif formula_id == 'drag_force':
            result['results']['F_D'] = drag_force(float(inputs.get('CD', 0.03)), float(inputs.get('rho', 1.225)), float(inputs.get('V', 50)), float(inputs.get('A', 20)))
        elif formula_id == 'lift_drag_ratio':
            result['results']['LD'] = lift_drag_ratio(float(inputs.get('CL', 1.2)), float(inputs.get('CD', 0.03)))
        elif formula_id == 'induced_drag':
            result['results']['CDi'] = induced_drag(float(inputs.get('CL', 1.2)), float(inputs.get('AR', 8)), float(inputs.get('e', 0.8)))
        elif formula_id == 'skin_friction_drag':
            result['results']['F_Df'] = skin_friction_drag(float(inputs.get('Cf', 0.003)), float(inputs.get('rho', 1.225)), float(inputs.get('V', 50)), float(inputs.get('A_wet', 40)))
        elif formula_id == 'wave_drag':
            result['results']['Cdw'] = wave_drag(float(inputs.get('M', 0.95)), float(inputs.get('t_c', 0.12)))
        elif formula_id == 'bluff_body_drag':
            result['results']['F_D'] = bluff_body_drag(float(inputs.get('CD', 1.2)), float(inputs.get('rho', 1.225)), float(inputs.get('V', 30)), float(inputs.get('A_front', 2)))
        elif formula_id == 'stall_speed':
            result['results']['V_stall'] = stall_speed(float(inputs.get('W', 50000)), float(inputs.get('rho', 1.225)), float(inputs.get('S', 25)), float(inputs.get('CL_max', 1.5)))
        elif formula_id == 'aspect_ratio_fx':
            result['results']['AR'] = aspect_ratio_fx(float(inputs.get('b', 12)), float(inputs.get('S', 24)))
        elif formula_id == 'turbulence_intensity':
            result['results']['Tu'] = turbulence_intensity(float(inputs.get('u_rms', 2)), float(inputs.get('U_mean', 20)))
        elif formula_id == 'turbulent_kinetic_energy':
            result['results']['k'] = turbulent_kinetic_energy(float(inputs.get('u_rms', 2)), float(inputs.get('v_rms', 1.5)), float(inputs.get('w_rms', 1)))
        elif formula_id == 'kolmogorov_length_scale':
            result['results']['eta'] = kolmogorov_length_scale(float(inputs.get('epsilon', 0.01)), float(inputs.get('nu', 1e-6)))
        elif formula_id == 'kolmogorov_time_scale':
            result['results']['tau_eta'] = kolmogorov_time_scale(float(inputs.get('epsilon', 0.01)), float(inputs.get('nu', 1e-6)))
        elif formula_id == 'kolmogorov_velocity_scale':
            result['results']['u_eta'] = kolmogorov_velocity_scale(float(inputs.get('epsilon', 0.01)), float(inputs.get('nu', 1e-6)))
        elif formula_id == 'eddy_viscosity_mixing_length':
            result['results']['nu_t'] = eddy_viscosity_mixing_length(float(inputs.get('l_m', 0.01)), float(inputs.get('dU_dy', 500)))
        elif formula_id == 'reynolds_stress_uv':
            result['results']['tau_t'] = reynolds_stress_uv(float(inputs.get('rho', 998)), float(inputs.get('nu_t', 0.05)), float(inputs.get('dU_dy', 500)))
        elif formula_id == 'viscous_sublayer_thickness':
            result['results']['y_vs'] = viscous_sublayer_thickness(float(inputs.get('nu', 1e-6)), float(inputs.get('u_tau', 0.5)))
        elif formula_id == 'friction_velocity':
            result['results']['u_tau'] = friction_velocity(float(inputs.get('tau_w', 10)), float(inputs.get('rho', 998)))
        elif formula_id == 'logarithmic_law':
            result['results']['u_plus'] = logarithmic_law(float(inputs.get('y_plus', 100)))
        elif formula_id == 'cfl_condition':
            result['results']['CFL'] = cfl_condition(float(inputs.get('U', 10)), float(inputs.get('dt', 0.001)), float(inputs.get('dx', 0.02)))
        elif formula_id == 'grid_reynolds_number':
            result['results']['Re_dx'] = grid_reynolds_number(float(inputs.get('U', 1)), float(inputs.get('dx', 0.01)), float(inputs.get('nu', 1e-6)))
        elif formula_id == 'peclet_number':
            result['results']['Pe'] = peclet_number(float(inputs.get('U', 1)), float(inputs.get('L', 1)), float(inputs.get('alpha', 1.5e-5)))
        elif formula_id == 'courant_number_wave':
            result['results']['Co'] = courant_number_wave(float(inputs.get('c', 340)), float(inputs.get('dt', 0.001)), float(inputs.get('dx', 0.1)))
        elif formula_id == 'numerical_diffusion_coeff':
            result['results']['D_num'] = numerical_diffusion_coeff(float(inputs.get('U', 1)), float(inputs.get('dx', 0.01)), float(inputs.get('scheme_order', 1)))
        elif formula_id == 'mesh_reynolds_requirement':
            result['results']['dx_max'] = mesh_reynolds_requirement(float(inputs.get('U', 1)), float(inputs.get('nu', 1e-6)))
        elif formula_id == 'taylor_microscale':
            result['results']['lambda_mu'] = taylor_microscale(float(inputs.get('lambda_g', 0.05)), float(inputs.get('U', 10)), float(inputs.get('nu', 1e-5)))
        elif formula_id == 'turbulent_viscosity_ratio':
            result['results']['nu_t_ratio'] = turbulent_viscosity_ratio(float(inputs.get('nu_t', 0.001)), float(inputs.get('nu', 1e-6)))
        elif formula_id == 'dissipation_rate_estimate':
            result['results']['epsilon'] = dissipation_rate_estimate(float(inputs.get('k', 0.1)), float(inputs.get('L_integral', 0.5)))
        elif formula_id == 'y_plus_estimate':
            result['results']['y_plus'] = y_plus_estimate(float(inputs.get('y', 0.001)), float(inputs.get('u_tau', 0.5)), float(inputs.get('nu', 1e-6)))
        elif formula_id == 'crit_cav_factor':
            result['results']['sigma_cr'] = critical_cavitation_factor(float(inputs.get('V', 10)), float(inputs.get('D', 0.1)), float(inputs.get('sigma_st', 0.073)), float(inputs.get('rho', 998))) or 0
        # --- Sprint 5: Pumps & Turbomachinery ---
        elif formula_id == 'pump_hydraulic_power':
            result['results'] = pump_hydraulic_power(inputs)
        elif formula_id == 'pump_shaft_power':
            result['results'] = pump_shaft_power(inputs)
        elif formula_id == 'pump_efficiency':
            result['results'] = pump_efficiency(inputs)
        elif formula_id == 'specific_speed_metric':
            result['results'] = specific_speed_metric(inputs)
        elif formula_id == 'specific_speed_imperial':
            result['results'] = specific_speed_imperial(inputs)
        elif formula_id == 'affinity_law_Q':
            result['results'] = affinity_law_Q(inputs)
        elif formula_id == 'affinity_law_H':
            result['results'] = affinity_law_H(inputs)
        elif formula_id == 'npsh_available':
            result['results'] = npsh_available(inputs)
        elif formula_id == 'suction_specific_speed':
            result['results'] = suction_specific_speed(inputs)
        # --- Sprint 5: Flow Measurement ---
        elif formula_id == 'venturi_flow_rate':
            result['results'] = venturi_flow_rate(inputs)
        elif formula_id == 'venturi_mass_flow':
            result['results'] = venturi_mass_flow(inputs)
        elif formula_id == 'orifice_flow_rate':
            result['results'] = orifice_flow_rate(inputs)
        elif formula_id == 'pitot_velocity':
            result['results'] = pitot_velocity(inputs)
        elif formula_id == 'weir_rectangular':
            result['results'] = weir_rectangular(inputs)
        elif formula_id == 'weir_vnotch':
            result['results'] = weir_vnotch(inputs)
        elif formula_id == 'nozzle_flow_rate':
            result['results'] = nozzle_flow_rate(inputs)
        elif formula_id == 'rotameter_flow':
            result['results'] = rotameter_flow(inputs)
        # --- Sprint 5: External Aerodynamics ---
        elif formula_id == 'lift_force':
            result['results'] = lift_force(inputs)
        elif formula_id == 'drag_force':
            result['results'] = drag_force(inputs)
        elif formula_id == 'lift_drag_ratio':
            result['results'] = lift_drag_ratio(inputs)
        elif formula_id == 'induced_drag':
            result['results'] = induced_drag(inputs)
        elif formula_id == 'skin_friction_drag':
            result['results'] = skin_friction_drag(inputs)
        elif formula_id == 'wave_drag':
            result['results'] = wave_drag(inputs)
        elif formula_id == 'bluff_body_drag':
            result['results'] = bluff_body_drag(inputs)
        elif formula_id == 'stall_speed':
            result['results'] = stall_speed(inputs)
        elif formula_id == 'aspect_ratio_fx':
            result['results'] = aspect_ratio_fx(inputs)
        # --- Sprint 5: Turbulence ---
        elif formula_id == 'turbulence_intensity':
            result['results'] = turbulence_intensity(inputs)
        elif formula_id == 'turbulent_kinetic_energy':
            result['results'] = turbulent_kinetic_energy(inputs)
        elif formula_id == 'kolmogorov_length_scale':
            result['results'] = kolmogorov_length_scale(inputs)
        elif formula_id == 'kolmogorov_time_scale':
            result['results'] = kolmogorov_time_scale(inputs)
        elif formula_id == 'kolmogorov_velocity_scale':
            result['results'] = kolmogorov_velocity_scale(inputs)
        elif formula_id == 'eddy_viscosity_mixing_length':
            result['results'] = eddy_viscosity_mixing_length(inputs)
        elif formula_id == 'reynolds_stress_uv':
            result['results'] = reynolds_stress_uv(inputs)
        elif formula_id == 'viscous_sublayer_thickness':
            result['results'] = viscous_sublayer_thickness(inputs)
        elif formula_id == 'friction_velocity':
            result['results'] = friction_velocity(inputs)
        elif formula_id == 'logarithmic_law':
            result['results'] = logarithmic_law(inputs)
        # --- Sprint 5: CFD Fundamentals ---
        elif formula_id == 'cfl_condition':
            result['results'] = cfl_condition(inputs)
        elif formula_id == 'grid_reynolds_number':
            result['results'] = grid_reynolds_number(inputs)
        elif formula_id == 'peclet_number':
            result['results'] = peclet_number(inputs)
        elif formula_id == 'courant_number_wave':
            result['results'] = courant_number_wave(inputs)
        elif formula_id == 'numerical_diffusion_coeff':
            result['results'] = numerical_diffusion_coeff(inputs)
        elif formula_id == 'mesh_reynolds_requirement':
            result['results'] = mesh_reynolds_requirement(inputs)
        elif formula_id == 'taylor_microscale':
            result['results'] = taylor_microscale(inputs)
        elif formula_id == 'turbulent_viscosity_ratio':
            result['results'] = turbulent_viscosity_ratio(inputs)
        elif formula_id == 'dissipation_rate_estimate':
            result['results'] = dissipation_rate_estimate(inputs)
        elif formula_id == 'y_plus_estimate':
            result['results'] = y_plus_estimate(inputs)

        else:
            result['error'] = f'Unknown formula_id: {formula_id}'

    except Exception as e:
        result['error'] = str(e)

    return _clean(result)