"""
Sprint 4: Non-Newtonian Fluids + Multi-Phase Flow + Cavitation
Injects into fluid_mechanics_calc.py (functions + catalog + dispatch)
"""

import math

# =============================================================================
# Category 14: Non-Newtonian Fluid Models
# =============================================================================

def bingham_shear_stress(tau_y, mu_p, gamma_dot):
    """Bingham plastic: tau = tau_y + mu_p * gamma_dot"""
    if gamma_dot < 0: return None
    if tau_y < 0 or mu_p < 0: return None
    return tau_y + mu_p * gamma_dot

def bingham_pipe_flow_rate(tau_y, mu_p, dP, L, R_pipe):
    """Buckingham-Reiner: Q = (pi*R^4*dP)/(8*mu_p*L) * (1 - 4/3*phi + phi^4/3)
    where phi = tau_y / tau_w and tau_w = dP * R / (2*L)"""
    if dP <= 0 or L <= 0 or R_pipe <= 0: return None
    if mu_p <= 0: return None
    tau_w = dP * R_pipe / (2 * L)
    if tau_w <= tau_y: return 0.0  # no flow below yield
    phi = tau_y / tau_w
    factor = 1 - 4/3 * phi + phi**4 / 3
    if factor <= 0: return 0.0
    Q = (math.pi * R_pipe**4 * dP) / (8 * mu_p * L) * factor
    return Q

def power_law_apparent_viscosity(K, n, gamma_dot):
    """Ostwald-de Waele: mu_app = K * gamma_dot^(n-1)"""
    if gamma_dot <= 0: return None
    if K < 0: return None
    return K * gamma_dot**(n - 1)

def power_law_pipe_flow_velocity(K, n, dP, L, R_pipe):
    """Power-law pipe flow: V_avg = (dP/(2*K*L))^(1/n) * n/(3n+1) * R^((n+1)/n)"""
    if dP <= 0 or L <= 0 or R_pipe <= 0: return None
    if K <= 0 or n <= 0: return None
    factor = dP / (2 * K * L)
    return factor**(1/n) * n / (3*n + 1) * R_pipe**((n+1)/n)

def generalized_reynolds_number_power_law(rho, V, D, K, n):
    """Metzner-Reed: Re_MR = rho * V^(2-n) * D^n / (K * 8^(n-1) * ((3n+1)/(4n))^n)"""
    if V <= 0 or D <= 0 or rho <= 0: return None
    if K <= 0 or n <= 0: return None
    num = rho * V**(2 - n) * D**n
    den = K * 8**(n - 1) * ((3*n + 1) / (4*n))**n
    if den <= 0: return None
    return num / den

def dodge_metzner_friction_factor(Re_MR, n):
    """Dodge-Metzner: 1/sqrt(f) = 4/n^0.75 * log10(Re_MR * f^(1-n/2)) - 0.4/n^1.2"""
    if Re_MR <= 0 or n <= 0: return None
    # Iterative solution
    f = 0.01
    for _ in range(30):
        try:
            rhs = 4 / n**0.75 * math.log10(Re_MR * f**(1 - n/2)) - 0.4 / n**1.2
            f_new = 1 / rhs**2
            if abs(f_new - f) < 1e-10:
                f = f_new
                break
            f = f_new
        except (ValueError, ZeroDivisionError):
            return None
    return f

def herschel_bulkley_shear_stress(tau_y, K, n, gamma_dot):
    """Herschel-Bulkley: tau = tau_y + K * gamma_dot^n"""
    if gamma_dot < 0: return None
    if tau_y < 0 or K < 0 or n <= 0: return None
    return tau_y + K * gamma_dot**n

def casson_shear_stress(tau_y, mu_c, gamma_dot):
    """Casson: sqrt(tau) = sqrt(tau_y) + sqrt(mu_c * gamma_dot)"""
    if gamma_dot < 0: return None
    if tau_y < 0 or mu_c < 0: return None
    inner = math.sqrt(tau_y) + math.sqrt(mu_c * gamma_dot)
    return inner**2


# =============================================================================
# Category 15: Multi-Phase Flow
# =============================================================================

def homogeneous_void_fraction(x, rho_g, rho_l):
    """Homogeneous void fraction: alpha = 1 / (1 + (1-x)/x * rho_g/rho_l)"""
    if x <= 0 or x >= 1: return None
    if rho_g <= 0 or rho_l <= 0: return None
    return 1 / (1 + (1 - x) / x * rho_g / rho_l)

def homogeneous_two_phase_density(x, rho_g, rho_l):
    """Homogeneous two-phase density: rho_tp = 1 / (x/rho_g + (1-x)/rho_l)"""
    if x < 0 or x > 1: return None
    if rho_g <= 0 or rho_l <= 0: return None
    if x == 0: return rho_l
    if x == 1: return rho_g
    return 1 / (x / rho_g + (1 - x) / rho_l)

