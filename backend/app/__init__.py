"""
Application Factory Pattern
Creates and configures the Flask application instance.
Follows Flask best practices for large applications.
"""

from flask import Flask
from config import config_by_name, default_config
from app.extensions import init_extensions, cors
from app.middleware.error_handler import register_error_handlers


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

    @app.route('/ai-agent')
    def ai_agent_page():
        return render_template('ai_agent.html')

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
