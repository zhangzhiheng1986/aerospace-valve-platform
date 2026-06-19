"""
AI Co-Pilot Engine for Aerospace Valve R&D Platform
Inspired by Claude Coworks + OpenClaw agent engineering principles.

Key features:
- Multi-intent natural language understanding for aerospace engineering
- Tool-using agent with 8+ domain tools
- Session memory with context window
- Structured recommendation output
- Offline-capable, no external LLM API required
"""

import re
import json
import math
import time
import uuid
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# ============================================================
# Session Manager
# ============================================================
class SessionManager:
    """Manages agent conversation sessions with memory."""
    
    MAX_SESSIONS = 50
    MAX_MESSAGES_PER_SESSION = 40
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, user_name: str = "Engineer") -> str:
        sid = str(uuid.uuid4())[:8]
        self.sessions[sid] = {
            'id': sid,
            'user_name': user_name,
            'messages': [],
            'context': {},
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
        }
        self._cleanup_old_sessions()
        return sid
    
    def get_session(self, sid: str) -> Optional[Dict]:
        s = self.sessions.get(sid)
        if s:
            s['last_active'] = datetime.now().isoformat()
        return s
    
    def add_message(self, sid: str, role: str, content: str, data: Any = None):
        s = self.get_session(sid)
        if not s:
            return
        s['messages'].append({
            'role': role,
            'content': content,
            'data': data,
            'timestamp': datetime.now().isoformat(),
        })
        if len(s['messages']) > self.MAX_MESSAGES_PER_SESSION:
            s['messages'] = s['messages'][-self.MAX_MESSAGES_PER_SESSION:]
    
    def _cleanup_old_sessions(self):
        if len(self.sessions) > self.MAX_SESSIONS:
            sorted_sessions = sorted(
                self.sessions.items(),
                key=lambda x: x[1]['last_active']
            )
            for sid, _ in sorted_sessions[:len(self.sessions) - self.MAX_SESSIONS]:
                del self.sessions[sid]


# ============================================================
# Intent Parser
# ============================================================
class IntentParser:
    """Natural language intent parser for aerospace engineering domain."""
    
    INTENTS = {
        'calculate': {
            'keywords_cn': [
                '计算', '算一下', '求解', '求', '等于多少', '结果',
                '流量', '流速', '压力', '压降', '雷诺数', '马赫数',
                '水头', '功率', '效率', '扬程', '推力', '升力', '阻力',
                '力矩', '应力', '应变', '温度', '热量', '传热',
                '泄漏率', '泄漏',  '弹簧力', 
                '努塞尔', '普朗特', '摩擦系数', '水力直径',
                '空化', '气蚀', 'NPSH', '比转速',
            ],
            'keywords_en': [
                'calculate', 'compute', 'solve', 'find', 'determine',
                'flow rate', 'velocity', 'pressure drop', 'reynolds',
                'mach', 'power', 'efficiency', 'thrust', 'lift', 'drag',
                'leak rate', 'npsh', 'head', 'torque', 'nusselt',
            ],
        },
        'analyze_valve': {
            'keywords_cn': [
                '分析', '评估', '诊断', '检查', '验证', '校核',
                '阀门', '电磁阀', '减压阀', '单向阀', '止回阀',
                '安全阀', '球阀', '蝶阀', '截止阀', '调节阀',
                '电磁铁', '线圈', '阀芯', '阀座', '弹簧',
                'O形圈', 'O型圈', '密封圈', '密封副',
            ],
            'keywords_en': [
                'analyze', 'evaluate', 'diagnose', 'check', 'verify',
                'valve', 'solenoid', 'pressure reducing', 'check valve',
                'relief', 'ball valve', 'butterfly', 'globe',
                'o-ring', 'seal', 'spring',
            ],
        },
        'compliance': {
            'keywords_cn': [
                '标准', '合规', '鉴定', '验证', '试验', '测试',
                'QJ', 'HB', 'GJB', 'MIL', 'ISO', 'SAE',
                '鉴定级', '验收级', '爆破', '寿命', '热真空',
                '温度循环', '振动', '冲击', '湿热',
            ],
            'keywords_en': [
                'standard', 'compliance', 'qualification', 'certification',
                'qj20156', 'iso', 'military', 'acceptance',
                'proof', 'burst', 'life cycle', 'thermal vacuum',
            ],
        },
        'material': {
            'keywords_cn': [
                '材料', '材质', '属性', '性能', '密度', '强度',
                '弹性模量', '屈服', '抗拉', '硬度', '热膨胀',
                '钛合金', '不锈钢', '铝合金', '铜合金', '镍合金',
                '复合材料', '陶瓷', '橡胶', '氟塑料',
                'TC4', 'TC6', 'GH4169', '1Cr18Ni9Ti', '7075',
            ],
            'keywords_en': [
                'material', 'property', 'density', 'strength', 'modulus',
                'titanium', 'stainless', 'aluminum', 'copper', 'nickel',
                'composite', 'ceramic', 'elastomer',
                'yield', 'tensile', 'hardness', 'thermal expansion',
            ],
        },
        'knowledge': {
            'keywords_cn': [
                '什么是', '解释', '说明', '介绍', '定义', '原理',
                '为什么', '如何', '怎么', '基础知识', '概念',
                '教程', '指南', '手册', '参考',
            ],
            'keywords_en': [
                'what is', 'explain', 'describe', 'definition', 'principle',
                'how to', 'why', 'concept', 'tutorial', 'guide',
            ],
        },
        'compare': {
            'keywords_cn': [
                '对比', '比较', '哪个更好', '优缺点', '选择',
                '方案', '方案对比', '多方案', '权衡',
                'trade', 'off', '取舍', '推荐',
            ],
            'keywords_en': [
                'compare', 'versus', 'vs', 'which is better',
                'trade-off', 'recommend', 'alternative',
            ],
        },
        'optimize': {
            'keywords_cn': [
                '优化', '最佳', '最优', '最小化', '最大化',
                '改进', '提升', '降低', '减少', '增加',
                '目标', '约束', '参数优化',
            ],
            'keywords_en': [
                'optimize', 'optimal', 'minimize', 'maximize',
                'improve', 'reduce', 'increase', 'best',
            ],
        },
        'process': {
            'keywords_cn': [
                '工艺', '加工', '制造', '生产', '车间',
                '热处理', '时效', '退火', '固溶', '淬火', '堆焊',
                '阳极化', '钝化', '喷丸', '涂层',
                '车削', '铣削', '磨削', '线切割', '电火花',
                '钎焊', '熔焊', '氩弧焊', '电子束', '激光焊',
                '装配', '紧固', '定力矩', '洁净度', '气密',
                '工艺路线', '工序', '工时', '设备选型',
            ],
            'keywords_en': [
                'process', 'manufacturing', 'machining', 'fabrication',
                'heat treatment', 'aging', 'anneal', 'solution', 'quench',
                'weld', 'brazing', 'electron beam', 'laser weld', 'tig',
                'anodize', 'passivation', 'shot peening', 'coating',
                'turning', 'milling', 'grinding', 'edm', 'wire edm',
                'assembly', 'fastening', 'torque', 'leak test',
                'process route', 'workflow', 'cycle time',
            ],
        },
    }
    
    @classmethod
    def parse(cls, message: str) -> Dict[str, float]:
        """Parse user message and return intent scores."""
        scores = {}
        message_lower = message.lower()
        for intent, data in cls.INTENTS.items():
            score = 0
            for kw in data['keywords_cn']:
                if kw in message:
                    score += 1.5
            for kw in data['keywords_en']:
                if kw.lower() in message_lower:
                    score += 1.0
            scores[intent] = score
        return scores


