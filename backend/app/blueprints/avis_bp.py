"""
avis_bp.py -- Avis Intelligent Agent Platform Blueprint
Multi-agent system integration with department collaboration and memory.

Endpoints:
  POST /api/avis/chat          - Main chat
  POST /api/avis/session       - Create session
  GET  /api/avis/session/<id>  - Get session
  GET  /api/avis/agents        - List agents
  POST /api/avis/agent/<id>    - Direct agent call
  GET  /api/avis/health        - Health check
  -- Memory --
  GET  /api/avis/memory/snapshots
  GET  /api/avis/memory/snapshots/search?q=
  GET  /api/avis/memory/snapshots/<id>
  POST /api/avis/memory/snapshots/diff
  GET  /api/avis/memory/experiences
  GET  /api/avis/memory/experiences/patterns
  GET  /api/avis/memory/experiences/export
  GET  /api/avis/memory/feedback
  POST /api/avis/memory/feedback
  GET  /api/avis/memory/archives
  POST /api/avis/memory/archives/<session_id>
  GET  /api/avis/memory/archives/<session_id>
  POST /api/avis/admin/reload
  -- Nudge Engine --
  POST /api/avis/nudge/analyze
  GET  /api/avis/nudge/list
  POST /api/avis/nudge/acknowledge
  POST /api/avis/nudge/dismiss
  GET  /api/avis/nudge/stats
  -- Multi-Department Collaboration --
  GET  /api/avis/departments
  GET  /api/avis/departments/<dept_id>
  GET  /api/avis/agents-list
  GET  /api/avis/agents/<agent_id>
  GET  /api/avis/workflows
  GET  /api/avis/workflows/<wf_id>
  GET  /api/avis/collab/runs
  POST /api/avis/collab/runs
  GET  /api/avis/collab/runs/<run_id>
  POST /api/avis/collab/runs/<run_id>/advance
  POST /api/avis/collab/runs/<run_id>/approve
  POST /api/avis/collab/runs/<run_id>/reject
  POST /api/avis/collab/route
  GET  /api/avis/org-chart
"""

import json
import sys
import os
import importlib
import traceback
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
try:
    from avis_platform.core.knowledge_graph import EntityNotFoundError
except ImportError:
    EntityNotFoundError = Exception  # fallback

avis_bp = Blueprint('avis', __name__)

# Ensure avis-platform paths are on sys.path at module load time
_bp_dir = os.path.dirname(os.path.abspath(__file__))
_workspace = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_bp_dir))))
_avis_root = os.path.join(_workspace, 'avis-platform')
if not os.path.isdir(_avis_root):
    _avis_root = os.path.join(os.getcwd(), 'avis-platform')
_avis_core = os.path.join(_avis_root, 'core')
_avis_agents = os.path.join(_avis_root, 'agents')
# Add workspace root to sys.path so "avis_platform" package resolves
if _workspace not in sys.path:
    sys.path.insert(0, _workspace)
# Add avis-platform root so `from core.xxx` and `from agents.xxx` resolve
if _avis_root not in sys.path:
    sys.path.insert(0, _avis_root)
if _avis_core not in sys.path:
    sys.path.insert(0, _avis_core)
if _avis_agents not in sys.path:
    sys.path.insert(0, _avis_agents)

# ============================================================
# Orchestrator singleton
# ============================================================

_orchestrator = None


def _get_orchestrator():
    global _orchestrator
    if _orchestrator is not None:
        return _orchestrator

    try:
        # Find avis-platform relative to workspace root
        # blueprint is at: workspace/aerospace-valve-platform/backend/app/blueprints/avis_bp.py
        _bp_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up: blueprints -> app -> backend -> aerospace-valve-platform -> workspace
        _workspace = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_bp_dir))))
        avis_root = os.path.join(_workspace, 'avis-platform')

        if not os.path.isdir(avis_root):
            avis_root = os.path.join(os.getcwd(), 'avis-platform')

        core_path = os.path.join(avis_root, 'core')
        agents_path = os.path.join(avis_root, 'agents')
        skills_path = os.path.join(avis_root, 'skills')

        if core_path not in sys.path:
            sys.path.insert(0, core_path)
        if agents_path not in sys.path:
            sys.path.insert(0, agents_path)

        from avis_orchestrator import AvisOrchestrator

        # Force-reload agent modules to pick up file changes
        for mod_name in ['design_agent', 'compliance_agent', 'material_agent',
                          'simulation_agent', 'knowledge_agent', 'general_agent', 'avis_orchestrator']:
            if mod_name in sys.modules:
                importlib.reload(sys.modules[mod_name])

        from design_agent import DesignAgent
        from compliance_agent import ComplianceAgent
        from material_agent import MaterialAgent
        from simulation_agent import SimulationAgent
        from knowledge_agent import KnowledgeAgent
        from general_agent import GeneralAgent

        orch = AvisOrchestrator(skills_dir=skills_path)
        orch.register_agent('design', DesignAgent())
        orch.register_agent('compliance', ComplianceAgent())
        orch.register_agent('material', MaterialAgent())
        orch.register_agent('simulation', SimulationAgent())
        orch.register_agent('knowledge', KnowledgeAgent())
        orch.register_agent('general', GeneralAgent())

        _orchestrator = orch
        n = len(orch.agent_pool)
        names = ', '.join(orch.registry.AGENTS[a]['name'] for a in orch.agent_pool)
        print(f"[Avis] Orchestrator initialized with {n} agents: {names}")
        return _orchestrator

    except Exception as e:
        traceback.print_exc()
        print(f"[Avis] Failed to init orchestrator: {e}")
        return None


