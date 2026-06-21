# -*- coding: utf-8 -*-
"""Seal Pair Designer Blueprint - Aerospace Valve Seal Pair Design v4.0"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from seal_pair_designer import api_seal_design, api_compare_designs, api_sensitivity_analysis, get_seal_design_info

seal_pair_bp = Blueprint('seal_pair', __name__, url_prefix='/api/seal_pair')


@seal_pair_bp.route('/design', methods=['POST'])
def design():
    data = request.get_json(silent=True) or {}
    result = api_seal_design(data)
    return jsonify(result)


@seal_pair_bp.route('/compare', methods=['POST'])
def compare():
    data = request.get_json(silent=True) or {}
    configs = data.get('configs', [])
    gas = data.get('gas', 'N2')
    result = api_compare_designs(configs, gas)
    return jsonify(result)


@seal_pair_bp.route('/sensitivity', methods=['POST'])
def sensitivity():
    data = request.get_json(silent=True) or {}
    base_config = data.get('base_config', {})
    param_name = data.get('param_name', 'roughness_Ra_um')
    values = data.get('values', [0.1, 0.4, 0.8])
    result = api_sensitivity_analysis(base_config, param_name, values)
    return jsonify(result)


@seal_pair_bp.route('/info', methods=['GET'])
def info():
    result = get_seal_design_info()
    return jsonify(result)
