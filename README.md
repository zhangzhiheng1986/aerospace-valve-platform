# 🚀 航空航天阀门研发平台

一个全栈Web应用，可以将Python代码自动转换为可视化交互工具，专为航空航天阀门研发设计。

## ✨ 核心功能

### 1. Python代码智能分析
- 使用AST（抽象语法树）解析Python代码
- 自动识别函数、参数、返回值类型
- 检测导入的库（numpy、matplotlib等）
- 智能识别可视化代码

### 2. 自动UI生成
根据代码分析自动生成交互式界面：
- **数值参数** → 滑块控件
- **字符串参数** → 文本输入框
- **布尔参数** → 复选框
- **可视化代码** → 图表展示区

### 3. 安全代码执行
- 沙箱环境执行Python代码
- 捕获stdout输出（print语句）
- 自动保存matplotlib图表
- 返回执行结果和变量状态

### 4. 用户友好界面
- CodeMirror代码编辑器（语法高亮、自动补全）
- 实时代码分析
- 一键生成可视化工具
- 响应式布局

## 📦 技术栈

**后端：**
- Flask 3.0.0 - Web框架
- Flask-CORS - 跨域支持
- Python 3.11+ - 核心语言
- NumPy - 数值计算
- Matplotlib - 数据可视化

**前端：**
- HTML5 + CSS3 + JavaScript
- CodeMirror 5.65 - 代码编辑器
- Fetch API - 异步请求

## 🚀 快速开始

### 1. 安装依赖
```bash
cd aerospace-valve-platform/backend
pip install -r requirements.txt
```

### 2. 启动服务器
```bash
cd aerospace-valve-platform/backend
python app.py
```

### 3. 访问应用
打开浏览器访问：http://127.0.0.1:5000

## 📖 使用指南

### 基本流程
1. **输入代码**：在左侧代码编辑器输入Python代码（已预载阀门流量计算示例）
2. **分析代码**：点击"🔍 分析代码"按钮，查看代码结构
3. **生成工具**：点击"🎨 生成可视化工具"，自动生成交互界面
4. **执行代码**：在右侧面板调整参数，点击"运行代码"
5. **查看结果**：查看执行输出和可视化图表

### 示例代码说明
预载的示例代码实现了：
- `calculate_valve_flow()` - 计算阀门流量
- `plot_flow_curve()` - 绘制流量特性曲线
- 使用numpy进行数值计算
- 使用matplotlib生成可视化图表

### API接口

#### POST /api/analyze
分析Python代码
```json
{
  "code": "def add(a, b):\n    return a + b"
}
```

#### POST /api/execute
执行Python代码
```json
{
  "code": "print('Hello')",
  "params": {"a": 1, "b": 2}
}
```

#### POST /api/generate-ui
生成UI配置
```json
{
  "code": "def func(x): pass"
}
```

## 🏗️ 项目结构

```
aerospace-valve-platform/
├── backend/
│   ├── app.py                 # Flask后端应用
│   └── requirements.txt       # Python依赖
├── frontend/
│   └── index.html            # 前端页面
├── exports/                   # 导出文件目录
└── README.md                 # 项目说明
```

## 🔧 核心类说明

### PythonCodeAnalyzer
负责分析Python代码：
- `analyze()` - 主分析方法
- `_extract_imports()` - 提取导入信息
- `_extract_functions()` - 提取函数定义
- `_detect_visualization()` - 检测可视化库
- `_suggest_ui_components()` - 推荐UI组件

### CodeExecutor
负责安全执行代码：
- `execute(params)` - 执行代码
- 捕获stdout输出
- 保存matplotlib图表为base64
- 返回执行结果

## 🎯 应用场景

1. **航空航天阀门研发**
   - 流量计算工具
   - 压力特性分析
   - 性能曲线绘制

2. **工程计算工具快速原型**
   - 数学模型可视化
   - 参数化设计工具
   - 数据分析工具

3. **教学演示**
   - 算法可视化
   - 物理模拟演示
   - 交互式教材

## 🔒 安全说明

当前版本为开发原型，代码执行在沙箱环境中进行，但仍有改进空间：
- 限制可导入的库
- 限制执行时间
- 限制内存使用
- 禁用危险操作

**生产环境部署前请加强安全措施！**

## 📝 未来改进

- [ ] 支持更多可视化库（Plotly、Seaborn）
- [ ] 代码执行队列和超时控制
- [ ] 用户代码保存和分享
- [ ] 导出为独立Web应用
- [ ] 支持更多编程语言
- [ ] 添加用户认证系统

## 👨‍💻 开发者

作为全栈开发工程师，为您量身定制此平台。

## 📄 许可证

MIT License

---

**祝您使用愉快！如有问题，欢迎反馈。** 🎉
