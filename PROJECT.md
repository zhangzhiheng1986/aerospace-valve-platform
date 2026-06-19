# Avis 航空航天阀门研发平台 - 项目完整文档

## 📋 项目概述

### 项目名称
**Avis** (Aerospace Valve Intelligent Suite) - 航空航天阀门研发智能套件
官方中文名: **Avis 航空航天阀门研发平台**

### 项目代号
- 正式代号: **Avis** (2026-06-19 起启用)
- 历史代号: AV-RD (Aerospace Valve R&D Platform, 2026-05-29 ~ 2026-06-19)

### 项目目标
将Tkinter桌面程序 (`solenoid_optimizer_gui_1.py`) 转换为Web平台的在线可视化工具，让用户可以通过浏览器进行电磁阀优化计算。

### 完成时间
2026-05-14 22:25 GMT+8

### 当前状态
✅ **已完成并上线运行**

---

## 🎯 核心功能

### 1. 电磁阀优化算法
- **PSO (粒子群优化)**：全局搜索最优线圈参数
- **穷举搜索**：对AWG线径进行遍历，确保找到最优解
- **多约束满足**：
  - 外径约束
  - 轴向长度约束
  - 电流限制
  - 温度限制（热平衡）
  - 气隙磁通密度约束

### 2. 物理模型
- **电磁学计算**：安培定律、磁通量、电磁力
- **热力学计算**：铜线电阻、热平衡、温升
- **材料特性**：铜线参数、饱和磁通密度

### 3. Web界面功能
- 参数输入（内径、外径、轴向长度、气隙等）
- 实时优化进度显示
- 详细结果展示（最佳AWG、电磁力、电流、温度、匝数、线圈质量、功耗）
- 日志显示区域

---

## 🛠️ 技术架构

### 后端技术栈
- **Python 3.x**
- **Flask**：Web框架
- **NumPy**：数值计算
- **dataclasses**：数据结构定义

### 前端技术栈
- **HTML5 + CSS3**：页面结构和样式
- **Vanilla JavaScript**：前端逻辑
- **Fetch API**：与后端通信

### 项目文件结构
```
aerospace-valve-platform/
├── backend/
│   ├── app.py                    # Flask后端主程序
│   ├── solenoid_optimizer.py     # 优化引擎（核心算法）
│   ├── test_api_simple.py        # API测试脚本
│   └── test_api.py               # API测试脚本（含emoji，有编码问题）
└── frontend/
    └── solenoid.html             # 前端页面
```

### 关键API端点
1. **`/solenoid`** (GET)
   - 功能：返回前端页面
   - 返回：HTML页面

2. **`/api/solenoid/optimize`** (POST)
   - 功能：执行电磁阀优化
   - 请求体：
     ```json
     {
       "geom_params": {},
       "n_particles": 20,
       "n_iterations": 50
     }
     ```
   - 返回：
     ```json
     {
       "success": true,
       "best_awg": 27,
       "best_fit": 24.451,
       "best_info": {
         "N": 1821,
         "I": 0.599,
         "R_hot": 58.2,
         "temperature": 180.0,
         "F_N": 24.451,
         "D_out_actual_mm": 38.5,
         "saturation": false
       },
       "mass_g": 48.5,
       "power_W": 20.9
     }
     ```

---

## 🚀 启动和部署

### 当前运行状态
- **服务器**：Flask开发服务器
- **地址**：http://127.0.0.1:5000
- **局域网地址**：http://10.104.25.172:5000
- **进程ID**：14388
- **Session ID**：dawn-dune
- **状态**：✅ 运行中

### 启动命令
```powershell
cd aerospace-valve-platform\backend
python app.py
```

### 停止命令
```powershell
# 方法1：在运行服务器的终端按 Ctrl+C
# 方法2：通过进程ID杀掉进程
taskkill /PID 14388 /F
```

### 访问方式
在浏览器中打开：
```
http://127.0.0.1:5000/solenoid
```

或局域网访问：
```
http://10.104.25.172:5000/solenoid
```

---

## 🐛 已修复的问题

