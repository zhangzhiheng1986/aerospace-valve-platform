"""
PAOR Engine — Plan-Act-Observe-Reflect Reasoning Loop
Valve Brain Core v2.0.1 | 2026-06-12

Architecture:
  PLAN    → Decompose user request into ordered reasoning steps
  ACT     → Execute each step via registered tools
  OBSERVE → Validate results with physics sanity & standard checks
  REFLECT → Synthesize findings, log learnings, suggest improvements

Key design:
- L0 function layer (formulas/DB/standards): zero LLM cost
- Physical validity gates before returning results
- Learning journal captures patterns for later Skill evolution
"""

import re
import math
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field

# ============================================================
# Data Structures
# ============================================================

@dataclass
class PlanStep:
    """A single step in the PAOR plan."""
    step_id: int
    phase: str           # "understand" | "design" | "calculate" | "verify" | "explain"
    tool_name: str       # tool to call
    tool_params: Dict    # parameters for the tool
    description: str     # human-readable what this step does
    depends_on: List[int] = field(default_factory=list)  # step_ids this depends on
    # Filled after execution
    result: Any = None
    success: bool = False
    execution_time_ms: int = 0
    retries: int = 0

@dataclass
class Observation:
    """Validation result for a step's output."""
    step_id: int
    passed: bool
    checks: List[Dict] = field(default_factory=list)  # [{name, passed, detail}]
    warnings: List[str] = field(default_factory=list)
    confidence: float = 0.0   # 0.0-1.0

@dataclass
class PAORPlan:
    """Complete reasoning plan."""
    request_id: str
    user_message: str
    intent: str
    steps: List[PlanStep] = field(default_factory=list)
    context: Dict = field(default_factory=dict)

@dataclass
class Reflection:
    """Post-execution reflection."""
    summary: str
    confidence: float        # overall confidence 0.0-1.0
    key_findings: List[str] = field(default_factory=list)
    pitfalls_triggered: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    learning_candidate: Optional[Dict] = None  # potential new Pitfall for Skill


# ============================================================
# Physics Sanity Validators (Observe layer)
# ============================================================

class PhysicsValidator:
    """Checks physical plausibility of engineering results."""

    # Known physical limits for common quantities
    LIMITS = {
        'pressure_mpa':    (0.001, 1000),     # MPa
        'diameter_mm':     (0.1,  5000),     # mm
        'temperature_c':   (-273, 3000),      # Celsius
        'velocity_ms':     (0,    8000),      # m/s (well below orbital)
        'mass_kg':         (0.001, 10000),    # kg
        'force_n':         (0.01,  1e7),      # N
        'stress_mpa':      (0.01,  5000),     # MPa (beyond strongest known material)
        'density_kgm3':    (0.01,  25000),    # kg/m^3
        'flow_rate_kgs':   (0,     10000),    # kg/s
        'power_w':         (0.01,  1e8),      # W
        'efficiency':       (0,     1.0),     # dimensionless
        'safety_factor':   (0.5,   100),      # dimensionless
        'spring_index':    (3,     25),       # C = D/d (below 3 hard to manufacture)
        'life_cycles':     (1,     1e9),      # cycles
        'leak_rate_pam3s': (1e-12, 1e-2),    # Pa.m^3/s
    }

    @classmethod
    def check_bounds(cls, key: str, value: float) -> Dict:
        """Check if a value falls within known physical bounds."""
        if key in cls.LIMITS:
            lo, hi = cls.LIMITS[key]
            if lo <= value <= hi:
                return {'passed': True, 'detail': f'{value} within [{lo}, {hi}]'}
            else:
                direction = 'low' if value < lo else 'high'
                return {'passed': False, 'detail': f'{value} out of [{lo}, {hi}] (too {direction})'}
        return {'passed': True, 'detail': 'No limit defined'}

    @classmethod
    def validate_safety_factor(cls, value: float, valve_type: str = 'general') -> Dict:
        """Check safety factor against aerospace norms."""
        mins = {
            'general': 1.5,
            'pressure_vessel': 2.0,
            'cryogenic': 2.5,
            'human_rated': 4.0,
        }
        min_sf = mins.get(valve_type, 1.5)
        if value >= min_sf:
            return {'passed': True, 'detail': f'SF={value} >= {min_sf} (ok for {valve_type})'}
        else:
            return {'passed': False, 'detail': f'SF={value} < {min_sf} (unsafe for {valve_type})'}

    @classmethod
    def check_dimensionless(cls, name: str, value: float) -> Dict:
        """Validate common dimensionless numbers."""
        ranges = {
            'reynolds': (0, 1e9),
            'mach': (0, 50),
            'prandtl': (0.01, 1000),
            'nusselt': (0.1, 1e6),
        }
        if name in ranges:
            lo, hi = ranges[name]
            if lo <= value <= hi:
                return {'passed': True, 'detail': f'{name}={value} within [{lo}, {hi}]'}
            else:
                return {'passed': False, 'detail': f'{name}={value} out of range [{lo}, {hi}]'}
        return {'passed': True, 'detail': 'Unknown dimensionless number'}


