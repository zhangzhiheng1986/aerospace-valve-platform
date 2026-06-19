"""
Core Blueprint: main pages (/, /admin, /login) and simulation pages.
"""

from flask import Blueprint, render_template, redirect
from app.middleware.auth import login_required_page, admin_required_page

core_bp = Blueprint('core', __name__)


@core_bp.route('/')
@core_bp.route('/index.html')
def index():
    """Main dashboard - AI Agent centric."""
    return render_template('index.html')


@core_bp.route('/classic')
@core_bp.route('/index_classic.html')
def class_index():
    """Classic dashboard view."""
    return render_template('index_classic.html')


@core_bp.route('/login')
def login_page():
    """Login page."""
    return render_template('login.html')


@core_bp.route('/admin')
@admin_required_page
def admin_page(current_user):
    """Admin dashboard."""
    return render_template('admin.html')


@core_bp.route('/departments')
def departments_page():
    """Multi-department collaboration dashboard."""
    return render_template('departments.html')


@core_bp.route('/projects')
def projects_page():
    """Project management dashboard."""
    return render_template('projects.html')


@core_bp.route('/filesystem')
def filesystem_page():
    """Avis file system browser."""
    return render_template('filesystem.html')


@core_bp.route('/cron')
def cron_page():
    """Avis cron task manager."""
    return render_template('cron.html')


@core_bp.route('/expert')
def expert_page():
    """Avis expert system."""
    return render_template('expert.html')


@core_bp.route('/product-structure')
def product_structure_page():
    """Avis product structure library."""
    return render_template('product_structure.html')


@core_bp.route('/knowledge-graph')
def knowledge_graph_page():
    """Avis knowledge graph engine."""
    return render_template('knowledge_graph.html')


@core_bp.route('/auto-optimizer')
def auto_optimizer_page():
    """Avis auto-optimizer dashboard."""
    return render_template('auto_optimizer.html')


@core_bp.route('/multi-agent')
def multi_agent_page():
    """Avis multi-agent collaboration dashboard."""
    return render_template('multi_agent.html')


@core_bp.route('/llm-status')
def llm_status_page():
    """LLM service status dashboard."""
    return render_template('llm_status.html')