"""
Core Blueprint: main pages (/, /admin, /login) and simulation pages.
"""

from flask import Blueprint, render_template, redirect
from app.middleware.auth import login_required_page, admin_required_page

core_bp = Blueprint('core', __name__)


@core_bp.route('/')
def index():
    """Main dashboard."""
    return render_template('index.html')


@core_bp.route('/login')
def login_page():
    """Login page."""
    return render_template('login.html')


@core_bp.route('/admin')
@admin_required_page
def admin_page(current_user):
    """Admin dashboard."""
    return render_template('admin.html')