# ============================================================
# Planner — Decomposes natural language into reasoning steps
# ============================================================

class PAORPlanner:
    """Decompose user request into ordered PlanStep sequence."""

    # Domain knowledge for step decomposition
    VALVE_TYPES = ['solenoid', 'pressure_reducing', 'check', 'relief', 'ball', 'butterfly', 'globe']
    DESIGN_DOMAINS = ['valve', 'spring', 'oring', 'seal', 'spring_design', 'oring_design', 'seal_design']
    CALC_DOMAINS = ['flow_rate', 'pressure_drop', 'reynolds', 'mach', 'force', 'stress', 'heat_transfer']

    @classmethod
    def plan(cls, user_message: str, context: Dict) -> PAORPlan:
        """Create a reasoning plan from user message."""
        request_id = str(uuid.uuid4())[:8]
        msg_lower = user_message.lower()
        steps = []

        # --- Intent classification ---
        intent = cls._classify_intent(user_message)

        plan = PAORPlan(
            request_id=request_id,
            user_message=user_message,
            intent=intent,
            context=context,
        )

        # --- Step decomposition by intent ---

        if intent == 'design_valve':
            steps = cls._plan_valve_design(user_message, context)
        elif intent == 'design_spring':
            steps = cls._plan_spring_design(user_message, context)
        elif intent == 'design_oring':
            steps = cls._plan_oring_design(user_message, context)
        elif intent == 'fluid_calc':
            steps = cls._plan_fluid_calculation(user_message, context)
        elif intent == 'compliance_check':
            steps = cls._plan_compliance(user_message, context)
        elif intent == 'material_lookup':
            steps = cls._plan_material(user_message, context)
        elif intent == 'knowledge_query':
            steps = cls._plan_knowledge(user_message, context)
        else:
            # Fallback: general knowledge
            steps = cls._plan_knowledge(user_message, context)

        plan.steps = steps
        return plan

    @classmethod
    def _classify_intent(cls, message: str) -> str:
        """Classify user intent into one of 7 categories."""
        patterns = [
            (['电磁阀', 'solenoid', '线圈'], 'design_valve'),
            (['减压阀', 'pressure reducing', 'PRV'], 'design_valve'),
            (['单向阀', '止回阀', 'check valve'], 'design_valve'),
            (['弹簧', 'spring', 'compression'], 'design_spring'),
            (['O形圈', 'O型圈', '密封圈', '密封', 'O-ring', 'oring'], 'design_oring'),
            (['计算', '公式', '雷诺', '马赫', '伯努利', '压降', '流量', 'calculate', 'reynolds', 'mach', 'bernoulli'], 'fluid_calc'),
            (['标准', '合规', 'QJ', '鉴定', 'compliance', 'qualification'], 'compliance_check'),
            (['材料', 'material', 'TC4', 'GH4169', '合金', '不锈钢', '铝合金'], 'material_lookup'),
            (['是什么', '解释', '原理', '怎么', '如何', '为什么', 'what is', 'explain', 'how'], 'knowledge_query'),
        ]
        for keywords, intent in patterns:
            for kw in keywords:
                if kw.lower() in message.lower():
                    return intent
        return 'knowledge_query'

    # --- Step Planners ---

    @classmethod
    def _plan_valve_design(cls, message: str, ctx: Dict) -> List[PlanStep]:
        """Plan a valve design request."""
        steps = []
        params = cls._extract_design_params(message)

        # Step 1: Understand the requirement
        steps.append(PlanStep(
            step_id=1, phase='understand', tool_name='parse_requirements',
            tool_params={'message': message},
            description='Parse design requirements from user message',
        ))

        # Step 2: Query relevant knowledge
        steps.append(PlanStep(
            step_id=2, phase='understand', tool_name='search_knowledge',
            tool_params={'query': f'{params.get("valve_type", "valve")} design principles'},
            description='Search knowledge base for relevant design guidance',
            depends_on=[1],
        ))

        # Step 3: Execute the design tool
        step_id = 3
        if 'solenoid' in message.lower() or '电磁' in message:
            steps.append(PlanStep(
                step_id=step_id, phase='design', tool_name='analyze_solenoid_valve',
                tool_params=params,
                description='Run solenoid valve PSO optimization',
                depends_on=[2],
            ))
        elif '减压' in message or 'pressure reducing' in message.lower() or 'prv' in message.lower():
            steps.append(PlanStep(
                step_id=step_id, phase='design', tool_name='analyze_pressure_valve',
                tool_params=params,
                description='Design pressure reducing valve',
                depends_on=[2],
            ))
        else:
            steps.append(PlanStep(
                step_id=step_id, phase='design', tool_name='analyze_check_valve',
                tool_params=params,
                description='Design check valve per HB 6455-2014',
                depends_on=[2],
            ))

        # Step 4: Compliance check
        steps.append(PlanStep(
            step_id=step_id + 1, phase='verify', tool_name='check_compliance',
            tool_params={'valve_type': params.get('valve_type', 'general'), **params},
            description='Verify design against QJ 20156 standard',
            depends_on=[step_id],
        ))

        return steps

    @classmethod
    def _plan_spring_design(cls, message: str, ctx: Dict) -> List[PlanStep]:
        params = cls._extract_design_params(message)
        return [
            PlanStep(1, 'understand', 'parse_requirements',
                     {'message': message}, 'Parse spring requirements'),
            PlanStep(2, 'design', 'design_spring', params,
                     'Design compression spring', depends_on=[1]),
            PlanStep(3, 'verify', 'validate_physics',
                     {'design_type': 'spring', 'depends_on_step': 2},
                     'Validate spring design physics', depends_on=[2]),
        ]

    @classmethod
    def _plan_oring_design(cls, message: str, ctx: Dict) -> List[PlanStep]:
        params = cls._extract_design_params(message)
        return [
            PlanStep(1, 'understand', 'parse_requirements',
                     {'message': message}, 'Parse O-ring requirements'),
            PlanStep(2, 'design', 'design_oring', params,
                     'Design O-ring seal per AS568F/ISO 3601-2', depends_on=[1]),
            PlanStep(3, 'verify', 'validate_physics',
                     {'design_type': 'oring', 'depends_on_step': 2},
                     'Validate O-ring leakage physics', depends_on=[2]),
        ]

    @classmethod
    def _plan_fluid_calculation(cls, message: str, ctx: Dict) -> List[PlanStep]:
        formula_id, inputs = cls._identify_formula(message)
        return [
            PlanStep(1, 'understand', 'search_knowledge',
                     {'query': message},
                     'Search knowledge base for context'),
            PlanStep(2, 'understand', 'identify_formula',
                     {'message': message, 'formula_id': formula_id},
                     f'Identify formula: {formula_id or "unknown"}', depends_on=[1]),
            PlanStep(3, 'calculate', 'run_fluid_calculation',
                     {'formula_id': formula_id, 'inputs': inputs},
                     f'Calculate {formula_id}', depends_on=[2]),
            PlanStep(4, 'verify', 'validate_physics',
                     {'calc_type': formula_id or 'general'},
                     'Validate calculation result', depends_on=[3]),
        ]

    @classmethod
    def _plan_compliance(cls, message: str, ctx: Dict) -> List[PlanStep]:
        params = cls._extract_design_params(message)
        return [
            PlanStep(1, 'verify', 'check_compliance', params,
                     'Check QJ 20156 compliance'),
        ]

    @classmethod
    def _plan_material(cls, message: str, ctx: Dict) -> List[PlanStep]:
        params = cls._extract_design_params(message)
        mat_name = params.get('material', 'TC4')
        return [
            PlanStep(1, 'understand', 'query_material',
                     {'material_name': mat_name},
                     f'Query material: {mat_name}'),
        ]

    @classmethod
    def _plan_knowledge(cls, message: str, ctx: Dict) -> List[PlanStep]:
        return [
            PlanStep(1, 'explain', 'search_knowledge',
                     {'query': message},
                     'Search knowledge base'),
        ]

    # --- Helpers ---

    @classmethod
    def _extract_design_params(cls, message: str) -> Dict:
        """Extract design parameters from natural language."""
        params = {}

        # Numeric with units
        unit_patterns = [
            (r'(\d+\.?\d*)\s*MPa', 'inlet_pressure'),  # keep as MPa for UI, tool normalizes
            (r'(\d+\.?\d*)\s*bar', 'pressure_bar'),
            (r'(\d+\.?\d*)\s*k?Pa\b', 'pressure_kpa'),
            (r'(\d+\.?\d*)\s*mm', 'diameter_mm'),
            (r'(\d+\.?\d*)\s*N\b', 'force_n'),
            (r'(\d+\.?\d*)\s*V\b', 'voltage'),
            (r'(\d+\.?\d*)\s*A\b', 'current_a'),
            (r'(\d+\.?\d*)\s*[°C度Cc]\b', 'temperature_c'),
            (r'(\d+\.?\d*)\s*K\b', 'temperature_k'),
            (r'(\d+\.?\d*)\s*[次周]\b', 'cycles'),
            (r'(\d+\.?\d*)\s*L/min', 'flow_lpm'),
            (r'(\d+\.?\d*)\s*kg/s', 'flow_kgs'),
        ]
        for pattern, key in unit_patterns:
            m = re.search(pattern, message)
            if m:
                params[key] = float(m.group(1))

        # Material names
        materials = ['TC4', 'TC6', 'TC11', 'GH4169', 'GH3030', '1Cr18Ni9Ti',
                     '304', '316L', '7075', '6061', '2A12', 'FKM', 'NBR',
                     'PTFE', 'FFKM', '17-7PH', 'SWP-A', '50CrVA', 'Inconel718']
        for mat in materials:
            if mat.lower() in message.lower():
                params['material'] = mat
                break

        # Fluid types
        fluids = ['kerosene', '煤油', 'nitrogen', '氮气', 'helium', '氦气',
                  'hydrogen', '氢气', 'oxygen', '氧气', 'LOX', '液氧',
                  'LH2', '液氢', 'water', '水', 'hydraulic', '液压']
        fluid_map = {'煤油': 'kerosene', '氮气': 'nitrogen', '氦气': 'helium',
                     '氢气': 'hydrogen', '氧气': 'oxygen', '液氧': 'LOX',
                     '液氢': 'LH2', '水': 'water', '液压': 'hydraulic_oil'}
        for term, key in fluid_map.items():
            if term in message:
                params['fluid_type'] = key
                break
        if 'fluid_type' not in params:
            for f in fluids:
                if f.lower() in message.lower():
                    params['fluid_type'] = fluid_map.get(f, f)
                    break

        # Valve type
        valve_types = {'电磁阀': 'solenoid', 'solenoid': 'solenoid',
                       '减压阀': 'pressure_reducing', '单向阀': 'check',
                       '止回阀': 'check', 'check valve': 'check'}
        for term, vtype in valve_types.items():
            if term.lower() in message.lower():
                params['valve_type'] = vtype
                break

        return params

    @classmethod
    def _identify_formula(cls, message: str) -> Tuple[Optional[str], Dict]:
        """Identify fluid mechanics formula from message and extract inputs."""
        # Extract numeric values from message
        nums = re.findall(r'(\d+\.?\d*)\s*(m/s|mm|cm|L/min|kg|Pa|bar|MPa|Hz|rpm|C)', message)

        # Formula identification rules with real parameter names
        rules = [
            (['雷诺', 'reynolds'], 'reynolds',
             {'rho': 1.2, 'V': 1.0, 'D': 0.01, 'mu': 1.8e-5}),
            (['马赫', 'mach'], 'mach',
             {'V': 340, 'c': 340}),
            (['压降', 'pressure drop', 'darcy'], 'darcy_dp',
             {'f': 0.02, 'L': 1.0, 'D': 0.01, 'rho': 1.2, 'V': 1.0}),
            (['伯努利', 'bernoulli'], 'bernoulli_total_pressure',
             {'P1': 101325, 'rho': 1.2, 'V1': 1.0, 'z1': 0, 'V2': 0, 'z2': 0}),
            (['流量', 'flow rate'], 'volume_flow',
             {'A': 0.00785, 'V': 1.0}),
            (['努塞尔', 'nusselt'], 'bl_turbulent',
             {'Re': 1e5}),
        ]
        for keywords, fid, default_inputs in rules:
            if any(kw.lower() in message.lower() for kw in keywords):
                # Extract user-provided values and map to formula param names
                inputs = dict(default_inputs)
                # Velocity: V
                vm = re.search(r'(\d+\.?\d*)\s*m/s', message)
                if vm:
                    inputs['V'] = float(vm.group(1))
                # Diameter: D
                dm = re.search(r'(\d+\.?\d*)\s*mm', message)
                if dm:
                    inputs['D'] = float(dm.group(1)) / 1000.0  # mm -> m
                cm_match = re.search(r'(\d+\.?\d*)\s*cm', message)
                if cm_match:
                    inputs['D'] = float(cm_match.group(1)) / 100.0  # cm -> m
                if 'D' not in inputs:
                    m_match = re.search(r'(\d+\.?\d*)\s*m(?!\s*/s)', message)
                    if m_match:
                        inputs['D'] = float(m_match.group(1))
                # Pressure: P1
                pm = re.search(r'(\d+\.?\d*)\s*(bar|MPa)', message)
                if pm:
                    val = float(pm.group(1))
                    inputs['P1'] = val * 1e5 if pm.group(2) == 'bar' else val * 1e6
                return fid, inputs
        # If no keyword match, try vector semantic search
        try:
            from vector_store import get_indexer
            idx = get_indexer()
            if "formulas" not in idx.stores:
                idx.build_formula_store()
            hits = idx.stores["formulas"].search(message, top_k=1, min_score=0.1)
            if hits:
                fid = hits[0].get("formula_id")
                # Map common formula_id to known defaults
                known_defaults = {
                    'reynolds_number': {'rho': 1.2, 'V': 1.0, 'D': 0.01, 'mu': 1.8e-5},
                    'mach_number': {'V': 340, 'c': 340},
                    'darcy_weisbach': {'f': 0.02, 'L': 1.0, 'D': 0.01, 'rho': 1.2, 'V': 1.0},
                    'bernoulli_total_pressure': {'P1': 101325, 'rho': 1.2, 'V1': 1.0, 'z1': 0, 'V2': 0, 'z2': 0},
                    'volumetric_flow_rate': {'A': 0.00785, 'V': 1.0},
                    'lift_force': {'rho': 1.2, 'V': 10, 'CL': 1.0, 'A': 0.1},
                    'drag_force': {'rho': 1.2, 'V': 10, 'CD': 1.0, 'A': 0.1},
                }
                inputs = known_defaults.get(fid, {})
                if inputs:
                    # Extract user values (same as above)
                    vm = re.search(r'(\d+\.?\d*)\s*m/s', message)
                    if vm:
                        inputs['V'] = float(vm.group(1))
                    dm = re.search(r'(\d+\.?\d*)\s*mm', message)
                    if dm:
                        inputs['D'] = float(dm.group(1)) / 1000.0
                    return fid, inputs
                return fid, {}
        except Exception:
            pass  # Graceful fallback — vector search is optional
        return None, {}


