#!/usr/bin/env python3
"""
Sprint 5 full injection into fluid_mechanics_calc.py (restored version).
1. Import Sprint 5 functions
2. Inject dispatch entries into compute_formula()
3. Inject get_all_formulas() category entries
"""
import os, py_compile

base = os.path.dirname(os.path.abspath(__file__))
target = os.path.join(base, 'fluid_mechanics_calc.py')
with open(target, 'r', encoding='utf-8') as f:
    c = f.read()

orig = len(c)
print(f"File: {target} ({orig} bytes)")

# === STEP 1: Import ===
mk1 = "# Sprint 4: Non-Newtonian, Multi-Phase, Cavitation"
blk1 = """# Sprint 5: Pumps, Flow Measurement, Aerodynamics, Turbulence, CFD
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

"""
c = c.replace(mk1, blk1 + mk1)
print(f"  Import: {len(c) - orig:+d} bytes")

# === STEP 2: Dispatch (after crit_cav_factor inline dispatch) ===
mk2 = "        elif formula_id == 'crit_cav_factor':\n            result['results']['sigma_cr'] = critical_cavitation_factor(float(inputs.get('V', 10)), float(inputs.get('D', 0.1)), float(inputs.get('sigma_st', 0.073)), float(inputs.get('rho', 998))) or 0"
assert c.count(mk2) == 1, f"Dispatch marker count: {c.count(mk2)}"

blk2 = """        # --- Sprint 5: Pumps & Turbomachinery ---
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
            result['results'] = y_plus_estimate(inputs)"""

c = c.replace(mk2, mk2 + "\n" + blk2)
print(f"  Dispatch: {len(c) - orig:+d} bytes")

# === STEP 3: get_all_formulas() - insert 5 new categories after cat 16 ===
mk3 = """            {'id': 'crit_cav_factor', 'name': 'Critical Cavitation Factor', 'eq': 'sigma_cr = sigma_st/(0.5*rho*V^2*D)', 'inputs': ['V', 'D', 'sigma_st', 'rho'], 'output': 'sigma_cr'},
            ]
        },
    }"""
assert c.count(mk3) == 1, f"get_all_formulas marker count: {c.count(mk3)}"

blk3 = """            {'id': 'crit_cav_factor', 'name': 'Critical Cavitation Factor', 'eq': 'sigma_cr = sigma_st/(0.5*rho*V^2*D)', 'inputs': ['V', 'D', 'sigma_st', 'rho'], 'output': 'sigma_cr'},
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
    }"""
c = c.replace(mk3, blk3)
print(f"  get_all_formulas: {len(c) - orig:+d} bytes")

with open(target, 'w', encoding='utf-8') as f:
    f.write(c)

py_compile.compile(target, doraise=True)
print("ok py_compile")