# ============================================================
# Tool Registry (Agent Tools)
# ============================================================
class ToolRegistry:
    """Registry of agent-callable tools."""
    
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, func, description: str, parameters: Dict = None):
        self.tools[name] = {
            'func': func,
            'description': description,
            'parameters': parameters or {},
        }
    
    def get_tool(self, name: str):
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        return [
            {'name': name, 'description': t['description'], 'parameters': t['parameters']}
            for name, t in self.tools.items()
        ]


# ============================================================
# AI Agent Engine
# ============================================================
class AIAgentEngine:
    """Main AI co-pilot engine."""
    
    def __init__(self):
        self.sessions = SessionManager()
        self.tools = ToolRegistry()
        self._register_tools()
    
    def _register_tools(self):
        """Register all available agent tools."""
        self.tools.register(
            'search_knowledge',
            self._tool_search_knowledge,
            'Search the aerospace valve knowledge base for concepts, definitions, and design guidance.',
            {'query': 'string (search query)'}
        )
        self.tools.register(
            'run_fluid_calculation',
            self._tool_run_fluid_calculation,
            'Execute any fluid mechanics formula calculation with given inputs.',
            {'formula_id': 'string', 'inputs': 'object (parameter key-value pairs)'}
        )
        self.tools.register(
            'analyze_solenoid_valve',
            self._tool_analyze_solenoid,
            'Design and optimize a solenoid valve (electromagnetic actuator + spring + orifice).',
            {'voltage': 'number', 'stroke': 'number', 'force_required': 'number', 'awg': 'number (optional)', 'material': 'string (optional)'}
        )
        self.tools.register(
            'analyze_pressure_valve',
            self._tool_analyze_prv,
            'Design a pressure reducing valve for aerospace fluid systems.',
            {'inlet_pressure': 'number (Pa)', 'outlet_pressure': 'number (Pa)', 'fluid_type': 'string', 'material': 'string'}
        )
        self.tools.register(
            'analyze_check_valve',
            self._tool_analyze_check,
            'Design a check/one-way valve per HB 6455-2014 standard.',
            {'nominal_diameter': 'number (mm)', 'pressure_rating': 'number (MPa)', 'fluid_type': 'string'}
        )
        self.tools.register(
            'design_spring',
            self._tool_design_spring,
            'Design a compression spring for aerospace valve applications.',
            {'wire_diameter': 'number (mm, optional)', 'outer_diameter': 'number (mm)', 'free_length': 'number (mm)', 'active_coils': 'number', 'material': 'string'}
        )
        self.tools.register(
            'design_oring',
            self._tool_design_oring,
            'Design an O-ring seal using AS568F / ISO 3601-2 standards with Roth leakage model.',
            {'application_type': 'string (piston_seal/rod_seal/face_seal)', 'housing_diameter': 'number (mm)', 'pressure': 'number (MPa)', 'material': 'string (optional)'}
        )
        self.tools.register(
            'check_compliance',
            self._tool_check_compliance,
            'Verify valve design against QJ 20156-2014 aerospace qualification standard.',
            {'valve_type': 'string', 'rated_pressure': 'number (MPa)', 'rated_temperature': 'number (C)', 'design_life': 'number (cycles)'}
        )
        self.tools.register(
            'query_material',
            self._tool_query_material,
            'Look up aerospace material properties (21 materials, 7 categories).',
            {'material_name': 'string (e.g. TC4, GH4169, 1Cr18Ni9Ti)'}
        )
        self.tools.register(
            'compare_designs',
            self._tool_compare_designs,
            'Compare multiple design scenarios for trade-off analysis.',
            {'scenarios': 'array of design parameter sets'}
        )
        # Sprint 12: Manufacturing process tools
        self.tools.register(
            'list_processes',
            self._tool_list_processes,
            'List manufacturing processes (machining, heat treatment, surface, welding, assembly).',
            {'category': 'string (optional: machining/heat_treatment/surface_treatment/welding/assembly)'}
        )
        self.tools.register(
            'get_process_detail',
            self._tool_get_process_detail,
            'Get full parameters for a specific manufacturing process (cutting speed, temp, time, etc.).',
            {'process_id': 'string (e.g. titanium_turning, aluminum_t6)'}
        )
        self.tools.register(
            'recommend_process',
            self._tool_recommend_process,
            'Recommend a complete manufacturing process package for a given material and valve type.',
            {'material': 'string (e.g. Inconel 718, 316L, TC4)', 'valve_type': 'string (e.g. relief, solenoid, check)'}
        )
        self.tools.register(
            'get_process_route',
            self._tool_get_process_route,
            'Get a step-by-step process route (work instruction) for a specific valve component.',
            {'route_id': 'string (e.g. solenoid_valve_body, relief_valve_seat)'}
        )
    
    # ---- Tool Implementations ----
    
    def _tool_search_knowledge(self, **kwargs) -> Dict:
        """Search knowledge base."""
        query = kwargs.get('query', '')
        try:
            from knowledge_base import search_knowledge
            results = search_knowledge(query)
            return {
                'success': True,
                'query': query,
                'results': results[:5] if results else [],
                'total': len(results) if results else 0,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_run_fluid_calculation(self, **kwargs) -> Dict:
        """Run fluid mechanics calculation."""
        formula_id = kwargs.get('formula_id', '')
        inputs = kwargs.get('inputs', {})
        try:
            from fluid_mechanics_calc import compute_formula
            result = compute_formula(formula_id, inputs)
            return {'success': True, 'formula_id': formula_id, 'result': result}
        except ImportError:
            try:
                from fluid_mechanics_calc import compute
                result = compute(formula_id, inputs)
                return {'success': True, 'formula_id': formula_id, 'result': result}
            except Exception as e2:
                return {'success': False, 'error': str(e2)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_analyze_solenoid(self, **kwargs) -> Dict:
        """Analyze/optimize solenoid valve using PSO hybrid optimizer."""
        try:
            from solenoid_optimizer import run_optimization
            voltage = float(kwargs.get('voltage', 28))
            stroke = float(kwargs.get('stroke', 2.0))
            geom_params = {
                'D_inner_mm': float(kwargs.get('D_inner_mm', 20)),
                'D_outer_max_mm': float(kwargs.get('D_outer_max_mm', 40)),
                'L_axial_max_mm': float(kwargs.get('L_axial_max_mm', 30)),
                'air_gap_main_mm': float(kwargs.get('air_gap_main_mm', stroke)),
                'armature_length_mm': float(kwargs.get('armature_length_mm', 55)),
                'V_rated': voltage,
                'I_current_limit': float(kwargs.get('current_limit', 2.0)),
            }
            result = run_optimization(geom_params, 20, 50)
            if result.get('success'):
                return {
                    'success': True, 'type': 'solenoid',
                    'best_awg': result.get('best_awg'),
                    'mass_g': result.get('mass_g'),
                    'power_W': result.get('power_W'),
                    'best_info': result.get('best_info', {}),
                }
            return {'success': False, 'error': result.get('message', 'Optimization failed')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_analyze_prv(self, **kwargs) -> Dict:
        """Design pressure reducing valve."""
        try:
            from pressure_reducing_valve import PressureReducingValveDesigner, ValveInputParams
            params = ValveInputParams(
                fluid_type=kwargs.get('fluid_type', 'hydraulic_oil'),
                inlet_pressure=float(kwargs.get('inlet_pressure', 2.0)),
                outlet_pressure=float(kwargs.get('outlet_pressure', 0.5)),
                flow_rate=float(kwargs.get('flow_rate', 5.0)),
                fluid_temperature=float(kwargs.get('fluid_temperature', 50)),
            )
            designer = PressureReducingValveDesigner(params)
            result = designer.design()
            return {'success': True, 'type': 'pressure_valve', 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_analyze_check(self, **kwargs) -> Dict:
        """Design check valve (HB 6455-2014 / QJ 1142A-2008)."""
        try:
            from check_valve import run_check_valve_design
            data = {
                'medium_type': kwargs.get('medium_type', 'hydraulic_oil'),
                'valve_type': kwargs.get('valve_type', 'poppet'),
                'nominal_diameter': float(kwargs.get('nominal_diameter', 8.0)),
                'cracking_pressure': float(kwargs.get('cracking_pressure', 0.05)),
                'flow_rate': float(kwargs.get('flow_rate', 10.0)),
            }
            result = run_check_valve_design(data)
            return {'success': True, 'type': 'check_valve', 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_design_spring(self, **kwargs) -> Dict:
        """Design compression spring (4 aerospace materials, fatigue + stability check)."""
        try:
            from spring_design import design_spring
            data = {
                'material': kwargs.get('material', '50CrVA'),
                'wire_diameter': float(kwargs.get('wire_diameter', 1.0)),
                'outer_diameter': float(kwargs.get('outer_diameter', 10.0)),
                'free_length': float(kwargs.get('free_length', 30.0)),
                'active_coils': float(kwargs.get('active_coils', 8)),
                'force_required': float(kwargs.get('force_required', 10.0)),
                'deflection': float(kwargs.get('deflection', 5.0)),
            }
            result = design_spring(data)
            return {'success': True, 'type': 'spring', 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_design_oring(self, **kwargs) -> Dict:
        """Design O-ring seal (SAE AS568F / ISO 3601-2, Roth leakage model)."""
        try:
            from oring_design import design_oring
            data = {
                'seal_type': kwargs.get('seal_type', 'piston'),
                'bore_diameter': float(kwargs.get('bore_diameter', 25.0)),
                'pressure': float(kwargs.get('pressure', 2.0)),
                'temperature': float(kwargs.get('temperature', 80)),
                'material': kwargs.get('material', 'NBR'),
            }
            result = design_oring(data)
            return {'success': True, 'type': 'oring', 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_check_compliance(self, **kwargs) -> Dict:
        """Check valve design compliance per QJ 20156-2014 (proof 1.5x, burst 2.0x, life>=20000)."""
        try:
            from qj20156_module import get_standard_info
            info = get_standard_info()
            # Run specific checks if design params provided
            checks = {}
            if kwargs.get('rated_pressure'):
                try:
                    from qj20156_module import calc_proof_pressure
                    checks['proof_pressure'] = calc_proof_pressure(float(kwargs['rated_pressure']))
                except: pass
            if kwargs.get('design_life'):
                try:
                    from qj20156_module import verify_life_cycles
                    checks['life_cycles'] = verify_life_cycles(int(kwargs['design_life']))
                except: pass
            return {
                'success': True, 'type': 'compliance',
                'standard_info': info,
                'checks': checks,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _material_to_dict(mat) -> Dict:
        """Convert MaterialProperty object to serializable dict."""
        if isinstance(mat, dict):
            return mat
        d = {}
        for attr in dir(mat):
            if not attr.startswith('_'):
                try:
                    val = getattr(mat, attr)
                    if not callable(val):
                        # Convert Enum/MaterialCategory to string
                        if hasattr(val, 'value'):
                            d[attr] = val.value
                        else:
                            d[attr] = val
                except Exception:
                    pass
        return d

    def _tool_query_material(self, **kwargs) -> Dict:
        """Query material database with fuzzy name matching."""
        material_name = kwargs.get('material_name', 'TC4')
        try:
            from materials_database import AerospaceMaterialsDatabase
            db = AerospaceMaterialsDatabase()
            # Try exact match first
            material = db.get_material(material_name)
            if material:
                return {'success': True, 'material': self._material_to_dict(material)}
            # Fuzzy match: search all material names for substring
            for key, val in db.materials.items():
                if material_name.lower() in key.lower():
                    return {'success': True,
                            'material': self._material_to_dict(val),
                            'matched_name': key, 'matched_by': 'fuzzy'}
            return {'success': False,
                    'error': f'Material "{material_name}" not found in {len(db.materials)} materials',
                    'available': [k for k in list(db.materials.keys())[:10]]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_compare_designs(self, **kwargs) -> Dict:
        """Compare multiple design scenarios."""
        scenarios = kwargs.get('scenarios', [])
        results = []
        for i, scenario in enumerate(scenarios):
            try:
                if scenario.get('type') == 'solenoid':
                    r = self._tool_analyze_solenoid(**scenario.get('params', {}))
                elif scenario.get('type') == 'prv':
                    r = self._tool_analyze_prv(**scenario.get('params', {}))
                elif scenario.get('type') == 'check':
                    r = self._tool_analyze_check(**scenario.get('params', {}))
                elif scenario.get('type') == 'spring':
                    r = self._tool_design_spring(**scenario.get('params', {}))
                elif scenario.get('type') == 'oring':
                    r = self._tool_design_oring(**scenario.get('params', {}))
                else:
                    r = {'error': f'Unknown type: {scenario.get("type")}'}
                results.append({
                    'scenario': i + 1,
                    'label': scenario.get('label', f'Scenario {i+1}'),
                    'result': r,
                })
            except Exception as e:
                results.append({
                    'scenario': i + 1,
                    'label': scenario.get('label', f'Scenario {i+1}'),
                    'error': str(e),
                })
        return {'success': True, 'type': 'comparison', 'results': results}

    def _tool_list_processes(self, **kwargs) -> Dict:
        """List manufacturing processes (machining/HT/surface/welding/assembly)."""
        try:
            from tool_bridge import get_tool_handler
            return get_tool_handler('list_processes')(kwargs)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _tool_get_process_detail(self, **kwargs) -> Dict:
        """Get full parameters for a specific process."""
        try:
            from tool_bridge import get_tool_handler
            return get_tool_handler('get_process_detail')(kwargs)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _tool_recommend_process(self, **kwargs) -> Dict:
        """Recommend process route based on material and valve type."""
        try:
            from tool_bridge import get_tool_handler
            return get_tool_handler('recommend_process')(kwargs)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _tool_get_process_route(self, **kwargs) -> Dict:
        """Get full process route (step-by-step instructions)."""
        try:
            from tool_bridge import get_tool_handler
            return get_tool_handler('get_process_route')(kwargs)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ---- Main Processing Pipeline ----
    
    def process_message(self, session_id: str, message: str) -> Dict:
        """Process user message and return agent response."""
        session = self.sessions.get_session(session_id)
        if not session:
            return {'error': 'Session not found', 'need_new_session': True}
        
        self.sessions.add_message(session_id, 'user', message)
        
        try:
            # Step 1: Parse intent
            intents = IntentParser.parse(message)
            primary_intent = max(intents, key=intents.get) if any(v > 0 for v in intents.values()) else 'knowledge'
            # Process intent priority: if strong process signals present, override
            process_signals = ['工艺', '加工', '制造', '热处理', '车削', '铣削',
                               '阳极', '钝化', '喷丸', '电子束', '钎焊', '堆焊',
                               'process', 'machining', 'manufacturing', 'weld',
                               'anodize', 'passivation', 'brazing']
            msg_lower = message.lower()
            if intents.get('process', 0) > 0 and any(s.lower() in msg_lower for s in process_signals):
                primary_intent = 'process'
            
            # Step 2: Extract parameters from message
            params = self._extract_parameters(message)
            
            # Step 3: Build response
            response = self._build_response(primary_intent, intents, params, message, session)
            
            # Step 4: Store in session
            self.sessions.add_message(session_id, 'agent', response.get('text', ''), response.get('data'))
            
            return response
            
        except Exception as e:
            error_response = {
                'text': self._format_error(str(e)),
                'intent': 'error',
                'action': None,
                'tool_results': None,
                'suggestions': ['请检查输入参数', '尝试其他表达方式'],
            }
            self.sessions.add_message(session_id, 'agent', error_response['text'])
            return error_response
    
    def _extract_parameters(self, message: str) -> Dict:
        """Extract numeric and named parameters from natural language."""
        params = {}
        
        # Extract numbers with units
        number_patterns = [
            (r'(\d+\.?\d*)\s*MPa', 'pressure_mpa'),
            (r'(\d+\.?\d*)\s*bar', 'pressure_bar'),
            (r'(\d+\.?\d*)\s*Pa', 'pressure_pa'),
            (r'(\d+\.?\d*)\s*mm', 'diameter_mm'),
            (r'(\d+\.?\d*)\s*cm', 'diameter_cm'),
            (r'(\d+\.?\d*)\s*mm\s*[(（]外径[)）]', 'outer_diameter_mm'),
            (r'(\d+\.?\d*)\s*mm\s*[(（]内径[)）]', 'inner_diameter_mm'),
            (r'(\d+\.?\d*)\s*mm\s*[(（]行程[)）]', 'stroke_mm'),
            (r'(\d+\.?\d*)\s*mm\s*[(（]长度[)）]', 'length_mm'),
            (r'(\d+\.?\d*)\s*N', 'force_n'),
            (r'(\d+\.?\d*)\s*V', 'voltage_v'),
            (r'(\d+\.?\d*)\s*A', 'current_a'),
            (r'(\d+\.?\d*)\s*kg', 'mass_kg'),
            (r'(\d+\.?\d*)\s*度\s*[Cc]', 'temperature_c'),
            (r'(\d+\.?\d*)\s*[Cc]', 'temperature_c'),
            (r'(\d+\.?\d*)\s*K', 'temperature_k'),
            (r'(\d+\.?\d*)\s*次', 'cycles'),
            (r'(\d+\.?\d*)\s*万次', 'cycles_10k'),
        ]
        for pattern, key in number_patterns:
            m = re.search(pattern, message)
            if m:
                params[key] = float(m.group(1))
        
        # Extract material names
        material_names = [
            'TC4', 'TC6', 'TC11', 'TC18', 'TA15', 'TA2',
            'GH4169', 'GH3030', 'GH3536',
            '1Cr18Ni9Ti', '0Cr17Ni4Cu4Nb', '2Cr13', '4Cr13', '304', '316L',
            '7075', '2A12', '2A14', '6061',
            'QBe2', 'H62',
            'FKM', 'FFKM', 'NBR', 'EPDM', 'PTFE', 'PU',
        ]
        for mat in material_names:
            if mat.lower() in message.lower():
                params['material'] = mat
                break
        
        # Extract fluid types
        fluid_types = [
            'nitrogen', 'helium', 'hydrogen', 'oxygen', 'air', 'argon',
            'kerosene', 'hydrazine', 'MMH', 'N2O4', 'UDMH',
            'LH2', 'LOX', 'water', 'hydraulic_oil',
        ]
        for fluid in fluid_types:
            if fluid.lower() in message.lower():
                params['fluid_type'] = fluid
                break
        
        return params
    
    def _build_response(self, primary_intent: str, intents: Dict, params: Dict, 
                        message: str, session: Dict) -> Dict:
        """Build structured agent response based on intent and context."""
        response = {
            'intent': primary_intent,
            'intent_scores': intents,
            'action': None,
            'tool_results': None,
            'text': '',
            'suggestions': [],
        }
        
        if primary_intent == 'calculate':
            response = self._handle_calculate(message, params, response)
        elif primary_intent == 'analyze_valve':
            response = self._handle_analyze_valve(message, params, response)
        elif primary_intent == 'compliance':
            response = self._handle_compliance(message, params, response)
        elif primary_intent == 'material':
            response = self._handle_material(message, params, response)
        elif primary_intent == 'compare':
            response = self._handle_compare(message, params, response, session)
        elif primary_intent == 'optimize':
            response = self._handle_optimize(message, params, response)
        elif primary_intent == 'process':
            response = self._handle_process(message, params, response)
        else:
            response = self._handle_knowledge(message, params, response)
        
        return response
    
    # ---- Intent Handlers ----
    
    def _handle_calculate(self, message: str, params: Dict, response: Dict) -> Dict:
        """Handle calculation intent - auto-execute fluid mechanics formulas."""
        response['action'] = 'run_fluid_calculation'
        
        # Try formula-id-based matching
        formula_id = None
        formula_inputs = {}
        
        if '雷诺数' in message or 'reynolds' in message.lower():
            formula_id = 'reynolds_number'
            diam = params.get('diameter_mm') or params.get('diameter') or 10
            vel = params.get('velocity') or 1.0
            nu = params.get('kinematic_viscosity') or 1.5e-5
            formula_inputs = {'diameter': float(diam), 'velocity': float(vel), 'kinematic_viscosity': float(nu)}
            
        elif '压降' in message or 'pressure drop' in message.lower():
            formula_id = 'darcy_weisbach'
            length = params.get('length') or 1.0
            diam = params.get('diameter') or params.get('diameter_mm') or 10
            vel = params.get('velocity') or 1.0
            rho = params.get('density') or 1.2
            friction = params.get('friction_factor') or 0.02
            formula_inputs = {'length': float(length), 'diameter': float(diam), 'velocity': float(vel),
                             'density': float(rho), 'friction_factor': float(friction)}
            
        elif '马赫数' in message or '马赫' in message or 'mach' in message.lower():
            formula_id = 'mach_number'
            vel = params.get('velocity') or 340
            gamma = params.get('gamma') or 1.4
            R = params.get('gas_constant') or 287
            T = params.get('temperature') or 288
            formula_inputs = {'velocity': float(vel), 'gamma': float(gamma), 'R': float(R), 'temperature': float(T)}
            
        elif '流量' in message or 'flow rate' in message.lower() or 'flowrate' in message.lower():
            formula_id = 'volumetric_flow_rate'
            area = params.get('area') or params.get('cross_section') or 0.00785
            vel = params.get('velocity') or 1.0
            formula_inputs = {'area': float(area), 'velocity': float(vel)}
            
        elif '贝努利' in message or 'bernoulli' in message.lower():
            formula_id = 'bernoulli_equation'
            p1 = params.get('pressure1') or 101325
            v1 = params.get('velocity1') or 1.0
            z1 = params.get('height1') or 0
            v2 = params.get('velocity2') or 0
            z2 = params.get('height2') or 0
            rho = params.get('density') or 1.2
            formula_inputs = {'p1': float(p1), 'v1': float(v1), 'z1': float(z1), 'v2': float(v2), 'z2': float(z2), 'density': float(rho)}
        
        if formula_id:
            result = self._tool_run_fluid_calculation(formula_id=formula_id, inputs=formula_inputs)
            response['tool_executed'] = True
            response['tool_results'] = result
            
            if result.get('success'):
                r = result.get('result', {})
                value = r if isinstance(r, (int, float)) else r.get('value', r)
                response['text'] = (
                    f'=== {formula_id.replace("_", " ").title()} ===\n\n'
                    f'Inputs: {formula_inputs}\n\n'
                    f'Result: {value}\n'
                )
                response['suggestions'] = ['Recalculate with different values', 'Open Fluid Mechanics Calculator']
            else:
                response['text'] = (
                    f'Calculation attempted for "{formula_id}" but encountered an error:\n'
                    f'{result.get("error", "Unknown error")}\n\n'
                    'Please try the [Fluid Mechanics Calculator](/fluid_mechanics) directly.'
                )
        else:
            response['text'] = (
                '=== Fluid Mechanics Calculations ===\n\n'
                'I can calculate:\n'
                '- Reynolds number / Mach number\n'
                '- Pressure drop (Darcy-Weisbach)\n'
                '- Flow rate / Bernoulli equation\n'
                '- And 200+ more formulas\n\n'
                'What would you like to calculate? Provide the formula name and key parameters.\n'
                'Or open the [Fluid Mechanics Calculator](/fluid_mechanics) for the full catalog.'
            )
            response['suggestions'] = ['Calculate Reynolds number', 'Calculate pressure drop', 'Calculate Mach number']
        
        return response

    def _handle_analyze_valve(self, message: str, params: Dict, response: Dict) -> Dict:
        """Handle valve analysis intent - auto-execute tools when params available."""
        
        if '电磁阀' in message or 'solenoid' in message.lower():
            response['action'] = 'analyze_solenoid'
            voltage = params.get('voltage') or 28
            stroke = params.get('stroke') or 2.0
            force = params.get('force_required') or params.get('force') or 10
            
            result = self._tool_analyze_solenoid(voltage=voltage, stroke=stroke, force_required=force)
            response['tool_executed'] = True
            response['tool_results'] = result
            
            if result.get('success'):
                r = result.get('result', {})
                response['text'] = (
                    '=== Solenoid Valve PSO Optimization ===\n\n'
                    f'Input: {voltage}V, {stroke}mm stroke, {force}N target\n\n'
                    f'Turns: {r.get("turns", "N/A")}\n'
                    f'Wire dia: {r.get("wire_diameter", "N/A")} mm\n'
                    f'Current: {r.get("current", "N/A")} A\n'
                    f'Power: {r.get("power", "N/A")} W\n'
                    f'Force: {r.get("force", "N/A")} N\n'
                )
                response['suggestions'] = ['Adjust stroke', 'Compare AWG', 'Open Solenoid Designer']
            else:
                response['text'] = f'Solenoid optimization error: {result.get("error")}'
        
        elif '减压阀' in message or 'pressure reducing' in message.lower():
            response['action'] = 'analyze_prv'
            inlet = params.get('inlet_pressure') or params.get('inlet') or 10e6
            outlet = params.get('outlet_pressure') or params.get('outlet') or 2e6
            fluid = params.get('fluid') or 'nitrogen'
            mat = params.get('material') or '1Cr18Ni9Ti'
            
            result = self._tool_analyze_prv(inlet_pressure=inlet, outlet_pressure=outlet, fluid_type=fluid, material=mat)
            response['tool_executed'] = True
            response['tool_results'] = result
            
            if result.get('success'):
                r = result.get('result', {})
                response['text'] = (
                    '=== Pressure Reducing Valve Design ===\n\n'
                    f'Inlet: {inlet/1e6:.1f} MPa | Outlet: {outlet/1e6:.1f} MPa | Fluid: {fluid} | Material: {mat}\n\n'
                    f'Seat dia: {r.get("seat_diameter", "N/A")} mm\n'
                    f'Poppet stroke: {r.get("poppet_stroke", "N/A")} mm\n'
                    f'Spring K: {r.get("spring_stiffness", "N/A")} N/mm\n'
                    f'Cv: {r.get("cv", "N/A")}\n'
                )
                response['suggestions'] = ['Adjust outlet', 'Compare helium', 'Open PRV Designer']
            else:
                response['text'] = f'PRV design error: {result.get("error")}'
        
        elif '单向阀' in message or '止回阀' in message or 'check valve' in message.lower():
            response['action'] = 'analyze_check'
            diam = params.get('diameter') or params.get('nominal_diameter') or 10
            press = params.get('pressure_rating') or params.get('pressure') or 21
            fluid = params.get('fluid') or 'nitrogen'
            
            result = self._tool_analyze_check(nominal_diameter=diam, pressure_rating=press, fluid_type=fluid)
            response['tool_executed'] = True
            response['tool_results'] = result
            
            if result.get('success'):
                r = result.get('result', {})
                response['text'] = (
                    '=== Check Valve Design (HB 6455-2014) ===\n\n'
                    f'DN: {diam}mm | Pressure: {press}MPa | Fluid: {fluid}\n\n'
                    f'Cracking P: {r.get("cracking_pressure", "N/A")} MPa\n'
                    f'Flow resistance: {r.get("flow_resistance", "N/A")}\n'
                    f'Reverse leak: {r.get("reverse_leakage", "N/A")} Pa*m3/s\n'
                )
                response['suggestions'] = ['Compare diameters', 'Check sealing', 'Open Check Valve Designer']
            else:
                response['text'] = f'Check valve error: {result.get("error")}'
        
        elif 'O' in message and ('形' in message or '型' in message or 'ring' in message):
            response['action'] = 'design_oring'
            app = params.get('application_type') or 'piston_seal'
            diam = params.get('housing_diameter') or params.get('diameter') or 25
            press = params.get('pressure') or 21
            mat = params.get('material') or 'FKM'
            
            result = self._tool_design_oring(application_type=app, housing_diameter=diam, pressure=press, material=mat)
            response['tool_executed'] = True
            response['tool_results'] = result
            
            if result.get('success'):
                r = result.get('result', {})
                response['text'] = (
                    '=== O-Ring Design (AS568F) ===\n\n'
                    f'Type: {app} | Groove: {diam}mm | P: {press}MPa | Material: {mat}\n\n'
                    f'AS568#: {r.get("as568_dash", "N/A")}\n'
                    f'CS: {r.get("cs", "N/A")} mm\n'
                    f'ID: {r.get("id", "N/A")} mm\n'
                    f'Compression: {r.get("compression_ratio", "N/A")}%\n'
                    f'Leak rate: {r.get("leak_rate", "N/A")} Pa*m3/s\n'
                )
                response['suggestions'] = ['Compare NBR', 'Adjust compression', 'Open O-ring Designer']
            else:
                response['text'] = f'O-ring error: {result.get("error")}'
        
        elif '弹簧' in message or 'spring' in message.lower():
            response['action'] = 'design_spring'
            od = params.get('outer_diameter') or params.get('diameter') or 20
            fl = params.get('free_length') or 50
            ac = params.get('active_coils') or params.get('coils') or 8
            mat = params.get('material') or '1Cr18Ni9Ti'
            wd = params.get('wire_diameter') or 0
            
            result = self._tool_design_spring(wire_diameter=wd, outer_diameter=od, free_length=fl, active_coils=int(ac), material=mat)
            response['tool_executed'] = True
            response['tool_results'] = result
            
            if result.get('success'):
                r = result.get('result', {})
                response['text'] = (
                    '=== Compression Spring Design ===\n\n'
                    f'OD: {od}mm | Free L: {fl}mm | Coils: {ac} | Material: {mat}\n\n'
                    f'Wire dia: {r.get("wire_diameter", "N/A")} mm\n'
                    f'Stiffness: {r.get("stiffness", "N/A")} N/mm\n'
                    f'Max load: {r.get("max_load", "N/A")} N\n'
                    f'Fatigue SF: {r.get("fatigue_safety", "N/A")}\n'
                    f'Stability: {r.get("stability", "N/A")}\n'
                )
                response['suggestions'] = ['Compare materials', 'Adjust coils', 'Open Spring Designer']
            else:
                response['text'] = f'Spring design error: {result.get("error")}'
        
        else:
            response['text'] = (
                '=== Valve Design Capabilities ===\n\n'
                'I can analyze and design these valve types:\n'
                '- Solenoid Valve (PSO + AWG search)\n'
                '- Pressure Reducing Valve (5 fluids, 5 materials)\n'
                '- Check Valve (HB 6455-2014)\n'
                '- Spring Design (4 materials, iterative solver)\n'
                '- O-Ring Seal (AS568F, Roth leak model)\n'
                '- Seal Pair (Hertz contact + Roth flow)\n\n'
                'Specify valve type and parameters, I will run the calculation immediately.'
            )
            response['suggestions'] = ['Analyze solenoid', 'Design O-ring', 'Design spring']
        
        return response

    def _handle_compliance(self, message: str, params: Dict, response: Dict) -> Dict:
        """Handle compliance verification intent."""
        response['action'] = 'check_compliance'
        
        # Run compliance check if we have parameters
        if params:
            result = self._tool_check_compliance(**params)
            if result.get('success') and result.get('compliance'):
                c = result['compliance']
                info = result.get('standard_info', {})
                response['text'] = (
                    '=== QJ 20156-2014 标准合规检查 ===\n\n'
                    f'【标准要求】(QJ 20156-2014 航天阀门通用规范)\n'
                    f'• 鉴定压力: {c.get("proof_factor", 1.5)} 倍额定压力\n'
                    f'• 爆破压力: {c.get("burst_factor", 2.0)} 倍额定压力\n'
                    f'• 设计寿命: >= {c.get("min_life", 20000)} 次\n'
                    f'• 热真空循环: {c.get("thermal_cycles", 6)} 循环\n'
                    f'• 泄漏率: <= {c.get("max_leak_rate", "1e-6")} Pa*m^3/s (He)\n\n'
                )
                if params.get('design_life'):
                    life_ok = params['design_life'] >= c.get('min_life', 20000)
                    response['text'] += f'检查结果: 设计寿命 {params["design_life"]} 次 → {"✅ 合格" if life_ok else "❌ 不满足要求"}'
            else:
                response['text'] = '标准信息已获取。请提供具体参数进行合规检查。'
        else:
            response['text'] = (
                '=== QJ 20156-2014 航天阀门鉴定标准 ===\n\n'
                '主要鉴定要求：\n'
                '• 鉴定压力: 1.5x 额定工作压力\n'
                '• 爆破压力: 2.0x 额定工作压力\n'
                '• 最低寿命: 20000 次循环\n'
                '• 热真空试验: 6 循环, < 1e-3 Pa\n'
                '• 泄漏率: < 1e-6 Pa*m^3/s (氦检)\n'
                '• 温度循环: -40 ~ +80degC\n'
                '• 振动试验: 按照GJB 150.16A\n\n'
                '请提供您的阀门参数，我来帮您逐项核对。'
            )
        
        response['tool_results'] = params
        response['suggestions'] = ['输入额定压力', '输入设计寿命', '查看完整标准']
        return response
    
    def _handle_material(self, message: str, params: Dict, response: Dict) -> Dict:
        """Handle material query intent."""
        mat_name = params.get('material')
        if mat_name:
            result = self._tool_query_material(material_name=mat_name)
            response['tool_executed'] = True
            response['tool_results'] = result
            if result.get('success') and result.get('material'):
                m = result['material']
                response['text'] = (
                    f'=== {mat_name} 材料属性 ===\n\n'
                    f'类别: {m.get("category", "N/A")}\n'
                    f'密度: {m.get("density", "N/A")} kg/m^3\n'
                    f'弹性模量: {m.get("elastic_modulus", "N/A")} GPa\n'
                    f'屈服强度: {m.get("yield_strength", "N/A")} MPa\n'
                    f'抗拉强度: {m.get("tensile_strength", "N/A")} MPa\n'
                    f'泊松比: {m.get("poisson_ratio", "N/A")}\n'
                    f'热膨胀系数: {m.get("thermal_expansion", "N/A")} 1/K\n'
                    f'导热系数: {m.get("thermal_conductivity", "N/A")} W/(m*K)\n'
                    f'适用温度: {m.get("temp_min", "N/A")} ~ {m.get("temp_max", "N/A")} degC\n'
                    f'硬度: {m.get("hardness", "N/A")}\n\n'
                    f'典型应用: {m.get("applications", "航空航天阀门/结构件")}'
                )
                response['tool_results'] = m
            else:
                response['text'] = (
                    f'抱歉，未找到材料 "{mat_name}" 的信息。\n\n'
                    '平台材料数据库包含21种航空航天材料：\n'
                    '• 钛合金: TC4, TC6, TC11, TC18, TA15, TA2\n'
                    '• 高温合金: GH4169, GH3030, GH3536\n'
                    '• 不锈钢: 1Cr18Ni9Ti, 0Cr17Ni4Cu4Nb, 2Cr13, 4Cr13, 304, 316L\n'
                    '• 铝合金: 7075, 2A12, 2A14, 6061\n'
                    '• 铜合金: QBe2, H62\n'
                    '• 密封材料: FKM, FFKM, NBR, EPDM, PTFE, PU'
                )
        else:
            response['text'] = (
                '=== 材料数据库 ===\n\n'
                '平台包含 21 种航空航天材料的完整属性数据：\n'
                '7 类别: 钛合金/高温合金/不锈钢/铝合金/铜合金/密封材料/复合材料\n'
                '每项30+属性字段: 密度/弹性模量/强度/膨胀/导热/适用温度...\n\n'
                '请告诉我具体材料名称（如 TC4、GH4169、7075）。\n'
                '或浏览 [材料数据库](/materials) 查看完整列表。'
            )
        
        response['suggestions'] = ['查询TC4', '查询GH4169', '查询7075', '对比TC4和TC6']
        return response
    
    def _handle_compare(self, message: str, params: Dict, response: Dict, session: Dict) -> Dict:
        """Handle comparison intent."""
        response['text'] = (
            '=== 方案对比分析 ===\n\n'
            '我可以帮您对比多个设计方案。请描述需要对比的方案，例如：\n\n'
            '• "对比电磁阀线径AWG24和AWG26的性能"\n'
            '• "对比TC4和GH4169在21MPa下的弹簧设计"\n'
            '• "对比O形圈活塞密封和杆密封的泄漏率"\n\n'
            '或者说明两个具体方案的参数差异，我来帮你定量分析。'
        )
        response['suggestions'] = ['对比电磁阀线径', '对比两种材料', '对比两种密封类型']
        return response
    
    def _handle_optimize(self, message: str, params: Dict, response: Dict) -> Dict:
        """Handle optimization intent."""
        response['text'] = (
            '=== 参数优化建议 ===\n\n'
            '平台支持以下优化能力：\n\n'
            '• 电磁阀 PSO粒子群优化 (多目标: 电磁力/功耗/体积)\n'
            '• 弹簧迭代求解器 (自动搜索最佳钢丝直径)\n'
            '• O形圈 ASA568数据库搜索 (自动匹配最接近标准尺寸)\n'
            '• 密封副 Hertz接触应力优化\n'
            '• 流体力学公式批量演练 (多方案对比)\n\n'
            '请指定需要优化的对象和约束条件。'
        )
        response['suggestions'] = ['优化电磁阀线径', '优化弹簧圈数', '优化密封压缩比']
        return response

    def _handle_process(self, message: str, params: Dict, response: Dict) -> Dict:
        """Handle manufacturing process intent (Sprint 12).

        Strategy:
        1. If message asks for a specific process (e.g. 'titanium turning params')
           -> call get_process_detail
        2. If user mentions a material + valve type (e.g. 'Inconel 718 relief valve process')
           -> call recommend_process
        3. If user asks for a route (e.g. 'how to make solenoid valve body')
           -> call get_process_route
        4. Otherwise -> list all process categories
        """
        msg_lower = message.lower()
        # Detect material keywords
        material = None
        mat_keywords = {
            'inconel 718': 'Inconel 718', 'inconel718': 'Inconel 718',
            'inconel': 'Inconel', 'monel': 'Monel',
            '316l': '316L', '17-4ph': '17-4PH', '17-4': '17-4PH',
            'stainless': 'Stainless Steel', 'stainless steel': 'Stainless Steel',
            'titanium': 'TC4', 'tc4': 'TC4', 'ta15': 'TA15',
            'aluminum': 'Aluminum', 'aluminium': 'Aluminum', '6061': 'Aluminum',
            '7075': 'Aluminum', 'stellite': 'Stellite',
        }
        for kw, mat in mat_keywords.items():
            if kw in msg_lower:
                material = mat
                break
        # Detect valve type
        valve_type = None
        vt_keywords = {
            'solenoid': 'solenoid', 'electromagnetic': 'solenoid',
            'check': 'check', 'one-way': 'check', 'one way': 'check',
            'relief': 'relief', 'pressure reducing': 'relief', 'reducing': 'relief',
            'regulating': 'regulating', 'shutoff': 'shutoff', 'shut-off': 'shutoff',
            'ball': 'ball', 'butterfly': 'butterfly',
        }
        for kw, vt in vt_keywords.items():
            if kw in msg_lower:
                valve_type = vt
                break
        # Detect if user wants a specific process detail
        process_keywords = [
            'titanium_turning', 'titanium_milling', 'aluminum_turning', 'aluminum_t6',
            'stainless_turning', 'nickel_alloy_turning', 'cobalt_alloy_turning',
            'stainless_milling', 'edm_wire_cutting',
            'titanium_aging', 'stainless_17_4ph_h900', 'stainless_316l_annealing',
            'inconel_718_aging', 'stellite_overlay',
            'aluminum_anodize_hard', 'aluminum_chemical_conv', 'titanium_nitriding',
            'stainless_passivation', 'inconel_shot_peening', 'ptfe_coating',
            'inconel_718_ebw', 'stainless_316l_tig', 'titanium_tc4_lbw', 'stellite_braze',
            'thread_lubricant', 'torque_control', 'cleanliness', 'leak_test',
        ]
        specific_process = None
        for pid in process_keywords:
            if pid in msg_lower or pid.replace('_', ' ') in msg_lower:
                specific_process = pid
                break
        # Decision tree
        if specific_process:
            response['action'] = 'get_process_detail'
            response['tool_results'] = self._tool_get_process_detail(process_id=specific_process)
            d = response['tool_results']
            if d.get('success'):
                params_lines = []
                for k, v in d.items():
                    if k in ('success', '_tool', 'id', 'category'):
                        continue
                    if v is None or v == '':
                        continue
                    if isinstance(v, list) and len(v) == 2 and isinstance(v[0], (int, float)):
                        params_lines.append(f'  {k}: {v[0]} - {v[1]}')
                    else:
                        params_lines.append(f'  {k}: {v}')
                response['text'] = (
                    f"=== {d.get('name', specific_process)} ===\n\n"
                    f"Category: {d.get('category', '-')}\n"
                    f"Standard: {d.get('std', '-')}\n"
                    f"Applicability: {d.get('applicability', '-')}\n\n"
                    f"Parameters:\n" + "\n".join(params_lines)
                )
            response['suggestions'] = ['查 Inconel 718 EBW 焊接参数', '查 316L 钝化规范', '查钛合金时效处理']
        elif material and valve_type:
            response['action'] = 'recommend_process'
            response['tool_results'] = self._tool_recommend_process(material=material, valve_type=valve_type)
            r = response['tool_results']
            if r.get('success'):
                procs = r.get('process_details', [])
                proc_list = "\n".join([f"  {i+1}. {p['name']} ({p['category']})"
                                       for i, p in enumerate(procs)]) or '  (No process match)'
                route = r.get('route_suggestion', 'None')
                kp = "\n".join([f"  - {k}" for k in r.get('key_points', [])])
                response['text'] = (
                    f"=== {material} / {valve_type} 工艺推荐 ===\n\n"
                    f"Recommended Processes:\n{proc_list}\n\n"
                    f"Suggested Route: {route}\n\n"
                    f"Key Points:\n{kp}"
                )
            response['suggestions'] = [f'查 {material} 加工参数', f'查 {valve_type} 工艺路线', '生成车间作业指导书']
        elif material:
            response['action'] = 'recommend_process'
            response['tool_results'] = self._tool_recommend_process(material=material, valve_type='')
            r = response['tool_results']
            if r.get('success'):
                procs = r.get('process_details', [])
                proc_list = "\n".join([f"  {i+1}. {p['name']} ({p['category']})"
                                       for i, p in enumerate(procs)]) or '  (No process match)'
                response['text'] = (
                    f"=== {material} 工艺包 ===\n\n"
                    f"Recommended Processes:\n{proc_list}\n\n"
                    f"Tip: Specify valve type (e.g. relief/solenoid/check) for a complete process route."
                )
            response['suggestions'] = [f'{material} 减压阀工艺', f'{material} 电磁阀工艺', f'{material} 单向阀工艺']
        else:
            # No material: list all process categories
            response['action'] = 'list_processes'
            response['tool_results'] = self._tool_list_processes()
            r = response['tool_results']
            if r.get('success'):
                cats = r.get('categories', [])
                cat_list = "\n".join([f"  - {c['name']}: {c['count']} processes" for c in cats])
                response['text'] = (
                    '=== Avis 阀门工艺库 ===\n\n'
                    '5大工艺类别:\n' + cat_list + '\n\n'
                    '请指定: 材料 (如 Inconel 718 / 316L / TC4) + 阀门类型 (relief/solenoid/check)\n'
                    '或具体工艺 (如 titanium_turning / aluminum_t6)'
                )
            response['suggestions'] = [
                'Inconel 718 减压阀工艺',
                '316L 电磁阀工艺',
                'TC4 钛合金时效处理',
                'titanium_turning 参数',
            ]
        return response
    
    def _handle_knowledge(self, message: str, params: Dict, response: Dict) -> Dict:
        """Handle knowledge/information intent."""
        # Try searching knowledge base
        try:
            kb_result = self._tool_search_knowledge(query=message)
            if kb_result.get('success') and kb_result.get('results'):
                results = kb_result['results']
                response['text'] = (
                    f'=== 知识库搜索结果 ({len(results)} 条) ===\n\n'
                )
                for i, r in enumerate(results[:3], 1):
                    title = r.get('title', f'Result {i}')
                    snippet = r.get('content', '')[:150]
                    response['text'] += f'{i}. **{title}**\n{snippet}...\n\n'
                response['text'] += (
                    f'共找到 {kb_result["total"]} 条相关结果。\n'
                    '[浏览完整知识库](/knowledge) 获取详细内容。'
                )
                response['tool_results'] = results[:3]
                return response
        except Exception:
            pass
        
        # Fallback: general engineering guidance
        if '阀门' in message and ('类型' in message or '分类' in message):
            response['text'] = (
                '=== 航空航天阀门分类 ===\n\n'
                '按功能分类：\n'
                '• 电磁阀 — 电控开关，用于推进剂/气体控制\n'
                '• 减压阀 — 将高压转换为稳定低压输出\n'
                '• 单向阀 — 防止流体反向流动\n'
                '• 安全阀 — 超压保护泄放\n'
                '• 调节阀 — 精确流量/压力调节\n'
                '• 隔离阀 — 管路切断隔离\n\n'
                '按驱动方式：电磁驱动 / 气动 / 液压 / 手动\n'
                '按工作介质：气体 / 液体 / 低温 / 高温'
            )
        elif '密封' in message:
            response['text'] = (
                '=== 航空航天密封技术 ===\n\n'
                '主要密封形式：\n'
                '• O形圈密封 — 最常用，AS568F标准，FKM/FFKM\n'
                '• 金属密封 — 高温高压，Hertz接触理论\n'
                '• 波纹管密封 — 零泄漏要求\n'
                '• 磁流体密封 — 旋转轴密封\n'
                '• 迷宫密封 — 非接触式\n\n'
                '泄漏率标准 (QJ 20156): < 1e-6 Pa*m^3/s (He)\n'
                '泄漏模型: Roth分子流模型 (Kn > 1)'
            )
        elif '弹簧' in message:
            response['text'] = (
                '=== 阀门弹簧设计要点 ===\n\n'
                '关键参数:\n'
                '• 弹簧刚度 k = Gd^4 / (8nD^3)\n'
                '• 应力 tau = 8KFD / (pi*d^3) (Wahl系数K修正)\n'
                '• 固有频率 f = (d/(2pi*n*D^2)) * sqrt(G/(2*rho))\n\n'
                '航空材料: 1Cr18Ni9Ti, GH4169, QBe2, 4Cr13\n'
                '设计约束: 静强度 > 1.5x, 疲劳 > 20000次, 稳定性'
            )
        else:
            response['text'] = (
                '我是您的AI协同工程师，可以帮助您：\n\n'
                '**设计计算**\n'
                '• 电磁阀 / 减压阀 / 单向阀 / 弹簧 / O形圈 / 密封副\n'
                '• 流体力学 (207公式 / 21类别)\n\n'
                '**合规验证**\n'
                '• QJ 20156-2014 航天阀门鉴定标准\n'
                '• HB 6455-2014 / SAE AS568F / ISO 3601-2\n\n'
                '**知识查询**\n'
                '• 21种航空材料 / 48项性能指标 / 31400字知识库\n\n'
                '**对比优化**\n'
                '• 多方案对比 / PSO参数优化 / 迭代求解\n\n'
                '请直接告诉我您的工程问题！'
            )
        
        response['suggestions'] = ['阀门类型分类', '密封技术概述', '弹簧设计要点']
        return response
    
    # ---- Formatting Helpers ----
    
    def _format_error(self, error_msg: str) -> str:
        return f'处理请求时遇到问题: {error_msg}\n\n请尝试重新表述您的问题，或访问相应的计算模块直接操作。'


# ============================================================
# Global Engine Instance
# ============================================================
_engine = AIAgentEngine()

def get_engine() -> AIAgentEngine:
    return _engine
