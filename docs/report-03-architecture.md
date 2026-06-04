# 报告三：架构设计报告
## 角色：首席架构设计师

---

## 一、架构愿景

将当前"135条公式 + 13分类 + 双语SPA"的单体 Blueprint 应用，演进为**模块化、可扩展的世界级流体力学计算平台**，同时保持当前的简单性（无需引入前端框架）。

### 设计原则
1. **渐进增强** — 每次改动不影响现有功能
2. **模块即文件** — 延续PROJECT.md的架构哲学
3. **零框架** — Vanilla JS + Flask Blueprint
4. **性能优先** — 前端本地搜索、懒加载i18n、服务端缓存

---

## 二、系统架构总览

```
┌─────────────────────────────────────────────────────┐
│                   CDN / 反向代理                      │
│              (nginx / Serveo / Render)                │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│              Flask Application (WSGI)                │
│  ┌──────────────────────────────────────────────┐   │
│  │           Blueprint: fluid_mechanics          │   │
│  │  /api/fluid_mechanics/                       │   │
│  │    ├── /i18n?lang=zh&page=0&limit=20         │   │
│  │    ├── /search?q=雷诺                         │   │
│  │    ├── /compute  (POST)                       │   │
│  │    ├── /fluids                                │   │
│  │    ├── /unit-systems                          │   │
│  │    └── /categories                            │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │        计算引擎 (fluid_mechanics_calc.py)      │   │
│  │  ┌──────────┐ ┌───────────┐ ┌───────────┐   │   │
│  │  │ 公式执行器│ │单位转换器  │ │ 流体属性库 │   │   │
│  │  │compute()  │ │convert()  │ │FLUID_DB   │   │   │
│  │  └──────────┘ └───────────┘ └───────────┘   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│          前端 SPA (fluid_mechanics.html)             │
│  ┌──────────────────────────────────────────────┐   │
│  │  组件层                                      │   │
│  │  ├── SearchBar    (公式搜索)                  │   │
│  │  ├── CategoryNav  (分类导航)                  │   │
│  │  ├── FormulaPanel (公式卡片)                  │   │
│  │  ├── InputForm    (参数输入)                  │   │
│  │  ├── ResultView   (计算结果)                  │   │
│  │  ├── ChartView    (Chart.js图表)              │   │
│  │  ├── ComparePanel (对比模式)                  │   │
│  │  ├── FavoritesBar (收藏栏)                    │   │
│  │  └── ExportBar    (导出控制)                  │   │
│  │                                               │   │
│  │  数据层                                       │   │
│  │  ├── I18NManager  (双语管理)                  │   │
│  │  ├── UnitManager  (单位转换)                  │   │
│  │  ├── HistoryStore (localStorage历史)          │   │
│  │  ├── FavoritesStore (localStorage收藏)        │   │
│  │  └── StateManager (UI状态)                    │   │
│  │                                               │   │
│  │  渲染层                                       │   │
│  │  ├── MathJax (LaTeX公式渲染)                  │   │
│  │  ├── Chart.js (数据图表)                      │   │
│  │  └── CSS Custom Properties (深色主题)          │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 三、核心设计决策

### 3.1 单位系统架构

**决策**: SI内部存储 + 显示层转换

```
用户输入 (PSI, inch, °F)
       │
       ▼  unitManager.toSI()
┌──────────────┐
│ 内部全部SI单位 │ ← compute_formula() 始终用SI
│ Pa, m, K, kg │
└──────┬───────┘
       │
       ▼  unitManager.fromSI()
用户显示 (bar, mm, °C)
```

**优势**:
- 不改变任何现有calc函数
- 精度保留在计算层
- 仅需一个UnitManager JS类 + 一个后端转换表

### 3.2 i18n 懒加载策略

**问题**: `fluid_mechanics_i18n.py` 126KB, 全量加载浪费带宽

**方案**: 分页API + 前端缓存
```
GET /api/fluid_mechanics/i18n?page=0&limit=20
→ 返回前20条公式的i18n数据 + 总页码

首次加载: 仅加载分类列表 + 搜索索引 (约5KB)
点击分类: 懒加载该分类下公式 (约10-15KB/分类)
搜索: 使用本地缓存的轻量搜索索引
```

### 3.3 搜索架构

**决策**: 前端内存搜索 (无需后端搜索)

```
启动时: GET /api/fluid_mechanics/search-index
→ 返回 [{id, name_zh, name_en, category, keywords}, ...]
→ 约8KB紧凑JSON

用户输入: 前端 Fuse.js (或自写 fuzzyMatch)
→ <100ms 响应
→ 无服务端负载
```

### 3.4 导出架构

```
前端收集: 公式名 + 输入/输出值 + 单位 + 时间戳
        │
        ├── PDF: → POST /api/fluid_mechanics/export/pdf
        │         后端: WeasyPrint/reportlab 生成
        │
        ├── Excel: → POST /api/fluid_mechanics/export/xlsx
        │           后端: openpyxl 生成
        │
        └── Clipboard: → 前端 navigator.clipboard.writeText()