def _clean_response(obj):
    """Clean Infinity/NaN for JSON serialization."""
    import math
    if isinstance(obj, dict):
        return {k: _clean_response(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_response(v) for v in obj]
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
    return obj


# ============================================================
# Chat
# ============================================================

@avis_bp.route('/api/avis/chat', methods=['POST'])
def avis_chat():
    orch = _get_orchestrator()
    if not orch:
        return jsonify({'error': 'Orchestrator not available'}), 503

    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    session_id = data.get('session_id', '')

    if not message:
        return jsonify({'error': 'message is required'}), 400

    try:
        result = orch.process(message, session_id=session_id)

        system_msg = result.get('system_message', '')
        agents = result.get('agents', [])

        response_text = ''
        if result.get('response'):
            response_text = result['response']
        elif result.get('plan', {}).get('summary'):
            response_text = result['plan']['summary']

        welcome_text = (
            "### Avis 阀门智能体\n"
            "- @设计大师: 阀门方案设计与优化\n"
            "- @标准官: 标准合规检查\n"
            "- @材料专家: 材料推荐与选型\n"
            "- @仿真专家: CFD/FEM 仿真验证\n\n"
            "请描述您的工程需求，或 @ 特定专家。"
        )

        return jsonify(_clean_response({
            'success': True,
            'response': response_text or welcome_text,
            'agents': agents,
            'intent': result.get('intent', {}),
            'plan': result.get('plan', {}),
            'context_summary': result.get('context_summary', {}),
            'execution_time_ms': result.get('execution_time_ms', 0),
            'session_id': result.get('session_id', ''),
        }))

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================================
# Sessions
# ============================================================

@avis_bp.route('/api/avis/session', methods=['POST'])
def avis_create_session():
    orch = _get_orchestrator()
    if not orch:
        return jsonify({'error': 'Orchestrator not available'}), 503
    try:
        sess_id = orch.create_session()
        return jsonify({'session_id': sess_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/session/<session_id>', methods=['GET'])
def avis_get_session(session_id):
    orch = _get_orchestrator()
    if not orch:
        return jsonify({'error': 'Orchestrator not available'}), 503
    try:
        info = orch.get_session(session_id)
        if not info:
            return jsonify({'error': 'session not found'}), 404
        return jsonify(_clean_response(info))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# Agents
# ============================================================

@avis_bp.route('/api/avis/agents', methods=['GET'])
def avis_list_agents():
    orch = _get_orchestrator()
    if not orch:
        return jsonify({'agents': []})
    agents = []
    for aid, ag in orch.agent_pool.items():
        agents.append({
            'id': aid,
            'name': getattr(ag, 'name', aid),
            'icon': getattr(ag, 'icon', ''),
            'description': getattr(ag, 'description', ''),
        })
    return jsonify({'agents': agents})


@avis_bp.route('/api/avis/agent/<agent_id>', methods=['POST'])
def avis_agent_call(agent_id):
    orch = _get_orchestrator()
    if not orch:
        return jsonify({'error': 'Orchestrator not available'}), 503
    if agent_id not in orch.agent_pool:
        return jsonify({'error': f'agent {agent_id} not found'}), 404

    data = request.get_json(silent=True) or {}
    message = data.get('message', '')

    try:
        agent = orch.agent_pool[agent_id]
        intent = orch.intent_parser.parse(message)
        session = orch.sessions.create('Engineer')
        result = agent.execute(
            message=message,
            intent=intent,
            session=session,
            context={}
        )
        return jsonify(_clean_response({
            'agent': agent_id,
            'success': result.get('success', False),
            'response': result.get('response', ''),
            'steps': result.get('steps', []),
            'params': result.get('params', {}),
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# Health
# ============================================================

@avis_bp.route('/api/avis/health', methods=['GET'])
def avis_health():
    orch = _get_orchestrator()
    return jsonify({
        'status': 'ok' if orch else 'degraded',
        'agents': list(orch.agent_pool.keys()) if orch else [],
        'memory': {
            'enabled': orch.memory is not None if orch else False,
        },
    })


@avis_bp.route('/api/avis/debug-intent', methods=['GET'])
def debug_intent():
    """Debug route: test intent parsing with query param ?msg=xxx"""
    orch = _get_orchestrator()
    msg = request.args.get('msg', '推荐液氧阀门的阀体材料')
    from avis_orchestrator import IntentParser
    intent = IntentParser.parse(msg)
    return jsonify({
        'msg': msg,
        'intent': intent,
        'intents_keys': list(IntentParser.INTENTS.keys()),
        'material_keywords': IntentParser.INTENTS.get('material_query', {}).get('keywords', []),
    })


# ============================================================
# LLM Service API
# ============================================================

@avis_bp.route('/api/avis/llm/status', methods=['GET'])
def llm_status():
    """Get LLM service status, model, costs, call statistics, and agent types."""
    try:
        from core.llm_service import get_llm_service
        svc = get_llm_service()
        stats = svc.get_stats()

        # Build agent type list with status
        agent_types = ['design', 'compliance', 'material', 'simulation', 'knowledge', 'general']
        agents = []
        for at in agent_types:
            agents.append({
                'type': at,
                'enabled': stats.get('enabled', False),
            })

        # Try to get base_url from client if available
        base_url = ''
        if hasattr(svc, '_client') and svc._client:
            base_url = getattr(svc._client, 'base_url', '')

        return jsonify(_clean_response({
            'enabled': stats.get('enabled', False),
            'model': stats.get('model', 'unknown'),
            'base_url': base_url,
            'calls': stats.get('calls', 0),
            'successes': stats.get('successes', 0),
            'failures': stats.get('failures', 0),
            'total_cost': stats.get('total_cost', 0.0),
            'total_latency_ms': stats.get('total_latency_ms', 0),
            'avg_latency_ms': stats.get('avg_latency_ms', 0),
            'last_call': stats.get('last_call'),
            'session_spend': stats.get('session_spend', 0),
            'session_budget': stats.get('session_budget', 0),
            'agents': agents,
        }))
    except Exception as e:
        traceback.print_exc()
        return jsonify({'enabled': False, 'error': str(e)}), 500


@avis_bp.route('/api/avis/llm/test', methods=['POST'])
def llm_test():
    """Test LLM connectivity by sending a simple message."""
    try:
        from core.llm_service import get_llm_service
        svc = get_llm_service()
        if not svc.enabled:
            return jsonify({'success': False, 'error': 'LLM service is disabled', 'response': ''})
        data = request.get_json(silent=True) or {}
        test_msg = data.get('message', 'Hello. Please reply in Chinese with: Hello, I am Avis Platform LLM Service.')
        result = svc._call(
            system='You are a helpful assistant. Please reply concisely in Chinese.',
            user=test_msg,
            temperature=0.3,
            max_tokens=200
        )
        return jsonify({
            'success': result.get('success', False),
            'response': result.get('text', ''),
            'latency_ms': result.get('latency_ms', 0),
            'cost_usd': result.get('cost_usd', 0),
            'model': svc.model,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'response': ''})


@avis_bp.route('/api/avis/llm/reset-budget', methods=['POST'])
def llm_reset_budget():
    """Reset the LLM spending budget."""
    try:
        from core.llm_service import get_llm_service
        svc = get_llm_service()
        svc.reset_budget()
        stats = svc.get_stats()
        return jsonify({
            'success': True,
            'message': 'Budget has been reset',
            'session_spend': stats.get('session_spend', 0),
            'session_budget': stats.get('session_budget', 0),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================
# Memory System API
# ============================================================

def _get_mem():
    orch = _get_orchestrator()
    if not orch or not orch.memory:
        return None
    return orch.memory


@avis_bp.route('/api/avis/memory/snapshots', methods=['GET'])
def memory_snapshots():
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    try:
        snaps = mem.snapshot_manager.list_snapshots()
        return jsonify({'snapshots': snaps, 'count': len(snaps)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/snapshots/search', methods=['GET'])
def memory_search_snapshots():
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    q = request.args.get('q', '')
    try:
        results = mem.snapshot_manager.search(q)
        return jsonify({'results': results, 'query': q})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/snapshots/<snap_id>', methods=['GET'])
def memory_get_snapshot(snap_id):
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    try:
        snap = mem.snapshot_manager.get_snapshot(snap_id)
        if not snap:
            return jsonify({'error': 'snapshot not found'}), 404
        return jsonify(_clean_response(snap))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/snapshots/diff', methods=['POST'])
def memory_diff_snapshots():
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    data = request.get_json(silent=True) or {}
    id_a = data.get('id_a', '')
    id_b = data.get('id_b', '')
    if not id_a or not id_b:
        return jsonify({'error': 'id_a and id_b required'}), 400
    try:
        diff = mem.snapshot_manager.diff(id_a, id_b)
        return jsonify(_clean_response(diff))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/experiences', methods=['GET'])
def memory_experiences():
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    try:
        exps = mem.experience_index.list_experiences()
        return jsonify({'experiences': exps, 'count': len(exps)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/experiences/patterns', methods=['GET'])
def memory_experience_patterns():
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    try:
        patterns = mem.experience_index.get_patterns()
        return jsonify({'patterns': patterns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/experiences/export', methods=['GET'])
def memory_export_report():
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    try:
        report = mem.experience_index.export_report()
        return jsonify({'report': report, 'format': 'markdown'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/feedback', methods=['GET'])
def memory_get_feedback():
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    try:
        fb = mem.get_skill_feedback()
        return jsonify({'feedback': fb})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/feedback', methods=['POST'])
def memory_post_feedback():
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    data = request.get_json(silent=True) or {}
    skill_name = data.get('skill', '')
    issue = data.get('issue', '')
    suggestion = data.get('suggestion', '')
    if not skill_name or not issue:
        return jsonify({'error': 'skill and issue required'}), 400
    try:
        result = mem.apply_skill_feedback(skill_name, issue, suggestion)
        return jsonify({'feedback': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/archives', methods=['GET'])
def memory_list_archives():
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    try:
        archives = mem.list_archives()
        return jsonify({'archives': archives, 'count': len(archives)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/archives/<session_id>', methods=['POST'])
def memory_archive_session(session_id):
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    try:
        archive = mem.archive_session(session_id)
        return jsonify({'archive': _clean_response(archive)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/memory/archives/<session_id>', methods=['GET'])
def memory_get_archive(session_id):
    mem = _get_mem()
    if not mem:
        return jsonify({'error': 'memory system not available'}), 503
    try:
        archive = mem.get_archive(session_id)
        if not archive:
            return jsonify({'error': 'Archive not found'}), 404
        return jsonify({'archive': _clean_response(archive)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# Admin
# ============================================================

@avis_bp.route('/api/avis/admin/reload', methods=['POST'])
def admin_reload():
    global _orchestrator
    _orchestrator = None
    orch = _get_orchestrator()
    if orch:
        mem_enabled = orch.memory is not None
        return jsonify({
            'status': 'reloaded',
            'agents': list(orch.agent_pool.keys()),
            'memory_enabled': mem_enabled,
        })
    return jsonify({'status': 'failed'}), 500


# ============================================================
# Multi-Department Collaboration API
# ============================================================

def _collab_engine():
    """Lazy init collaboration engine."""
    from collab_engine import get_collab_engine
    return get_collab_engine()


@avis_bp.route('/api/avis/departments', methods=['GET'])
def list_departments():
    """List all departments with agent counts."""
    from departments import get_all_agents
    dept_summary = _collab_engine().get_department_summary()
    return jsonify({
        'departments': dept_summary,
        'total_agents': len(get_all_agents(flat=True))
    })


@avis_bp.route('/api/avis/departments/<dept_id>', methods=['GET'])
def get_department_detail(dept_id):
    """Get a single department with its agents."""
    from departments import get_department
    dept = get_department(dept_id)
    if not dept:
        return jsonify({'error': 'department not found'}), 404
    return jsonify(dept)


@avis_bp.route('/api/avis/agents-list', methods=['GET'])
def list_agents():
    """List all agents across departments with workload."""
    agents = _collab_engine().get_active_agents()
    return jsonify({'agents': agents})


@avis_bp.route('/api/avis/agents/<agent_id>', methods=['GET'])
def get_agent_detail(agent_id):
    """Get agent detail with workload."""
    result = _collab_engine().get_agent_workload(agent_id)
    if 'error' in result:
        return jsonify(result), 404
    return jsonify(result)


@avis_bp.route('/api/avis/workflows', methods=['GET'])
def list_workflows():
    """List all available collaboration workflows."""
    from departments import get_workflows
    return jsonify({'workflows': get_workflows()})


@avis_bp.route('/api/avis/workflows/<wf_id>', methods=['GET'])
def get_workflow_detail(wf_id):
    """Get full workflow with stages."""
    from departments import get_workflow
    wf = get_workflow(wf_id)
    if not wf:
        return jsonify({'error': 'workflow not found'}), 404
    return jsonify(wf)


@avis_bp.route('/api/avis/collab/runs', methods=['GET'])
def list_collab_runs():
    """List all collaboration runs."""
    status = request.args.get('status')
    runs = _collab_engine().get_all_runs(status=status)
    return jsonify({'runs': runs, 'count': len(runs)})


@avis_bp.route('/api/avis/collab/runs', methods=['POST'])
def create_collab_run():
    """Create a new collaboration run."""
    data = request.get_json(silent=True) or {}
    workflow_id = data.get('workflow_id', '')
    task = data.get('task', '')
    if not workflow_id or not task:
        return jsonify({'error': 'workflow_id and task required'}), 400

    result = _collab_engine().create_run(workflow_id, task)
    if result is None:
        return jsonify({'error': 'invalid workflow_id'}), 400
    return jsonify(result)


@avis_bp.route('/api/avis/collab/runs/<run_id>', methods=['GET'])
def get_collab_run(run_id):
    """Get a collaboration run detail."""
    result = _collab_engine().get_run(run_id)
    if result is None:
        return jsonify({'error': 'run not found'}), 404
    return jsonify(result)


@avis_bp.route('/api/avis/collab/runs/<run_id>/advance', methods=['POST'])
def advance_collab_run(run_id):
    """Advance a run to the next stage."""
    data = request.get_json(silent=True) or {}
    result_data = data.get('result')
    notes = data.get('notes', '')
    ok, info = _collab_engine().advance_run(run_id, result_data, notes)
    if not ok:
        return jsonify(info), 400
    return jsonify(info)


@avis_bp.route('/api/avis/collab/runs/<run_id>/approve', methods=['POST'])
def approve_collab_run(run_id):
    """Approve current review gate."""
    data = request.get_json(silent=True) or {}
    reviewer = data.get('reviewer', '总设计师')
    notes = data.get('notes', '')
    ok, info = _collab_engine().approve_run(run_id, reviewer, notes)
    if not ok:
        return jsonify(info), 400
    return jsonify(info)


@avis_bp.route('/api/avis/collab/runs/<run_id>/reject', methods=['POST'])
def reject_collab_run(run_id):
    """Reject current review and send back for rework."""
    data = request.get_json(silent=True) or {}
    reviewer = data.get('reviewer', '总设计师')
    reason = data.get('reason', '')
    ok, info = _collab_engine().reject_run(run_id, reviewer, reason)
    if not ok:
        return jsonify(info), 400
    return jsonify(info)


@avis_bp.route('/api/avis/collab/route', methods=['POST'])
def route_task():
    """Analyze and route a task to best workflow/department."""
    data = request.get_json(silent=True) or {}
    task = data.get('task', '')
    if not task:
        return jsonify({'error': 'task required'}), 400
    result = _collab_engine().route_task(task)
    return jsonify(result)


@avis_bp.route('/api/avis/org-chart', methods=['GET'])
def org_chart():
    """Get organization chart data for visualization."""
    _get_orchestrator()  # Ensure sys.path includes avis-platform/core
    from departments import DEPARTMENTS
    chart = {
        'name': '航空航天阀门研发中心',
        'name_en': 'Aerospace Valve R&D Center',
        'departments': [
            {
                'id': dept_id,
                'name': d['name'],
                'name_en': d['name_en'],
                'code': d['code'],
                'color': d['color'],
                'icon': d['icon'],
                'agents': [
                    {
                        'id': a['id'],
                        'name': a['name'],
                        'icon': a['icon'],
                        'rank': a['rank'],
                        'specialties': a['specialties'][:3]
                    }
                    for a in d['agents']
                ]
            }
            for dept_id, d in DEPARTMENTS.items()
        ]
    }
    return jsonify(chart)


# ============================================================
# Project Management API
# ============================================================

def _pm():
    """Lazy init ProjectManager."""
    from project_manager import get_project_manager
    return get_project_manager()


# ---- Dashboard ----

@avis_bp.route('/api/avis/pm/dashboard', methods=['GET'])
def pm_dashboard():
    """Get PM dashboard with stats, risks, reviews, templates."""
    try:
        return jsonify(_pm().get_dashboard())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- Templates ----

@avis_bp.route('/api/avis/pm/templates', methods=['GET'])
def pm_list_templates():
    """List available project templates."""
    from project_manager import AEROSPACE_VALVE_PROJECT_TEMPLATES
    return jsonify({'templates': [
        {'id': tid, 'name': t['name'], 'name_en': t.get('name_en', ''),
         'description': t['description'], 'trl_target': t.get('trl_target', 6),
         'milestone_count': len(t.get('milestones', []))}
        for tid, t in AEROSPACE_VALVE_PROJECT_TEMPLATES.items()
    ]})


@avis_bp.route('/api/avis/pm/templates/<template_id>', methods=['GET'])
def pm_get_template(template_id):
    """Get template detail with milestones and tasks."""
    from project_manager import AEROSPACE_VALVE_PROJECT_TEMPLATES
    tmpl = AEROSPACE_VALVE_PROJECT_TEMPLATES.get(template_id)
    if not tmpl:
        return jsonify({'error': 'template not found'}), 404
    return jsonify(tmpl)


# ---- Projects CRUD ----

@avis_bp.route('/api/avis/pm/projects', methods=['GET'])
def pm_list_projects():
    """List projects with optional filters."""
    status = request.args.get('status')
    priority = request.args.get('priority')
    search = request.args.get('search', '')
    limit = int(request.args.get('limit', 50))
    try:
        projects = _pm().list_projects(status=status, priority=priority, search=search, limit=limit)
        return jsonify({'projects': projects, 'count': len(projects)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/pm/projects', methods=['POST'])
def pm_create_project():
    """Create a new project (optionally from template)."""
    data = request.get_json(silent=True) or {}
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    try:
        project = _pm().create_project(data)
        return jsonify(project.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/pm/projects/<project_id>', methods=['GET'])
def pm_get_project(project_id):
    """Get project full detail with milestones, tasks, reviews, risks."""
    proj = _pm().get_project(project_id)
    if not proj:
        return jsonify({'error': 'project not found'}), 404
    return jsonify(proj.to_dict())


@avis_bp.route('/api/avis/pm/projects/<project_id>', methods=['PUT'])
def pm_update_project(project_id):
    """Update project fields."""
    data = request.get_json(silent=True) or {}
    proj = _pm().update_project(project_id, data)
    if not proj:
        return jsonify({'error': 'project not found'}), 404
    return jsonify(proj.to_dict())


@avis_bp.route('/api/avis/pm/projects/<project_id>', methods=['DELETE'])
def pm_delete_project(project_id):
    """Delete a project."""
    ok = _pm().delete_project(project_id)
    if not ok:
        return jsonify({'error': 'project not found'}), 404
    return jsonify({'deleted': True})


# ---- Project Advancement ----

@avis_bp.route('/api/avis/pm/projects/<project_id>/advance', methods=['POST'])
def pm_advance_project(project_id):
    """Advance project status."""
    ok, info = _pm().advance_project(project_id)
    if not ok:
        return jsonify(info), 400
    return jsonify(info)


# ---- Milestones ----

@avis_bp.route('/api/avis/pm/projects/<project_id>/milestones', methods=['POST'])
def pm_create_milestone(project_id):
    """Add a milestone to a project."""
    data = request.get_json(silent=True) or {}
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    ms = _pm().add_milestone(project_id, data)
    if not ms:
        return jsonify({'error': 'project not found'}), 404
    return jsonify(ms.to_dict()), 201


@avis_bp.route('/api/avis/pm/projects/<project_id>/milestones/<milestone_id>', methods=['PUT'])
def pm_update_milestone(project_id, milestone_id):
    """Update a milestone."""
    data = request.get_json(silent=True) or {}
    ms = _pm().update_milestone(project_id, milestone_id, data)
    if not ms:
        return jsonify({'error': 'milestone not found'}), 404
    return jsonify(ms.to_dict())


@avis_bp.route('/api/avis/pm/projects/<project_id>/milestones/<milestone_id>', methods=['DELETE'])
def pm_delete_milestone(project_id, milestone_id):
    """Delete a milestone."""
    ok = _pm().delete_milestone(project_id, milestone_id)
    if not ok:
        return jsonify({'error': 'milestone not found'}), 404
    return jsonify({'deleted': True})


@avis_bp.route('/api/avis/pm/projects/<project_id>/milestones/<milestone_id>/advance', methods=['POST'])
def pm_advance_milestone(project_id, milestone_id):
    """Advance milestone to next status (with review gate check)."""
    ok, info = _pm().advance_milestone(project_id, milestone_id)
    if not ok:
        return jsonify(info), 400
    return jsonify(info)


# ---- Tasks ----

@avis_bp.route('/api/avis/pm/projects/<project_id>/milestones/<milestone_id>/tasks', methods=['POST'])
def pm_create_task(project_id, milestone_id):
    """Add a task to a milestone."""
    data = request.get_json(silent=True) or {}
    if not data.get('title'):
        return jsonify({'error': 'title is required'}), 400
    task = _pm().add_task(project_id, milestone_id, data)
    if not task:
        return jsonify({'error': 'project or milestone not found'}), 404
    return jsonify(task.to_dict()), 201


@avis_bp.route('/api/avis/pm/projects/<project_id>/tasks/<task_id>', methods=['PUT'])
def pm_update_task(project_id, task_id):
    """Update a task (status, assignment, etc)."""
    data = request.get_json(silent=True) or {}
    task = _pm().update_task(project_id, task_id, data)
    if not task:
        return jsonify({'error': 'task not found'}), 404
    return jsonify(task.to_dict())


@avis_bp.route('/api/avis/pm/projects/<project_id>/tasks/<task_id>', methods=['DELETE'])
def pm_delete_task(project_id, task_id):
    """Delete a task."""
    ok = _pm().delete_task(project_id, task_id)
    if not ok:
        return jsonify({'error': 'task not found'}), 404
    return jsonify({'deleted': True})


# ---- Reviews ----

@avis_bp.route('/api/avis/pm/projects/<project_id>/reviews', methods=['POST'])
def pm_create_review(project_id):
    """Create a design review."""
    data = request.get_json(silent=True) or {}
    review = _pm().create_review(project_id, data)
    if not review:
        return jsonify({'error': 'project not found'}), 404
    return jsonify(review.to_dict()), 201


@avis_bp.route('/api/avis/pm/projects/<project_id>/reviews/<review_id>', methods=['PUT'])
def pm_update_review(project_id, review_id):
    """Update review status (pass/fail)."""
    data = request.get_json(silent=True) or {}
    review = _pm().update_review(project_id, review_id, data)
    if not review:
        return jsonify({'error': 'review not found'}), 404
    return jsonify(review.to_dict())


# ---- Risks ----

@avis_bp.route('/api/avis/pm/projects/<project_id>/risks', methods=['POST'])
def pm_create_risk(project_id):
    """Create a risk item."""
    data = request.get_json(silent=True) or {}
    risk = _pm().create_risk(project_id, data)
    if not risk:
        return jsonify({'error': 'project not found'}), 404
    return jsonify(risk.to_dict()), 201


@avis_bp.route('/api/avis/pm/projects/<project_id>/risks/<risk_id>', methods=['PUT'])
def pm_update_risk(project_id, risk_id):
    """Update risk status/mitigation."""
    data = request.get_json(silent=True) or {}
    risk = _pm().update_risk(project_id, risk_id, data)
    if not risk:
        return jsonify({'error': 'risk not found'}), 404
    return jsonify(risk.to_dict())


# ---- Team Assignment ----

@avis_bp.route('/api/avis/pm/projects/<project_id>/team', methods=['POST'])
def pm_assign_team(project_id):
    """Assign agents to project by department."""
    data = request.get_json(silent=True) or {}
    dept_code = data.get('dept_code', '')
    agent_ids = data.get('agent_ids', [])
    if not dept_code:
        return jsonify({'error': 'dept_code required'}), 400
    ok = _pm().assign_team(project_id, dept_code, agent_ids)
    if not ok:
        return jsonify({'error': 'project not found'}), 404
    proj = _pm().get_project(project_id)
    return jsonify({'team': proj.to_dict()['team']})


# ---- Gantt ----

@avis_bp.route('/api/avis/pm/projects/<project_id>/gantt', methods=['GET'])
def pm_gantt(project_id):
    """Get Gantt chart data for a project."""
    result = _pm().get_gantt_data(project_id)
    if not result:
        return jsonify({'error': 'project not found'}), 404
    return jsonify(result)


# ---- TRL Reference ----

@avis_bp.route('/api/avis/pm/trl', methods=['GET'])
def pm_trl_reference():
    """Get TRL level definitions."""
    from project_manager import TRL_LEVELS, REVIEW_GATES
    return jsonify({
        'trl_levels': [{'level': k, 'description': v} for k, v in TRL_LEVELS.items()],
        'review_gates': [
            {'code': k, 'name': v['name'], 'en': v['en'], 'phase': v['phase'], 'order': v['order']}
            for k, v in REVIEW_GATES.items()
        ],
    })


# ============================================================
# SSE Streaming Endpoints
# ============================================================

@avis_bp.route('/chat/stream', methods=['GET'])
def chat_stream():
    """GET /chat/stream?session_id=xxx -- SSE streaming chat.

    Client connects via EventSource:
        const es = new EventSource('/chat/stream?session_id=' + sid);
        es.onmessage = (e) => { const data = JSON.parse(e.data); ... };
    """
    session_id = request.args.get('session_id', '')
    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    try:
        from avis_platform.core.sse_engine import sse_manager
    except ImportError:
        # Fallback: direct import from project root
        _root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'avis-platform')
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from core.sse_engine import sse_manager

    stream = sse_manager.create_stream(session_id)

    def generate():
        try:
            for event_text in stream:
                yield event_text
        except GeneratorExit:
            sse_manager.close_stream(session_id)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
            'Access-Control-Allow-Origin': '*'
        }
    )


@avis_bp.route('/chat/stream/send', methods=['POST'])
def chat_stream_send():
    """POST /chat/stream/send -- push an event to an SSE stream.

    Body: {"session_id": "xxx", "text": "user message", "stream": true}
    The orchestrator processes the message and pushes events to the stream.
    """
    data = request.get_json() or {}
    session_id = data.get('session_id', '')
    text = data.get('text', '')

    if not session_id or not text:
        return jsonify({"error": "session_id and text required"}), 400

    # Get or create stream
    try:
        from avis_platform.core.sse_engine import sse_manager
    except ImportError:
        _root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'avis-platform')
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from core.sse_engine import sse_manager

    stream = sse_manager.get_stream(session_id)
    if not stream:
        stream = sse_manager.create_stream(session_id)

    # Get orchestrator
    orchestrator = _get_orchestrator()

    # Process in background thread to not block the HTTP response
    def process_and_stream():
        try:
            # Send thinking event
            stream.send({"type": "thinking", "message": "Analyzing..."}, event="status")

            # Process message
            result = orchestrator.process(text, session_id=session_id)

            # Stream chunks of the response
            if result.get('response'):
                # Split response into sentences for streaming effect
                sentences = result['response'].replace('\u3002', '\u3002|||').replace('. ', '.|||').split('|||')
                for i, sentence in enumerate(sentences):
                    if sentence.strip():
                        stream.send({
                            "type": "chunk",
                            "index": i,
                            "content": sentence.strip(),
                            "agent": result.get('agent', {}).get('name', 'unknown')
                        }, event="chunk")

            # Send final result
            stream.send({
                "type": "complete",
                "result": result
            }, event="complete")

        except Exception as e:
            stream.send({
                "type": "error",
                "message": str(e)
            }, event="error")
        finally:
            stream.send({"type": "done"}, event="done")

    threading.Thread(target=process_and_stream, daemon=True).start()

    return jsonify({"status": "accepted", "session_id": session_id})


@avis_bp.route('/chat/stream/close', methods=['POST'])
def chat_stream_close():
    """POST /chat/stream/close -- close an SSE stream."""
    data = request.get_json() or {}
    session_id = data.get('session_id', '')

    try:
        from avis_platform.core.sse_engine import sse_manager
    except ImportError:
        _root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'avis-platform')
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from core.sse_engine import sse_manager

    sse_manager.close_stream(session_id)
    return jsonify({"status": "closed", "session_id": session_id})


@avis_bp.route('/chat/stream/status', methods=['GET'])
def chat_stream_status():
    """GET /chat/stream/status -- get active streams info."""
    try:
        from avis_platform.core.sse_engine import sse_manager
    except ImportError:
        _root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'avis-platform')
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from core.sse_engine import sse_manager

    return jsonify({
        "active_streams": len(sse_manager._streams),
        "session_ids": list(sse_manager._streams.keys())
    })


# ============================================================
# File System API
# ============================================================

_fs_manager = None


def _fs():
    global _fs_manager
    if _fs_manager is not None:
        return _fs_manager
    from file_system import WorkspaceFileManager
    _fs_manager = WorkspaceFileManager()
    return _fs_manager


@avis_bp.route('/api/avis/fs/list', methods=['GET'])
@avis_bp.route('/api/avis/fs/list/<path:path>', methods=['GET'])
def fs_list_dir(path=''):
    try:
        result = _fs().list_dir(path)
        return jsonify(_clean_response(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/fs/read/<path:path>', methods=['GET'])
def fs_read(path):
    try:
        content = _fs().read_file(path)
        return jsonify({'path': path, 'content': content})
    except FileNotFoundError:
        return jsonify({'error': 'file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/fs/write/<path:path>', methods=['POST', 'PUT'])
def fs_write(path):
    data = request.get_json(silent=True) or {}
    content = data.get('content', '')
    if not content and not data.get('allow_empty'):
        return jsonify({'error': 'content required'}), 400
    try:
        result = _fs().write_file(path, content)
        return jsonify(_clean_response(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/fs/delete/<path:path>', methods=['DELETE'])
def fs_delete(path):
    try:
        ok = _fs().delete_file(path)
        return jsonify({'deleted': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/fs/search', methods=['GET'])
def fs_search():
    pattern = request.args.get('q', '*')
    try:
        results = _fs().search_files(pattern)
        return jsonify({'results': results, 'pattern': pattern, 'count': len(results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/fs/tree', methods=['GET'])
@avis_bp.route('/api/avis/fs/tree/<path:path>', methods=['GET'])
def fs_tree(path=''):
    depth = int(request.args.get('depth', 5))
    try:
        result = _fs().get_tree(path, max_depth=depth)
        return jsonify(_clean_response(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/fs/bootstrap', methods=['GET'])
def fs_bootstrap():
    try:
        result = _fs().ensure_bootstrap()
        return jsonify(_clean_response(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/fs/daily-note', methods=['POST'])
def fs_daily_note():
    data = request.get_json(silent=True) or {}
    content = data.get('content', '')
    date_str = data.get('date', '')
    try:
        result = _fs().create_daily_note(content, date_str)
        return jsonify(_clean_response(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/fs/stats', methods=['GET'])
def fs_stats():
    try:
        stats = _fs().get_stats()
        return jsonify(_clean_response(stats))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/fs/info/<path:path>', methods=['GET'])
def fs_info(path):
    try:
        info = _fs().get_file_info(path)
        return jsonify(_clean_response(info))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# Cron Engine API
# ============================================================

_cron_scheduler = None


def _cron():
    global _cron_scheduler
    if _cron_scheduler is not None:
        return _cron_scheduler
    from cron_engine import create_scheduler
    workspace = os.path.join(_avis_root, 'memory')
    orch = _get_orchestrator()
    _cron_scheduler = create_scheduler(workspace, orch)
    return _cron_scheduler


@avis_bp.route('/api/avis/cron/jobs', methods=['GET'])
def cron_list_jobs():
    enabled_only = request.args.get('enabled', '').lower() == 'true'
    try:
        jobs = _cron().list_jobs(enabled_only=enabled_only)
        return jsonify({'jobs': jobs, 'count': len(jobs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/cron/jobs', methods=['POST'])
def cron_add_job():
    data = request.get_json(silent=True) or {}
    if not data.get('name') or not data.get('schedule') or not data.get('payload'):
        return jsonify({'error': 'name, schedule, and payload required'}), 400
    try:
        job = _cron().add_job(data)
        return jsonify(_clean_response(job.to_dict())), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/cron/jobs/<job_id>', methods=['GET'])
def cron_get_job(job_id):
    try:
        job = _cron().get_job(job_id)
        if not job:
            return jsonify({'error': 'job not found'}), 404
        return jsonify(_clean_response(job.to_dict()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/cron/jobs/<job_id>', methods=['PUT'])
def cron_update_job(job_id):
    data = request.get_json(silent=True) or {}
    try:
        job = _cron().update_job(job_id, data)
        if not job:
            return jsonify({'error': 'job not found'}), 404
        return jsonify(_clean_response(job.to_dict()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/cron/jobs/<job_id>', methods=['DELETE'])
def cron_remove_job(job_id):
    try:
        ok = _cron().remove_job(job_id)
        return jsonify({'deleted': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/cron/jobs/<job_id>/enable', methods=['POST'])
def cron_enable_job(job_id):
    try:
        ok = _cron().enable_job(job_id)
        return jsonify({'enabled': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/cron/jobs/<job_id>/disable', methods=['POST'])
def cron_disable_job(job_id):
    try:
        ok = _cron().disable_job(job_id)
        return jsonify({'disabled': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/cron/jobs/<job_id>/run', methods=['POST'])
def cron_run_job(job_id):
    try:
        result = _cron().run_job(job_id)
        return jsonify(_clean_response(result))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/cron/due', methods=['GET'])
def cron_due_jobs():
    try:
        jobs = _cron().get_due_jobs()
        return jsonify({'jobs': [j.to_dict() for j in jobs], 'count': len(jobs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/cron/history/<job_id>', methods=['GET'])
def cron_run_history(job_id):
    limit = int(request.args.get('limit', 20))
    try:
        history = _cron().get_run_history(job_id, limit=limit)
        return jsonify({'history': history, 'job_id': job_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# Expert System API
# ============================================================

_expert_advisor = None


def _expert():
    global _expert_advisor
    if _expert_advisor is not None:
        return _expert_advisor
    from expert_system import ExpertAdvisor
    _expert_advisor = ExpertAdvisor()
    return _expert_advisor


@avis_bp.route('/api/avis/expert/analyze', methods=['POST'])
def expert_analyze():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({'error': 'design context required'}), 400
    try:
        result = _expert().analyze(data)
        return jsonify(_clean_response(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/expert/safety', methods=['POST'])
def expert_safety():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({'error': 'design params required'}), 400
    try:
        result = _expert().safety_assessment(data)
        return jsonify(_clean_response(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/expert/standards', methods=['POST'])
def expert_standards():
    data = request.get_json(silent=True) or {}
    try:
        result = _expert().get_applicable_standards(data)
        return jsonify({'standards': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/expert/rules', methods=['GET'])
def expert_list_rules():
    domain = request.args.get('domain', '')
    try:
        rules = _expert().engine.list_rules(domain=domain or None)
        return jsonify({'rules': rules, 'count': len(rules)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/expert/rules/<rule_id>', methods=['GET'])
def expert_get_rule(rule_id):
    try:
        rule = _expert().engine.get_rule(rule_id)
        if not rule:
            return jsonify({'error': 'rule not found'}), 404
        return jsonify(rule.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/expert/reason', methods=['POST'])
def expert_reason():
    data = request.get_json(silent=True) or {}
    facts = data.get('facts', {})
    domain = data.get('domain', None)
    try:
        result = _expert().engine.reason(facts, domain=domain)
        return jsonify(_clean_response(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# Event Bus API
# ============================================================

@avis_bp.route('/api/avis/events/publish', methods=['POST'])
def event_publish():
    """POST /api/avis/events/publish - publish an event."""
    data = request.get_json(silent=True) or {}
    topic = data.get('topic', '')
    event_data = data.get('data', {})
    source = data.get('source', 'api')
    priority = data.get('priority', 0)

    if not topic:
        return jsonify({"error": "topic required"}), 400

    from avis_platform.core.event_bus import event_bus
    event = event_bus.publish(topic, event_data, source_agent=source, priority=priority)

    return jsonify({
        "status": "published",
        "event": event.to_dict()
    })


@avis_bp.route('/api/avis/events/subscribe', methods=['POST'])
def event_subscribe():
    """POST /api/avis/events/subscribe - subscribe to a topic."""
    data = request.get_json(silent=True) or {}
    agent_id = data.get('agent_id', '')
    topic = data.get('topic', '')
    handler_name = data.get('handler', 'default_handler')

    if not agent_id or not topic:
        return jsonify({"error": "agent_id and topic required"}), 400

    from avis_platform.core.event_bus import event_bus
    sub = event_bus.subscribe(agent_id, topic, handler_name)

    return jsonify({
        "status": "subscribed",
        "subscription": {
            "id": sub.id,
            "agent_id": sub.agent_id,
            "topic": sub.topic
        }
    })


@avis_bp.route('/api/avis/events/unsubscribe', methods=['POST'])
def event_unsubscribe():
    """POST /api/avis/events/unsubscribe - remove a subscription."""
    data = request.get_json(silent=True) or {}
    sub_id = data.get('subscription_id', '')

    if not sub_id:
        return jsonify({"error": "subscription_id required"}), 400

    from avis_platform.core.event_bus import event_bus
    ok = event_bus.unsubscribe(sub_id)

    return jsonify({"status": "unsubscribed" if ok else "not_found"})


@avis_bp.route('/api/avis/events/subscriptions', methods=['GET'])
def event_subscriptions():
    """GET /api/avis/events/subscriptions?agent_id=xxx - list subscriptions."""
    agent_id = request.args.get('agent_id', None)

    from avis_platform.core.event_bus import event_bus
    subs = event_bus.get_subscriptions(agent_id=agent_id or None)

    return jsonify({"subscriptions": subs, "count": len(subs)})


@avis_bp.route('/api/avis/events/log', methods=['GET'])
def event_log():
    """GET /api/avis/events/log?topic=xxx&source=xxx&since=xxx&limit=50 - query event log."""
    topic = request.args.get('topic', '')
    source = request.args.get('source', '')
    since = request.args.get('since', '')
    limit = request.args.get('limit', 50, type=int)

    from avis_platform.core.event_bus import event_bus

    kwargs = {"limit": limit}
    if topic:
        kwargs["topic"] = topic
    if source:
        kwargs["source"] = source
    if since:
        try:
            kwargs["since"] = float(since)
        except ValueError:
            pass

    events = event_bus.get_event_log(**kwargs)
    return jsonify({"events": events, "count": len(events)})


@avis_bp.route('/api/avis/events/stats', methods=['GET'])
def event_stats():
    """GET /api/avis/events/stats - bus statistics."""
    from avis_platform.core.event_bus import event_bus
    return jsonify(event_bus.get_stats())


@avis_bp.route('/api/avis/events/defaults/init', methods=['POST'])
def event_defaults_init():
    """POST /api/avis/events/defaults/init - initialize default subscriptions."""
    from avis_platform.core.event_bus import event_bus, DEFAULT_SUBSCRIPTIONS

    results = []
    for agent_id, topic, handler in DEFAULT_SUBSCRIPTIONS:
        sub = event_bus.subscribe(agent_id, topic, handler)
        results.append({"agent_id": agent_id, "topic": topic, "id": sub.id})

    return jsonify({
        "status": "initialized",
        "subscriptions": len(results),
        "results": results
    })


@avis_bp.route('/api/avis/events/correlated/<correlation_id>', methods=['GET'])
def event_correlated(correlation_id):
    """GET /api/avis/events/correlated/<correlation_id> - get events by correlation."""
    from avis_platform.core.event_bus import event_bus
    events = event_bus.get_correlated(correlation_id)
    return jsonify({"events": events, "count": len(events)})


# ============================================================
# Rate Limiter & Security Endpoints
# ============================================================


@avis_bp.route('/admin/ratelimit/stats', methods=['GET'])
def ratelimit_stats():
    """GET /api/avis/admin/ratelimit/stats -- rate limiter status."""
    from avis_platform.core.rate_limiter import rate_limiter as rl
    return jsonify(rl.get_stats())


@avis_bp.route('/admin/ratelimit/reset', methods=['POST'])
def ratelimit_reset():
    """POST /api/avis/admin/ratelimit/reset -- reset rate limits."""
    data = request.get_json() or {}
    ip = data.get('ip', '')

    from avis_platform.core.rate_limiter import rate_limiter as rl
    rl.reset(ip=ip or None)
    return jsonify({"status": "reset"})


# === API Key Management Endpoints ===


@avis_bp.route('/admin/apikeys/generate', methods=['POST'])
def apikey_generate():
    """POST /api/avis/admin/apikeys/generate -- generate new API key."""
    data = request.get_json() or {}
    label = data.get('label', '')
    expires_in = data.get('expires_in', None)  # seconds

    from avis_platform.core.auth_hardening import api_key_manager as akm
    raw, hashed = akm.generate_key(label=label, expires_in=expires_in)

    return jsonify({
        "api_key": raw,
        "label": label,
        "warning": "Store this key securely. It will not be shown again."
    })


@avis_bp.route('/admin/apikeys/list', methods=['GET'])
def apikey_list():
    """GET /api/avis/admin/apikeys/list -- list all API keys."""
    from avis_platform.core.auth_hardening import api_key_manager as akm
    return jsonify({"keys": akm.list_keys()})


@avis_bp.route('/admin/apikeys/revoke', methods=['POST'])
def apikey_revoke():
    """POST /api/avis/admin/apikeys/revoke -- revoke an API key."""
    data = request.get_json() or {}
    api_key = data.get('api_key', '')

    from avis_platform.core.auth_hardening import api_key_manager as akm
    ok = akm.revoke(api_key)
    return jsonify({"status": "revoked" if ok else "not_found"})


# === Security Status Endpoint ===


@avis_bp.route('/admin/security/status', methods=['GET'])
def security_status():
    """GET /api/avis/admin/security/status -- security overview."""
    import time as _time
    from avis_platform.core.rate_limiter import rate_limiter as rl
    from avis_platform.core.auth_hardening import failed_attempts as fa, api_key_manager as akm

    return jsonify({
        "rate_limiter": rl.get_stats(),
        "api_keys": len(akm.list_keys()),
        "blocked_ips": sum(1 for v in fa._blocked.values() if v > _time.time()),
        "session_timeout": 86400,  # 24h JWT
    })


# === Nudge Engine Endpoints ===

@avis_bp.route('/api/avis/nudge/analyze', methods=['POST'])
def nudge_analyze():
    """POST /api/avis/nudge/analyze - run all analyzers on provided context."""
    context = request.get_json() or {}

    from avis_platform.core.nudge_engine import nudge_engine
    nudges = nudge_engine.analyze(context)

    return jsonify({
        "status": "analyzed",
        "nudges": [n.to_dict() for n in nudges],
        "count": len(nudges)
    })


@avis_bp.route('/api/avis/nudge/list', methods=['GET'])
def nudge_list():
    """GET /api/avis/nudge/list?type=xxx&priority=xxx&agent=xxx&unread=true&limit=50"""
    nudge_type = request.args.get('type', '')
    priority = request.args.get('priority', '')
    target_agent = request.args.get('agent', '')
    unread = request.args.get('unread', '')
    limit = request.args.get('limit', 50, type=int)

    from avis_platform.core.nudge_engine import nudge_engine

    kwargs = {"limit": limit}
    if nudge_type:
        kwargs["nudge_type"] = nudge_type
    if priority:
        kwargs["priority"] = priority
    if target_agent:
        kwargs["target_agent"] = target_agent
    if unread == 'true':
        kwargs["acknowledged"] = False
        kwargs["dismissed"] = False

    nudges = nudge_engine.get_nudges(**kwargs)
    return jsonify({"nudges": nudges, "count": len(nudges)})


@avis_bp.route('/api/avis/nudge/acknowledge', methods=['POST'])
def nudge_acknowledge():
    """POST /api/avis/nudge/acknowledge - acknowledge one or all nudges."""
    data = request.get_json() or {}
    nudge_id = data.get('nudge_id', '')
    all_nudges = data.get('all', False)
    target_agent = data.get('agent', '')

    from avis_platform.core.nudge_engine import nudge_engine

    if all_nudges:
        nudge_engine.acknowledge_all(target_agent=target_agent or None)
        return jsonify({"status": "all_acknowledged"})
    elif nudge_id:
        ok = nudge_engine.acknowledge(nudge_id)
        return jsonify({"status": "acknowledged" if ok else "not_found"})
    else:
        return jsonify({"error": "nudge_id or all=true required"}), 400


@avis_bp.route('/api/avis/nudge/dismiss', methods=['POST'])
def nudge_dismiss():
    """POST /api/avis/nudge/dismiss - dismiss a nudge."""
    data = request.get_json() or {}
    nudge_id = data.get('nudge_id', '')

    if not nudge_id:
        return jsonify({"error": "nudge_id required"}), 400

    from avis_platform.core.nudge_engine import nudge_engine
    ok = nudge_engine.dismiss(nudge_id)
    return jsonify({"status": "dismissed" if ok else "not_found"})


@avis_bp.route('/api/avis/nudge/stats', methods=['GET'])
def nudge_stats():
    """GET /api/avis/nudge/stats - engine statistics."""
    from avis_platform.core.nudge_engine import nudge_engine
    return jsonify(nudge_engine.get_stats())


# === API Documentation Endpoints ===

@avis_bp.route('/docs', methods=['GET'])
def api_docs_ui():
    """GET /api/avis/docs — Swagger UI for API documentation."""
    from avis_platform.core.api_docs import SWAGGER_UI_HTML
    return SWAGGER_UI_HTML, 200, {'Content-Type': 'text/html; charset=utf-8'}


@avis_bp.route('/docs/openapi.json', methods=['GET'])
def api_docs_json():
    """GET /api/avis/docs/openapi.json — OpenAPI 3.0 specification."""
    from avis_platform.core.api_docs import create_spec_for_avis

    spec = create_spec_for_avis(avis_bp)
    return jsonify(spec)


# ============================================================
# Product Structure Library API (13 endpoints)
# ============================================================

@avis_bp.route('/api/avis/ps/stats', methods=['GET'])
def ps_stats():
    """GET /api/avis/ps/stats - product structure statistics."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    return jsonify(ps.get_stats())


@avis_bp.route('/api/avis/ps/search', methods=['GET'])
def ps_search():
    """GET /api/avis/ps/search?q=query - search across all entities."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    q = request.args.get('q', '')
    return jsonify(ps.search(q) if q else {"series": [], "models": [], "assemblies": [], "components": []})


# --- Series CRUD ---

@avis_bp.route('/api/avis/ps/series', methods=['GET'])
def ps_list_series():
    """GET /api/avis/ps/series - list all product series."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    return jsonify([s.to_dict() for s in ps.list_series()])


@avis_bp.route('/api/avis/ps/series', methods=['POST'])
def ps_create_series():
    """POST /api/avis/ps/series - create a product series."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    data = request.get_json(force=True) or {}
    series = ps.create_series(
        name=data.get('name', 'New Series'),
        code=data.get('code', ''),
        valve_type=data.get('valve_type', ''),
        description=data.get('description', '')
    )
    return jsonify(series.to_dict()), 201


@avis_bp.route('/api/avis/ps/series/<sid>', methods=['GET'])
def ps_get_series(sid):
    """GET /api/avis/ps/series/<id> - get series detail."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    s = ps.get_series(sid)
    if not s:
        return jsonify({"error": "Series not found"}), 404
    return jsonify(s.to_dict())


@avis_bp.route('/api/avis/ps/series/<sid>', methods=['PUT'])
def ps_update_series(sid):
    """PUT /api/avis/ps/series/<id> - update a series."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    data = request.get_json(force=True) or {}
    s = ps.update_series(sid, **data)
    if not s:
        return jsonify({"error": "Series not found"}), 404
    return jsonify(s.to_dict())


@avis_bp.route('/api/avis/ps/series/<sid>', methods=['DELETE'])
def ps_delete_series(sid):
    """DELETE /api/avis/ps/series/<id> - delete a series and its models."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    if ps.delete_series(sid):
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Series not found"}), 404


# --- Model CRUD ---

@avis_bp.route('/api/avis/ps/models', methods=['GET'])
def ps_list_models():
    """GET /api/avis/ps/models?series_id=... - list models."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    sid = request.args.get('series_id', '')
    return jsonify([m.to_dict() for m in ps.list_models(sid)])


@avis_bp.route('/api/avis/ps/models', methods=['POST'])
def ps_create_model():
    """POST /api/avis/ps/models - create a product model."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    data = request.get_json(force=True) or {}
    model = ps.create_model(
        model_name=data.get('model_name', 'New Model'),
        series_id=data.get('series_id', ''),
        description=data.get('description', ''),
        fluid_type=data.get('fluid_type', ''),
        design_pressure_mpa=data.get('design_pressure_mpa', 0.0),
        design_temperature_c=data.get('design_temperature_c', 20.0),
        nominal_size=data.get('nominal_size', ''),
        connection_type=data.get('connection_type', ''),
        top_assemblies=data.get('top_assemblies', [])
    )
    return jsonify(model.to_dict()), 201


@avis_bp.route('/api/avis/ps/models/<mid>', methods=['GET'])
def ps_get_model(mid):
    """GET /api/avis/ps/models/<id> - get model detail."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    m = ps.get_model(mid)
    if not m:
        return jsonify({"error": "Model not found"}), 404
    result = m.to_dict()
    result['total_mass_kg'] = round(ps.get_total_mass(mid), 4)
    return jsonify(result)


@avis_bp.route('/api/avis/ps/models/<mid>', methods=['PUT'])
def ps_update_model(mid):
    """PUT /api/avis/ps/models/<id> - update a model."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    data = request.get_json(force=True) or {}
    m = ps.update_model(mid, **data)
    if not m:
        return jsonify({"error": "Model not found"}), 404
    return jsonify(m.to_dict())


@avis_bp.route('/api/avis/ps/models/<mid>', methods=['DELETE'])
def ps_delete_model(mid):
    """DELETE /api/avis/ps/models/<id> - delete a model."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    if ps.delete_model(mid):
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Model not found"}), 404


# --- Assembly CRUD ---

@avis_bp.route('/api/avis/ps/assemblies', methods=['GET'])
def ps_list_assemblies():
    """GET /api/avis/ps/assemblies - list all assemblies."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    return jsonify([a.to_dict() for a in ps.list_assemblies()])


@avis_bp.route('/api/avis/ps/assemblies', methods=['POST'])
def ps_create_assembly():
    """POST /api/avis/ps/assemblies - create an assembly."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    data = request.get_json(force=True) or {}
    assy = ps.create_assembly(
        name=data.get('name', 'New Assembly'),
        assembly_type=data.get('assembly_type', ''),
        description=data.get('description', '')
    )
    return jsonify(assy.to_dict()), 201


@avis_bp.route('/api/avis/ps/assemblies/<aid>', methods=['GET'])
def ps_get_assembly(aid):
    """GET /api/avis/ps/assemblies/<id> - get assembly detail."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    a = ps.get_assembly(aid)
    if not a:
        return jsonify({"error": "Assembly not found"}), 404
    return jsonify(a.to_dict())


@avis_bp.route('/api/avis/ps/assemblies/<aid>', methods=['PUT'])
def ps_update_assembly(aid):
    """PUT /api/avis/ps/assemblies/<id> - update an assembly."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    data = request.get_json(force=True) or {}
    a = ps.update_assembly(aid, **data)
    if not a:
        return jsonify({"error": "Assembly not found"}), 404
    return jsonify(a.to_dict())


@avis_bp.route('/api/avis/ps/assemblies/<aid>', methods=['DELETE'])
def ps_delete_assembly(aid):
    """DELETE /api/avis/ps/assemblies/<id> - delete an assembly."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    if ps.delete_assembly(aid):
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Assembly not found"}), 404


@avis_bp.route('/api/avis/ps/assemblies/<aid>/components', methods=['POST'])
def ps_add_component_to_assembly(aid):
    """POST /api/avis/ps/assemblies/<id>/components - add component to assembly."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    data = request.get_json(force=True) or {}
    cid = data.get('component_id', '')
    if not cid:
        return jsonify({"error": "component_id required"}), 400
    if ps.add_component_to_assembly(aid, cid):
        return jsonify({"status": "added"})
    return jsonify({"error": "Assembly or component not found"}), 404


@avis_bp.route('/api/avis/ps/assemblies/<pid>/children/<cid>', methods=['POST'])
def ps_add_child_assembly(pid, cid):
    """POST /api/avis/ps/assemblies/<parent_id>/children/<child_id> - add sub-assembly."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    if ps.add_child_assembly(pid, cid):
        return jsonify({"status": "added"})
    return jsonify({"error": "Assembly not found"}), 404


# --- Component CRUD ---

@avis_bp.route('/api/avis/ps/components', methods=['GET'])
def ps_list_components():
    """GET /api/avis/ps/components?material=...&standard=... - list components."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    material = request.args.get('material', '')
    standard = request.args.get('standard', '')
    return jsonify([c.to_dict() for c in ps.list_components(material, standard)])


@avis_bp.route('/api/avis/ps/components', methods=['POST'])
def ps_create_component():
    """POST /api/avis/ps/components - create a component."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    data = request.get_json(force=True) or {}
    comp = ps.create_component(
        name=data.get('name', 'New Component'),
        part_number=data.get('part_number', ''),
        material=data.get('material', ''),
        specification=data.get('specification', ''),
        standard=data.get('standard', ''),
        quantity_per_assembly=data.get('quantity_per_assembly', 1),
        unit=data.get('unit', 'pcs'),
        mass_kg=data.get('mass_kg', 0.0),
        supplier=data.get('supplier', ''),
        notes=data.get('notes', '')
    )
    return jsonify(comp.to_dict()), 201


@avis_bp.route('/api/avis/ps/components/<cid>', methods=['GET'])
def ps_get_component(cid):
    """GET /api/avis/ps/components/<id> - get component detail."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    c = ps.get_component(cid)
    if not c:
        return jsonify({"error": "Component not found"}), 404
    return jsonify(c.to_dict())


@avis_bp.route('/api/avis/ps/components/<cid>', methods=['PUT'])
def ps_update_component(cid):
    """PUT /api/avis/ps/components/<id> - update a component."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    data = request.get_json(force=True) or {}
    c = ps.update_component(cid, **data)
    if not c:
        return jsonify({"error": "Component not found"}), 404
    return jsonify(c.to_dict())


@avis_bp.route('/api/avis/ps/components/<cid>', methods=['DELETE'])
def ps_delete_component(cid):
    """DELETE /api/avis/ps/components/<id> - delete a component."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    if ps.delete_component(cid):
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Component not found"}), 404


# --- BOM Operations ---

@avis_bp.route('/api/avis/ps/bom/tree/<mid>', methods=['GET'])
def ps_bom_tree(mid):
    """GET /api/avis/ps/bom/tree/<model_id> - get full BOM tree."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    tree = ps.get_bom_tree(mid)
    if not tree:
        return jsonify({"error": "Model not found"}), 404
    return jsonify(tree.to_dict())


@avis_bp.route('/api/avis/ps/bom/flat/<mid>', methods=['GET'])
def ps_bom_flat(mid):
    """GET /api/avis/ps/bom/flat/<model_id> - get flat BOM list."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    model = ps.get_model(mid)
    if not model:
        return jsonify({"error": "Model not found"}), 404
    flat = ps.get_flat_bom(mid)
    total_mass = ps.get_total_mass(mid)
    return jsonify({
        "model_name": model.model_name,
        "model_id": mid,
        "total_mass_kg": round(total_mass, 4),
        "items": flat,
        "item_count": len(flat)
    })


@avis_bp.route('/api/avis/ps/bom/export/csv/<mid>', methods=['GET'])
def ps_bom_export_csv(mid):
    """GET /api/avis/ps/bom/export/csv/<model_id> - export BOM as CSV."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    model = ps.get_model(mid)
    if not model:
        return jsonify({"error": "Model not found"}), 404
    csv_data = ps.export_bom_csv(mid)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment; filename={model.model_name}_BOM.csv"}
    )


@avis_bp.route('/api/avis/ps/bom/export/json/<mid>', methods=['GET'])
def ps_bom_export_json(mid):
    """GET /api/avis/ps/bom/export/json/<model_id> - export BOM as JSON."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    tree = ps.export_bom_tree_json(mid)
    if not tree:
        return jsonify({"error": "Model not found"}), 404
    return jsonify(tree)


# --- Clone / Variant ---

@avis_bp.route('/api/avis/ps/models/<mid>/clone', methods=['POST'])
def ps_clone_model(mid):
    """POST /api/avis/ps/models/<id>/clone - clone a model as variant."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    data = request.get_json(force=True) or {}
    new_name = data.get('new_name', '')
    if not new_name:
        return jsonify({"error": "new_name required"}), 400
    cloned = ps.clone_model(mid, new_name)
    if not cloned:
        return jsonify({"error": "Source model not found"}), 404
    return jsonify(cloned.to_dict()), 201


# --- Seed Presets ---

@avis_bp.route('/api/avis/ps/seed', methods=['POST'])
def ps_seed():
    """POST /api/avis/ps/seed - seed with preset aerospace valve data."""
    from avis_platform.core.product_structure import get_product_structure
    ps = get_product_structure()
    ps.seed_presets()
    return jsonify({"status": "seeded", "stats": ps.get_stats()})


# ============================================================
# Multi-Agent Collaboration Engine API
# ============================================================

_multi_orch = None


def _multi():
    """Lazy init MultiAgentOrchestrator."""
    global _multi_orch
    if _multi_orch is not None:
        return _multi_orch
    from avis_platform.core.multi_agent_collab import get_multi_agent_orchestrator
    _multi_orch = get_multi_agent_orchestrator()
    return _multi_orch


@avis_bp.route('/api/avis/collab/create', methods=['POST'])
def collab_create():
    """POST /api/avis/collab/create - create a multi-agent collaboration task.

    Body: {"task_desc": "...", "title": "...", "force_template": "...",
           "protocol": "ORCHESTRATOR", "consensus": "expert_override"}
    """
    data = request.get_json(silent=True) or {}
    task_desc = data.get('task_desc', '').strip()
    if not task_desc:
        return jsonify({'error': 'task_desc is required'}), 400

    try:
        from avis_platform.core.multi_agent_collab import ProtocolType, ConsensusModel

        protocol = None
        if data.get('protocol'):
            try:
                protocol = ProtocolType(data['protocol'])
            except ValueError:
                pass

        consensus = None
        if data.get('consensus'):
            try:
                consensus = ConsensusModel(data['consensus'])
            except ValueError:
                pass

        result = _multi().create_collaboration(
            task_desc=task_desc,
            title=data.get('title', ''),
            force_template=data.get('force_template', ''),
            protocol=protocol,
            consensus=consensus,
            metadata=data.get('metadata', {}),
        )
        return jsonify(_clean_response(result))
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/collab/teams', methods=['GET'])
def collab_list_teams():
    """GET /api/avis/collab/teams - list all active collaboration teams."""
    try:
        teams = _multi().list_active_collaborations()
        return jsonify({'teams': teams, 'count': len(teams)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/collab/team/<team_id>', methods=['GET'])
def collab_team_status(team_id):
    """GET /api/avis/collab/team/<team_id> - get team status and task progress."""
    try:
        status = _multi().get_team_status(team_id)
        if not status:
            return jsonify({'error': 'team not found'}), 404
        return jsonify(_clean_response(status))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/collab/team/<team_id>/execute', methods=['POST'])
def collab_execute(team_id):
    """POST /api/avis/collab/team/<team_id>/execute - start executing the collaboration task."""
    try:
        result = _multi().execute_collaboration(team_id)
        if 'error' in result:
            return jsonify(result), 404 if 'not found' in result['error'] else 400
        return jsonify(_clean_response(result))
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/collab/team/<team_id>/message', methods=['POST'])
def collab_send_message(team_id):
    """POST /api/avis/collab/team/<team_id>/message - send an inter-agent message.

    Body: {"sender": "design", "receiver": "material", "content": "...", "msg_type": "request"}
    """
    data = request.get_json(silent=True) or {}
    sender = data.get('sender', '').strip()
    receiver = data.get('receiver', '').strip()
    content = data.get('content', '').strip()

    if not sender or not receiver or not content:
        return jsonify({'error': 'sender, receiver, and content are required'}), 400

    try:
        msg = _multi().send_message(
            team_id=team_id,
            sender=sender,
            receiver=receiver,
            content=content,
            msg_type=data.get('msg_type', 'info'),
        )
        if msg is None:
            return jsonify({'error': 'team not found'}), 404
        return jsonify(_clean_response(msg))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/collab/team/<team_id>', methods=['DELETE'])
def collab_cancel(team_id):
    """DELETE /api/avis/collab/team/<team_id> - cancel and remove a collaboration team."""
    try:
        ok = _multi().cancel_collaboration(team_id)
        if not ok:
            return jsonify({'error': 'team not found'}), 404
        return jsonify({'cancelled': True, 'team_id': team_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/collab/protocols', methods=['GET'])
def collab_protocols():
    """GET /api/avis/collab/protocols - list available communication protocols."""
    from avis_platform.core.multi_agent_collab import CollaborationProtocol
    return jsonify({'protocols': CollaborationProtocol.list_protocols()})


@avis_bp.route('/api/avis/collab/agents', methods=['GET'])
def collab_available_agents():
    """GET /api/avis/collab/agents - list agents available for collaboration."""
    try:
        agents = _multi().get_available_agents()
        return jsonify({'agents': agents})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/collab/templates', methods=['GET'])
def collab_templates():
    """GET /api/avis/collab/templates - list decomposition templates."""
    try:
        templates = _multi().get_decomposition_templates()
        return jsonify({'templates': templates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/collab/team/<team_id>/messages', methods=['GET'])
def collab_team_messages(team_id):
    """GET /api/avis/collab/team/<team_id>/messages - get team message log."""
    try:
        log = _multi().get_team_message_log(team_id)
        if log is None:
            return jsonify({'error': 'team not found'}), 404
        return jsonify({'messages': log, 'count': len(log)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/collab/team/<team_id>/resolve', methods=['POST'])
def collab_resolve(team_id):
    """POST /api/avis/collab/team/<team_id>/resolve - resolve a conflict.

    Body: {"issue": "...", "positions": {"design": "option A", "material": "option B"}}
    """
    data = request.get_json(silent=True) or {}
    issue = data.get('issue', '').strip()
    if not issue:
        return jsonify({'error': 'issue is required'}), 400

    try:
        result = _multi().resolve_conflict(
            team_id=team_id,
            issue=issue,
            positions=data.get('positions', {}),
        )
        if result is None:
            return jsonify({'error': 'team not found'}), 404
        return jsonify(_clean_response(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# Knowledge Graph Engine API
# ============================================================

_kg_engine = None


def _kg():
    """Lazy init KnowledgeGraphEngine."""
    global _kg_engine
    if _kg_engine is not None:
        return _kg_engine
    from avis_platform.core.knowledge_graph import get_engine
    _kg_engine = get_engine()
    # Auto-seed if empty
    if _kg_engine.graph_db.get_stats()['total_entities'] == 0:
        _kg_engine.seed_aerospace_knowledge()
    return _kg_engine


@avis_bp.route('/api/avis/kg/stats', methods=['GET'])
def kg_stats():
    """GET /api/avis/kg/stats - graph statistics."""
    try:
        stats = _kg().graph_db.get_stats()
        consistency = _kg().reasoner.validate_consistency()
        stats['consistency'] = {
            'consistent': consistency['consistent'],
            'issue_count': consistency['total_issues'],
        }
        return jsonify(stats)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/kg/entities', methods=['GET'])
def kg_entities():
    """GET /api/avis/kg/entities?type=&q= - search entities."""
    try:
        entity_type = request.args.get('type', '').strip()
        query_text = request.args.get('q', '').strip()

        if query_text:
            results = _kg().search(query_text)
            entities_list = [r['entity'] for r in results['results']]
        elif entity_type:
            entities_list = [e.to_dict() for e in
                           _kg().query.find_by_type(entity_type)]
        else:
            entities_list = [e.to_dict() for e in
                           _kg().graph_db.entities.values()]

        entities_list.sort(key=lambda e: e['name'].lower())
        return jsonify({'results': entities_list, 'count': len(entities_list)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/kg/entity/<eid>', methods=['GET'])
def kg_entity_detail(eid):
    """GET /api/avis/kg/entity/<eid> - entity detail with neighbors."""
    try:
        result = _kg().explain(eid)
        return jsonify(result)
    except EntityNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/kg/path', methods=['GET'])
def kg_path():
    """GET /api/avis/kg/path?from=<eid>&to=<eid> - find paths between entities."""
    try:
        from_id = request.args.get('from', '').strip()
        to_id = request.args.get('to', '').strip()
        if not from_id or not to_id:
            return jsonify({'error': 'from and to parameters required'}), 400

        paths = _kg().graph_db.find_path(from_id, to_id, max_depth=6)
        return jsonify({
            'paths': paths,
            'count': len(paths),
            'from': from_id,
            'to': to_id,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/kg/subgraph', methods=['GET'])
def kg_subgraph():
    """GET /api/avis/kg/subgraph?ids=<eid1,eid2>&depth=2 - extract subgraph."""
    try:
        ids_str = request.args.get('ids', '').strip()
        depth = int(request.args.get('depth', 2))
        if not ids_str:
            return jsonify({'error': 'ids parameter required'}), 400

        entity_ids = [eid.strip() for eid in ids_str.split(',') if eid.strip()]
        subgraph = _kg().graph_db.get_subgraph(entity_ids, depth=depth)
        return jsonify(subgraph)
    except ValueError:
        return jsonify({'error': 'Invalid depth parameter'}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/kg/reason', methods=['POST'])
def kg_reason():
    """POST /api/avis/kg/reason - run inference."""
    try:
        result = _kg().reasoner.apply_rules()
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/kg/compliance/<component_type>', methods=['GET'])
def kg_compliance(component_type):
    """GET /api/avis/kg/compliance/<component_type> - standards for component."""
    try:
        result = _kg().query.find_compliance_path(component_type)
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/kg/materials/<material>/alternatives', methods=['GET'])
def kg_material_alternatives(material):
    """GET /api/avis/kg/materials/<material>/alternatives - alternative materials."""
    try:
        result = _kg().query.find_alternative_materials(material)
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/kg/seed', methods=['POST'])
def kg_seed():
    """POST /api/avis/kg/seed - seed aerospace knowledge."""
    try:
        result = _kg().seed_aerospace_knowledge()
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/kg/validate', methods=['GET'])
def kg_validate():
    """GET /api/avis/kg/validate - run consistency validation."""
    try:
        result = _kg().reasoner.validate_consistency()
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================================
# Auto-Optimizer Engine API (7 endpoints)
# ============================================================

_optimizer_engine = None


def _opt_engine():
    global _optimizer_engine
    if _optimizer_engine is not None:
        return _optimizer_engine
    from avis_platform.core.auto_optimizer import get_optimizer_engine
    _optimizer_engine = get_optimizer_engine()
    return _optimizer_engine


@avis_bp.route('/api/avis/optimize/create', methods=['POST'])
def optimize_create():
    """POST /api/avis/optimize/create - create optimization problem from design type + specs.

    Body: {
        "design_type": "solenoid|spring|seal|pressure_reducing",
        "specs": {"burst_pressure_mpa": 30.0, "max_mass_kg": 5.0, ...}
    }
    """
    data = request.get_json(silent=True) or {}
    design_type = data.get('design_type', '').strip()
    if not design_type:
        return jsonify({'error': 'design_type is required'}), 400

    try:
        engine = _opt_engine()
        problem = engine.create_problem(design_type, data.get('specs', {}))
        return jsonify(_clean_response({
            'problem': problem.to_dict(),
            'design_type': design_type,
            'status': 'created',
        }))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/optimize/run', methods=['POST'])
def optimize_run():
    """POST /api/avis/optimize/run - run optimization.

    Body: {
        "problem": {...problem dict...},
        "method": "pso|ga|random|grid",
        "max_iter": 200,
        "population": 50
    }
    """
    data = request.get_json(silent=True) or {}
    problem_data = data.get('problem')
    if not problem_data:
        return jsonify({'error': 'problem dict is required'}), 400

    try:
        from avis_platform.core.auto_optimizer import OptimizationProblem
        engine = _opt_engine()

        # Reconstruct problem from dict
        problem = OptimizationProblem.from_dict(problem_data)
        # Re-attach built-in evaluator by creating fresh problem
        design_type = None
        for dt in ['solenoid', 'spring', 'seal', 'pressure_reducing']:
            from avis_platform.core.auto_optimizer import DESIGN_TYPE_TEMPLATES
            template = DESIGN_TYPE_TEMPLATES.get(dt, {})
            tvars = template.get('variables', [])
            if len(tvars) == len(problem.variables):
                if all(tv.name == pv.name for tv, pv in zip(tvars, problem.variables)):
                    design_type = dt
                    break

        if design_type:
            fresh = engine.create_problem(design_type, {})
            problem.evaluator = fresh.evaluator

        method = data.get('method', 'pso')
        max_iter = int(data.get('max_iter', 200))
        population = int(data.get('population', 50))

        run_id, result = engine.optimize(problem, method=method,
                                         max_iter=max_iter, population=population)

        return jsonify(_clean_response({
            'run_id': run_id,
            'result': result.to_dict(),
        }))
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/optimize/result/<run_id>', methods=['GET'])
def optimize_result(run_id):
    """GET /api/avis/optimize/result/<run_id> - get optimization results."""
    try:
        engine = _opt_engine()
        record = engine.get_result(run_id)
        if not record:
            return jsonify({'error': 'run not found'}), 404
        return jsonify(_clean_response({
            'run_id': run_id,
            'result': record['result'],
            'problem': record['problem'],
            'method': record.get('method'),
            'timestamp': record.get('timestamp'),
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/optimize/compare', methods=['POST'])
def optimize_compare():
    """POST /api/avis/optimize/compare - compare methods on same problem.

    Body: {
        "design_type": "spring",
        "specs": {...},
        "max_iter": 100,
        "population": 50
    }
    """
    data = request.get_json(silent=True) or {}
    design_type = data.get('design_type', '').strip()
    if not design_type:
        return jsonify({'error': 'design_type is required'}), 400

    try:
        engine = _opt_engine()
        problem = engine.create_problem(design_type, data.get('specs', {}))
        max_iter = int(data.get('max_iter', 100))
        population = int(data.get('population', 50))
        comparison = engine.compare_methods(problem, max_iter=max_iter, population=population)
        return jsonify(_clean_response(comparison))
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/optimize/history', methods=['GET'])
def optimize_history():
    """GET /api/avis/optimize/history - list past optimization runs."""
    try:
        engine = _opt_engine()
        limit = int(request.args.get('limit', 20))
        history = engine.get_history(limit=limit)
        runs = []
        for h in history:
            runs.append({
                'run_id': h.get('run_id'),
                'problem_name': h.get('problem_name'),
                'method': h.get('method'),
                'best_fitness': h.get('result', {}).get('best_fitness'),
                'feasible': h.get('result', {}).get('feasible'),
                'timestamp': h.get('timestamp'),
                'elapsed_seconds': h.get('result', {}).get('elapsed_seconds'),
            })
        return jsonify({'runs': runs, 'count': len(runs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/optimize/templates', methods=['GET'])
def optimize_templates():
    """GET /api/avis/optimize/templates - list design type templates."""
    try:
        from avis_platform.core.auto_optimizer import DESIGN_TYPE_TEMPLATES
        templates = []
        for dt_id, t in DESIGN_TYPE_TEMPLATES.items():
            templates.append({
                'id': dt_id,
                'name': t['name'],
                'description': t['description'],
                'variable_count': len(t['variables']),
                'variables': [v.to_dict() for v in t['variables']],
            })
        return jsonify({'templates': templates, 'count': len(templates)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@avis_bp.route('/api/avis/optimize/suggest', methods=['POST'])
def optimize_suggest():
    """POST /api/avis/optimize/suggest - full auto-suggest pipeline.

    Body: {
        "design_type": "spring",
        "specs": {...},
        "method": "pso"
    }
    """
    data = request.get_json(silent=True) or {}
    design_type = data.get('design_type', '').strip()
    if not design_type:
        return jsonify({'error': 'design_type is required'}), 400

    try:
        engine = _opt_engine()
        method = data.get('method', 'pso')
        result = engine.suggest(design_type, data.get('specs', {}), method=method)
        return jsonify(_clean_response(result))
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
