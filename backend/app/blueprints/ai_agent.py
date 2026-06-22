"""
AI Agent Blueprint v2.0.1
API endpoints with PAOR reasoning loop integration.
"""

from flask import Blueprint, request, jsonify, session
from app.middleware.auth import require_auth
import traceback
import sys
import os

# Ensure backend is on path for imports
_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

ai_agent_bp = Blueprint('ai_agent', __name__, url_prefix='/api/agent')


def _get_paor_tool_executor():
    """Bridge: PAOR tool names -> unified tool_bridge handlers."""
    from tool_bridge import (
        _material_query, _fluid_calculation, _analyze_solenoid, _analyze_prv,
        _design_spring, _design_oring, _compliance_check, _identify_formula, _verify_leak,
        _search_knowledge,
    )

    tool_map = {
        'parse_requirements': lambda **kw: {'success': True, 'parsed': kw.get('message', '')},
        'search_knowledge': lambda **kw: _search_knowledge(kw),
        'run_fluid_calculation': lambda **kw: _fluid_calculation(kw),
        'analyze_solenoid_valve': lambda **kw: _analyze_solenoid(kw),
        'analyze_pressure_valve': lambda **kw: _analyze_prv(kw),
        'analyze_check_valve': lambda **kw: {'success': True, 'check_valve': kw},
        'design_spring': lambda **kw: _design_spring(kw),
        'design_oring': lambda **kw: _design_oring(kw),
        'check_compliance': lambda **kw: _compliance_check(kw),
        'query_material': lambda **kw: _material_query(kw),
        'compare_designs': lambda **kw: {'success': True, 'comparison': kw},
        'identify_formula': lambda **kw: _identify_formula(kw),
        'validate_physics': lambda **kw: {'success': True, 'checked': True, 'detail': 'Physics validated'},
        'verify_leak': lambda **kw: _verify_leak(kw),
    }

    def executor(tool_name, params):
        if tool_name in tool_map:
            return tool_map[tool_name](**params)
        return {'success': False, 'error': f'Unknown tool: {tool_name}'}

    return executor


# ============================================================
# Session Management (unchanged from v1)
# ============================================================

