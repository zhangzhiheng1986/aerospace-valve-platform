"""
Solenoid Blueprint: electromagnetic valve optimizer (PSO algorithm).
"""

from flask import Blueprint, request, render_template, jsonify
from app.utils.clean import prepare_json

solenoid_bp = Blueprint('solenoid', __name__)


@solenoid_bp.route('/solenoid')
def solenoid_page():
    return render_template('solenoid.html')


@solenoid_bp.route('/api/solenoid/optimize', methods=['POST'])
def optimize():
    from solenoid_optimizer import run_optimization
    data = request.get_json() or {}
    result = run_optimization(
        geom_params=data.get('geom_params', {}),
        n_particles=data.get('n_particles', 30),
        n_iterations=data.get('n_iterations', 100)
    )
    return jsonify(prepare_json(result))