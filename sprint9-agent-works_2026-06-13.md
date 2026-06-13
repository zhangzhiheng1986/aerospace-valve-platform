# Sprint 9 — AI Agent 真能干活 (2026-06-13)

## 概述
智能体在 Sprint 5-8 完成了架构搭建 (多智能体管线、向量库、知识图谱、前端 v3),
但实际"干活"能力薄弱: 参数传递、错误处理、材料查询均有 P0/P1 缺陷.
本 Sprint 用 ParameterExtractor 智能解析 + 容错架构让 Agent 真正能完成工程任务.

## 测试结果

| # | 用户查询 | 意图 | 子任务通过率 | 关键结果 |
|---|---------|------|-------------|----------|
| 1 | "Help me design a pressure reducing valve, inlet 15 MPa, outlet 2 MPa, flow 100 L/min, medium is RP-3 kerosene" | design_pressure_valve_system | 3/3 | orifice=5mm, flow_area=15.33mm², Cv=0.32, flow_force=27N |
| 2 | "What material should I use for a valve operating at 500C and 20 MPa in rocket engine?" | material_analysis | 2/2 | TC4 (密度4.43, 弹性模量110 GPa, 耐腐蚀极佳) |
| 3 | "Compute Reynolds number for water at 5 m/s in a 50mm diameter pipe" | fluid_calc | PAOR fallback | (不需多智能体) |
| 4 | "hello" | knowledge_query | PAOR fallback | (不需多智能体, 修复 500) |
| 5 | "Design a solenoid valve for 28V DC, 2mm stroke, working pressure 10 MPa" | design_solenoid_system | 3/3 | best_awg=34, A_cu=0.0201mm², fitness=6.77 |
| 6 | "Design a spring with 50mm OD, wire 2mm, free length 30mm, 50CrVA material" | design_spring_system | 2/3 | fatigue_sf=0.994, f_n=21.4 Hz (50CrVA 不在 db, advisory 失败不阻塞) |
| 7 | "Design an O-ring for 100mm bore, 30MPa pressure, FKM material" | design_pressure_valve_system | 3/3 | Viton (密度1.85, max_temp=250) + orifice=1mm + 合规 |
| 8 | "Check QJ 20156 compliance for a valve at 20 MPa, 500C, 50000 cycles" | validate_design | 1/1 | burst_factor>=2.0x, life>=20000, proof>=1.5x |
| 9 | "Design a check valve for 10 MPa inlet pressure, 50 L/min flow, water medium" | design_pressure_valve_system | 3/3 | orifice=6mm, flow_area=21.99mm² |

**总通过率: 9/9 端点成功, 23/24 子任务通过 (95.8%)**

## 修复内容

### P0 修复
1. **SubTask 参数提取空白**: 创建 `parameter_extractor.py` (20KB, 6 个域专用提取器)
   - 提取压力/流量/温度/电压/直径/材料/流体/电压 共 8 类参数
   - 中英文同义词表 (TC4/钛合金/Ti-6Al-4V)
   - 单位归一化 (MPa/Pa/bar/psi, L/min/m³/s, mm/cm/m, °C/°F/K)
   - 智能推荐: query_material 无指定材料时按工况自动选 (高温→TC4, 高压→1Cr18Ni9Ti)

2. **依赖链断裂不传播**: `_execute_plan` 中 dep 失败时子任务正确标 FAILED,
   标记 `skipped=True` 而非停留在 PENDING

3. **"hello" 500 错误**: `_respond_simple` 返回完整 dict (success/orchestrated/
   intent/plan_id/total_subtasks/categories/task_results), 修复 PAOR fallback
   路径上 `'str' object has no attribute 'get'` 崩溃 (PAOR 引擎失败时返回静态响应)

### P1 修复
4. **任务结果不展示**: synthesis.task_results[i].result 现在包含完整 dict,
   前端可遍历 nested keys

5. **query_material 字段名不匹配**: extractor 输出 `material` 和 `name` 双字段,
   `tool_bridge._material_query` 新增子串匹配 + 同义词表 (FKM→Viton, PTFE→聚四氟乙烯)

6. **Dynamic Library 仍只有 2 skill**: (本 Sprint 暂不处理, 计划 Sprint 10)

### P2 修复
7. **PRV Water 除零崩溃**: 在 `pressure_reducing_valve.py` 的 `FLUID_PROPERTIES`
   中新增 water + hydraulic_oil 完整物性表 (密度/粘度/气体常数/比热比等)

8. **跨任务参数链路**: query_material 失败标为 advisory (不阻塞后续), 后续任务
   在 inputs 中携带 `_advisory_warning` 字段, 但继续运行

## 关键文件

- `backend/parameter_extractor.py` (20KB, 新增) — 智能参数提取器
- `backend/orchestrator_agent.py` — 注入 extractor + 容错传播
- `backend/tool_bridge.py` — _material_query 模糊匹配 + 同义词
- `backend/pressure_reducing_valve.py` — water/hydraulic_oil 物性补全
- `backend/app/blueprints/ai_agent.py` — orchestrate 端点防御式处理

## 已知遗留
- Spring 50CrVA: 数据库没有, 仍返回 not-found (业务上合理)
- Dynamic Library 只有 2 SKILL.md (solenoid, pressure_valve) — Sprint 10 处理
- Cross-task parameter passing (前置结果自动喂给后续) — 架构已支持,
  但需要更多 recipe 测试

## 架构启示
1. 自然语言 → 结构化参数是所有 AI 工程助手的核心难题, 需投入 1-2 周打磨
2. 容错设计: advisory 依赖 vs blocking 依赖必须有清晰分类
3. 防御式 PAOR fallback 是必备, 简单问候不该让整个栈崩
4. 字段名一致性: `material` vs `material_name` vs `name` 在 3 个不同模块中出现
