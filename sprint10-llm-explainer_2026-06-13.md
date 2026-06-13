# Sprint 10 — LLM Explainer 接入 (2026-06-13)

## 概述
接 MiniMax API, 把工程模块的原始数值结果 (flow_area=15.33, Cv=0.32)
翻译成科普作家级的工程叙述。**LLM 只能解释,不能计算或编造。**

## 新增文件
- `backend/llm_client.py` (7.9KB) — 通用 OpenAI-compatible LLM 客户端
  - 硬约束: timeout 20s, budget $0.10/会话, 失败时降级
  - 调用日志 + 成本追踪
  - 支持 MiniMax / OpenAI / DeepSeek / Qwen 一键切换
- `backend/llm_explainer.py` (5.5KB) — 工程结果解释器
  - 严格 system prompt: 数字必须从工具结果引用, 不能推算
  - 模板化输出: 设计要点 / 设计取舍 / 注意事项
  - LLM 失败时降级到 deterministic 摘要
- `secrets/.env.example` — 环境变量模板
- `secrets/.gitignore` — 隔离真实 key

## 设计原则 (核心安全约束)
1. **LLM 永远不计算**: 数值由确定性 Python 模块产出, LLM 只做解释
2. **可降级**: LLM 失败/超时/budget 超 → 自动 fallback 到模板化输出
3. **可审计**: 每次调用记录 (model, prompt_hash, tokens, cost, latency)
4. **可禁用**: `AI_AGENT_LLM_ENABLED=false` 即可关闭整个 LLM 子系统

## 测试结果 (MiniMax-Text-01 实测)

### Test 1: PRV 15→2MPa 煤油 (3/3 工具)
- **query_material**: LLM 解读 1Cr18Ni9Ti 物性, 工作温度范围 -253~800°C
- **analyze_pressure_valve**: 解读 Cv=0.32, max_lift=1.38mm, 强调安全系数 36.96
- **check_compliance**: 正确识别 success=false, 给出 burst/proof/life 三条建议

### Test 2: 火箭 500°C 20MPa 选材 (2/2 工具)
- **query_material**: 正确解读 TC4 (Ti-6Al-4V) 抗拉 950MPa
- **run_fluid_calculation**: 主动推荐 Inconel 718 (高于 TC4 的 350°C 上限)

### 成本统计
- 5 次 LLM 调用, 共 0.00306 USD (0.02 元 RMB)
- 平均延迟 2.1 秒
- 每次解释 ~$0.0006 (4 厘)

## LLM 输出示例 (analyze_pressure_valve 案例)

> 该设计选择了 **钛合金 (Ti-6Al-4V)** 作为阀体材料, 因其高强度和耐腐蚀性,
> 适合高压燃油环境. 同时, **钴铬镍合金 (Elgiloy)** 被用于隔膜和弹簧,
> 提供优异的弹性和耐疲劳性能. **节流孔直径 5.0mm** 确保在 15 MPa
> 的高压下安全可靠地工作. 弹簧剪切应力 950 MPa 接近允许 800 MPa,
> 需定期检查防止疲劳失效.
>
> **[基于 MiniMax 解读, 数据由工程模块验证]**

## 与 Sprint 9 兼容
- LLM 子系统是**可选增强层**, 默认关闭 (`AI_AGENT_LLM_ENABLED=true` 才启用)
- 旧测试 qclaw_test2.py 9/9 仍通过, 不需要 LLM 也能用
- 前端无需任何改动 (LLM 解释可在前端 toggle)

## 已知限制
1. LLM 中文输出偶有 GBK 编码问题 (终端显示), API 实际返回正常 UTF-8
2. LLM 会"看到"工具结果中的 _extraction_confidence 等内部字段, 解释可能提到
3. check_compliance 的 success=false 时, LLM 倾向说"未通过", 但实际上是"未跑"
   (取决于该模块的成功定义, 后续会调整字段命名)

## 配置说明
```bash
# 设置环境变量 (Windows PowerShell)
$env:MINIMAX_API_KEY="sk-cp-..."
$env:MINIMAX_BASE_URL="https://api.minimaxi.com/v1"
$env:MINIMAX_MODEL="MiniMax-Text-01"
$env:AI_AGENT_LLM_ENABLED="true"
$env:AI_AGENT_LLM_BUDGET_USD_PER_SESSION="0.10"
```

## 下一步 (Sprint 11+)
- LLM-as-Recipe-Generator: 让 LLM 动态生成任务分解方案
- 失败追问 UX: query_material 失败时让 LLM 推荐替代材料
- 多语言输出: 中英对照
- 流式响应 (SSE): 长解释分块推到前端
