# -*- coding: utf-8 -*-
"""
Sprint 5 — Super Fluid Mechanics Calculator Expansion
Categories: Pumps, Flow Measurement, Aerodynamics, Turbulence, CFD Basics
35 new formulas
"""
import math

# ==================== Category 17: Pumps & Turbomachinery ====================

def pump_hydraulic_power(Q, rho, H, g=9.81):
    """Hydraulic power [W]: P_h = rho * g * Q * H"""
    return rho * g * Q * H

def pump_shaft_power(P_h, eta=0.75):
    """Shaft power [W]: P_s = P_h / eta"""
    if eta <= 0:
        return None
    return P_h / eta

def pump_efficiency(P_h, P_s):
    """Pump efficiency: eta = P_h / P_s"""
    if P_s <= 0:
        return None
    return P_h / P_s

def specific_speed_metric(Q, H, N):
    """Specific speed (metric): Ns = N * sqrt(Q) / H^(3/4)"""
    if H <= 0:
        return None
    return N * math.sqrt(Q) / (H ** 0.75)

def specific_speed_imperial(Q_gpm, H_ft, N_rpm):
    """Specific speed (US): Ns_us = N * sqrt(Q_gpm) / H_ft^(3/4)"""
    if H_ft <= 0:
        return None
    return N_rpm * math.sqrt(Q_gpm) / (H_ft ** 0.75)

def affinity_law_Q(D1, D2, N1, N2):
    """Affinity law - flow rate: Q2/Q1 = (D2/D1)^3 * (N2/N1)"""
    if D1 <= 0 or N1 <= 0:
        return None
    return (D2 / D1) ** 3 * (N2 / N1)

def affinity_law_H(D1, D2, N1, N2):
    """Affinity law - head: H2/H1 = (D2/D1)^2 * (N2/N1)^2"""
    if D1 <= 0 or N1 <= 0:
        return None
    return (D2 / D1) ** 2 * (N2 / N1) ** 2

def npsh_available(P_atm, P_v, h_s, h_f, rho=998, g=9.81):
    """NPSH available [m]: NPSHa = (P_atm - P_v)/(rho*g) + h_s - h_f"""
    if rho <= 0:
        return None
    return (P_atm - P_v) / (rho * g) + h_s - h_f

def suction_specific_speed(Q, NPSHr, N):
    """Suction specific speed: Nss = N * sqrt(Q) / NPSHr^(3/4)"""
    if NPSHr <= 0:
        return None
    return N * math.sqrt(Q) / (NPSHr ** 0.75)


# ==================== Category 18: Flow Measurement ====================

def venturi_flow_rate(Cd, A2, rho, dp, beta):
    """Venturi meter volumetric flow [m3/s]: Q = Cd*A2*sqrt(2*dp/(rho*(1-beta^4)))"""
    if rho <= 0 or beta >= 1:
        return None
    return Cd * A2 * math.sqrt(2 * dp / (rho * (1 - beta ** 4)))

def venturi_mass_flow(Cd, A2, rho, dp, beta):
    """Venturi mass flow [kg/s]"""
    if rho <= 0 or beta >= 1:
        return None
    return Cd * A2 * math.sqrt(2 * rho * dp / (1 - beta ** 4))

def orifice_flow_rate(Cd, A0, rho, dp, beta):
    """Orifice plate volumetric flow [m3/s]"""
    if rho <= 0 or beta >= 1:
        return None
    return Cd * A0 * math.sqrt(2 * dp / (rho * (1 - beta ** 4)))

def pitot_velocity(dp, rho=1.225):
    """Pitot tube velocity [m/s]: V = sqrt(2*dp/rho)"""
    if rho <= 0:
        return None
    return math.sqrt(2 * dp / rho)

def weir_rectangular(Cd, b, H):
    """Rectangular weir flow [m3/s]: Q = Cd * (2/3) * b * sqrt(2g) * H^(3/2)"""
    if H < 0:
        return None
    g = 9.81
    return Cd * (2/3) * b * math.sqrt(2 * g) * (H ** 1.5)

def weir_vnotch(Cd, theta_deg, H):
    """V-notch (triangular) weir [m3/s]: Q = Cd * (8/15) * tan(theta/2) * sqrt(2g) * H^(5/2)"""
    if H < 0:
        return None
    g = 9.81
    theta = math.radians(theta_deg)
    return Cd * (8/15) * math.tan(theta/2) * math.sqrt(2*g) * (H ** 2.5)

def nozzle_flow_rate(Cd, A_n, rho, dp):
    """Flow nozzle [m3/s]: Q = Cd * A_n * sqrt(2*dp/rho)"""
    if rho <= 0:
        return None
    return Cd * A_n * math.sqrt(2 * dp / rho)

def rotameter_flow(Cd, A_annulus, V_float, rho_f, rho, g=9.81, A_float=1):
    """Rotameter flow [m3/s]: Q = Cd*A_annulus*sqrt(2*g*V_float*(rho_f-rho)/(rho*A_float))"""
    denom = rho * A_float
    if denom <= 0:
        return None
    return Cd * A_annulus * math.sqrt(2 * g * V_float * (rho_f - rho) / denom)


# ==================== Category 19: External Aerodynamics ====================

def lift_force(CL, rho, V, A):
    """Lift force [N]: FL = 0.5 * CL * rho * V^2 * A"""
    return 0.5 * CL * rho * V * V * A

def drag_force(CD, rho, V, A):
    """Drag force [N]: FD = 0.5 * CD * rho * V^2 * A"""
    return 0.5 * CD * rho * V * V * A

def lift_drag_ratio(CL, CD):
    """L/D ratio"""
    if CD == 0:
        return None
    return CL / CD

