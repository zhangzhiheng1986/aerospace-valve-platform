# 报告五：全面测试计划
## 角色：首席测试工程专家

---

## 一、测试策略矩阵

| 测试层 | 覆盖目标 | 工具 | 通过标准 |
|--------|----------|------|----------|
| **L0: 单元测试** | 135条calc函数 | pytest | 100% pass |
| **L1: API测试** | 所有fluid_mechanics端点 | requests/pytest | 200 OK + 字段完整性 |
| **L2: 集成测试** | 前后端链路 | Selenium/手动 | 端到端用例通过 |
| **L3: 回归测试** | 已有功能不受影响 | 全量测试套件 | 无回归失败 |
| **L4: 性能测试** | 加载/搜索/计算延迟 | Lighthouse + timing | 满足NFR标准 |
| **L5: 兼容性测试** | 5浏览器 + 移动端 | BrowserStack/手动 | UI无断裂 |
| **L6: 国际化测试** | 中英双语完整性 | DOM遍历 | 0%缺失/泄漏 |

---

## 二、L0: 单元测试用例 (Calc Engine)

```python
# test_calc_engine.py
TEST_CASES = [
    # Basic Properties
    {"id": "density", "inputs": {"mass": 10, "volume": 2}, "output": "density", "expected": 5.0, "tolerance": 0.001},
    {"id": "specific_weight", "inputs": {"rho": 1000, "g": 9.81}, "output": "gamma", "expected": 9810, "tolerance": 1},
    {"id": "reynolds", "inputs": {"rho": 1000, "V": 2, "D": 0.05, "mu": 0.001}, "output": "Re", "expected": 100000, "tolerance": 1},
    {"id": "f_laminar", "inputs": {"Re": 1000}, "output": "f", "expected": 0.064, "tolerance": 0.001},
    {"id": "f_blasius", "inputs": {"Re": 50000}, "output": "f", "expected": 0.0208, "tolerance": 0.001},
    {"id": "darcy_dp", "inputs": {"f": 0.02, "L": 100, "D": 0.1, "rho": 1000, "V": 3}, "output": "dP", "expected": 90000, "tolerance": 100},
    {"id": "valve_Cv", "inputs": {"Q_gpm": 100, "dP_psi": 10, "SG": 1.0}, "output": "Cv", "expected": 31.62, "tolerance": 0.1},
    {"id": "orifice_flow", "inputs": {"C_d": 0.62, "A_o": 0.00196, "rho": 1000, "dP": 50000}, "output": "Q", "expected": 0.0121, "tolerance": 0.001},
    {"id": "mach", "inputs": {"V": 340, "a": 340}, "output": "M", "expected": 1.0, "tolerance": 0.001},
    {"id": "normal_shock_P", "inputs": {"M1": 2.0, "k": 1.4}, "output": "P_ratio", "expected": 4.5, "tolerance": 0.1},
    {"id": "joukowsky", "inputs": {"rho": 1000, "a": 1400, "dV": 2}, "output": "dP", "expected": 2.8e6, "tolerance": 1000},
    {"id": "weymouth", "inputs": {"P1_psi": 800, "P2_psi": 600, "T_R": 520, "L_mi": 50, "D_in": 12, "SG": 0.6, "Z": 0.9, "E": 1.0}, "output": "Q_scfd", "tolerance": 0.01},
    {"id": "pump_power", "inputs": {"Q": 0.01, "dP": 200000, "eta": 0.8}, "output": "P_pump", "expected": 2500, "tolerance": 10},
    # ... 剩余122条公式的测试用例
]

def test_all_formulas():
    results = []
    for tc in TEST_CASES:
        r = fmc.compute_formula(tc["id"], tc["inputs"])
        actual = r["results"][tc["output"]]
        if tc.get("tolerance"):
            ok = abs(actual - tc["expected"]) <= tc["tolerance"]
        else:
            ok = actual == tc["expected"]
        results.append({"id": tc["id"], "pass": ok, "expected": tc["expected"], "actual": actual})
    return results
```

**目标**: 135条公式 × 1-3个测试用例/公式 = ~200个测试点

---

## 三、L1: API测试用例

