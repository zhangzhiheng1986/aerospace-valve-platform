# Sprint 3 — OrchestratorAgent + 多Agent协作管道

**时间**: 2026-06-12 13:57-14:18
**状态**: ✅ 交付

## 目标

实现 MVP 8 周路线中的 Sprint 3：OrchestratorAgent + Design/Compliance 子Agent 协作管道。

## 交付物

### 1. `backend/orchestrator_agent.py` (~22KB)
核心编排引擎：
- **OrchestratorAgent**: 主引擎，ThreadPoolExecutor 并发执行
- **TaskDecomposer**: 规则驱动任务分解（5种意图→4种配方）
- **AgentRegistry**: 子Agent注册中心，工具→Agent路由映射
- **SubAgent**: 领域Agent基类，工具注册+超时执行+线程安全
- **`_json_safe()`**: 递归JSON序列化清理（解决MaterialCategory等对象不可序列化）

关键设计：
- 依赖拓扑排序：每个SubTask声明depends_on，引擎按波次→并发行执行独立任务
- 失败隔离：子任务失败不会影响独立任务，依赖失败则标记pending
- 简单查询路由：`_is_simple_query()` 检测 informational/design 区分

### 2. `backend/app/blueprints/ai_agent.py` 扩展
新增3个端点：
- `POST /api/agent/orchestrate` — 多Agent编排入口
- `GET /api/agent/orchestrator/stats` — Agent池统计
- `_init_orchestrator()` — 懒加载绑定Design+Compliance两个子Agent

### 3. Agent矩阵
| Agent | 角色 | 工具数 | 工具列表 |
|---|---|---|---|
| Design Expert | design | 8 | query_material, analyze_solenoid, analyze_prv, design_spring, design_oring, run_fluid_calculation, identify_formula |
| Compliance Checker | compliance | 4 | check_compliance, verify_leak, verify_rated, verify_life |

### 4. 意图配方（TaskDecomposer.RECIPES）
- `design_solenoid_system`: material → solenoid → compliance
- `design_pressure_valve_system`: material → prv → compliance
- `design_review`: material + spring (parallel) → compliance
- `validate_design`: compliance only
- `material_analysis`: material + fluid_calc (parallel)

## 测试结果

4/5 通过。1个失败是PRV模块自身的 `float division by zero`（工具层bug，非编排层问题）。

| # | 场景 | 结果 | 耗时 |
|---|------|------|------|
| 1 | Stats端点（2 Agent注册） | ✅ | - |
| 2 | 简单查询路由（TC4是什么） | ✅ | - |
| 3 | 电磁阀全链（3子任务） | ✅ | 1651ms |
| 4 | PRV+合规 | ⚠️ | 6ms (PRV ZeroDivision) |
| 5 | 设计审查（3子任务） | ✅ | 1441ms |

## 已知问题
1. PRV工具 `_tool_analyze_prv` 存在 ZeroDivisionError（`pressure_reducing_valve.py` bug，需单独修复）
2. 合规Agent的 verify_leak/verify_rated/verify_life 为Mock实现（返回pass=True）
3. 简单查询检测规则较粗糙（基于英文关键词，不支持中文"什么是"）
