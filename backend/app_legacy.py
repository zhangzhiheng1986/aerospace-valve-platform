from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, make_response
from flask_cors import CORS
import ast
import sys
import io
import contextlib
import json
import traceback
from typing import Dict, List, Any
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np

# 导入电磁阀优化器
from solenoid_optimizer import run_optimization

# 导入材料数据库
from materials_database import db as materials_db, get_all_materials, get_material_detail, search_materials

# 导入认证系统
from auth_system import auth, UserRole

# 导入CMS系统
from cms_module import (
    get_articles, get_article, create_article, update_article, delete_article,
    get_categories, get_category, create_category, update_category, delete_category,
    get_tags, get_stats
)

# 导入模板库模块
import template_library as tlib

# 导入密封副设计模块
from seal_design import calculate_seal_design, run_compare, run_sensitivity, get_catalog

# 导入新闻资讯模块
import news_feed

# 导入QJ 20156-2012标准模块
from qj20156_module import (
    get_standard_info, design_assistant,
    generate_thermal_vacuum_profile, generate_thermal_cycle_profile,
    verify_leak_rate, verify_rated_output_pressure, verify_lockup_pressure,
    calc_proof_pressure, calc_burst_pressure, calc_elastic_element_overload,
    verify_life_cycles, verify_cleanliness, calc_safety_margin
)

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)


# ==================== 认证装饰器 ====================

def require_auth(permission='viewer'):
    """认证装饰器"""
    def decorator(f):
        def wrapped(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'success': False, 'message': '未提供认证Token'}), 401
            
            is_valid, user = auth.verify_session(token)
            if not is_valid:
                return jsonify({'success': False, 'message': 'Token无效或已过期'}), 401
            
            if not auth.check_permission(user['id'], permission):
                return jsonify({'success': False, 'message': '权限不足'}), 403
            
            return f(user, *args, **kwargs)
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator


def login_required_page(f):
    """页面认证装饰器 - 通过Cookie检查登录状态，未登录重定向到登录页"""
    def wrapped(*args, **kwargs):
        token = request.cookies.get('auth_token', '')
        if token:
            is_valid, user = auth.verify_session(token)
            if is_valid:
                return f(user, *args, **kwargs)
        return redirect('/login?redirect=' + request.path)
    wrapped.__name__ = f.__name__
    return wrapped


def admin_required_page(f):
    """管理员页面装饰器 - 非管理员重定向到登录页"""
    def wrapped(*args, **kwargs):
        token = request.cookies.get('auth_token', '')
        if token:
            is_valid, user = auth.verify_session(token)
            if is_valid and user.get('role') == '管理员':
                return f(user, *args, **kwargs)
        return redirect('/login?redirect=' + request.path)
    wrapped.__name__ = f.__name__
    return wrapped