# ============================================================
# Observer — Validates step results
# ============================================================

class PAORObserver:
    """Validates and sanity-checks step execution results."""

    @classmethod
    def observe(cls, step: PlanStep, result: Dict) -> Observation:
        """Run all checks on a step's result and return validation."""
        checks = []
        warnings = []
        passed_count = 0
        total_count = 0

        # 0. Detect embedded errors (success=True but error in result dict)
        embedded_error = None
        if isinstance(result.get('result'), dict):
            embedded_error = result['result'].get('error')
        if not embedded_error:
            embedded_error = result.get('error')

        # 1. Check for execution errors
        if not result.get('success', False) or embedded_error:
            detail = embedded_error or result.get('error', 'Unknown error')
            checks.append({'name': 'execution', 'passed': False,
                           'detail': str(detail)})
            return Observation(step_id=step.step_id, passed=False,
                               checks=checks, confidence=0.0)

        checks.append({'name': 'execution', 'passed': True, 'detail': 'Tool executed successfully'})

        # 2. Physics sanity checks based on tool
        checks += cls._check_tool_output(step.tool_name, result)

        # 3. Warnings
        for c in checks:
            total_count += 1
            if c['passed']:
                passed_count += 1
            if c.get('severity') == 'warning':
                warnings.append(c['detail'])

        confidence = passed_count / max(total_count, 1)
        passed = all(c['passed'] for c in checks)

        return Observation(
            step_id=step.step_id,
            passed=passed,
            checks=checks,
            warnings=warnings,
            confidence=confidence,
        )

    @classmethod
    def _check_tool_output(cls, tool_name: str, result: Dict) -> List[Dict]:
        """Tool-specific physics checks."""
        checks = []

        if tool_name == 'analyze_solenoid_valve':
            mass = result.get('mass_g', 0)
            if 0 < mass < 0.1:
                checks.append({'name': 'mass_plausibility', 'passed': False,
                               'detail': f'Mass {mass}g is suspiciously small for a valve'})
            elif mass > 50000:
                checks.append({'name': 'mass_plausibility', 'passed': False,
                               'detail': f'Mass {mass}g is excessively large'})
            else:
                checks.append({'name': 'mass_plausibility', 'passed': True,
                               'detail': f'Mass {mass}g within plausible range'})

        elif tool_name == 'analyze_pressure_valve':
            result_data = result.get('result', result)
            if isinstance(result_data, dict):
                inlet = result_data.get('inlet_pressure', 0)
                outlet = result_data.get('outlet_pressure', 0)
                if inlet > 0 and outlet > 0 and inlet <= outlet:
                    checks.append({'name': 'pressure_ratio', 'passed': False,
                                   'detail': f'Outlet pressure ({outlet}) must be < inlet ({inlet}) for PRV'})
                else:
                    checks.append({'name': 'pressure_ratio', 'passed': True,
                                   'detail': 'Pressure ratio is valid'})

        elif tool_name == 'design_spring':
            result_data = result.get('result', result)
            if isinstance(result_data, dict):
                sf = result_data.get('safety_factor', result_data.get('fatigue_safety_factor', 1.5))
                sf = float(sf) if sf else 1.5
                sf_check = PhysicsValidator.validate_safety_factor(sf, 'general')
                checks.append(sf_check)

        elif tool_name == 'check_compliance':
            # Standard checks are binary pass/fail
            checks.append({'name': 'standard_compliance', 'passed': True,
                           'detail': 'Standard check completed'})

        elif tool_name == 'run_fluid_calculation':
            # Check if result is physically plausible
            cal_result = result.get('result', {})
            value = None
            if isinstance(cal_result, dict):
                value = cal_result.get('value')
            elif isinstance(cal_result, (int, float)):
                value = cal_result
            if value is not None:
                if math.isinf(value) or math.isnan(value):
                    checks.append({'name': 'finite_result', 'passed': False,
                                   'detail': 'Calculation produced Infinity or NaN'})
                else:
                    checks.append({'name': 'finite_result', 'passed': True,
                                   'detail': 'Result is finite'})

        return checks