### 1. NumPy类型JSON序列化错误
- **错误**：`TypeError: Object of type bool_ is not JSON serializable`
- **原因**：NumPy的`bool_`、`int64`、`float64`等类型无法被Flask的`jsonify()`序列化
- **解决**：添加`convert_numpy_types()`函数，递归转换NumPy类型为原生Python类型
- **代码位置**：`solenoid_optimizer.py` 第317-331行

### 2. `Fields` vs `fields` 名称错误
- **错误**：`NameError: name 'Fields' is not defined`
- **原因**：代码中使用了`Fields`（大写F），但正确函数名是`fields`（小写f，从dataclasses导入）
- **解决**：将所有`Fields`改为`fields`
- **代码位置**：`solenoid_optimizer.py` 第451行附近

### 3. 模块导入错误
- **错误**：`ModuleNotFoundError: No module named 'solenoid_optimizer_v3'`
- **原因**：`app.py`尝试从已删除的`solenoid_optimizer_v3.py`导入
- **解决**：更新`app.py`中的导入语句，从正确的`solenoid_optimizer.py`导入
- **代码位置**：`app.py` 第18行

### 4. 文件混乱问题
- **问题**：系统中存在多个版本的优化器文件（`solenoid_optimizer.py`和`solenoid_optimizer_v3.py`）
- **解决**：删除旧的`solenoid_optimizer_v3.py`，只保留正确的`solenoid_optimizer.py`

### 5. PowerShell编码问题
- **问题**：测试脚本中的emoji导致Unicode编码错误
- **解决**：创建`test_api_simple.py`（不含emoji）用于测试

---

## 📝 核心代码说明

### 1. `convert_numpy_types()` 函数
**作用**：递归转换NumPy类型为原生Python类型，解决JSON序列化问题

**代码**：
```python
def convert_numpy_types(obj):
    """递归转换NumPy类型为原生Python类型"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return convert_numpy_types(obj.tolist())
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj
```

**使用位置**：`run_optimization()`函数返回结果前调用

### 2. Flask API端点
**代码** (`app.py`):
```python
@app.route('/api/solenoid/optimize', methods=['POST'])
def solenoid_optimize():
    data = request.get_json()
    geom_params = data.get('geom_params', {})
    n_particles = data.get('n_particles', 20)
    n_iterations = data.get('n_iterations', 50)
    
    # 日志捕获
    log_capture = io.StringIO()
    def log_callback(msg):
        log_capture.write(msg + '\n')
    
    result = run_optimization(geom_params, n_particles, n_iterations, log_callback)
    result['logs'] = log_capture.getvalue().split('\n')
    
    return jsonify(result)
```

### 3. 前端AJAX调用
**代码** (`solenoid.html`):
```javascript
fetch('/api/solenoid/optimize', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        geom_params: getParamsFromForm(),
        n_particles: document.getElementById('n_particles').value,
        n_iterations: document.getElementById('n_iterations').value
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        displayResults(data);
    } else {
        alert('优化失败: ' + data.message);
    }
});
```

---

## 📚 依赖和环境

### Python依赖
```txt
Flask>=2.0.0
flask-cors>=3.0.0
numpy>=1.20.0
```

### 系统环境
- **操作系统**：Windows 10 (10.0.22621)
- **Python版本**：3.x
- **Node版本**：v22.21.1 (OpenClaw环境)
- **Shell**：PowerShell

---

## 🔧 维护和更新指南

### 修改优化算法
1. 编辑 `backend/solenoid_optimizer.py`
2. 重启Flask服务器：
   ```powershell
   # 停止旧服务器
   taskkill /PID <旧PID> /F
   
   # 启动新服务器
   cd aerospace-valve-platform\backend
   python app.py
   ```

### 修改前端页面
1. 编辑 `frontend/solenoid.html`
2. 刷新浏览器页面（无需重启服务器）

### 修改API接口
1. 编辑 `backend/app.py`
2. 重启Flask服务器

### 查看服务器日志
```powershell
# 如果服务器在前台运行，日志会直接输出到终端
# 如果服务器在后台运行（通过OpenClaw的exec工具），使用：
process log --sessionId dawn-dune --limit 50
```

---

## 🚀 未来改进方向

### 1. 性能优化
- [ ] 使用生产级WSGI服务器（如Gunicorn、uWSGI）替代Flask开发服务器
- [ ] 添加计算缓存机制，避免重复计算
- [ ] 实现异步计算，避免阻塞Web请求