class PythonCodeAnalyzer:
    """Python代码分析器 - 提取函数、参数、可视化需求"""
    
    def __init__(self, code: str):
        self.code = code
        self.tree = None
        self.functions = []
        self.imports = []
        self.variables = []
        
    def analyze(self) -> Dict[str, Any]:
        """分析代码并返回结构化信息"""
        try:
            self.tree = ast.parse(self.code)
            self._extract_imports()
            self._extract_functions()
            self._extract_variables()
            
            return {
                'success': True,
                'functions': self.functions,
                'imports': self.imports,
                'variables': self.variables,
                'has_visualization': self._detect_visualization(),
                'suggested_ui': self._suggest_ui_components()
            }
        except SyntaxError as e:
            return {
                'success': False,
                'error': f'语法错误: {str(e)}',
                'line': e.lineno,
                'offset': e.offset
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'分析失败: {str(e)}'
            }
    
    def _extract_imports(self):
        """提取导入的库"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                self.imports.append(f"{node.module} ({', '.join([a.name for a in node.names])})")
    
    def _extract_functions(self):
        """提取函数定义"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args': [],
                    'returns': None,
                    'docstring': ast.get_docstring(node),
                    'line': node.lineno
                }
                
                # 提取参数
                for arg in node.args.args:
                    arg_info = {
                        'name': arg.arg,
                        'type': self._get_annotation(arg.annotation) if arg.annotation else 'any',
                        'default': None
                    }
                    func_info['args'].append(arg_info)
                
                # 提取返回值类型
                if node.returns:
                    func_info['returns'] = self._get_annotation(node.returns)
                
                self.functions.append(func_info)
    
    def _extract_variables(self):
        """提取全局变量"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.variables.append({
                            'name': target.id,
                            'line': node.lineno
                        })
    
    def _get_annotation(self, annotation) -> str:
        """获取类型注解的字符串表示"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            return f"{annotation.value.id}[{self._get_annotation(annotation.slice)}]"
        else:
            return 'any'
    
    def _detect_visualization(self) -> bool:
        """检测代码是否包含可视化库"""
        viz_libs = ['matplotlib', 'plotly', 'seaborn', 'bokeh', 'pygal', 'altair']
        return any(lib in self.code.lower() for lib in viz_libs)
    
    def _suggest_ui_components(self) -> List[Dict[str, Any]]:
        """根据代码分析建议UI组件"""
        components = []
        
        # 如果有matplotlib/plotly，建议图表组件
        if self._detect_visualization():
            components.append({
                'type': 'chart',
                'library': 'plotly',
                'title': '可视化结果'
            })
        
        # 为每个函数生成输入组件
        for func in self.functions:
            for arg in func['args']:
                if arg['type'] in ['int', 'float', 'number']:
                    components.append({
                        'type': 'slider',
                        'function': func['name'],
                        'param': arg['name'],
                        'min': 0,
                        'max': 100,
                        'step': 1,
                        'default': 50
                    })
                elif arg['type'] in ['str', 'string']:
                    components.append({
                        'type': 'text_input',
                        'function': func['name'],
                        'param': arg['name'],
                        'placeholder': f'输入{arg["name"]}'
                    })
                elif arg['type'] == 'bool':
                    components.append({
                        'type': 'checkbox',
                        'function': func['name'],
                        'param': arg['name'],
                        'default': False
                    })
        
        return components


