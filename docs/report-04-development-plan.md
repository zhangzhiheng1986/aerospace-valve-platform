# 报告四：全栈开发实施计划
## 角色：首席全栈开发工程师

---

## 一、开发总览

基于报告二（需求分析）和报告三（架构设计），Phase 1 开发任务分解如下。

### Sprint 1: 数据修复 (2h) 🔴 Blocking

| Task | 文件 | 改动 |
|------|------|------|
| T1.1 | `fluid_mechanics_i18n.py` | 给135条公式添加 `category` 字段 |
| T1.2 | `fluid_mechanics_i18n.py` | 添加 `keywords` 搜索关键词列表 |
| T1.3 | `fluid_mechanics_i18n.py` | 添加 `reference` 参考文献字段 |
| T1.4 | `fluid_mechanics_i18n.py` | 补全 `name_en` 英文名称 |
| T1.5 | `fluid_mechanics_calc.py` | 确保 `get_all_formulas()` 返回正确映射 |

### Sprint 2: 搜索系统 (1.5h) 🔴 Core

| Task | 文件 | 改动 |
|------|------|------|
| T2.1 | `fluid_mechanics_calc.py` | 新增 `build_search_index()` 函数 |
| T2.2 | `app/blueprints/fluid_mechanics.py` | 新增 `GET /api/fluid_mechanics/search-index` 端点 |
| T2.3 | `fluid_mechanics.html` | 前端搜索栏UI + fuzzyMatch逻辑 |
| T2.4 | `fluid_mechanics.html` | 搜索结果下拉面板 + 键盘导航 |

### Sprint 3: 单位系统 (3h) 🔴 Core

| Task | 文件 | 改动 |
|------|------|------|
| T3.1 | 新建 `backend/unit_converter.py` | 三制式转换表 + `convert(value, from_unit, to_unit)` |
| T3.2 | `app/blueprints/fluid_mechanics.py` | `GET /api/fluid_mechanics/unit-systems` 端点 |
| T3.3 | `fluid_mechanics.html` | UnitManager JS类 + 单位选择器UI |
| T3.4 | `fluid_mechanics.html` | 输入/输出标签+占位符随单位变化 |
| T3.5 | `fluid_mechanics.html` | 所有fetch调用前做单位转换到SI |

### Sprint 4: 导出功能 (1.5h) 🟡 High Value

| Task | 文件 | 改动 |
|------|------|------|
| T4.1 | `fluid_mechanics.html` | 剪贴板复制按钮 (navigator.clipboard) |
| T4.2 | `fluid_mechanics.html` | 打印友好CSS (@media print) |
| T4.3 | 新建 `backend/export_utils.py` | PDF生成 (reportlab) |
| T4.4 | `app/blueprints/fluid_mechanics.py` | `POST /api/fluid_mechanics/export/pdf` |

### Sprint 5: UX增强 (2h) 🟡 High Value

| Task | 文件 | 改动 |
|------|------|------|
| T5.1 | `fluid_mechanics.html` | 分类导航改为图标+计数面板 |
| T5.2 | `fluid_mechanics.html` | 收藏★按钮 + localStorage |
| T5.3 | `fluid_mechanics.html` | "我的收藏"标签页 |
| T5.4 | `fluid_mechanics.html` | 计算历史记录 (最近20条) |
| T5.5 | `fluid_mechanics.html` | 公式适用条件/限制提示 (Tooltip) |

---

## 二、技术实施细节

### T1: i18n category补全脚本

```python
# 通过calc模块的get_all_formulas()反向映射
FORMULA_TO_CATEGORY = {}
for cat_id, cat_data in get_all_formulas().items():
    for f in cat_data.get("formulas", []):
        FORMULA_TO_CATEGORY[f["id"]] = cat_id

# 写入FORMULA_I18N的每个条目
for fk in FORMULA_I18N:
    if fk in FORMULA_TO_CATEGORY:
        FORMULA_I18N[fk]["category"] = FORMULA_TO_CATEGORY[fk]
```

### T2: 搜索实现

```javascript
// 前端fuzzyMatch (零依赖)
function fuzzyMatch(query, text) {
    const q = query.toLowerCase();
    const t = text.toLowerCase();
    let qi = 0;
    for (let i = 0; i < t.length && qi < q.length; i++) {
        if (t[i] === q[qi]) qi++;
    }
    return qi === q.length;
}

// 搜索执行
function searchFormulas(query) {
    if (query.length < 2) return [];
    return SEARCH_INDEX.filter(f =>
        fuzzyMatch(query, f.name_zh) ||
        fuzzyMatch(query, f.name_en) ||
        f.keywords.some(k => fuzzyMatch(query, k))
    ).slice(0, 20);
}
```

### T3: 单位转换器

```python
# backend/unit_converter.py
UNIT_CONVERSIONS = {
    "length": {"m": 1.0, "mm": 1000.0, "cm": 100.0, "ft": 3.28084, "in": 39.3701},
    "pressure": {"Pa": 1.0, "kPa": 0.001, "bar": 1e-5, "psi": 0.000145038, "MPa": 1e-6},
    "density": {"kg/m3": 1.0, "g/cm3": 0.001, "lb/ft3": 0.062428},
    "velocity": {"m/s": 1.0, "ft/s": 3.28084, "km/h": 3.6, "mph": 2.23694},
    "viscosity_dynamic": {"Pa.s": 1.0, "cP": 1000.0, "lb/(ft.s)": 0.671969},
    "viscosity_kinematic": {"m2/s": 1.0, "cSt": 1e6, "ft2/s": 10.7639},
    "flow_rate": {"m3/s": 1.0, "L/s": 1000.0, "gpm": 15850.3, "scfm": 2118.88},
    "temperature": {"K": 1.0, "C": "offset", "F": "offset"},
    "force": {"N": 1.0, "lbf": 0.224809, "kgf": 0.101972},
    "power": {"W": 1.0, "kW": 0.001, "hp": 0.00134102},
}

def convert(value, from_unit, to_unit, category):
    if category == "temperature":
        # Special offset handling
        ...
    factor_from = UNIT_CONVERSIONS[category][from_unit]
    factor_to = UNIT_CONVERSIONS[category][to_unit]
    return value * factor_to / factor_from
```

---

## 三、文件变更清单 (Phase 1)

| 文件 | 操作 | 预计Δ行数 |
|------|------|-----------|
| `fluid_mechanics_i18n.py` | 修改 | +500 (category/keywords/ref/en补全) |
| `fluid_mechanics_calc.py` | 修改 | +50 (search_index函数) |
| `app/blueprints/fluid_mechanics.py` | 修改 | +80 (新端点) |
| `backend/unit_converter.py` | 新建 | +150 |
| `backend/export_utils.py` | 新建 | +100 |
| `fluid_mechanics.html` | 修改 | +400 (搜索/单位/导出/收藏) |

---

## 四、风险管理

| 风险 | 缓解 |
|------|------|
| HTML文件过大(34→55KB+) | PHP2再拆分为CSS+JS外部文件 |
| 单位转换精度损失 | 内部全SI，仅显示层转换 |
| i18n文件126KB+新增字段更大 | 分页API懒加载 |
| GBK编码破坏新文件 | 所有.py文件ASCII-only |
| 大量公式输入要求 | 流体属性库预填减少输入 |

---

*报告编制日期: 2026-06-04 | 工程师: 全栈开发AI Agent v1.0*