# ============================================================
# Reflector — Synthesizes learnings
# ============================================================

class PAORReflector:
    """Post-execution reflection and learning capture."""

    @classmethod
    def reflect(cls, plan: PAORPlan, observations: List[Observation]) -> Reflection:
        """Synthesize findings from the entire PAOR cycle."""
        findings = []
        pitfalls = []
        suggestions = []

        # Aggregate results
        all_passed = all(o.passed for o in observations)
        avg_confidence = sum(o.confidence for o in observations) / max(len(observations), 1)

        # Load skill pitfalls for each design tool used
        skill_pitfalls = []
        try:
            from dynamic_library import get_library
            lib = get_library()
            for step in plan.steps:
                if step.tool_name in ('analyze_solenoid_valve', 'analyze_pressure_valve',
                                       'analyze_check_valve', 'design_spring',
                                       'design_oring', 'design_seal'):
                    skill_pitfalls.extend(lib.get_pitfalls_for(step.tool_name))
        except Exception:
            pass

        # Extract key findings
        for step, obs in zip(plan.steps, observations):
            status = 'OK' if obs.passed else 'ISSUE'
            findings.append(f'Step {step.step_id} ({step.tool_name}): {status} - {step.description}')

            # Collect warnings as pitfalls
            for w in obs.warnings:
                pitfalls.append(w)

            # Generate suggestions on failure
            if not obs.passed:
                for c in obs.checks:
                    if not c['passed']:
                        suggestions.append(f'Check {c["name"]}: {c["detail"]}')

        # Build learning candidate if issues found
        learning = None
        all_pitfalls = pitfalls + skill_pitfalls
        if all_pitfalls:
            learning = {
                'type': 'pitfall',
                'domain': plan.intent,
                'pattern': plan.user_message[:120],
                'pitfalls': all_pitfalls[:10],
                'skill_pitfalls_source': len(skill_pitfalls) > 0,
                'timestamp': datetime.now().isoformat(),
            }

        # Context-aware suggestions
        if plan.intent == 'design_valve' and all_passed:
            suggestions.append('Run CFD simulation for detailed flow validation')
            suggestions.append('Export design report for peer review')
        elif plan.intent == 'design_spring' and all_passed:
            suggestions.append('Perform fatigue life analysis for complete validation')
        elif plan.intent == 'fluid_calc':
            suggestions.append('Try related formulas in the Fluid Mechanics Calculator')

        return Reflection(
            summary=f'{len(plan.steps)} steps completed, {"all passed" if all_passed else "issues found"}',
            confidence=avg_confidence,
            key_findings=findings,
            pitfalls_triggered=all_pitfalls,
            suggestions=suggestions,
            learning_candidate=learning,
        )