### 2. 功能扩展
- [ ] 添加更多可视化图表（电磁力曲线、温度分布等）
- [ ] 支持参数保存和加载
- [ ] 添加用户认证系统
- [ ] 支持多种优化算法选择（PSO、 Genetic Algorithm等）

### 3. 用户体验
- [ ] 添加实时进度条
- [ ] 支持中英文切换
- [ ] 添加参数说明tooltip
- [ ] 优化移动端显示

### 4. 部署优化
- [ ] 使用Docker容器化部署
- [ ] 配置Nginx反向代理
- [ ] 添加HTTPS支持
- [ ] 实现负载均衡

---

## 📊 测试结果

### API测试
- **测试脚本**：`test_api_simple.py`
- **测试时间**：2026-05-14 22:24 GMT+8
- **测试结果**：
  - ✅ 状态码：200
  - ✅ 响应时间：0.02s
  - ✅ 优化成功：最佳AWG 27，电磁力 24.451 N

### 前端测试
- **测试时间**：2026-05-14 22:24 GMT+8
- **测试结果**：
  - ✅ 页面加载成功（HTTP 200）
  - ✅ 内容长度：24,624 字节
  - ✅ 编码：UTF-8

---

## 📞 联系方式和支持

如需进一步开发或遇到问题，请联系：
- **开发者**：QClaw (OpenClaw Agent)
- **用户**：张老师（张小贤）
- **工作区**：`C:\Users\Administrator\.qclaw\workspace`

---

## 📅 项目时间线

| 时间 | 事件 |
|------|------|
| 2026-05-14 21:31 | 项目启动，分析用户需求 |
| 2026-05-14 21:46 | 创建后端优化引擎 `solenoid_optimizer.py` |
| 2026-05-14 21:59 | 更新Flask后端，添加电磁阀优化API |
| 2026-05-14 22:08 | 创建前端页面 `solenoid.html` |
| 2026-05-14 22:15 | 修复NumPy JSON序列化错误 |
| 2026-05-14 22:17 | 修复`Fields`名称错误 |
| 2026-05-14 22:21 | 删除旧版本文件，清理项目 |
| 2026-05-14 22:24 | 测试通过，项目上线 |
| 2026-05-14 22:28 | 完成项目文档 |

---

## 🎓 经验教训

### 1. 跨平台兼容性
- Windows PowerShell不支持Linux命令（如`awk`、`xargs`）
- 需要使用Windows等效命令（如`Select-String`、`ForEach-Object`）

### 2. NumPy类型处理
- NumPy类型（如`np.bool_`、`np.int64`）不是JSON可序列化的
- 需要显式转换为原生Python类型

### 3. 文件管理
- 避免创建多个版本的相似文件（如`v3`后缀）
- 及时清理旧版本文件，避免导入混乱

### 4. 编码问题
- Windows PowerShell默认编码可能不是UTF-8
- 测试脚本应避免使用emoji等特殊字符

### 5. 调试技巧
- 使用`try-except`捕获详细错误信息
- 在Flask中添加日志捕获功能
- 使用`process log`查看后台服务器输出

---

## 📖 参考资料

### Python库文档
- [Flask官方文档](https://flask.palletsprojects.com/)
- [NumPy官方文档](https://numpy.org/doc/)
- [dataclasses官方文档](https://docs.python.org/3/library/dataclasses.html)

### 优化算法
- PSO (Particle Swarm Optimization) 算法原理
- 电磁阀电磁学原理
- 热力学平衡计算

### Web开发
- [MDN Web Docs](https://developer.mozilla.org/)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

---

## 🔚 结语

本项目成功将Tkinter桌面应用转换为Web应用，实现了核心优化算法的完整迁移，并提供了友好的Web界面。

项目现已上线运行，用户可以通过浏览器在线使用电磁阀优化工具，无需安装Python环境或依赖库。

如有任何问题或需要进一步开发，请参考本文档的"维护和更新指南"章节。

---

**文档版本**：v1.0  
**最后更新**：2026-05-14 22:30 GMT+8  
**作者**：QClaw (OpenClaw Agent)