def mcadams_viscosity(x, mu_g, mu_l):
    """McAdams two-phase viscosity: 1/mu_tp = x/mu_g + (1-x)/mu_l"""
    if x < 0 or x > 1: return None
    if mu_g <= 0 or mu_l <= 0: return None
    return 1 / (x / mu_g + (1 - x) / mu_l)

def lockhart_martinelli_X(x, rho_g, rho_l, mu_g, mu_l):
    """Lockhart-Martinelli parameter: X = ((1-x)/x)^0.9 * (rho_g/rho_l)^0.5 * (mu_l/mu_g)^0.1"""
    if x <= 0 or x >= 1: return None
    if rho_g <= 0 or rho_l <= 0: return None
    if mu_g <= 0 or mu_l <= 0: return None
    return ((1 - x) / x)**0.9 * (rho_g / rho_l)**0.5 * (mu_l / mu_g)**0.1

def chisholm_two_phase_multiplier(X, C):
    """Chisholm: phi_l^2 = 1 + C/X + 1/X^2"""
    if X <= 0: return None
    return 1 + C / X + 1 / X**2

def drift_flux_void_fraction(j_g, j_l, C0):
    """Drift flux: alpha = j_g / (C0 * (j_g + j_l) + V_gj)"""
    j_total = j_g + j_l
    if j_total <= 0: return None
    # Default V_gj = 0.25 m/s for bubbly flow
    V_gj = 0.25
    return j_g / (C0 * j_total + V_gj)

def baker_flow_pattern_map(G_g, G_l, lmbda, psi):
    """Baker flow pattern coordinates: G_g/lmbda vs G_l*lmbda*psi/G_g"""
    if G_g <= 0 or G_l <= 0 or lmbda <= 0 or psi <= 0: return None
    x_baker = G_g / lmbda
    y_baker = G_l * lmbda * psi / G_g
    return {'x_baker': x_baker, 'y_baker': y_baker}

def taitel_dukler_transition(v_sg, D, rho_g, rho_l, sigma_st):
    """Taitel-Dukler bubbly-to-slug transition velocity"""
    if D <= 0 or rho_l <= 0 or sigma_st <= 0: return None
    g = 9.81
    v_sg_crit = 0.25 * (g * (rho_l - rho_g) * sigma_st / rho_l**2)**0.25
    return v_sg_crit

def slug_frequency(v_sl, v_sg, D):
    """Estimated slug frequency: f_s = 0.0226 * (v_sl/g/D * (19.75 + v_m^2/g/D))^1.2"""
    if D <= 0: return None
    g = 9.81
    v_m = v_sl + v_sg
    if v_m <= 0: return None
    inner = v_sl / (g * D) * (19.75 + v_m**2 / (g * D))
    if inner <= 0: return None
    return 0.0226 * inner**1.2


# =============================================================================
# Category 16: Cavitation
# =============================================================================

def cavitation_number(P_ref, P_v, rho, V):
    """Cavitation number: sigma = (P_ref - P_v) / (0.5 * rho * V^2)"""
    if rho <= 0 or V <= 0: return None
    return (P_ref - P_v) / (0.5 * rho * V**2)

def thoma_cavitation_parameter(H_atm, H_v, H_s):
    """Thoma parameter: sigma_T = (H_atm - H_v - H_s) / H"""
    if H_s + H_v <= 0: return None
    H = 20  # default pump head
    return (H_atm - H_v - H_s) / H

def npsh_available(P_atm, P_v, h_s, h_f, rho):
    """NPSH_a = (P_atm - P_v) / (rho * g) + h_s - h_f"""
    g = 9.81
    if rho <= 0: return None
    return (P_atm - P_v) / (rho * g) + h_s - h_f

def npsh_required_by_suction_specific_speed(N, Q, S):
    """NPSH_r = (N * sqrt(Q) / S)^(4/3)"""
    if Q <= 0 or S <= 0: return None
    return (N * math.sqrt(Q) / S)**(4.0/3.0)

def rayleigh_plesset_radius(R0, P_v, P_inf, rho, t):
    """Rayleigh-Plesset simplified: R_max(t) = R0 + sqrt(2*(P_v - P_inf)/(3*rho)) * t"""
    if rho <= 0: return None
    dp = P_v - P_inf
    if dp <= 0: return R0  # no growth
    return R0 + math.sqrt(2 * dp / (3 * rho)) * t

def bubble_natural_frequency(P_inf, rho, R0, k):
    """Minnaert: f_n = 1/(2*pi*R0) * sqrt(3*k*P_inf/rho)"""
    if R0 <= 0 or rho <= 0 or P_inf <= 0 or k <= 0: return None
    return 1 / (2 * math.pi * R0) * math.sqrt(3 * k * P_inf / rho)

def cavitation_erosion_power(rho, V, A, sigma_f):
    """Erosion power estimate: P_eros = sigma_f * rho * V^3 * A / 2"""
    if rho <= 0 or A <= 0: return None
    sigma_eff = sigma_f if sigma_f < 1.0 else None
    if sigma_eff is None: return None
    return sigma_eff * rho * V**3 * A / 2