class CodeExecutor:
    """安全的Python代码执行器"""
    
    def __init__(self, code: str):
        self.code = code
        self.result = None
        self.error = None
        self.output = None
        self.figures = []
        
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行代码并返回结果"""
        # 重定向stdout捕获打印输出
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        # 创建执行环境
        exec_globals = {
            '__builtins__': __builtins__,
            'np': np,
            'matplotlib': matplotlib,
            'plt': plt,
        }
        
        # 如果提供了参数，添加到执行环境
        if params:
            exec_globals.update(params)
        
        try:
            # 执行代码
            exec(self.code, exec_globals)
            
            # 捕获matplotlib图表
            if plt.get_fignums():
                for fig_num in plt.get_fignums():
                    fig = plt.figure(fig_num)
                    buf = BytesIO()
                    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
                    buf.seek(0)
                    img_str = base64.b64encode(buf.read()).decode('utf-8')
                    self.figures.append(img_str)
                plt.close('all')
            
            self.output = buffer.getvalue()
            self.result = exec_globals.get('result', None)
            
            return {
                'success': True,
                'output': self.output,
                'result': str(self.result) if self.result else None,
                'figures': self.figures,
                'variables': {k: str(v) for k, v in exec_globals.items() 
                            if not k.startswith('_') and k not in ['__builtins__', 'np', 'matplotlib', 'plt']}
            }
            
        except Exception as e:
            self.error = traceback.format_exc()
            return {
                'success': False,
                'error': self.error,
                'output': buffer.getvalue()
            }
        finally:
            sys.stdout = old_stdout


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/solenoid')
def solenoid():
    """电磁阀优化工具页面"""
    return render_template('solenoid.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """分析Python代码"""
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({'success': False, 'error': '代码不能为空'})
    
    analyzer = PythonCodeAnalyzer(code)
    result = analyzer.analyze()
    
    return jsonify(result)


@app.route('/api/execute', methods=['POST'])
def execute_code():
    """执行Python代码"""
    data = request.json
    code = data.get('code', '')
    params = data.get('params', {})
    
    if not code:
        return jsonify({'success': False, 'error': '代码不能为空'})
    
    executor = CodeExecutor(code)
    result = executor.execute(params)
    
    return jsonify(result)


@app.route('/api/generate-ui', methods=['POST'])
def generate_ui():
    """根据代码生成UI配置"""
    data = request.json
    code = data.get('code', '')
    
    analyzer = PythonCodeAnalyzer(code)
    analysis = analyzer.analyze()
    
    if not analysis['success']:
        return jsonify(analysis)
    
    # 生成UI配置
    ui_config = {
        'title': '航空航天阀门计算工具',
        'layout': 'vertical',
        'components': []
    }
    
    # 添加输入组件
    for component in analysis['suggested_ui']:
        if component['type'] in ['slider', 'text_input', 'checkbox']:
            ui_config['components'].append({
                'id': f"{component['function']}_{component['param']}",
                'type': component['type'],
                'label': f"{component['param']} ({component['function']})",
                'placeholder': component.get('placeholder', ''),
                'min': component.get('min'),
                'max': component.get('max'),
                'step': component.get('step'),
                'default': component.get('default')
            })
    
    # 添加执行按钮
    ui_config['components'].append({
        'id': 'execute_btn',
        'type': 'button',
        'label': '运行代码',
        'action': 'execute'
    })
    
    # 添加输出区域
    ui_config['components'].append({
        'id': 'output',
        'type': 'output',
        'label': '执行结果'
    })
    
    if analysis['has_visualization']:
        ui_config['components'].append({
            'id': 'chart',
            'type': 'chart',
            'label': '可视化图表'
        })
    
    return jsonify({
        'success': True,
        'ui_config': ui_config,
        'analysis': analysis
    })




    if not code:
        return jsonify({'success': False, 'error': '代码不能为空'})
    
    analyzer = PythonCodeAnalyzer(code)
    result = analyzer.analyze()
    
    return jsonify(result)


    
    if not code:
        return jsonify({'success': False, 'error': '代码不能为空'})
    
    executor = CodeExecutor(code)
    result = executor.execute(params)
    
    return jsonify(result)


    analyzer = PythonCodeAnalyzer(code)
    analysis = analyzer.analyze()
    
    if not analysis['success']:
        return jsonify(analysis)
    
    # 生成UI配置
    ui_config = {
        'title': '航空航天阀门计算工具',
        'layout': 'vertical',
        'components': []
    }
    
    # 添加输入组件
    for component in analysis['suggested_ui']:
        if component['type'] in ['slider', 'text_input', 'checkbox']:
            ui_config['components'].append({
                'id': f"{component['function']}_{component['param']}",
                'type': component['type'],
                'label': f"{component['param']} ({component['function']})",
                'placeholder': component.get('placeholder', ''),
                'min': component.get('min'),
                'max': component.get('max'),
                'step': component.get('step'),
                'default': component.get('default')
            })
    
    # 添加执行按钮
    ui_config['components'].append({
        'id': 'execute_btn',
        'type': 'button',
        'label': '运行代码',
        'action': 'execute'
    })
    
    # 添加输出区域
    ui_config['components'].append({
        'id': 'output',
        'type': 'output',
        'label': '执行结果'
    })
    
    if analysis['has_visualization']:
        ui_config['components'].append({
            'id': 'chart',
            'type': 'chart',
            'label': '可视化图表'
        })
    
    return jsonify({
        'success': True,
        'ui_config': ui_config,
        'analysis': analysis
    })

@app.route('/api/solenoid/optimize', methods=['POST'])
def solenoid_optimize():
    """电磁阀优化API"""
    data = request.json
    
    geom_params = data.get('geom_params', {})
    n_particles = data.get('n_particles', 20)
    n_iterations = data.get('n_iterations', 50)
    
    # 日志列表
    log_messages = []
    
    def log_callback(msg):
        log_messages.append(msg)
        print(f"[Optimizer] {msg}")
    
    # 进度列表
    progress_messages = []
    
    def progress_callback(current, total, awg):
        msg = f"{current}/{total} - AWG {awg}"
        progress_messages.append(msg)
        print(f"[Progress] {msg}")
    
    try:
        result = run_optimization(
            geom_params=geom_params,
            n_particles=n_particles,
            n_iterations=n_iterations,
            log_callback=log_callback,
            progress_callback=progress_callback
        )
        result['logs'] = log_messages
        result['progress'] = progress_messages
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'优化失败: {str(e)}',
            'error': traceback.format_exc(),
            'logs': log_messages
        })


# ==================== 材料数据库API ====================

@app.route('/materials')
def materials_page():
    """材料数据库页面"""
    return render_template('materials.html')


@app.route('/api/materials/statistics')
def materials_statistics():
    """获取材料数据库统计信息"""
    try:
        stats = materials_db.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/materials/list')
def materials_list():
    """获取所有材料列表"""
    try:
        materials = get_all_materials()
        return jsonify(materials)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/materials/detail')
def materials_detail():
    """获取材料详细信息"""
    name = request.args.get('name', '')
    if not name:
        return jsonify({'error': '材料名称不能为空'}), 400
    
    try:
        material = get_material_detail(name)
        if material is None:
            return jsonify({'error': '材料不存在'}), 404
        return jsonify(material)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/materials/search')
def materials_search():
    """搜索材料"""
    category = request.args.get('category', None)
    min_temp = request.args.get('min_temp', None, type=float)
    max_temp = request.args.get('max_temp', None, type=float)
    
    try:
        materials = search_materials(category, min_temp, max_temp)
        return jsonify(materials)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/materials/recommend', methods=['POST'])
def materials_recommend():
    """材料推荐引擎"""
    data = request.json
    scenario = data.get('scenario', 'solenoid_valve')
    requirements = data.get('requirements', {})
    
    try:
        recommendations = materials_db.recommend_material(scenario, requirements)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/materials/calculate-wire', methods=['POST'])
def materials_calculate_wire():
    """计算绕组参数"""
    data = request.json
    material_name = data.get('material', '')
    awg = data.get('awg', 27)
    turns = data.get('turns', 1000)
    mean_diameter = data.get('mean_diameter', 25.0)
    
    if not material_name:
        return jsonify({'error': '材料名称不能为空'}), 400
    
    try:
        result = materials_db.calculate_wire_properties(
            material_name, awg, turns, mean_diameter
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/materials/awg/<int:awg>')
def materials_get_awg(awg):
    """获取AWG线规参数"""
    try:
        result = materials_db.get_conductor_for_awg(awg)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 认证API ====================

@app.route('/login')
def login_page():
    """登录页面"""
    return render_template('login.html')


@app.route('/admin')
@admin_required_page
def admin_page(current_user):
    """后台管理页面"""
    return render_template('admin.html')


@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    """用户注册"""
    data = request.json
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    real_name = data.get('real_name', '').strip()
    department = data.get('department', '').strip()
    role = data.get('role', UserRole.VIEWER.value)
    
    # 验证必填字段
    if not all([username, password, email, real_name, department]):
        return jsonify({'success': False, 'message': '所有字段为必填项'})
    
    # 验证用户名长度
    if len(username) < 3 or len(username) > 20:
        return jsonify({'success': False, 'message': '用户名长度应为3-20个字符'})
    
    # 验证密码长度
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度至少6个字符'})
    
    success, message = auth.register(username, password, email, real_name, department, role)
    return jsonify({'success': success, 'message': message})


@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """用户登录"""
    data = request.json
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    # 获取客户端信息
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    success, message, user_data = auth.login(username, password, ip_address, user_agent)
    resp = make_response(jsonify({'success': success, 'message': message, 'user': user_data}))
    if success and user_data:
        resp.set_cookie('auth_token', user_data['token'], httponly=True, max_age=86400, samesite='Lax', path='/')
    return resp


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """用户登出"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = request.cookies.get('auth_token', '')
    success, message = auth.logout(token)
    resp = make_response(jsonify({'success': success, 'message': message}))
    resp.delete_cookie('auth_token', path='/')
    return resp


