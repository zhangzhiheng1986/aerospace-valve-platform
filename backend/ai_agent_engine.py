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
                '泄漏率', '泄漏', '密封', '弹簧力', '弹簧',
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
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_analyze_solenoid(self, **kwargs) -> Dict:
        """Analyze solenoid valve."""
        try:
            from solenoid_optimizer import SolenoidOptimizer
            opt = SolenoidOptimizer()
            voltage = float(kwargs.get('voltage', 28))
            stroke = float(kwargs.get('stroke', 2.0))
            force = float(kwargs.get('force_required', 10))
            result = opt.optimize(voltage=voltage, stroke=stroke, force_required=force)
            return {'success': True, 'type': 'solenoid', 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_analyze_prv(self, **kwargs) -> Dict:
        """Analyze pressure reducing valve."""
        try:
            from pressure_reducing_valve import analyze_prv
            result = analyze_prv(
                inlet_pressure=float(kwargs.get('inlet_pressure', 10e6)),
                outlet_pressure=float(kwargs.get('outlet_pressure', 2e6)),
                fluid_type=kwargs.get('fluid_type', 'nitrogen'),
                material=kwargs.get('material', '1Cr18Ni9Ti'),
            )
            return {'success': True, 'type': 'pressure_valve', 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_analyze_check(self, **kwargs) -> Dict:
        """Analyze check valve."""
        try:
            from check_valve import analyze_check_valve
            result = analyze_check_valve(
                nominal_diameter=float(kwargs.get('nominal_diameter', 10)),
                pressure=float(kwargs.get('pressure_rating', 21)),
                fluid_type=kwargs.get('fluid_type', 'nitrogen'),
            )
            return {'success': True, 'type': 'check_valve', 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_design_spring(self, **kwargs) -> Dict:
        """Design compression spring."""
        try:
            from spring_design import design_compression_spring
            result = design_compression_spring(
                wire_diameter=float(kwargs.get('wire_diameter', 0)) or None,
                outer_diameter=float(kwargs.get('outer_diameter', 20)),
                free_length=float(kwargs.get('free_length', 50)),
                active_coils=int(kwargs.get('active_coils', 8)),
                material=kwargs.get('material', '1Cr18Ni9Ti'),
            )
            return {'success': True, 'type': 'spring', 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_design_oring(self, **kwargs) -> Dict:
        """Design O-ring seal."""
        try:
            from oring_design import analyze_oring
            result = analyze_oring(
                app_type=kwargs.get('application_type', 'piston_seal'),
                housing_diameter=float(kwargs.get('housing_diameter', 25)),
                pressure=float(kwargs.get('pressure', 21)),
                material=kwargs.get('material', 'FKM'),
            )
            return {'success': True, 'type': 'oring', 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_check_compliance(self, **kwargs) -> Dict:
        """Check QJ 20156 compliance."""
        try:
            from qj20156_module import get_standard_info, evaluate_compliance
            info = get_standard_info()
            eval_args = {}
            if kwargs.get('rated_pressure'):
                eval_args['rated_pressure'] = float(kwargs['rated_pressure'])
            if kwargs.get('rated_temperature'):
                eval_args['rated_temperature'] = float(kwargs['rated_temperature'])
            if kwargs.get('design_life'):
                eval_args['design_life'] = int(kwargs['design_life'])
            compliance = evaluate_compliance(**eval_args) if eval_args else {}
            return {
                'success': True,
                'standard_info': info,
                'compliance': compliance,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _tool_query_material(self, **kwargs) -> Dict:
        """Query material database."""
        material_name = kwargs.get('material_name', 'TC4')
        try:
            from materials_database import get_material_by_name
            material = get_material_by_name(material_name)
            if material:
                return {'success': True, 'material': material}
            else:
                return {'success': False, 'error': f'Material "{material_name}" not found'}
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
        else:
            response = self._handle_knowledge(message, params, response)
        
        return response
    
    # ---- Intent Handlers ----
    
    def _handle_calculate(self, message: str, params: Dict, response: Dict) -> Dict:
        """Handle calculation intent."""
        # Try to determine what to calculate
        if '雷诺数' in message or 'reynolds' in message.lower():
            diam = params.get('diameter_mm', 10) / 1000
            vel = params.get('diameter_mm') or 1.0  # fallback
            response['text'] = (
                '我来帮你计算雷诺数。雷诺数 Re = v * D / nu，'
                '需要流体的运动粘度。请提供以下参数：\n\n'
                f'• 管径: {diam*1000:.1f} mm (从你的描述中提取)\n'
                '• 流速: ? m/s (请确认)\n'
                '• 介质: ? (氮气/氦气/液氧等)\n\n'
                '你也可以直接使用 [流体力学计算器](/fluid_mechanics) 获取精确结果。'
            )
            response['suggestions'] = ['打开流体力学计算器', '输入流速和介质']
        elif '压降' in message or 'pressure drop' in message.lower():
            response['text'] = (
                '管道压降计算需要考虑沿程损失和局部损失。\n\n'
                '基本公式 (Darcy-Weisbach):\n'
                'ΔP = f * (L/D) * (rho * v^2 / 2)\n\n'
                '请提供：管长 L、管径 D、流速 v、流体类型。\n'
                '或使用流体力学计算器中的管道流动模块。'
            )
            response['suggestions'] = ['管道流动计算', '输入管长和管径']
        elif '马赫' in message or 'mach' in message.lower():
            response['text'] = (
                '马赫数 M = v / c，其中 c = sqrt(gamma * R * T) 为当地声速。\n\n'
                '对于理想气体：\n'
                '• 空气 (15degC): c ≈ 340 m/s\n'
                '• 氮气 (15degC): c ≈ 350 m/s\n'
                '• 氦气 (15degC): c ≈ 1000 m/s\n\n'
                '请在流体力学计算器中输入流速和气体类型。'
            )
            response['suggestions'] = ['可压缩流模块', '选择气体类型']
        else:
            response['text'] = (
                '我可以帮你执行各种流体力学和工程计算。请具体说明需要计算什么参数。\n\n'
                '支持的领域：\n'
                '• 流体力学 (雷诺数/马赫数/压降/流量)\n'
                '• 阀门设计 (电磁阀/减压阀/单向阀)\n'
                '• 弹簧设计 / 密封设计\n'
                '• 热力学分析 / CFD仿真\n\n'
                '你也可以直接在 [流体力学计算器](/fluid_mechanics) 中运行任意公式。'
            )
            response['suggestions'] = ['雷诺数计算', '管道压降计算', '阀门推力计算']
        
        return response
    
    def _handle_analyze_valve(self, message: str, params: Dict, response: Dict) -> Dict:
        """Handle valve analysis intent."""
        if '电磁阀' in message or 'solenoid' in message.lower():
            response['action'] = 'analyze_solenoid'
            response['text'] = (
                '=== 电磁阀智能分析 ===\n\n'
                '我使用PSO粒子群优化算法为您设计电磁阀。\n\n'
                '【推荐参数】(卫星姿控典型工况)\n'
                '• 电压: 28 V DC\n'
                '• 行程: 2.0 mm\n'
                '• 需求电磁力: 10 N\n'
                '• 线径: AWG 26\n'
                '• 工作介质: 氮气\n\n'
                '我可以帮您运行优化计算。是否需要我立即执行？\n'
            )
            response['suggestions'] = ['运行电磁阀优化', '调整行程为3mm', '对比AWG 24和26']
        
        elif '减压阀' in message or 'pressure reducing' in message.lower():
            response['action'] = 'analyze_prv'
            response['text'] = (
                '=== 减压阀设计分析 ===\n\n'
                '当前支持5种流体介质和3种材料。\n'
                '【典型航天工况】\n'
                '• 入口压力: 10 MPa (高压气瓶)\n'
                '• 出口压力: 2 MPa (下游系统)\n'
                '• 介质: 氮气\n'
                '• 阀体材料: 1Cr18Ni9Ti\n\n'
                '需要我基于这些参数运行设计计算吗？'
            )
            response['suggestions'] = ['运行减压阀分析', '对比氦气介质', '调整出口压力']
        
        elif '单向阀' in message or '止回阀' in message or 'check valve' in message.lower():
            response['action'] = 'analyze_check'
            response['text'] = (
                '=== 单向阀设计分析 (HB 6455-2014) ===\n\n'
                '标准要求：\n'
                '• 开启压力: <=0.05 MPa\n'
                '• 反向泄漏: <=1e-5 Pa*m^3/s (He)\n'
                '• 流阻系数: 优化最小化\n\n'
                '【典型参数】\n'
                '• 通径: 10 mm\n'
                '• 额定压力: 21 MPa\n'
                '• 介质: 氮气\n\n'
                '共有6个子模块可用。需要运行计算吗？'
            )
            response['suggestions'] = ['运行单向阀设计', '对比不同通径', '检查密封性能']
        
        elif 'O形' in message or 'O型' in message or 'oring' in message.lower() or 'o-ring' in message.lower():
            response['action'] = 'design_oring'
            response['text'] = (
                '=== O形密封圈设计 (SAE AS568F / ISO 3601-2) ===\n\n'
                '使用Roth分子流泄漏率模型。\n\n'
                '【推荐参数】\n'
                '• 密封类型: 活塞密封\n'
                '• 安装槽径: 25 mm\n'
                '• 工作压力: 21 MPa\n'
                '• 材料: FKM (氟橡胶)\n'
                '• 温度范围: -20 ~ 200degC\n\n'
                'ASA568数据库覆盖5~656mm。需要运行设计吗？'
            )
            response['suggestions'] = ['运行O形圈设计', '对比NBR和FKM', '检查泄漏率']
        
        elif '弹簧' in message or 'spring' in message.lower():
            response['action'] = 'design_spring'
            response['text'] = (
                '=== 压缩弹簧设计 ===\n\n'
                '支持4种航空材料，迭代求解器 + 疲劳/稳定性校核。\n\n'
                '【典型参数】\n'
                '• 外径: 20 mm\n'
                '• 自由长度: 50 mm\n'
                '• 有效圈数: 8\n'
                '• 材料: 1Cr18Ni9Ti\n'
                '• 钢丝直径: (自动迭代求解)\n\n'
                '需要运行弹簧设计计算吗？'
            )
            response['suggestions'] = ['运行弹簧设计', '对比不同材料', '校核疲劳寿命']
        
        else:
            response['text'] = (
                '=== 阀门设计分析能力 ===\n\n'
                '我可以帮您分析和设计以下阀类：\n'
                '• 电磁阀 (PSO粒子群优化 + AWG搜索)\n'
                '• 减压阀 (5流体5材料3预设)\n'
                '• 单向阀 (HB 6455-2014标准)\n'
                '• 弹簧设计 (4材料, 迭代, 疲劳/稳定性)\n'
                '• O形密封圈 (SAE AS568F, Roth泄漏率)\n'
                '• 密封副 (Hertz接触 + Roth分子流)\n\n'
                '请指定阀门类型和关键参数。'
            )
            response['suggestions'] = ['分析电磁阀', '设计O形圈', '设计压缩弹簧']
        
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