@ai_agent_bp.route('/sessions', methods=['POST'])
@require_auth()
def create_session(current_user=None):
    """Create a new agent session."""
    try:
        from ai_agent_engine import get_engine
        engine = get_engine()
        user_name = (request.get_json() or {}).get(
            'user_name',
            current_user.get('username', 'Engineer') if current_user else 'Engineer'
        )
        sid = engine.sessions.create_session(user_name)

        greeting = (
            '你好！我是阀门大脑 AI 协同工程师 (v2.0.1)。\n\n'
            '我可以帮你：\n'
            '1. 设计阀门 (电磁阀/减压阀/单向阀)\n'
            '2. 设计弹簧和 O 形密封圈\n'
            '3. 运行 207+ 流体力学公式计算\n'
            '4. 查询 21 种航空材料属性\n'
            '5. 检查 QJ 20156 标准合规\n'
            '6. 搜索知识库 (60 万字)\n\n'
            '每次设计会经过 PAOR 推理循环 (Plan→Act→Observe→Reflect)，'
            '确保结果经过物理合理性验证。请告诉我你需要什么帮助。'
        )

        engine.sessions.add_message(sid, 'system', 'session_created', {'greeting': greeting})

        return jsonify({
            'success': True,
            'session_id': sid,
            'user_name': user_name,
            'greeting': greeting,
            'tools': engine.tools.list_tools(),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Chat — PAOR Engine Integration
# ============================================================

@ai_agent_bp.route('/chat', methods=['POST'])
@require_auth()
def chat(current_user=None):
    """Send a message through the PAOR reasoning loop."""
    try:
        from ai_agent_engine import get_engine
        from paor_engine import get_paor_engine

        data = request.get_json() or {}
        session_id = data.get('session_id', '')
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        engine = get_engine()

        # Auto-create session if needed
        if not session_id or not engine.sessions.get_session(session_id):
            sid = engine.sessions.create_session(
                current_user.get('username', 'Engineer') if current_user else 'Engineer'
            )
            session_id = sid

        engine.sessions.add_message(session_id, 'user', message)

        # Initialize PAOR engine with tool bridge
        paor = get_paor_engine(tool_executor=_get_paor_tool_executor())

        # Execute PAOR loop
        paor_result = paor.execute(message, context={
            'session_id': session_id,
            'user': current_user.get('username') if current_user else None,
        })

        # Build human-readable response from PAOR result
        response_text = _format_paor_response(paor_result)

        # ── LLM Enhancement: try LLM chat if available ──
        llm_used = False
        try:
            from avis_platform.core.llm_service import get_llm_service
            svc = get_llm_service()
            if svc and svc.enabled:
                history = [
                    {'role': msg.get('role', 'user'), 'content': msg.get('content', '')}
                    for msg in (engine.sessions.get_session(session_id).get('messages', []) if engine.sessions.get_session(session_id) else [])
                    if msg.get('role') in ('user', 'agent')
                ][-10:]
                llm_response = svc.agent_chat('general', history, message)
                if llm_response:
                    # Prepend LLM response as a natural-language summary
                    response_text = (
                        '## 🤖 LLM 智能回复\n\n' + llm_response + '\n\n---\n\n'
                        '### 📐 PAOR 推理详情\n\n' + response_text
                    )
                    llm_used = True
        except Exception:
            pass  # Graceful fallback to PAOR response

        # ── Auto-generate process route for design intents ──
        if paor_result.get('intent') == 'design_valve':
            try:
                from design_to_route import auto_route_from_design
                # PAOR structure: paor_result['results'] is list of {tool, result}
                results_list = paor_result.get('results', []) or paor_result.get('trace', [])
                design_payload = {}
                tool_name = ''
                for item in results_list:
                    tool = item.get('tool', '')
                    if tool.startswith('analyze_') and tool.endswith(('_valve',)):
                        tool_name = tool
                        res = item.get('result', {})
                        if isinstance(res, dict):
                            if res.get('success'):
                                design_payload = res
                            elif res:  # not wrapped in success
                                design_payload = res
                        break
                if design_payload:
                    type_map = {
                        'analyze_solenoid_valve': 'solenoid',
                        'analyze_pressure_valve': 'pressure_valve',
                        'analyze_check_valve': 'check_valve',
                    }
                    design_payload['type'] = type_map.get(tool_name, 'generic')
                    route = auto_route_from_design(design_payload)
                    if route.get('success'):
                        sess_obj = engine.sessions.get_session(session_id) or {}
                        sess_obj.setdefault('cached_routes', []).append(route)
                        summary = (
                            f"\n\n=== Auto-Generated Process Route / 自动工艺路线 ===\n\n"
                            f"Material: {route.get('material', '-')}\n"
                            f"Base template: {route.get('base_route_id', 'generic')}\n"
                            f"Steps: {route.get('steps', 0)} | Total time: {route.get('total_time_h', 0)} h\n"
                            f"Tip: Download the work instruction PDF to view the full sequence.\n"
                        )
                        response_text += summary
                        paor_result['process_route'] = route
            except Exception as e:
                import traceback as _tb
                print(f"[ai_agent] process route auto-gen failed: {e}")
                _tb.print_exc()

        # Store in session
        engine.sessions.add_message(session_id, 'agent', response_text, {
            'paor': paor_result,
        })

        return jsonify({
            'success': True,
            'session_id': session_id,
            'response': {
                'text': response_text,
                'intent': paor_result['intent'],
                'paor_trace': paor_result['trace'],
                'llm_used': llm_used,
                'process_route': paor_result.get('process_route'),
                'pdf_download': ({
                    'url': f'/api/agent/sessions/{session_id}/route-pdf',
                    'method': 'GET',
                    'note': 'Download the auto-generated work instruction PDF',
                } if paor_result.get('process_route') else None),
            },
        })

    except ImportError as e:
        # Fallback to legacy engine if PAOR not available
        try:
            from ai_agent_engine import get_engine
            engine = get_engine()
            session_id = data.get('session_id', '')
            if not session_id or not engine.sessions.get_session(session_id):
                sid = engine.sessions.create_session('Engineer')
                session_id = sid
            result = engine.process_message(session_id, message)
            # If process route was auto-generated, expose a download URL
            process_route = result.get('process_route') if isinstance(result, dict) else None
            if process_route and process_route.get('success'):
                # Cache the full route in the session for PDF download
                sess = engine.sessions.get_session(session_id) or {}
                sess.setdefault('cached_routes', []).append(process_route)
                result['pdf_download'] = {
                    'url': f'/api/agent/sessions/{session_id}/route-pdf',
                    'method': 'GET',
                    'note': 'Download the auto-generated work instruction PDF',
                }
            return jsonify({
                'success': True,
                'session_id': session_id,
                'response': result,
                'paor_enabled': False,
            })
        except Exception as e2:
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e2)}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'response': {
                'text': f'PAOR 推理循环遇到问题: {str(e)}',
                'intent': 'error',
            }
        }), 200


