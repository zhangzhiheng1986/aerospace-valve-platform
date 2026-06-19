"""
Application Factory Pattern
Creates and configures the Flask application instance.
Follows Flask best practices for large applications.
"""

from flask import Flask
from config import config_by_name, default_config
from app.extensions import init_extensions, cors
from app.middleware.error_handler import register_error_handlers


def _load_env_file():
    """Load secrets/.env into os.environ at Flask startup."""
    import os
    # Compute secrets/.env path relative to the backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_dir, '..', 'secrets', '.env')
    env_path = os.path.normpath(env_path)
    if not os.path.exists(env_path):
        # Try workspace-level path
        workspace = os.path.dirname(backend_dir)
        env_path = os.path.join(workspace, 'secrets', '.env')
        env_path = os.path.normpath(env_path)
    if not os.path.exists(env_path):
        # Try avis-platform/secrets/.env
        workspace = os.path.dirname(backend_dir)
        env_path = os.path.join(workspace, 'avis-platform', 'secrets', '.env')
        env_path = os.path.normpath(env_path)
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name: one of 'dev'/'prod'/'test' (default: from FLASK_ENV or 'dev')

    Returns:
        Configured Flask application instance
    """
    import os

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', default_config)

    # ── Load secrets/.env into os.environ before anything else ──
    _load_env_file()

    app = Flask(__name__,
                static_folder='../../frontend',
                template_folder='../../frontend')

    # Load config
    config_class = config_by_name.get(config_name, config_by_name[default_config])
    app.config.from_object(config_class)
    app.config['ENV'] = config_name

    # Init extensions (CORS, logging)
    init_extensions(app)

    # Register global error handlers
    register_error_handlers(app)

    # ---------------------------------------------------------------
    # Register Blueprints
    # ---------------------------------------------------------------
    from app.blueprints.core import core_bp
    app.register_blueprint(core_bp)

    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.blueprints.solenoid import solenoid_bp
    app.register_blueprint(solenoid_bp)

    from app.blueprints.materials import materials_bp
    app.register_blueprint(materials_bp)

    from app.blueprints.valve_modules import valve_bp
    app.register_blueprint(valve_bp)

    from app.blueprints.knowledge import knowledge_bp
    app.register_blueprint(knowledge_bp)

    from app.blueprints.cms import cms_bp
    app.register_blueprint(cms_bp)

    from app.blueprints.templates_bp import templates_bp
    app.register_blueprint(templates_bp)

    from app.blueprints.users import users_bp
    app.register_blueprint(users_bp)

    from app.blueprints.news import news_bp
    app.register_blueprint(news_bp)

    from app.blueprints.fluid_mechanics import fm_bp
    app.register_blueprint(fm_bp)

    from app.blueprints.ai_agent import ai_agent_bp
    app.register_blueprint(ai_agent_bp)

    from app.blueprints.search import search_bp
    app.register_blueprint(search_bp)
    
    # Sprint 7: Knowledge Graph (migrated to avis_bp at /api/avis/kg/*)
    # Legacy graph_bp removed - superseded by avis knowledge_graph endpoints

    # Sprint 11: Avis Intelligent Agent Platform
    try:
        from app.blueprints.avis_bp import avis_bp
        app.register_blueprint(avis_bp)
    except ImportError:
        app.logger.warning('Avis blueprint not available - skipping')

    # Sprint 12: Valve Process Module (manufacturing process library)
    from app.blueprints.valve_process import valve_process_bp
    app.register_blueprint(valve_process_bp)

    # Auto-import any new news markdown files on startup
    _auto_import_news(app)

    # Routes for pages that need direct @app.route (legacy compatibility)
    _register_page_routes(app)

    return app


def _auto_import_news(app):
    """Auto-import any news markdown files from workspace on startup."""
    try:
        import os
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, backend_dir)
        from news_feed import import_latest_markdown
        result = import_latest_markdown()
        if result and result.get('items'):
            app.logger.info(
                'Auto-imported news: %s (%d items)',
                result.get('date'), len(result.get('items', []))
            )
    except Exception as e:
        app.logger.warning('News auto-import skipped: %s', e)


def _register_page_routes(app):
    """Register page-only routes (no API logic)."""
    from flask import render_template

    # Simulation pages (CFD, thermal, structural, docs)
    @app.route('/cfd')
    def cfd_page():
        return render_template('cfd.html')

    @app.route('/thermal')
    def thermal_page():
        return render_template('thermal.html')

    @app.route('/structural')
    def structural_page():
        return render_template('structural.html')

    @app.route('/docs')
    def docs_page():
        return render_template('docs.html')

    @app.route('/avis')
    def avis_dashboard_page():
        """Serve the Avis Intelligent Agent Platform dashboard."""
        from flask import request, redirect, send_from_directory
        from auth_system import auth
        import os as _os
        # Check auth
        token = request.cookies.get('auth_token', '')
        if not token:
            return redirect('/login?redirect=/avis')
        is_valid, user = auth.verify_session(token)
        if not is_valid:
            return redirect('/login?redirect=/avis')
        # Serve dashboard from avis-platform/dashboard/
        dashboard_path = _os.path.join(
            _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(__file__)))),
            'avis-platform', 'dashboard', 'index.html'
        )
        if _os.path.exists(dashboard_path):
            return send_from_directory(_os.path.dirname(dashboard_path),
                                       _os.path.basename(dashboard_path))
        return render_template('avis_dashboard.html', auth_token=token,
                              user_name=user.get('username', 'Engineer'))

    @app.route('/ai-agent')
    def ai_agent_page():
        from app.middleware.auth import login_required_page
        from flask import request, redirect
        from auth_system import auth
        # Check cookie-based auth
        token = request.cookies.get('auth_token', '')
        if not token:
            return redirect('/login?redirect=/ai-agent')
        is_valid, user = auth.verify_session(token)
        if not is_valid:
            return redirect('/login?redirect=/ai-agent')
        return render_template('ai_agent.html', auth_token=token, user_name=user.get('username', 'Engineer'))

    @app.route('/memory')
    def memory_page():
        """Sprint 14.2: Agent Memory dashboard."""
        from flask import request, redirect
        from auth_system import auth
        token = request.cookies.get('auth_token', '')
        if not token:
            return redirect('/login?redirect=/memory')
        is_valid, user = auth.verify_session(token)
        if not is_valid:
            return redirect('/login?redirect=/memory')
        return render_template('memory.html', auth_token=token, user_name=user.get('username', 'Engineer'))

    @app.route('/multi-agent')
    def multi_agent_page():
        """Sprint 14.1: 7-Agent Collaboration platform."""
        from flask import request, redirect
        from auth_system import auth
        token = request.cookies.get('auth_token', '')
        if not token:
            return redirect('/login?redirect=/multi-agent')
        is_valid, user = auth.verify_session(token)
        if not is_valid:
            return redirect('/login?redirect=/multi-agent')
        return render_template('multi_agent.html', auth_token=token, user_name=user.get('username', 'Engineer'))
        """Sprint 14.2: Agent Memory dashboard."""
        from flask import request, redirect
        from auth_system import auth
        token = request.cookies.get('auth_token', '')
        if not token:
            return redirect('/login?redirect=/memory')
        is_valid, user = auth.verify_session(token)
        if not is_valid:
            return redirect('/login?redirect=/memory')
        return render_template('memory.html', auth_token=token, user_name=user.get('username', 'Engineer'))

    # Legacy analysis APIs (non-module-specific)
    from app.middleware.auth import require_auth

    @app.route('/api/analyze', methods=['POST'])
    @require_auth()
    def legacy_analyze(current_user):
        """Legacy code analysis endpoint."""
        import sys, io, traceback, json
        from contextlib import redirect_stdout
        data = request.get_json() or {}
        code = data.get('code', '')
        result = {'output': '', 'error': None}
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                exec(compile(code, '<input>', 'exec'), {'__builtins__': __builtins__.__dict__})
            result['output'] = buf.getvalue()
        except Exception as e:
            result['error'] = traceback.format_exc()
        from flask import jsonify
        return jsonify(result)

    @app.route('/api/execute', methods=['POST'])
    @require_auth()
    def legacy_execute(current_user):
        """Legacy execute endpoint."""
        from flask import jsonify
        return jsonify({'success': True})

    @app.route('/api/generate-ui', methods=['POST'])
    @require_auth()
    def legacy_generate_ui(current_user):
        """Legacy UI generation endpoint."""
        from flask import jsonify
        return jsonify({'success': True, 'html': ''})

    from flask import request as _request