```

---

## 四、数据模型设计

### 4.1 公式元数据 (增强版)

```python
FORMULA_I18N = {
    "reynolds": {
        "name_zh": "雷诺数",
        "name_en": "Reynolds Number",
        "desc_zh": "...",
        "desc_en": "...",
        "latex": r"Re = \frac{\rho V D}{\mu}",
        "category": "4_pipe_flow",           # ← NEW: 必须添加
        "keywords": ["雷诺", "reynolds", "Re", "湍流", "turbulent"],  # ← NEW
        "inputs": {...},
        "output": {...},
        "application_zh": "...",
        "application_en": "...",              # ← NEW
        "reference": "ISO 5167-1:2022",      # ← NEW
        "limitation_zh": "适用于牛顿流体，Re < 10^8",  # ← NEW
        "limitation_en": "Newtonian fluids, Re < 10^8",
    }
}
```

### 4.2 单位转换元数据

```python
UNIT_SYSTEMS = {
    "SI": {
        "length": {"unit": "m", "factor": 1.0, "label": "m"},
        "pressure": {"unit": "Pa", "factor": 1.0, "label": "Pa"},
        "density": {"unit": "kg/m3", "factor": 1.0, "label": "kg/m³"},
        ...
    },
    "Imperial": {
        "length": {"unit": "ft", "factor": 3.28084, "label": "ft"},
        "pressure": {"unit": "psi", "factor": 0.000145038, "label": "psi"},
        ...
    },
    "US": {
        "length": {"unit": "in", "factor": 39.3701, "label": "in"},
        ...
    }
}
```

### 4.3 localStorage 数据结构

```javascript
// Favorites
{ "fm_favorites": ["reynolds", "darcy_dp", "valve_Cv"] }

// History (ring buffer, max 20)
{ "fm_history": [
    { "formula": "reynolds", "inputs": {"V":10,"D":0.05,"rho":1000,"mu":0.001},
      "outputs": {"Re":500000}, "unitSystem": "SI", "ts": 1717459200 },
    ...
]}

// User preferences
{ "fm_prefs": { "unitSystem": "SI", "lang": "zh", "theme": "dark" } }
```

---

## 五、API 设计 (新增/修改)

### 新增端点

| 方法 | 路径 | 功能 | 请求/响应 |
|------|------|------|-----------|
| GET | `/api/fluid_mechanics/search-index` | 搜索索引 | → `[{id, name_zh, name_en, cat, keywords}]` |
| GET | `/api/fluid_mechanics/i18n?page=0&limit=20` | 分页i18n | → `{total, page, formulas:[...]}` |
| GET | `/api/fluid_mechanics/unit-systems` | 单位系统列表 | → `{SI:{...}, Imperial:{...}, US:{...}}` |
| POST | `/api/fluid_mechanics/export/pdf` | 导出PDF | ← `{formula_id, inputs, outputs, unit_sys}` |
| POST | `/api/fluid_mechanics/export/xlsx` | 导出Excel | ← 同上 |

### 修改端点

| 方法 | 路径 | 变更 |
|------|------|------|
| POST | `/api/fluid_mechanics/compute` | 响应新增 `units: {...}` 字段，返回输出单位映射 |
| GET | `/api/fluid_mechanics/i18n` | 新增 `page`/`limit` 参数，默认不分页 |

---

## 六、前端文件结构规划

```
frontend/
├── fluid_mechanics.html    (主SPA, ~55KB, 当前34KB)
├── css/
│   └── fluid-theme.css     (提取出来的主题CSS)
└── js/
    ├── fm-i18n.js          (I18N管理)
    ├── fm-units.js         (单位转换)
    ├── fm-search.js        (搜索逻辑)
    ├── fm-charts.js        (Chart.js图表)
    ├── fm-storage.js       (localStorage管理)
    └── fm-export.js        (导出功能)
```

**决策**: Phase 1 先保留单文件HTML (避免重构风险)，JS模块以内联`<script>`标签组织。Phase 2 再拆分。

---

## 七、性能优化策略

| 策略 | 实施 | 预期效果 |
|------|------|----------|
| i18n分页懒加载 | API改造 + 前端按类加载 | 初始JS从126KB→5KB |
| 搜索索引预计算 | 启动时生成紧凑JSON | 搜索 <50ms |
| MathJax按需渲染 | 仅渲染当前公式 | 页面重绘 -70% CPU |
| CSS变量主题 | 已有，保持 | 主题切换 0ms |
| localStorage缓存 | 前端持久化 | 二次访问秒开 |
| 服务端ETag | Flask自动 | 304缓存命中 |

---

## 八、部署架构（不变）

```
GitHub (zhangzhiheng1986/aerospace-valve-platform)
    │
    ├── Render (自动部署, 海外)
    │   └── gunicorn + wsgi.py
    │
    └── 本地 (开发)
        ├── Flask :5000
        └── nginx :80 (可选反向代理)
```

---

*报告编制日期: 2026-06-04 | 设计师: 架构设计AI Agent v1.0*