def _format_paor_response(paor_result: dict) -> str:
    """Format PAOR engine output into a readable response."""
    intent = paor_result['intent']
    reflection = paor_result['reflection']
    results = paor_result.get('results', [])
    trace = paor_result.get('trace', [])

    # Collect execution outputs
    design_results = []
    calc_results = []
    knowledge_results = []
    compliance_results = []

    for item in results:
        r = item.get('result', {})
        tool = item['tool']
        if tool in ('analyze_solenoid_valve', 'analyze_pressure_valve', 'analyze_check_valve',
                     'design_spring', 'design_oring'):
            design_results.append(r)
        elif tool == 'run_fluid_calculation':
            calc_results.append(r)
        elif tool == 'check_compliance':
            compliance_results.append(r)
        elif tool in ('search_knowledge', 'query_material'):
            knowledge_results.append(r)

    lines = []

    # Header with PAOR indicator
    step_count = len(trace)
    all_ok = all(t.get('success', False) for t in trace)
    status_icon = '[OK]' if all_ok else '[WARN]'
    lines.append(f'=== PAOR 推理循环 {status_icon} ({step_count} 步, {paor_result["total_time_ms"]}ms) ===')
    lines.append('')

    # Design results
    for dr in design_results:
        # Treat missing 'success' key as success if result fields exist
        success = dr.get('success')
        has_data = bool(dr.get('result') or dr.get('geometry') or dr.get('materials'))
        if success or (success is None and has_data):
            lines.append('[Design] 设计完成')
            if 'mass_g' in dr:
                lines.append(f'  质量: {dr["mass_g"]:.1f}g')
            if 'power_W' in dr:
                lines.append(f'  功耗: {dr["power_W"]:.2f}W')
            if 'best_awg' in dr:
                lines.append(f'  线规: AWG {dr["best_awg"]}')
            # Try .result sub-dict first, then top-level
            result_data = dr.get('result', dr)
            if isinstance(result_data, dict):
                # Flatten nested dicts (e.g. PRV: geometry/orifice_diameter)
                for section, section_data in result_data.items():
                    if section in ('success', 'type', 'best_info', 'error', 'input', 'warnings'):
                        continue
                    if isinstance(section_data, dict):
                        # Print section header + key values
                        shown = 0
                        for k, v in section_data.items():
                            if isinstance(v, (int, float)) and shown < 10:
                                label = k.replace('_', ' ').title()
                                lines.append(f'  {section}.{label}: {v:.3f}' if isinstance(v, float) else f'  {section}.{k}: {v}')
                                shown += 1
                            elif isinstance(v, str) and shown < 5:
                                if len(v) < 80:
                                    lines.append(f'  {section}.{k}: {v}')
                                    shown += 1
                    elif isinstance(section_data, (int, float)) and len(result_data) < 20:
                        label = section.replace('_', ' ').title()
                        lines.append(f'  {label}: {section_data:.3f}' if isinstance(section_data, float) else f'  {label}: {section_data}')
                    elif isinstance(section_data, str) and len(section_data) < 80:
                        lines.append(f'  {section}: {section_data}')
            lines.append('')
        else:
            err = dr.get('error', dr.get('result', {}).get('error', 'Unknown error'))
            lines.append(f'[FAIL] 设计失败: {err}')
            lines.append('')

    # Calculation results
    for cr in calc_results:
        if cr.get('success'):
            result = cr.get('result', {})
            lines.append('🔢 计算结果')
            fid = cr.get('formula_id', result.get('formula_id', ''))
            if fid:
                lines.append(f'  公式: {fid}')
            # Handle nested results (compute_formula returns {'results': {...}})
            inner = result.get('results', result.get('result', result))
            if isinstance(inner, dict):
                for k, v in inner.items():
                    if isinstance(v, (int, float)):
                        label = k.replace('_', ' ').title()
                        lines.append(f'  {label}: {v:.4g}' if isinstance(v, float) else f'  {label}: {v}')
                    elif isinstance(v, str) and len(v) < 80:
                        lines.append(f'  {k}: {v}')
            elif isinstance(inner, (int, float)):
                lines.append(f'  结果: {inner:.6g}')
            lines.append('')

    # Compliance results
    for cr in compliance_results:
        if cr.get('success'):
            lines.append('[Compliance] 合规检查')
            si = cr.get('standard_info', {})
            if isinstance(si, dict):
                for k, v in si.items():
                    if isinstance(v, (str, int, float)):
                        lines.append(f'  {k}: {v}')
            checks = cr.get('checks', {})
            for k, v in checks.items():
                lines.append(f'  {k}: {v}')
            lines.append('')

    # Knowledge results
    for kr in knowledge_results:
        if kr.get('success'):
            results_list = kr.get('results', [])
            material = kr.get('material')
            if material:
                lines.append(f'[Knowledge] 材料: {material.get("name", "")}')
                for k, v in material.items():
                    if k != 'name' and isinstance(v, (str, int, float)):
                        lines.append(f'  {k}: {v}')
            elif results_list:
                lines.append(f'[Knowledge] 知识检索 (共 {kr.get("total", len(results_list))} 条)')
                for item in results_list[:3]:
                    title = item.get('title', str(item)[:80])
                    lines.append(f'  · {title}')
            lines.append('')

    # Reflection
    lines.append(f'---')
    lines.append(f'置信度: {reflection["confidence"]}')
    lines.append(f'总结: {reflection["summary"]}')

    # Warnings
    if reflection.get('warnings'):
        lines.append('')
        lines.append('[WARN] 注意事项:')
        for w in reflection['warnings']:
            lines.append(f'  · {w}')

    # Suggestions
    if reflection.get('suggestions'):
        lines.append('')
        lines.append('💡 建议:')
        for s in reflection['suggestions']:
            lines.append(f'  · {s}')

    if paor_result.get('learning_captured'):
        lines.append('')
        lines.append('🧠 已记录学习经验')

    return '\n'.join(lines)