@app.route('/api/auth/verify', methods=['GET'])
def auth_verify():
    """验证Token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    is_valid, user = auth.verify_session(token)
    return jsonify({'success': is_valid, 'user': user})


# ==================== 用户管理API ====================

@app.route('/api/users/statistics')
@require_auth('admin')
def users_statistics(current_user):
    """获取用户统计信息"""
    stats = auth.get_user_statistics()
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/users/list')
@require_auth('admin')
def users_list(current_user):
    """获取所有用户列表"""
    users = auth.get_all_users()
    return jsonify({'success': True, 'users': users})


@app.route('/api/users/<user_id>', methods=['PUT'])
@require_auth('admin')
def users_update(current_user, user_id):
    """更新用户信息"""
    data = request.json
    
    # 过滤允许更新的字段
    allowed_fields = ['email', 'real_name', 'department', 'role', 'is_active', 'avatar']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    success, message = auth.update_user(user_id, **update_data)
    return jsonify({'success': success, 'message': message})


@app.route('/api/users/<user_id>', methods=['DELETE'])
@require_auth('admin')
def users_delete(current_user, user_id):
    """删除用户"""
    success, message = auth.delete_user(user_id)
    return jsonify({'success': success, 'message': message})


@app.route('/api/users/change-password', methods=['POST'])
@require_auth('viewer')
def users_change_password(current_user):
    """修改密码"""
    data = request.json
    
    user_id = current_user['id']
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码长度至少6个字符'})
    
    success, message = auth.change_password(user_id, old_password, new_password)
    return jsonify({'success': success, 'message': message})


# ==================== 流体仿真API ====================

@app.route('/cfd')
def cfd_page():
    """流体仿真页面"""
    return render_template('cfd.html')


@app.route('/thermal')
def thermal_page():
    """热力学分析页面"""
    return render_template('thermal.html')


@app.route('/structural')
def structural_page():
    """结构强度分析页面"""
    return render_template('structural.html')


@app.route('/docs')
def docs_page():
    """文档和帮助页面"""
    return render_template('docs.html')


@app.route('/api/cfd/analyze', methods=['POST'])
def cfd_analyze():
    """CFD流体仿真分析"""
    try:
        from cfd_analyzer import run_cfd_analysis
        
        data = request.json
        result = run_cfd_analysis(
            fluid_name=data.get('fluid', 'water_20C'),
            geometry_params=data.get('geometry', {}),
            inlet_pressure=data.get('inlet_pressure', 500000),
            outlet_pressure=data.get('outlet_pressure', 100000),
            opening_ratio=data.get('opening_ratio', 1.0)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/thermal/analyze', methods=['POST'])
def thermal_analyze():
    """热力学分析"""
    try:
        from thermal_analyzer import run_thermal_analysis
        
        data = request.json
        result = run_thermal_analysis(
            material_name=data.get('material', 'copper'),
            component_params=data.get('component', {}),
            operating_conditions=data.get('conditions', {})
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/structural/analyze', methods=['POST'])
def structural_analyze():
    """结构强度分析"""
    try:
        from structural_analyzer import run_structural_analysis
        
        data = request.json
        result = run_structural_analysis(
            material_name=data.get('material', 'steel_304'),
            geometry=data.get('geometry', {}),
            loads=data.get('loads', {})
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


from pressure_reducing_valve import run_design as prv_run_design, FluidDatabase as PRVFluidDB, MaterialDatabase as PRVMatDB

from valve_metrics import (get_all_metrics, get_metrics_by_category, get_metric_by_id,
    get_all_valve_types, get_valve_type, get_all_domains, get_domain,
    get_leakage_classes, get_all_standards, get_stats as metrics_get_stats, search_metrics)

# ==================== Valve Metrics API ====================

@app.route('/valve_metrics')
def valve_metrics_page():
    return render_template('valve_metrics.html')

@app.route('/api/metrics/stats')
def metrics_stats():
    return jsonify(metrics_get_stats())

@app.route('/api/metrics/list')
def metrics_list():
    cat = request.args.get('category')
    if cat:
        return jsonify(get_metrics_by_category(cat))
    return jsonify(get_all_metrics())

@app.route('/api/metrics/search')
def metrics_search():
    q = request.args.get('q', '')
    return jsonify(search_metrics(q))

@app.route('/api/metrics/valve_types')
def metrics_valve_types():
    return jsonify(get_all_valve_types())

@app.route('/api/metrics/domains')
def metrics_domains():
    return jsonify(get_all_domains())

@app.route('/api/metrics/leakage_classes')
def metrics_leakage():
    return jsonify(get_leakage_classes())

@app.route('/api/metrics/standards')
def metrics_standards():
    return jsonify(get_all_standards())

from check_valve import run_check_valve_design as cv_design
from spring_design import design_spring, get_materials_list as spring_materials
from oring_design import design_oring, get_materials_list, get_cs_options

# ==================== Check Valve API ====================

@app.route('/check_valve')
def check_valve_page():
    return render_template('check_valve.html')

@app.route('/api/check_valve/design', methods=['POST'])
def check_valve_design():
    try:
        data = request.get_json()
        result = cv_design(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== Spring Design API ====================


@app.route('/spring_design')
def spring_design_page():
    return render_template('spring_design.html')

@app.route('/api/spring/design', methods=['POST'])
def spring_design_api():
    try:
        data = request.get_json()
        result = design_spring(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/spring/materials', methods=['GET'])
def spring_materials_list():
    return jsonify(spring_materials())


# ==================== O-Ring Seal Design API ====================

@app.route('/oring_design')
def oring_design_page():
    return render_template('oring_design.html')

@app.route('/api/oring/design', methods=['POST'])
def oring_design_api():
    try:
        data = request.get_json()
        result = design_oring(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/oring/materials', methods=['GET'])
def oring_materials_list():
    return jsonify(get_materials_list())

@app.route('/api/oring/cs_options', methods=['GET'])
def oring_cs_options():
    return jsonify(get_cs_options())


# ==================== QJ 20156-2012 Standard Compliance API ====================

@app.route('/qj20156')
def qj20156_page():
    return render_template('qj20156.html')

@app.route('/api/qj20156/info')
def qj20156_info():
    return jsonify(get_standard_info())

@app.route('/api/qj20156/design', methods=['POST'])
def qj20156_design_api():
    try:
        data = request.get_json()
        result = design_assistant(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/qj20156/thermal_vacuum', methods=['POST'])
def qj20156_thermal_vacuum():
    try:
        data = request.get_json()
        result = generate_thermal_vacuum_profile(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/qj20156/thermal_cycle', methods=['POST'])
def qj20156_thermal_cycle():
    try:
        data = request.get_json()
        result = generate_thermal_cycle_profile(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/qj20156/verify_leak', methods=['POST'])
def qj20156_verify_leak():
    try:
        data = request.get_json()
        result = verify_leak_rate(data.get('measured_leak', 0), data.get('leak_type', 'internal'))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/qj20156/verify_rated', methods=['POST'])
def qj20156_verify_rated():
    try:
        data = request.get_json()
        result = verify_rated_output_pressure(data.get('rated', 0), data.get('measured', 0))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/qj20156/verify_lockup', methods=['POST'])
def qj20156_verify_lockup():
    try:
        data = request.get_json()
        result = verify_lockup_pressure(data.get('rated_pressure', 0), data.get('lockup_pressure', 0))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/qj20156/proof_burst', methods=['POST'])
def qj20156_proof_burst():
    try:
        data = request.get_json()
        p = data.get('max_working_pressure_MPa', 5)
        proof = calc_proof_pressure(p)
        burst = calc_burst_pressure(p)
        safety = calc_safety_margin({
            'burst_pressure_MPa': p * 2.0,
            'proof_pressure_MPa': p * 1.5,
            'max_working_pressure_MPa': p
        })
        return jsonify({'proof': proof, 'burst': burst, 'safety': safety})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/qj20156/verify_life', methods=['POST'])
def qj20156_verify_life():
    try:
        data = request.get_json()
        result = verify_life_cycles(data.get('cycles', 0))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/qj20156/elastic_element', methods=['POST'])
def qj20156_elastic_element():
    try:
        data = request.get_json()
        result = calc_elastic_element_overload(data.get('working_pressure', 5))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== Pressure Reducing Valve API ====================

@app.route('/pressure_valve')
def pressure_valve_page():
    return render_template('pressure_valve.html')

@app.route('/api/pressure_valve/design', methods=['POST'])
def pressure_valve_design():
    try:
        data = request.get_json()
        result = prv_run_design(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/pressure_valve/fluids')
def pressure_valve_fluids():
    return jsonify(PRVFluidDB.get_all_fluids())

@app.route('/api/pressure_valve/materials')
def pressure_valve_materials():
    return jsonify(PRVMatDB.get_all_materials())

# ==================== Knowledge Base API ====================

@app.route('/knowledge')
def knowledge_page():
    """Knowledge base page"""
    return render_template('knowledge.html')


@app.route('/api/knowledge/chapters')
def kb_chapters():
    """Get all chapter summaries"""
    from knowledge_base import get_all_chapters
    return jsonify(get_all_chapters())


@app.route('/api/knowledge/chapter/<chapter_id>')
def kb_chapter(chapter_id):
    """Get full chapter detail"""
    from knowledge_base import get_chapter_detail
    ch = get_chapter_detail(chapter_id)
    if ch:
        return jsonify(ch)
    return jsonify({'error': 'Chapter not found'}), 404


@app.route('/api/knowledge/section/<chapter_id>/<section_id>')
def kb_section(chapter_id, section_id):
    """Get single section content"""
    from knowledge_base import get_section
    sec = get_section(chapter_id, section_id)
    if sec:
        return jsonify(sec)
    return jsonify({'error': 'Section not found'}), 404


@app.route('/api/knowledge/search')
def kb_search():
    """Search knowledge base"""
    from knowledge_base import search_knowledge
    q = request.args.get('q', '')
    return jsonify(search_knowledge(q))


@app.route('/api/knowledge/stats')
def kb_stats():
    """Knowledge base statistics"""
    from knowledge_base import get_stats
    return jsonify(get_stats())


@app.route('/api/knowledge/glossary')
def kb_glossary():
    """Get glossary terms"""
    from knowledge_base import get_glossary
    return jsonify(get_glossary())


# ==================== CMS API ====================

@app.route('/cms_admin')
@admin_required_page
def cms_admin_page(current_user):
    return render_template('cms_admin.html')


@app.route('/knowledge_articles')
def knowledge_articles_page():
    return render_template('knowledge_articles.html')


@app.route('/knowledge_articles/<slug_or_id>')
def knowledge_article_detail(slug_or_id):
    return render_template('knowledge_articles.html')


@app.route('/api/cms/stats', methods=['GET'])
def cms_stats():
    return jsonify(get_stats())


@app.route('/api/cms/articles', methods=['GET'])
def cms_articles_list():
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    return jsonify(get_articles(status, category_id, search, limit, offset))


@app.route('/api/cms/articles/<int:article_id>', methods=['GET'])
def cms_article_detail(article_id):
    art = get_article(article_id)
    if art:
        return jsonify({'success': True, 'article': art})
    return jsonify({'success': False, 'error': '文章不存在'}), 404


@app.route('/api/cms/articles', methods=['POST'])
@require_auth('admin')
def cms_article_create(current_user):
    data = request.json
    if not data or not data.get('title'):
        return jsonify({'success': False, 'error': '标题不能为空'}), 400
    result = create_article(
        title=data['title'],
        content=data.get('content', ''),
        category_id=data.get('category_id'),
        tags=data.get('tags', ''),
        summary=data.get('summary', ''),
        status=data.get('status', 'draft'),
        author=data.get('author', '')
    )
    return jsonify(result), 201 if result['success'] else 400


@app.route('/api/cms/articles/<int:article_id>', methods=['PUT'])
@require_auth('admin')
def cms_article_update(current_user, article_id):
    data = request.json
    result = update_article(article_id, **{k: v for k, v in data.items() if v is not None})
    return jsonify(result)


@app.route('/api/cms/articles/<int:article_id>', methods=['DELETE'])
@require_auth('admin')
def cms_article_delete(current_user, article_id):
    result = delete_article(article_id)
    return jsonify(result)


@app.route('/api/cms/categories', methods=['GET'])
def cms_categories_list():
    return jsonify(get_categories())


@app.route('/api/cms/categories', methods=['POST'])
@require_auth('admin')
def cms_category_create(current_user):
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'success': False, 'error': '分类名称不能为空'}), 400
    result = create_category(
        name=data['name'],
        description=data.get('description', ''),
        sort_order=data.get('sort_order', 0)
    )
    return jsonify(result), 201 if result['success'] else 400


@app.route('/api/cms/categories/<int:category_id>', methods=['PUT'])
@require_auth('admin')
def cms_category_update(current_user, category_id):
    data = request.json
    result = update_category(category_id, **{k: v for k, v in data.items() if v is not None})
    return jsonify(result)


@app.route('/api/cms/categories/<int:category_id>', methods=['DELETE'])
@require_auth('admin')
def cms_category_delete(current_user, category_id):
    result = delete_category(category_id)
    return jsonify(result)


@app.route('/api/cms/tags', methods=['GET'])
def cms_tags_list():
    return jsonify(get_tags())


# ==================== Template Library ====================

@app.route('/templates')
def template_library_page():
    return render_template('template_library.html')


@app.route('/api/templates/categories', methods=['GET'])
def tlib_categories():
    return jsonify(tlib.get_all_categories())


@app.route('/api/templates/categories/<int:cat_id>', methods=['GET'])
def tlib_category(cat_id):
    return jsonify(tlib.get_category(cat_id))


@app.route('/api/templates/stats', methods=['GET'])
def tlib_stats():
    return jsonify(tlib.get_template_stats())


@app.route('/api/templates', methods=['GET'])
def tlib_templates_list():
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    return jsonify(tlib.get_templates(category_id, search, limit, offset))


@app.route('/api/templates/<int:template_id>', methods=['GET'])
def tlib_template_detail(template_id):
    return jsonify(tlib.get_template(template_id))


@app.route('/api/templates', methods=['POST'])
@require_auth('admin')
def tlib_template_create(current_user):
    data = request.json
    if not data or not data.get('title'):
        return jsonify({'success': False, 'error': '标题不能为空'}), 400
    result = tlib.create_template(
        title=data['title'],
        content=data.get('content', ''),
        category_id=data.get('category_id'),
        description=data.get('description', ''),
        standard_refs=data.get('standard_refs', ''),
        version=data.get('version', '1.0')
    )
    return jsonify(result), 201 if result['success'] else 400


@app.route('/api/templates/<int:template_id>', methods=['PUT'])
@require_auth('admin')
def tlib_template_update(current_user, template_id):
    data = request.json
    result = tlib.update_template(template_id, **{k: v for k, v in data.items() if v is not None})
    return jsonify(result)


@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
@require_auth('admin')
def tlib_template_delete(current_user, template_id):
    result = tlib.delete_template(template_id)
    return jsonify(result)


# ==================== Seal Design API ====================

@app.route('/seal_design')
def seal_design_page():
    return render_template('seal_design.html')


@app.route('/api/seal/catalog', methods=['GET'])
def seal_catalog():
    return jsonify(get_catalog())


@app.route('/api/seal/design', methods=['POST'])
def seal_design_calc():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供设计参数'}), 400
        result = calculate_seal_design(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/seal/compare', methods=['POST'])
def seal_compare():
    try:
        data = request.get_json()
        if not data or not data.get('configs'):
            return jsonify({'success': False, 'error': '请提供对比方案列表'}), 400
        results = run_compare(data['configs'], data.get('gas', 'N2'))
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/seal/sensitivity', methods=['POST'])
def seal_sensitivity():
    try:
        data = request.get_json()
        if not all(k in data for k in ('base_config', 'param_name', 'param_values')):
            return jsonify({'success': False, 'error': '请提供基准配置、参数名和参数值列表'}), 400
        results = run_sensitivity(data['base_config'], data['param_name'], data['param_values'])
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== 新闻资讯模块 ====================

@app.route('/news')
def news_page():
    """每日资讯页面"""
    return render_template('news.html')

@app.route('/api/news/latest')
def api_news_latest():
    """获取最新资讯"""
    try:
        entries = news_feed.get_latest_news()
        return jsonify({'success': True, 'entries': entries})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/news/import', methods=['POST'])
def api_news_import():
    """从markdown文件导入最新资讯"""
    try:
        result = news_feed.import_latest_markdown()
        if result:
            return jsonify({'success': True, 'message': 'Import success', 'data': result})
        return jsonify({'success': False, 'message': 'No news file found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/news/stats')
def api_news_stats():
    """获取资讯统计"""
    try:
        stats = news_feed.get_news_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/news/date/<date_str>')
def api_news_by_date(date_str):
    """按日期获取资讯"""
    try:
        entry = news_feed.get_news_by_date(date_str)
        if entry:
            return jsonify({'success': True, 'entry': entry})
        return jsonify({'success': False, 'message': 'No news for this date'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/news/dates')
def api_news_dates():
    """获取所有资讯日期"""
    try:
        dates = news_feed.get_all_dates()
        return jsonify({'success': True, 'dates': dates})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
