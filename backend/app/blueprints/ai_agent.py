"""
AI Agent Blueprint
API endpoints for the AI co-pilot agent.
"""

from flask import Blueprint, request, jsonify, session
from app.middleware.auth import require_auth
import traceback

ai_agent_bp = Blueprint('ai_agent', __name__, url_prefix='/api/agent')


@ai_agent_bp.route('/sessions', methods=['POST'])
@require_auth()
def create_session(current_user=None):
    """Create a new agent session."""
    try:
        from ai_agent_engine import get_engine
        engine = get_engine()
        user_name = (request.get_json() or {}).get('user_name', current_user.get('username', 'Engineer') if current_user else 'Engineer')
        sid = engine.sessions.create_session(user_name)
        engine.sessions.add_message(sid, 'system', 'session_created', {
            'greeting': '你好！我是航空航天阀门AI协同工程师。我可以帮你：\n\n1. 运行工程计算（流体力学/阀门设计/弹簧/O形圈...）\n2. 查询材料属性（21种航空材料）\n3. 检查QJ 20156标准合规\n4. 搜索知识库（31400字航空航天阀门知识）\n5. 对比多个设计方案\n\n请告诉我你需要什么帮助。'
        })
        return jsonify({
            'success': True,
            'session_id': sid,
            'user_name': user_name,
            'greeting': '你好！我是航空航天阀门AI协同工程师。我可以帮你：\n\n1. 运行工程计算（流体力学/阀门设计/弹簧/O形圈...）\n2. 查询材料属性（21种航空材料）\n3. 检查QJ 20156标准合规\n4. 搜索知识库（31400字航空航天阀门知识）\n5. 对比多个设计方案\n\n请告诉我你需要什么帮助。',
            'tools': engine.tools.list_tools(),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_agent_bp.route('/chat', methods=['POST'])
@require_auth()
def chat(current_user=None):
    """Send a message to the AI agent."""
    try:
        from ai_agent_engine import get_engine
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
        
        result = engine.process_message(session_id, message)
        
        if result.get('need_new_session'):
            sid = engine.sessions.create_session(
                current_user.get('username', 'Engineer') if current_user else 'Engineer'
            )
            result = engine.process_message(sid, message)
            session_id = sid
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'response': result,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'response': {
                'text': f'处理请求时遇到问题: {str(e)}',
                'intent': 'error',
            }
        }), 200  # Return 200 so frontend can display error


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
                'messages': s['messages'][-20:],  # Last 20 messages
                'created_at': s['created_at'],
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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
            engine.sessions.add_message(session_id, 'agent', f'Executed tool: {tool_name}', result)
        
        return jsonify({
            'success': True,
            'tool': tool_name,
            'result': result,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
