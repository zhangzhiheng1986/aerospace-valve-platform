# 平台诊断与验证 — 2026-06-05

## 操作
1. Sprint 4 注入后清理临时脚本 (`_inject*`, `_fix*`, `_test*` 等)
2. Git 提交 13 个文件 (commit 41c31c1): Sprint 4 + 搜索UI + 文档
3. 全平台 12 模块冒烟测试

## 已知Bug审查结果

所有 MEMORY.md 记录的"已知Bug"均已确认修复或不存在：

| Bug | 诊断 | 状态 |
|-----|------|------|
| check_valve `KeyError: nominal_flow_rate` | 测试用了错误的参数名; 前端发送正确字段名 | ✅ 非Bug |
| seal_design `KeyError: seat_material` | 测试用 `stainless_steel` 而非 `316L_SS`; 前端发送正确材质码 | ✅ 非Bug |
| TEMPLATES list 404 | 路由是 `/api/templates` 非 `/api/templates/list`; 工作正常 | ✅ 已修复(bf65211) |
| MATERIALS AWG `get_awg` | 已重命名为 `get_conductor_for_awg()`; 工作正常 | ✅ 已修复(bf65211) |

## 全平台烟测试 (12/12 通过)
- solenoid, materials, knowledge, metrics, qj20156
- pressure_valve, check_valve, oring, spring
- seal, fluid_mechanics, templates