def critical_cavitation_factor(V, D, sigma_st, rho):
    """Empirical critical cavitation factor"""
    if V <= 0 or D <= 0 or rho <= 0: return None
    return sigma_st / (0.5 * rho * V**2 * D)


# =============================================================================
# Formula definitions for injection into get_all_formulas()
# =============================================================================

CATALOG_ENTRIES = """
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
"""

# Compute dispatch entries for the end of compute_formula()
COMPUTE_DISPATCH = """
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
        elif formula_id == 'npsh_a':
            result['results']['NPSH_a'] = npsh_available(float(inputs.get('P_atm', 101325)), float(inputs.get('P_v', 2340)), float(inputs.get('h_s', 2)), float(inputs.get('h_f', 0.5)), float(inputs.get('rho', 998))) or 0
        elif formula_id == 'npsh_r':
            result['results']['NPSH_r'] = npsh_required_by_suction_specific_speed(float(inputs.get('N', 1750)), float(inputs.get('Q', 0.1)), float(inputs.get('S', 8000))) or 0
        elif formula_id == 'rayleigh_plesset':
            result['results']['R_max'] = rayleigh_plesset_radius(float(inputs.get('R0', 1e-5)), float(inputs.get('P_v', 2340)), float(inputs.get('P_inf', 101325)), float(inputs.get('rho', 998)), float(inputs.get('t', 1e-6))) or 0
        elif formula_id == 'bubble_freq':
            result['results']['f_n'] = bubble_natural_frequency(float(inputs.get('P_inf', 101325)), float(inputs.get('rho', 998)), float(inputs.get('R0', 1e-5)), float(inputs.get('k', 1.4))) or 0
        elif formula_id == 'cav_erosion':
            result['results']['P_eros'] = cavitation_erosion_power(float(inputs.get('rho', 998)), float(inputs.get('V', 30)), float(inputs.get('A', 0.01)), float(inputs.get('sigma_f', 0.1))) or 0
        elif formula_id == 'crit_cav_factor':
            result['results']['sigma_cr'] = critical_cavitation_factor(float(inputs.get('V', 10)), float(inputs.get('D', 0.1)), float(inputs.get('sigma_st', 0.073)), float(inputs.get('rho', 998))) or 0
"""

if __name__ == "__main__":
    # Test all formulas
    tests = {
        'bingham_shear': bingham_shear_stress(10, 0.5, 100),
        'bingham_pipe_Q': bingham_pipe_flow_rate(10, 0.5, 100000, 1.0, 0.025),
        'power_law_mu_app': power_law_apparent_viscosity(1, 0.5, 100),
        'power_law_pipe_V': power_law_pipe_flow_velocity(1, 0.5, 100000, 1.0, 0.025),
        're_gen_power_law': generalized_reynolds_number_power_law(1000, 1.0, 0.05, 1, 0.5),
        'dodge_metzner_f': dodge_metzner_friction_factor(5000, 0.7),
        'hb_shear': herschel_bulkley_shear_stress(10, 1, 0.6, 100),
        'casson_shear': casson_shear_stress(5, 0.01, 100),
        'hom_void_frac': homogeneous_void_fraction(0.1, 1.2, 1000),
        'hom_tp_density': homogeneous_two_phase_density(0.1, 1.2, 1000),
        'mcadams_visc': mcadams_viscosity(0.1, 1.8e-5, 0.001),
        'LM_X': lockhart_martinelli_X(0.3, 1.2, 1000, 1.8e-5, 0.001),
        'chisholm_phi2': chisholm_two_phase_multiplier(1.0, 20),
        'drift_flux_alpha': drift_flux_void_fraction(0.5, 1.0, 1.2),
        'baker_map': baker_flow_pattern_map(100, 500, 1, 1),
        'taitel_dukler': taitel_dukler_transition(1.0, 0.05, 1.2, 1000, 0.073),
        'slug_freq': slug_frequency(1.0, 2.0, 0.05),
        'cav_number': cavitation_number(101325, 2340, 998, 10),
        'thoma_param': thoma_cavitation_parameter(10.33, 0.24, 3),
        'npsh_a': npsh_available(101325, 2340, 2, 0.5, 998),
        'npsh_r': npsh_required_by_suction_specific_speed(1750, 0.1, 8000),
        'rayleigh_plesset': rayleigh_plesset_radius(1e-5, 2340, 101325, 998, 1e-6),
        'bubble_freq': bubble_natural_frequency(101325, 998, 1e-5, 1.4),
        'cav_erosion': cavitation_erosion_power(998, 30, 0.01, 0.1),
        'crit_cav_factor': critical_cavitation_factor(10, 0.1, 0.073, 998),
    }
    for name, val in tests.items():
        status = "OK" if val is not None and (not isinstance(val, float) or not math.isnan(val)) else "FAIL"
        if isinstance(val, float):
            print(f"  {name}: {val:.6g} [{status}]")
        elif isinstance(val, dict):
            print(f"  {name}: {val} [{status}]")
        else:
            print(f"  {name}: {val} [{status}]")
    print("All tests complete.")