```python
# test_api_endpoints.py
API_TESTS = [
    {"method": "GET", "path": "/fluid_mechanics", "expected_status": 200, "check": "html_contains:fluid-mechanics"},
    {"method": "GET", "path": "/api/fluid_mechanics/i18n", "expected_status": 200, "check": "json_keys:categories,fluids,formulas"},
    {"method": "GET", "path": "/api/fluid_mechanics/i18n?page=0&limit=20", "expected_status": 200, "check": "json_keys:total,page,formulas"},
    {"method": "GET", "path": "/api/fluid_mechanics/search-index", "expected_status": 200, "check": "json_list_min:50"},
    {"method": "GET", "path": "/api/fluid_mechanics/categories", "expected_status": 200, "check": "json_count:13"},
    {"method": "GET", "path": "/api/fluid_mechanics/unit-systems", "expected_status": 200, "check": "json_keys:SI,Imperial,US"},
    {"method": "POST", "path": "/api/fluid_mechanics/compute", "body": {"formula_id":"density","inputs":{"mass":10,"volume":2}}, "expected_status": 200, "check": "json_path:results.density==5.0"},
    {"method": "POST", "path": "/api/fluid_mechanics/compute", "body": {"formula_id":"nonexistent","inputs":{}}, "expected_status": 200, "check": "json_key:error"},
]
```

---

## 四、L2: 前端集成测试场景

| 场景 | 步骤 | 验证点 |
|------|------|--------|
| SC1: 搜索→计算 | 输入"雷诺"→点击公式→填入数值→点计算 | 展示结果含LaTeX |
| SC2: 单位切换 | 选Imperial→输入psi/ft值→计算→切换SI | 数值等价转换 |
| SC3: 导出PDF | 计算→点导出→选PDF | 下载PDF文件，内容完整 |
| SC4: 收藏 | 点★→切换"我的收藏"标签页 | 公式出现在收藏列表 |
| SC5: 双语切换 | 点中/EN按钮 | 全页面UI语言切换 |
| SC6: 移动端 | iPhone模拟→搜索→计算 | 汉堡菜单正常，输入触碰正常 |
| SC7: 对比模式 | 左侧输入A→右侧输入B→对比 | 两列结果并排显示 |

---

## 五、L4: 性能基准

```javascript
// 性能度量脚本（浏览器console）
const metrics = {
    pageLoad: performance.timing.loadEventEnd - performance.timing.navigationStart,
    firstFormulaLoad: /* 点击第一个公式到渲染完成 */,
    searchTime: /* 输入到结果出现 */,
    computeTime: /* fetch到结果渲染 */,
    memoryUsage: performance.memory?.usedJSHeapSize,
};

// 目标
// pageLoad < 1500ms
// firstFormulaLoad < 300ms
// searchTime < 100ms
// computeTime < 500ms
```

---

## 六、已知Bug回归清单

| BugID | 描述 | 文件 | 状态 |
|-------|------|------|------|
| BUG-01 | check_valve.py KeyError: 'nominal_flow_rate' | check_valve.py:355 | 未修复 |
| BUG-02 | seal_design.py KeyError: 'seat_material' | seal_design.py:356 | 未修复 |
| BUG-03 | TEMPLATES list路由404 | valve_modules.py | 未修复 |
| BUG-04 | News import正则脆弱性 | news.py | 已修复(fc9f14a) |
| BUG-05 | QJ20156 ZeroDivisionError | qj20156_module.py | 已修复(3026eb8) |
| BUG-06 | MathJax二次跳转不渲染 | fluid_mechanics.html | 已修复 |
| BUG-07 | LaTeX Unicode转义序列 | fluid_mechanics_i18n.py | 已修复 |

---

## 七、上线检查清单

- [ ] 所有135条公式category字段非空
- [ ] 搜索索引包含所有公式
- [ ] 三制式单位切换等价性验证
- [ ] PDF导出含中文，无乱码
- [ ] 移动端Lighthouse > 90
- [ ] API端点全部返回200
- [ ] 无console错误（JS运行时）
- [ ] 无UnicodeEncodeError（GBK环境）
- [ ] 计算精度回归测试全通过
- [ ] 旧版API兼容（i18n不分页时仍返回全量）

---

*报告编制日期: 2026-06-04 | 工程师: 测试工程AI Agent v1.0*