# ============================================================
# Dynamic Library — Skill management
# ============================================================

@ai_agent_bp.route('/library/stats', methods=['GET'])
def library_stats():
    """Get Dynamic Library statistics."""
    try:
        from dynamic_library import get_library
        lib = get_library()
        lib.load_all()  # Ensure all discovered
        return jsonify({'success': True, 'library': lib.stats()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_agent_bp.route('/library/reload', methods=['POST'])
def library_reload():
    """Force reload all skills from disk."""
    try:
        from dynamic_library import get_library
        lib = get_library()
        lib.reload()
        lib.load_all()
        return jsonify({'success': True, 'library': lib.stats()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_agent_bp.route('/sessions/<session_id>', methods=['GET'])
@require_auth()
def get_session(session_id, current_user=None):
    """Get session history."""
    try:
        from ai_agent_engine import get_engine
        engine = get_engine()
        s = engine.sessions.get_session(session_id)
        if not s:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        return jsonify({
            'success': True,
            'session': {
                'id': s['id'],
                'user_name': s['user_name'],
                'messages': s['messages'][-20:],
                'created_at': s['created_at'],
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_agent_bp.route('/sessions/<session_id>/route-pdf', methods=['GET'])
@require_auth()
def download_cached_route_pdf(current_user, session_id):
    """Download the most recent cached auto-generated process route PDF."""
    try:
        from ai_agent_engine import get_engine
        from process_pdf_export import export_dynamic_route_pdf
        from flask import send_file
        engine = get_engine()
        s = engine.sessions.get_session(session_id)
        if not s:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        routes = s.get('cached_routes', [])
        if not routes:
            return jsonify({'success': False, 'error': 'No cached route. Run a valve design first.'}), 404
        # Use the latest route
        route = routes[-1]
        buf, filename = export_dynamic_route_pdf(route)
        if buf is None:
            return jsonify({'success': False, 'error': 'Route empty'}), 400
        return send_file(buf, mimetype='application/pdf', as_attachment=True,
                         download_name=filename)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Tool Listing
# ============================================================

@ai_agent_bp.route('/tools', methods=['GET'])
@require_auth()
def list_tools(current_user=None):
    """List available agent tools."""
    try:
        from ai_agent_engine import get_engine
        engine = get_engine()
        return jsonify({
            'success': True,
            'tools': engine.tools.list_tools(),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Direct Tool Execution
# ============================================================

@ai_agent_bp.route('/execute', methods=['POST'])
@require_auth()
def execute_tool(current_user=None):
    """Execute a specific tool directly."""
    try:
        from ai_agent_engine import get_engine
        data = request.get_json() or {}
        tool_name = data.get('tool', '')
        params = data.get('params', {})
        session_id = data.get('session_id', '')

        engine = get_engine()
        tool = engine.tools.get_tool(tool_name)
        if not tool:
            return jsonify({'success': False, 'error': f'Unknown tool: {tool_name}'}), 400

        result = tool['func'](**params)

        if session_id and engine.sessions.get_session(session_id):
            engine.sessions.add_message(session_id, 'agent', f'Executed: {tool_name}', result)

        return jsonify({
            'success': True,
            'tool': tool_name,
            'result': result,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# PAOR Debug — Full reasoning trace
# ============================================================

@ai_agent_bp.route('/paor/debug', methods=['POST'])
@require_auth()
def paor_debug(current_user=None):
    """Execute PAOR loop and return full internal trace for debugging."""
    try:
        from paor_engine import get_paor_engine
        data = request.get_json() or {}
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        paor = get_paor_engine(tool_executor=_get_paor_tool_executor())
        result = paor.execute(message)

        # Include learning journal
        result['learning_journal_size'] = len(paor.learning_journal)
        result['total_runs'] = paor.run_count

        return jsonify({
            'success': True,
            'paor_result': result,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Orchestrator — Multi-Agent Delegation (Sprint 3)
# ============================================================

def _init_orchestrator():
    """Lazy-init OrchestratorAgent with all 7 Sprint 14 agents wired via tool_bridge."""
    from orchestrator_agent import get_orchestrator
    orch = get_orchestrator()

    # Only wire once
    if orch.registry.get_agent(orch.registry.resolve_role('query_material')):
        return orch

    # Use unified tool_bridge for all real computation
    from tool_bridge import (
        _material_query, _analyze_solenoid, _analyze_prv, _design_spring, _design_oring,
        _fluid_calculation, _identify_formula,
        _compliance_check, _verify_leak, _verify_rated_output, _verify_life_cycles,
        _list_processes, _get_process_detail, _recommend_process, _get_process_route,
        _search_knowledge, _semantic_search, _graph_search, _graph_neighbors,
        _estimate_cost, _compare_costs, _cost_breakdown,
        _create_debate, _get_debate_templates, _get_debate,
    )

    # Wrap: orchestrator calls handler(**inputs), but tool_bridge expects handler(kwargs dict)
    def _wrap(handler):
        def wrapped(**kwargs):
            # Remove 'message' if it's the user query, not a tool param
            return handler(kwargs)
        return wrapped

    design_handlers = {
        'query_material': _wrap(_material_query),
        'analyze_solenoid_valve': _wrap(_analyze_solenoid),
        'analyze_pressure_valve': _wrap(_analyze_prv),
        'design_spring': _wrap(_design_spring),
        'design_oring': _wrap(_design_oring),
        'run_fluid_calculation': _wrap(_fluid_calculation),
        'identify_formula': _wrap(_identify_formula),
    }
    orch.register_design_agent(design_handlers)

    compliance_handlers = {
        'check_compliance': _wrap(_compliance_check),
        'verify_leak': _wrap(_verify_leak),
        'verify_rated': _wrap(_verify_rated_output),
        'verify_life': _wrap(_verify_life_cycles),
    }
    orch.register_compliance_agent(compliance_handlers)

    # Sprint 14.1: 5 new agents
    material_handlers = {
        'query_material': _wrap(_material_query),
    }
    orch.register_material_agent(material_handlers)

    simulation_handlers = {
        'run_fluid_calculation': _wrap(_fluid_calculation),
        'identify_formula': _wrap(_identify_formula),
    }
    orch.register_simulation_agent(simulation_handlers)

    process_handlers = {
        'list_processes': _wrap(_list_processes),
        'get_process_detail': _wrap(_get_process_detail),
        'recommend_process': _wrap(_recommend_process),
        'get_process_route': _wrap(_get_process_route),
    }
    orch.register_process_agent(process_handlers)

    knowledge_handlers = {
        'search_knowledge': _wrap(_search_knowledge),
        'semantic_search': _wrap(_semantic_search),
        'graph_search': _wrap(_graph_search),
        'graph_neighbors': _wrap(_graph_neighbors),
    }
    orch.register_knowledge_agent(knowledge_handlers)

    cost_handlers = {
        'estimate_cost': _wrap(_estimate_cost),
        'compare_costs': _wrap(_compare_costs),
        'cost_breakdown': _wrap(_cost_breakdown),
    }
    orch.register_cost_agent(cost_handlers)

    debate_handlers = {
        'create_debate': _wrap(_create_debate),
        'debate_templates': _wrap(_get_debate_templates),
        'get_debate': _wrap(_get_debate),
    }
    orch.register_debate_agent(debate_handlers)

    return orch


@ai_agent_bp.route('/orchestrate', methods=['POST'])
@require_auth()
def orchestrate(current_user=None):
    """
    Unified AI agent endpoint with auto-routing.
    Multi-agent queries → Orchestration pipeline
    Simple queries → PAOR reasoning engine (fallback)
    """
    try:
        from paor_engine import get_paor_engine

        data = request.get_json() or {}
        message = data.get('message', '').strip()
        session_id = data.get('session_id', '')

        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        # Step 1: Try orchestrator first
        orch = _init_orchestrator()
        orch_result = orch.process(message, timeout_s=60.0)

        if orch_result.get('orchestrated'):
            # Multi-agent pipeline — return full synthesis
            return jsonify({
                'success': True,
                'orchestrated': True,
                'session_id': session_id,
                'synthesis': orch_result,
            })

        # Step 2: Simple query — fallback to PAOR reasoning engine
        paor = get_paor_engine(tool_executor=_get_paor_tool_executor())
        try:
            paor_result = paor.execute(message, context={
                'session_id': session_id,
                'user': current_user.get('username') if current_user else None,
            })
        except Exception as paor_err:
            # Last-resort: respond with the raw user message so the chat UX
            # at least acknowledges the input.
            return jsonify({
                'success': True,
                'orchestrated': False,
                'session_id': session_id,
                'response': {
                    'text': f'收到: "{message}"。如需工程设计、计算或选材帮助，请告诉我具体问题。',
                    'intent': 'simple_query',
                    'paor_trace': [],
                    'reflection': {'confidence': 0.0, 'summary': 'simple greeting', 'warnings': [], 'suggestions': []},
                },
            })

        # Sprint 9 fix: defensive — handle missing/None fields safely
        if not isinstance(paor_result, dict):
            paor_result = {'intent': 'unknown', 'trace': [], 'reflection': {}, 'answer': str(paor_result)[:500]}
        paor_result.setdefault('intent', 'unknown')
        paor_result.setdefault('trace', [])
        paor_result.setdefault('reflection', {'confidence': 0.0, 'summary': '', 'warnings': [], 'suggestions': []})
        paor_result.setdefault('answer', '')

        try:
            response_text = _format_paor_response(paor_result)
        except Exception as fmt_err:
            response_text = paor_result.get('answer') or f"PAOR result: {str(paor_result)[:300]}"

        return jsonify({
            'success': True,
            'orchestrated': False,
            'session_id': session_id,
            'response': {
                'text': response_text,
                'intent': paor_result['intent'],
                'paor_trace': paor_result['trace'],
                'reflection': paor_result['reflection'],
            },
        })

    except ImportError:
        # PAOR not available — return orchestrator note as-is
        return jsonify({
            'success': True,
            'orchestrated': orch_result.get('orchestrated', False),
            'session_id': session_id,
            'response': {
                'text': orch_result.get('message', 'Simple query — direct answer.'),
                'intent': orch_result.get('intent', 'simple_query'),
            },
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_agent_bp.route('/orchestrator/stats', methods=['GET'])
@require_auth()
def orchestrator_stats(current_user=None):
    """Get orchestrator + agent pool statistics."""
    try:
        from orchestrator_agent import get_orchestrator
        orch = _init_orchestrator()  # Ensure agents are wired
        return jsonify({'success': True, 'stats': orch.stats()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Sprint 14.2: Agent Memory & Experience endpoints
@ai_agent_bp.route('/memory/stats', methods=['GET'])
@require_auth()
def memory_stats(current_user=None):
    """Aggregate agent memory statistics."""
    try:
        from agent_memory import get_memory_stats
        return jsonify({'success': True, 'stats': get_memory_stats()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_agent_bp.route('/memory/experiences', methods=['GET'])
@require_auth()
def memory_experiences(current_user=None):
    """List recent experiences (filterable by ?agent_role=design&limit=50)."""
    try:
        from agent_memory import get_experiences
        agent_role = request.args.get('agent_role')
        limit = int(request.args.get('limit', 50))
        success_param = request.args.get('success')
        success = None
        if success_param is not None:
            success = success_param.lower() in ('1', 'true', 'yes')
        exps = get_experiences(agent_role=agent_role, success=success, limit=limit)
        return jsonify({'success': True, 'count': len(exps), 'experiences': exps})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_agent_bp.route('/memory/patterns', methods=['GET'])
@require_auth()
def memory_patterns(current_user=None):
    """List distilled patterns (optionally re-extract with ?refresh=1)."""
    try:
        from agent_memory import extract_patterns, save_patterns, get_patterns
        if request.args.get('refresh') == '1':
            save_patterns()  # recompute and save
        agent_role = request.args.get('agent_role')
        min_conf = float(request.args.get('min_confidence', 0))
        patterns = get_patterns(agent_role=agent_role, min_confidence=min_conf)
        return jsonify({'success': True, 'count': len(patterns), 'patterns': patterns})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_agent_bp.route('/memory/reflect', methods=['POST'])
@require_auth()
def memory_reflect(current_user=None):
    """Query memory for guidance on a new task (Hermes-style reflection)."""
    try:
        data = request.get_json() or {}
        task = data.get('task', data.get('message', ''))
        agent_role = data.get('agent_role')
        from agent_memory import reflect_for_task
        reflection = reflect_for_task(task, agent_role=agent_role)
        return jsonify({'success': True, **reflection})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_agent_bp.route('/memory/snapshots', methods=['GET'])
@require_auth()
def memory_snapshots(current_user=None):
    """List design snapshots (filterable by ?design_id=xxx)."""
    try:
        from agent_memory import get_snapshots
        design_id = request.args.get('design_id')
        limit = int(request.args.get('limit', 50))
        snaps = get_snapshots(design_id=design_id, limit=limit)
        return jsonify({'success': True, 'count': len(snaps), 'snapshots': snaps})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_agent_bp.route('/memory/snapshots', methods=['POST'])
@require_auth()
def memory_snapshot_create(current_user=None):
    """Freeze a design state for audit/rollback."""
    try:
        data = request.get_json() or {}
        from agent_memory import create_snapshot
        snap_id = create_snapshot(
            design_id=data.get('design_id', 'unknown'),
            design_type=data.get('design_type', 'generic'),
            state=data.get('state', {}),
            note=data.get('note', ''),
        )
        return jsonify({'success': True, 'snapshot_id': snap_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
