---
name: seal-pair-designer
description: |
  Aerospace valve seal pair design calculator. Based on Hertz contact theory and Roth molecular flow leakage model.
  Supports contact stress analysis, leak rate calculation (molecular/viscous/transitional flow via Knudsen number),
  seal state determination (binary iteration for critical seal force), reliability assessment (Archard wear + LCF),
  multi-design comparison, and sensitivity analysis.
  Materials: 316L SS, Inconel 718, Ti-6Al-4V, 17-4PH, PTFE, PCTFE, PEEK, FKM, FFKM.
  Gases: N2, He, H2, O2, Air, CH4.
  Standards: ISO 5208, ANSI FCI 70-2, ECSS-E-ST-32-02C.
  Trigger: seal design, sealing calculation, leak rate, contact stress, seal pair, Hertz, Roth leakage.
keywords:
  - "seal design"
  - "leak rate"
  - "contact stress"
  - "Hertz"
  - "valve seal"
  - "seal pair"
  - "Roth"
metadata:
  openclaw:
    emoji: "\U0001f4dc"
---

# Seal Pair Designer Skill

Aerospace valve seal pair design calculation skill.

## Capabilities

| Module | Function | Theory |
|--------|----------|--------|
| HertzContactAnalysis | Contact stress/width | Hertz elastic contact theory |
| LeakRateCalculator | Leak rate, flow regime | Roth molecular flow + Kn number |
| SealStateAnalyzer | Seal state, critical force | Binary iteration |
| ReliabilityAnalyzer | Life prediction, wear | Archard wear + low cycle fatigue |
| AerospaceValveSealDesigner | Main design flow | Integrated |

## API Endpoints (via Flask)

All endpoints are under `/api/avis/seal/` prefix:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/avis/seal/design` | POST | Full seal pair design |
| `/api/avis/seal/compare` | POST | Multi-design comparison |
| `/api/avis/seal/sensitivity` | POST | Sensitivity analysis |
| `/api/avis/seal/info` | GET | Materials, gases, config info |

## Usage from Agent

```python
# Quick design
result = requests.post('http://127.0.0.1:5000/api/avis/seal/design', json={
    'seat_diameter_mm': 15.0,
    'pressure_bar': 10.0,
    'temperature_C': -183.0,
    'seat_material': 'INCONEL_718',
    'seal_material': 'PCTFE',
    'gas': 'O2',
    'target_leak_class': 'AA'
}).json()

# Compare designs
result = requests.post('http://127.0.0.1:5000/api/avis/seal/compare', json={
    'configs': [
        {'label': 'PTFE', 'seat_material': '316L_SS', 'seal_material': 'PTFE', ...},
        {'label': 'PEEK', 'seat_material': '316L_SS', 'seal_material': 'PEEK', ...}
    ],
    'gas': 'N2'
}).json()
```

## Input Parameters (design endpoint)

### Geometry
- `seat_diameter_mm`: Seat diameter [mm], default 10.0
- `contact_type`: sphere_on_flat / sphere_on_cone / cylinder_on_flat / cone_on_cone / flat_on_flat / concave_on_cone
- `seat_angle_deg`: Cone half-angle [deg], default 60.0
- `sphere_radius_mm`: Sphere radius [mm], default 5.0
- `roughness_Ra_um`: Surface roughness Ra [um], default 0.4

### Operating
- `pressure_bar`: Pressure differential [bar], default 10.0
- `temperature_C`: Temperature [C], default 20.0
- `gas`: N2 / He / H2 / O2 / Air / CH4

### Materials
- `seat_material`: Material key (see /info endpoint)
- `seal_material`: Material key (see /info endpoint)

### Options
- `seal_force_N`: Seal force [N] (None = auto-calculate)
- `target_leak_class`: AA / A / B / C / D / E / EE / F / G

## Output Fields

The design output includes:
- Contact mechanics: stress_max, stress_avg, contact_width, contact_area, seal_pressure
- Leak analysis: flow_regime, knudsen_number, effective_gap, leak_rate (multiple units), leak_class
- Safety: stress_ratios, safety_factors, safety_pass
- Reliability: predicted_cycle_life, wear_depth, reliability_index, estimated_mass
- Warnings and recommendations list

## Design Guidelines

1. For aerospace applications, target leak class AA or A
2. Cryogenic applications: use PCTFE or PEEK (not PTFE)
3. High-pressure metal-metal: use concave_on_cone contact type
4. Always check safety_pass before accepting a design