def induced_drag(CL, AR, e=0.8):
    """Induced drag coefficient: CDi = CL^2 / (pi * AR * e)"""
    if AR <= 0 or e <= 0:
        return None
    return CL * CL / (math.pi * AR * e)

def skin_friction_drag(Cf, rho, V, A_wet):
    """Skin friction drag [N]"""
    return 0.5 * Cf * rho * V * V * A_wet

def wave_drag(M, t_c):
    """Wave drag estimate (transonic): Cdw = f(M, t/c)"""
    if M <= 0.8:
        return 0.0
    return 10 * (M - 0.8) ** 3 * (t_c) ** 2

def bluff_body_drag(CD, rho, V, A_front):
    """Bluff body drag force [N]: FD = 0.5 * CD * rho * V^2 * A_front"""
    return 0.5 * CD * rho * V * V * A_front

def stall_speed(W, rho, S, CL_max):
    """Stall speed [m/s]: V_stall = sqrt(2W/(rho*S*CL_max))"""
    if rho <= 0 or S <= 0 or CL_max <= 0:
        return None
    return math.sqrt(2 * W / (rho * S * CL_max))

def aspect_ratio_fx(b, S):
    """Aspect ratio: AR = b^2 / S"""
    if S <= 0:
        return None
    return b * b / S


# ==================== Category 20: Turbulence ====================

def turbulence_intensity(u_rms, U_mean):
    """Turbulence intensity: Tu = u_rms / U_mean"""
    if U_mean == 0:
        return None
    return u_rms / U_mean

def turbulent_kinetic_energy(u_rms, v_rms, w_rms):
    """Turbulent kinetic energy [m2/s2]: k = 0.5*(u'^2 + v'^2 + w'^2)"""
    return 0.5 * (u_rms*u_rms + v_rms*v_rms + w_rms*w_rms)

def kolmogorov_length_scale(epsilon, nu):
    """Kolmogorov length scale [m]: eta = (nu^3/epsilon)^(1/4)"""
    if epsilon <= 0:
        return None
    return (nu ** 3 / epsilon) ** 0.25

def kolmogorov_time_scale(epsilon, nu):
    """Kolmogorov time scale [s]: tau = (nu/epsilon)^(1/2)"""
    if epsilon <= 0:
        return None
    return math.sqrt(nu / epsilon)

def kolmogorov_velocity_scale(epsilon, nu):
    """Kolmogorov velocity scale [m/s]: u_eta = (nu*epsilon)^(1/4)"""
    return (nu * epsilon) ** 0.25

def eddy_viscosity_mixing_length(l_m, dU_dy):
    """Eddy viscosity (mixing length) [m2/s]: nu_t = l_m^2 * |dU/dy|"""
    return l_m * l_m * abs(dU_dy)

def reynolds_stress_uv(rho, nu_t, dU_dy):
    """Reynolds shear stress [Pa]: tau_t = -rho * nu_t * dU/dy"""
    return -rho * nu_t * dU_dy

def viscous_sublayer_thickness(nu, u_tau):
    """Viscous sublayer thickness: y+ = 5 => y = 5*nu/u_tau"""
    if u_tau <= 0:
        return None
    return 5 * nu / u_tau

def friction_velocity(tau_w, rho):
    """Friction velocity [m/s]: u_tau = sqrt(tau_w/rho)"""
    if rho <= 0:
        return None
    return math.sqrt(tau_w / rho)

def logarithmic_law(y_plus, kappa=0.41, B=5.0):
    """Log-law: u+ = (1/kappa)*ln(y+) + B"""
    if y_plus <= 0:
        return None
    return (1/kappa) * math.log(y_plus) + B


# ==================== Category 21: CFD Fundamentals ====================

def cfl_condition(U, dt, dx):
    """CFL number: CFL = U*dt/dx (must be < 1 for explicit schemes)"""
    if dx <= 0:
        return None
    return U * dt / dx

def grid_reynolds_number(U, dx, nu):
    """Grid/mesh Reynolds number: Re_dx = U*dx/nu"""
    if nu <= 0:
        return None
    return U * dx / nu

def peclet_number(U, L, alpha):
    """Peclet number: Pe = U*L/alpha (convection vs diffusion)"""
    if alpha <= 0:
        return None
    return U * L / alpha

def courant_number_wave(c, dt, dx):
    """Courant number for wave: Co = c*dt/dx"""
    if dx <= 0:
        return None
    return c * dt / dx

def numerical_diffusion_coeff(U, dx, scheme_order=1):
    """Estimated numerical diffusion coefficient"""
    if scheme_order == 1:
        return 0.5 * U * dx
    return 0.5 * U * dx / scheme_order

def mesh_reynolds_requirement(U, nu, CFL_target=0.5):
    """Required dx for Re_dx < 2: dx < 2*nu/U"""
    if U <= 0:
        return None
    return 2 * nu / U

def taylor_microscale(lambda_g, U, nu):
    """Taylor microscale [m]: relation to Re_lambda = u'*lambda/nu"""
    if U <= 0:
        return None
    return math.sqrt(15 * nu / (U / lambda_g)) if lambda_g > 0 else None

def turbulent_viscosity_ratio(nu_t, nu):
    """Turbulent viscosity ratio"""
    if nu <= 0:
        return None
    return nu_t / nu

def dissipation_rate_estimate(k, L_integral, C_mu=0.09):
    """Turbulent dissipation rate: epsilon = C_mu^(3/4) * k^(3/2) / L"""
    if L_integral <= 0:
        return None
    return (C_mu ** 0.75) * (k ** 1.5) / L_integral

def y_plus_estimate(y, u_tau, nu):
    """Wall distance in wall units: y+ = y*u_tau/nu"""
    if nu <= 0:
        return None
    return y * u_tau / nu