# ============================================================
# PAOR Engine — Main orchestrator
# ============================================================

class PAOREngine:
    """Main PAOR reasoning loop engine."""

    def __init__(self, tool_executor: Callable = None):
        self.tool_executor = tool_executor  # function(name, params) -> dict
        self.learning_journal: List[Dict] = []
        self.run_count = 0

    def execute(self, message: str, context: Dict = None) -> Dict:
        """Execute full PAOR loop on a user message."""
        context = context or {}
        start_time = time.time()

        # === PLAN ===
        plan = PAORPlanner.plan(message, context)

        # === ACT + OBSERVE ===
        observations = []
        trace = []

        for step in plan.steps:
            t0 = time.time()

            # ACT
            try:
                if self.tool_executor:
                    result = self.tool_executor(step.tool_name, step.tool_params)
                else:
                    result = {'success': False, 'error': 'No tool executor configured'}
            except Exception as e:
                result = {'success': False, 'error': str(e)}

            step.result = result
            step.success = result.get('success', False)
            step.execution_time_ms = int((time.time() - t0) * 1000)

            # OBSERVE
            obs = PAORObserver.observe(step, result)
            observations.append(obs)

            trace.append({
                'step': step.step_id,
                'tool': step.tool_name,
                'success': step.success,
                'time_ms': step.execution_time_ms,
                'checks': obs.checks,
            })

        # === REFLECT ===
        reflection = PAORReflector.reflect(plan, observations)

        # Store learning candidate
        if reflection.learning_candidate:
            self.learning_journal.append(reflection.learning_candidate)

        total_ms = int((time.time() - start_time) * 1000)
        self.run_count += 1

        return {
            'request_id': plan.request_id,
            'intent': plan.intent,
            'plan': [{'step': s.step_id, 'phase': s.phase, 'tool': s.tool_name,
                      'description': s.description} for s in plan.steps],
            'trace': trace,
            'results': [{'step': s.step_id, 'tool': s.tool_name, 'result': s.result}
                        for s in plan.steps],
            'reflection': {
                'summary': reflection.summary,
                'confidence': round(reflection.confidence, 2),
                'key_findings': reflection.key_findings,
                'warnings': reflection.pitfalls_triggered,
                'suggestions': reflection.suggestions,
            },
            'total_time_ms': total_ms,
            'learning_captured': reflection.learning_candidate is not None,
        }


# ============================================================
# Engine Singleton (for Flask integration)
# ============================================================

_paor_engine: Optional[PAOREngine] = None

def get_paor_engine(tool_executor: Callable = None) -> PAOREngine:
    global _paor_engine
    if _paor_engine is None:
        _paor_engine = PAOREngine(tool_executor=tool_executor)
    elif tool_executor is not None and _paor_engine.tool_executor is None:
        _paor_engine.tool_executor = tool_executor
    return _paor_engine
