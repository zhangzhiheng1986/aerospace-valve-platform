# 航空航天阀门 AI 原生智能体协作平台 — 融合架构设计 v2.0

> **代号**: AV-Agent / "阀门大脑"  
> **作者**: QClaw  
> **日期**: 2026-06-12  
> **版本**: v2.0 (融合 OpenClaw + Hermes + ACP 架构思想)  
> **关联文档**: `.project/PLAN.md`

---

## 〇、设计哲学 — 三大架构思想的融合

本架构并非从零发明，而是深度吸纳当前最先进的 Agent 运行时架构的核心思想：

### 0.1 三大源头

```
OpenClaw 的"平台思维"    Hermes 的"进化思维"    ACP/Harness 的"协议思维"
      │                        │                      │
      ├─ Gateway 单进程多路复用  ├─ 自进化学习闭环       ├─ Protocol-First 架构宪法
      ├─ Skills 模块化知识注入  ├─ 动态技能创建/修补    ├─ JSON-RPC 2.0 + stdio/WS
      ├─ Session 强隔离         ├─ 主动记忆压缩          ├─ Editor as First Citizen
      ├─ Sub-agent 委派模式     ├─ Nudge Engine 后台复盘 ├─ 三层解耦: Channel/Protocol/Agent
      ├─ Bootstrap 文件驱动     ├─ "动态图书馆"懒加载    ├─ N+M 消除集成爆炸
      ├─ LCM 上下文无损管理     ├─ 安全护栏约束自主      ├─ cwd 绑定 + 进程边界统一
      ├─ Heartbeat/Cron 主动式  ├─ Multi-model 路由       └─ 持久化 Thread + Session 管理
      └─ Plugin/Hook 扩展点    └─ 冻结快照记忆
              │                        │                      │
              └────────────────────────┼──────────────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │   阀门大脑 融合架构      │
                          │   取其精髓，融会贯通     │
                          └─────────────────────────┘
```

### 0.2 融合映射表

| 源思想 | 来源 | 在阀门大脑中的落地 |
|--------|------|-------------------|
| **Skills 模块化注入** | OpenClaw | 阀门领域 Skills: `solenoid.SKILL.md`, `cfd.SKILL.md` 等，按需注入 Agent 上下文 |
| **Session 强隔离** | OpenClaw | 每个设计项目 = 独立 Session，上下文不污染 |
| **Sub-agent 委派** | OpenClaw | Orchestrator 委派子任务到 Design/Simulation/Material 等子 Agent |
| **Bootstrap 文件** | OpenClaw | `AGENTS.md` = 平台规则, `SOUL.md` = 各 Agent 人设，`USER.md` = 用户偏好 |
| **LCM 无损上下文** | OpenClaw | 长设计会话自动摘要/压缩/检索，跨天设计不丢失上下文 |
| **Heartbeat/Cron** | OpenClaw | 仿真任务定时监控、标准更新定时检查、设计评审周期提醒 |
| **自进化学习闭环** | Hermes | Agent 完成阀门设计后自动提取经验 → 创建/修补 Skill 文件 |
| **动态 Skills** | Hermes | Skills 首次为人手工编写 → 后续 Agent 自动从经验中修补 (Pitfalls) |
| **Nudge Engine** | Hermes | 后台定时复盘设计决策，提炼可复用模式，发现设计缺陷 |
| **动态图书馆懒加载** | Hermes | 不把 307 个公式全载入上下文，按当前任务动态加载所需公式组 |
| **冻结快照记忆** | Hermes | 关键设计节点冻结为不可变快照，便于回溯和审计 |
| **Protocol-First 架构** | ACP | 协议是系统“宪法”：Channel ↔ Protocol ↔ Agent 三层强制解耦 |
| **@mention 元路由** | ACP | 用户 @设计大师 直接唤醒 Design Agent，@材料专家 唤醒 Material Agent |
| **Agent-to-Agent** | ACP | Design Agent 可调用 Simulation Agent 验证方案，无需回主控 |
| **持久化 Thread** | ACP | 同一阀门设计项目跨数天/数周保持上下文的持久线程 |
| **cwd 绑定** | Harness | 编辑器的工程目录 = Agent 的工作目录，多项目切换不串味 |
| **Approval Bridge** | Harness | 危险操作三选一: Allow Once / Always / Deny，IDE 内渲染 |
| **Provider Resolver** | Harness | 单一配置真相源，所有入口(Web/IDE/CLI)共享同一凭证体系 |
| **Tool Set Boundary** | Harness | 不同入口(Web IDE CLI)拥有不同的可用工具集，防止权限误用 |
| **N+M 集成消除** | ACP | N 个编辑器 + M 个 Agent = N+M 次实现(而非 N×M) |

### 0.3 ACP/Harness 深度架构解析 — "LSP for AI Agents"

ACP (Agent Client Protocol) 对阀门大脑的意义远超 @mention 和 Agent-to-Agent 通信。
它是一套 **Protocol-First 的系统宪法**，定义了 Channel ↔ Protocol ↔ Agent 三层的解耦关系。

#### 0.3.1 ACP 的核心类比: LSP for AI Agents

```
LSP (2016):  编辑器 ←→ Language Server    → 一套语言服务, 所有编辑器可用
ACP (2025):  编辑器 ←→ Agent Runtime      → 一套 Agent 能力, 所有编辑器可用

三大协议定位 (互不替代, 相互补充):
  MCP:  Agent Runtime ←→ 外部工具       → Agent 如何发现和调用工具 (工具发现协议)
  A2A:  Agent A ←→ Agent B              → Agent 间如何协作 (Agent 通信协议)
  ACP:  编辑器(Client) ←→ Agent(Server) → 编辑器如何接入 Agent Runtime (会话集成协议)
```

#### 0.3.2 ACP 解决的五大工程问题

| # | 痛点 | ACP 方案 | 阀门大脑落地 |
|---|------|---------|------------|
| 1 | **集成爆炸 (N×M)** | 每个编辑器实现 ACP 一次，每个 Agent 实现 ACP 一次 → N+M | 平台任何入口 (Web/VS Code/JetBrains/CLI) 都通过同一 ACP Server 接入 |
| 2 | **上下文割裂** | 代码文件+Terminal+Agent 上下文在同一进程边界内流动 | 工程师在 VS Code 设计的阀门，Web 仪表盘立即感知 — 不再三套 AI 三套记忆 |
| 3 | **凭证重复** | Provider Resolver: 单一配置真相源 | 所有入口共享同一 LLM Key / 数据库连接，一处过期全局同步 |
| 4 | **工作目录错位 (cwd)** | Editor 的 workspace = Agent 的 cwd，随项目自动切换 | 阀门外壳项目 vs 阀芯项目，Agent 自动感知当前工程目录 |
| 5 | **权限越界** | Tool Set Boundary: 不同入口不同工具集 | Web UI 可发报告邮件，IDE 入口禁止消息操作 |

#### 0.3.3 Harness 六大核心机制

**① stdio JSON-RPC — 零配置进程通信**

```
Editor 进程                      ACP Server 进程 (阀门大脑)
    │                                  │
    │  stdin: {"jsonrpc":"2.0",        │
    │          "method":"chat.send",    │
    │          "params":{...}}           │
    ├──────────────────────────────────►│ (Agent 推理 + 工具调用)
    │                                  │
    │  stdout: {"event":               │
    │    "assistant.text.delta",        │
    │    "delta":"方案B 安全系数 2.8"}   │
    │◄──────────────────────────────────┤
stderr: 日志 (调试用, 不影响协议通信)
```

设计哲学: 日志走 stderr，数据走 stdout 绝不混杂；任何能读写 stdin/stdout 的进程都能充当 ACP Client；无需端口/防火墙/网络配置。

**② Approval Bridge — 危险操作三选一**

```
场景: Agent 要修改 QJ20156 标准爆破压力阈值

IDE 内弹出 (编辑器内渲染, 非终端弹窗):
╔══════════════════════════════════════╗
║ ⚠️  危险操作: 修改标准合规参数       ║
║                                      ║
║  [Allow Once]  [Allow Always]  [Deny]║
╚══════════════════════════════════════╝

安全默认: 超时或错误 → 自动 Deny (宁可停等，不冒险执行)
```

**③ Provider Resolver — 单真相配置体系**

```
~/.valvebrain/
├── .env              # API Keys (所有入口共享)
├── config.yaml       # Provider + 模型配置
└── skills/           # Skills 仓库

CLI 入口 ──┐
Web 入口 ──┼──→ 同一配置体系 (不是三套独立配置!)
IDE 入口 ──┘
```

ACP 与"编辑器插件生态"的根本区别: 插件在编辑器内部维护独立凭证，ACP 让 Editor 退到"客户端"位置，Agent Runtime 维护配置真值。

**④ Tool Set Boundary — 按入口裁剪工具集**

```
Web Dashboard 入口工具集:             IDE 入口工具集:
  ✅ 全部设计/仿真工具                 ✅ 阀门设计/材料工具
  ✅ 消息发送 (Email/IM 报告)          ✅ 文件操作 (read/write)
  ✅ Cron 任务管理                      ✅ Terminal 工具
  ✅ 报告导出                          ✅ execute_code
                                       ❌ 消息发送 (禁止!)
                                       ❌ Cron 管理 (禁止!)
```

不是技术限制，是**语义约束**: IDE 里设计阀门时，Agent 不应有能力操作消息通道。

**⑤ 幂等性与任务追踪**

- 每个 `chat.send` 携带 `idempotencyKey` → 网关缓存结果 → 网络重试不重复执行
- 所有事件携带 `runId` → 客户端可关联完整执行链 (从"开始设计"到"报告生成")

**⑥ 标准化错误模型**

```
-32001: 上下文溢出 → 触发自动压缩 (对接 LCM)
-32002: 需要用户审批 → 弹出确认框 (对接 Approval Bridge)
-32003: 账号限流 → 触发换号逻辑 (对接 Provider Resolver)
```

#### 0.3.4 阀门大脑: Protocol-First 三层解耦

```
┌─────────────────────────────────────────────────────────────┐
│                    Channel 层 (多渠道接入)                    │
│  Web Chat │ VS Code │ JetBrains │ CLI │ Telegram │ 微信 ...  │
└─────────────────────────┬───────────────────────────────────┘
                          │  所有渠道实现同一套 ACP 协议
┌─────────────────────────▼───────────────────────────────────┐
│                 ACP 协议层 (系统"宪法")                       │
│  · chat.send / session.create / tool.call                   │
│  · 幂等性 (idempotencyKey)                                  │
│  · 流式事件 (text.delta / tool.call.request / result)       │
│  · 错误标准化                                                │
└─────────────────────────┬───────────────────────────────────┘
                          │  协议解耦: 渠道开发者不懂 LLM
┌─────────────────────────▼───────────────────────────────────┐
│                 Agent Runtime (阀门大脑核心)                  │
│  · 领域 Agent 矩阵 (7+1)                                    │
│  · Skills 引擎 (OpenClaw 模块化 + Hermes 自进化)            │
│  · 记忆系统 (L1/L2/L3)                                      │
│  · PAOR 推理循环 + 学习闭环                                  │
└─────────────────────────────────────────────────────────────┘
```

**Protocol-First 核心约束:**
- 渠道开发者不需要懂 LLM — 只需实现 ACP 协议
- Agent 开发者不需要懂 Telegram/VS Code 协议 — 只需响应 ACP 方法
- 任何新客户端 (微信小程序 / 钉钉 / IDE 插件) 接入 → 立即获得全部 Agent 能力

---

### 0.4 Harness 六大组件 — "Agent = Model + Harness"

> 模型提供智能，Harness 让智能变得有用。
> 如果你不是模型本身，那你就是 Harness 的一部分。

#### 0.4.1 裸模型的四个硬伤

裸模型 (Raw Model) 有四个致命缺陷，Harness 的六大组件就是对付它们的解药:

| # | 硬伤 | 本质缺失 | Harness 解药 |
|---|------|---------|------------|
| 1 | 无法维持跨会话状态 | 长期记忆 | 文件系统 + AGENTS.md 记忆 |
| 2 | 无法执行代码 | 行动能力 | Bash + 沙箱 |
| 3 | 无法获取实时知识 | 感知能力 | Web Search + MCP |
| 4 | 无法搭建工作环境 | 环境操控 | 文件系统 + 上下文工程 + 编排 |

#### 0.4.2 六大组件全景

**组件一: 文件系统 — 最基础的原语**

文件系统是 Agent 的"外部大脑"，是突破上下文窗口限制的唯一途径。它提供三大能力:
- **工作空间与中间结果存储**: 复杂任务的中间产物写入文件，需要时读取 → 实现"按需加载"
- **Agent 协作的基础**: 多 Agent 之间的"共享白板"，Agent A 写入 → Agent B 读取继续
- **版本追踪与错误回滚**: 配合 Git，Agent 每一步操作可追溯、可回滚、可开分支实验

核心洞察: **文件系统 + Git = 给 Agent "试错"的能力**。Agent 可以大胆尝试，失败了就回滚。这极大地释放了模型的创造力。

阀门大脑落地:
- 每个设计项目 = 独立工作目录 (文件系统隔离)
- Git 追踪所有设计决策变更 (可审计)
- 仿真中间结果存入文件 → 按需加载 (不撑爆上下文)

**组件二: Bash + 沙箱 — 从"说"到"做"**

裸模型只能生成代码文本，不能执行。Bash 赋予 Agent 自我验证循环:

```
写代码 → 跑代码 → 看结果 → 修Bug → 再来
  ↑___________________________________|
         自我验证循环 (Self-Verification Loop)
```

实测数据: 具备自我验证循环的 Agent，任务完成率比"一次性生成"高 **40%-60%**。

**沙箱不是可选项 — 它是 Bash 的前提条件**:
- 资源限制 (CPU/内存/磁盘)
- 网络隔离 (白名单)
- 文件系统隔离 (只访问工作目录)
- 超时机制

阀门大脑落地:
- 所有 Agent 代码执行在 Docker 沙箱内
- 仿真计算超时自动终止
- 危险阀门参数修改需 Approval Bridge 确认

**组件三: 记忆 (AGENTS.md) — 不改权重也能给模型加知识**

核心等式: **上下文注入 = 不改权重给模型加知识**

传统微调: 改模型权重 (贵、慢、灾难性遗忘风险)
AGENTS.md: 把知识写入文件，下次自动注入上下文 (即时、透明、人类可编辑)

阀门大脑落地 (OpenClaw Bootstrap 体系):
```
aerospace-valve-platform/
├── AGENTS.md          # 全局规则: 阀门设计红蓝线
├── SOUL.md            # Agent 人设: 设计/仿真/材料专家人设
├── USER.md            # 用户偏好: 工程单位制、输出格式
├── TOOLS.md           # 工具手册: 各模块 API 签名
└── .project/
    ├── PLAN.md        # 长期路线图
    └── AI_AGENT_ARCHITECTURE.md # 本文档
```

**双向可编辑**: 人类可直接编辑 AGENTS.md 向 Agent 传达偏好 (如"所有设计必须引用 QJ20156 标准")

**层次化存放**: 根目录全局知识，子目录局部知识，Agent 进入某个目录时加载对应上下文

**组件四: Web Search + MCP — 突破知识的"时间牢笼"**

- **Web Search**: 让 Agent 搜索训练截止日期后的新知识 (新标准、新材料数据、社区最佳实践)
- **MCP (Model Context Protocol)**: 让 Agent 连接任意数据源 (内部数据库、项目管理工具、代码仓库)

MCP = "AI 世界的 USB 接口" — 任何遵循 MCP 规范的工具都可以即插即用。

协同示例 (阀门故障诊断):
```
  监控系统 ──MCP──→ 获取错误日志
  代码仓库 ──MCP──→ 查看变更历史
  Web Search ────→ 搜索社区解决方案
  项目管理 ──MCP──→ 检查已知问题
  Agent 整合 ────→ 生成修复方案
```

阀门大脑落地:
- Valve MCP Server: 暴露所有计算模块 (17个) 为 MCP 工具
- 标准更新: Web Search 定期拉取最新航天标准
- Knowledge Graph MCP: 连接 Neo4j 阀门知识图谱

**组件五: 上下文工程 — 对抗 AI 系统的"熵增"**

> Context Rot (上下文腐烂): 随着对话变长，上下文信噪比下降、矛盾信息累积、Token 浪费、推理质量退化。

四大对抗策略:

| 策略 | 说明 | 阀门大脑落地 |
|------|------|------------|
| **压缩 (Compression)** | 定期对历史上下文摘要压缩 | LCM 自动压缩 + Hermes 主动压缩 |
| **工具输出卸载** | 大段代码/日志存文件系统，上下文只保留摘要和文件引用 | 仿真结果 → 文件系统，Agent 只看到摘要 |
| **Skills 渐进加载** | 不同任务阶段加载不同知识 | 公式引擎 207 公式按类别动态加载，不全塞入 |
| **分层上下文结构** | 核心层(始终保留) / 工作层(按需更新) / 历史层(逐渐压缩) | L1 工作记忆 / L2 冻结快照 / L3 语义记忆 |

**组件六: 编排 + Hooks — 质量管控的最后防线**

编排 (Orchestration):
- 任务分解 DAG → 子 Agent 调度 → 结果聚合
- 四种协作模式: 串行 / 并行 / 辩论 / 层级

Hooks (质量门控):
- **Pre-hook**: 子 Agent 执行前检查 (如 Design Agent 必须先加载 AGENTS.md)
- **Post-hook**: 子 Agent 完成后校验 (如仿真结果必须在物理合理范围内)
- **Error-hook**: 异常时自动回退 (如材料选型失败 → 自动尝试备选材料)
- **Quality Gate**: 关键节点人工审批 (如修改标准参数 → Approval Bridge)

阀门大脑落地:
```
Orchestrator
  ├── Pre-hook → 检查权限 + 注入上下文
  ├── 子 Agent 执行
  ├── Post-hook → 结果校验 (数值范围/单位一致性/标准合规)
  ├── Quality Gate → 置信度 < 0.6 暂停, 危险操作需人工审批
  └── Error-hook → 自动重试 + 备选方案切换
```

---

## 一、愿景与定位


### 从工具集合 → 自进化的 AI 原生协作平台

```
第一代 (当前 v1.2):  用户 → 网页表单 → 计算工具 → 人工解读
第二代 (v2.0 AI原生): 用户 → 自然语言 → PAOR Agent → 自主执行+报告
第三代 (v3.0 多Agent): 用户 → @mention → Agent矩阵协作 → 综合方案
第四代 (v4.0 自进化):  用户 → 意图 → 自进化Agent生态 → 越用越强
```

### 核心差异

旧范式: **"你用多少，取决于开发者写了多少"** (OpenClaw 的静态 Skill 模式)
新范式: **"用得越久，它越懂阀门设计"** (Hermes 的自进化模式)
互联范式: **"每个专家 Agent 可被任意编排调用"** (ACP 的互操作模式)

---

## 二、融合架构总览

```
                        ┌──────────────────────────┐
                        │    Gateway 层 (OpenClaw)  │
                        │  单进程 · WebSocket ·     │
                        │  多渠道 · 认证 · 路由     │
                        └────────────┬─────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
    ┌─────────▼────────┐  ┌─────────▼────────┐  ┌─────────▼────────┐
    │  Session Manager │  │  Context Engine  │  │  Hook System     │
    │  (OpenClaw隔离)  │  │  (LCM + 懒加载)  │  │  (Plugin扩展点)  │
    └─────────┬────────┘  └─────────┬────────┘  └─────────┬────────┘
              │                      │                      │
    ┌─────────▼──────────────────────▼──────────────────────▼─────────┐
    │                     Agent 引擎层                                │
    │  ┌──────────────────────────────────────────────────────────┐  │
    │  │              Orchestrator (编排中枢)                      │  │
    │  │   · 意图解析 + 任务分解 DAG                              │  │
    │  │   · @mention 元路由 (ACP)                                │  │
    │  │   · Agent-to-Agent 调度 (ACP)                            │  │
    │  │   · 人机协同 置信度门控                                  │  │
    │  └────────────────────────┬─────────────────────────────────┘  │
    │                           │                                    │
    │     ┌─────────────────────┼─────────────────────┐              │
    │     │                     │                     │              │
    │  ┌──▼──────┐  ┌──────▼───┐  ┌──────▼───┐  ┌────▼──────┐      │
    │  │ Design  │  │Simulation│  │ Material │  │Compliance │ ...  │
    │  │ Agent   │  │  Agent   │  │  Agent   │  │  Agent    │      │
    │  │ 阀门设计│  │ CFD/FEM  │  │ 材料选型 │  │ 标准合规  │      │
    │  └──┬──────┘  └──────┬───┘  └──────┬───┘  └────┬──────┘      │
    │     │                │             │            │             │
    │     └────────────────┴──────┬──────┴────────────┘             │
    │                             │                                  │
    │              ┌──────────────▼──────────────┐                   │
    │              │     学习闭环 (Hermes)        │                   │
    │              │  · Nudge Engine 后台复盘     │                   │
    │              │  · Skill 自动创建/修补       │                   │
    │              │  · Pitfalls 经验积累         │                   │
    │              │  · 记忆冻结快照              │                   │
    │              └──────────────┬──────────────┘                   │
    └─────────────────────────────┼──────────────────────────────────┘
                                  │
    ┌─────────────────────────────┼──────────────────────────────────┐
    │                    协议与工具层                                 │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
    │  │   ACP    │  │   MCP    │  │ RESTful  │  │  WebSocket   │  │
    │  │ Agent间  │  │ 工具暴露 │  │ 传统 API │  │  实时推送    │  │
    │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
    │                                                                │
    │  ┌──────────────────────────────────────────────────────────┐ │
    │  │  Valve Skills 仓库 (OpenClaw Skill 模式 + Hermes 自进化)  │ │
    │  │  · solenoid.SKILL.md    · cfd.SKILL.md                     │ │
    │  │  · spring.SKILL.md      · material.SKILL.md                │ │
    │  │  · 每个 Skill 含: 步骤 + Pitfalls + 示例 + 经验版本号     │ │
    │  └──────────────────────────────────────────────────────────┘ │
    └────────────────────────────────────────────────────────────────┘
                                  │
    ┌─────────────────────────────┼──────────────────────────────────┐
    │                    数据与记忆层                                 │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
    │  │ 知识图谱 │  │ 向量存储 │  │ 关系数据 │  │  记忆系统    │  │
    │  │  Neo4j   │  │ Qdrant   │  │PostgreSQL│  │  L1/L2/L3    │  │
    │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
    └────────────────────────────────────────────────────────────────┘
```

---

## 三、核心子系统深度设计

### 3.1 Gateway 层 — 吸纳 OpenClaw 的单进程多路复用

**OpenClaw 核心洞察**: 一个 Gateway 进程管理所有渠道连接，不每渠道起独立服务。个人/小团队场景，运维复杂度比水平扩展更重要。

**阀门大脑落地**:

```python
# 统一 Gateway: 所有交互入口收归一个进程
class ValveGateway:
    """
    借鉴 OpenClaw Gateway 设计:
    - 单进程管理: Web UI + REST API + WebSocket + ACP + MCP
    - 不每协议起独立服务
    - 个人/小团队优先: 运维简单 > 水平扩展
    """
    def __init__(self):
        self.session_registry = SessionRegistry()    # OpenClaw: Session 强隔离
        self.channel_adapters = {                    # OpenClaw: 多渠道适配
            'web': WebChatAdapter(),
            'api': RESTAdapter(),
            'ws': WebSocketAdapter(),
            'acp': ACPAdapter(),                     # ACP: Agent 间通信
            'mcp': MCPServer(),                      # MCP: 工具暴露
        }
        self.lane_manager = LaneManager()            # OpenClaw: 消息路由/线程绑定
        self.auth_profiles = AuthManager()           # OpenClaw: 认证鉴权
```

### 3.2 Session 与 Context — 融合 OpenClaw 隔离 + Hermes 压缩

**核心冲突**: OpenClaw 用追加模式日志 (append-only memory)，Hermes 用主动压缩 (容量限制 + 冻结快照)。

**融合方案**: 三层记忆各取所长

```
┌──────────────────────────────────────────────────────┐
│  L1: 工作记忆 (OpenClaw Session)                      │
│  · 强隔离: 项目A与项目B互不污染                       │
│  · 滚动窗口: 最近 N 轮对话 + 当前任务上下文           │
│  · 生命周期: 单次会话                                 │
├──────────────────────────────────────────────────────┤
│  L2: 情景记忆 (Hermes 冻结快照)                       │
│  · 关键节点自动冻结: "方案确定" / "评审通过"          │
│  · 容量管理: 上限 50 个快照，LRU 淘汰                 │
│  · 不可变: 审计追溯，不被后续对话污染                 │
├──────────────────────────────────────────────────────┤
│  L3: 语义记忆 (OpenClaw LCM + Hermes 主动提炼)        │
│  · LCM: 长会话自动摘要压缩，跨天不丢失                │
│  · Nudge: 后台定时复盘 → 提炼可复用经验               │
│  · 知识图谱 + 向量库: 结构化 + 语义化双检索           │
└──────────────────────────────────────────────────────┘
```

### 3.3 Bootstrap 文件系统 — OpenClaw 精髓

每个 Agent / 项目 / 用户都有独立 Bootstrap 文件:

```
workspace/
├── AGENTS.md              # 平台规则 (继承 OpenClaw 模式)
│   "阀门设计必须通过 Compliance Agent 审查"
│   "安全系数低于 1.5 的设计必须人工确认"
│
├── SOUL.md                # 各 Agent 人设 (融合 Hermes 结构化格式)
│   # 身份 → 你的名称是「阀门设计大师」
│   # 经历 → 精通电磁阀/减压阀/单向阀全流程...
│   # 风格 → 用数据说话, 先算后说, 每步可追溯
│
├── USER.md                # 用户/团队偏好
│   "偏好材料: 钛合金 > 不锈钢"
│   "设计风格: 保守设计, 安全系数 ≥ 2.0"
│
├── TOOLS.md               # 领域工程经验 (自进化!)
│   "弹簧设计常见坑: 弹簧指数 < 4 会导致制造困难"
│   "上次 O形圈泄漏根因: 粗糙度 Ra 过低导致..."
│   # ↑ 这些条目最初由人写, 后续 Agent 自动追加
│
├── skills/                # 阀门 Skills (OpenClaw 模块化 + Hermes 自修补)
│   ├── solenoid.SKILL.md
│   ├── cfd.SKILL.md
│   ├── spring.SKILL.md
│   └── ...
│
└── memory/                # 每日日志 + 决策追溯
    └── 2026-06-12.md
```

### 3.4 Skills 系统 — OpenClaw 模块化 + Hermes 自进化

**这是融合的核心创新点。**

```
传统 OpenClaw Skill (静态):
  SKILL.md = 人写的固定指令, Agent 不会改它

Hermes Skill (动态):
  SKILL.md = 人写初始版本 → Agent 在实际使用中自动修补
  每次任务完成后: Agent 复盘 → 提炼新经验 → 追加到 SKILL.md 的 Pitfalls 节

阀门大脑 Skills (融合):
  第一阶段: 人写核心流程 (继承 OpenClaw)
  第二阶段: Agent 执行任务 + 遇到问题 + 人纠正
  第三阶段: Nudge Engine 后台复盘 → 自动更新 Pitfalls (继承 Hermes)
  第四阶段: 新版本 Skill 经安全扫描后生效
```

**阀门 Skill 模板示例**:

```markdown
# solenoid.SKILL.md — 电磁阀优化设计

> 版本: v2.3 | 最后更新: 2026-06-12 | 执行次数: 47 | 成功率: 94%

## 标准流程 (人写, v1.0)
1. 解析用户需求: 工作压力 / 介质 / 温度 / 流量
2. 选择电磁铁拓扑: 螺线管 vs 盘式 vs 比例
3. 运行 PSO 优化器 `run_optimization(geom_params, n_particles=50, n_iterations=100)`
4. 输出 Pareto 前沿: 电磁力 vs 功耗 vs 重量

## 常见陷阱 (Agent 自学习, 自动追加)
- ⚠️ 2026-06-05: 当行程 > 5mm 时，PSO 容易收敛到局部最优 → 增加粒子数到 80+
- ⚠️ 2026-06-08: 用户纠正: 低温液氧环境下，铜线电阻降 80%，需重新校准电流
- ⚠️ 2026-06-10: 磁路材料 Cr13 在 300°C 以上导磁性急剧下降

## 成功案例 (Agent 自记录)
- 2026-06-03: 火箭煤油电磁阀, 3.5MPa, 200°C, 质量优化 12%, 评审通过
- 2026-06-09: 卫星氦气阀, 0.5MPa, -196°C, 功耗优化 18%
```

### 3.5 @mention 元路由 — ACP 精髓

**ACP 核心理念**: 用户通过 `@agent_name` 精确路由到特定专家 Agent，类似 Slack/Discord 的 @mention。

```
用户输入:
  "@设计大师 帮我设计一个 10MPa 的火箭煤油减压阀"

Gateway 解析:
  1. 识别 @设计大师 → 路由到 Design Agent
  2. Design Agent 解析: 10MPa + 煤油 + 减压阀
  3. Design Agent 开始设计 → 输出方案
  4. Design Agent 主动 @仿真专家 进行验证
  5. 仿真结果返回 → Design Agent 调整方案
  6. 最终方案 + 仿真报告 → 呈现给用户

用户输入:
  "@材料专家 推荐用于 800°C 高温氢气环境的密封材料"

Gateway 解析:
  1. 识别 @材料专家 → 路由到 Material Agent
  2. Material Agent 查询材料数据库 + 兼容性矩阵
  3. 返回: 排名 Top3 + 理由 + 替代方案 + 成本对比
```

**路由规则** (可配置):

| @mention | 路由目标 | 能力范围 |
|----------|---------|---------|
| `@设计大师` | Design Agent | 所有阀门/弹簧/密封/O形圈设计 |
| `@仿真专家` | Simulation Agent | CFD/FEM/热力学仿真验证 |
| `@材料专家` | Material Agent | 材料推荐/兼容性/成本分析 |
| `@标准官` | Compliance Agent | 标准合规检查/适航审查 |
| `@研究员` | Knowledge Agent | 文献检索/技术调研/专利分析 |
| `@质量官` | Quality Agent | FMEA/故障树/风险评估 |
| (无 @mention) | Orchestrator | 自动判断所需专家并调度 |

**Agent-to-Agent 内部 @ (ACP 核心)** :

Design Agent 在完成任务后，可以自动发起对其他 Agent 的调用:
```python
# Design Agent 内部逻辑
if design.confidence < 0.9:
    # 自动请求仿真验证
    sim_result = self.route_to("@仿真专家", task="验证方案B的CFD性能")
    if sim_result.safety_factor < 1.5:
        # 自动请求材料审查
        mat_advice = self.route_to("@材料专家", task="方案B的材料在高温下是否合适")
```

### 3.6 自进化学习闭环 — Hermes 精髓

**Hermes 最核心的突破**: Agent 能从每次任务中学习，自动提炼经验，修补自身的能力边界。

**阀门大脑落地**:

```
┌─────────────────────────────────────────────────────────┐
│                    学习闭环 (Learning Loop)              │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  EXECUTE │ →  │ OBSERVE  │ →  │ REFLECT  │           │
│  │  执行任务 │    │ 观察结果 │    │ 反思提炼 │           │
│  └──────────┘    └──────────┘    └──────────┘           │
│       ↑                                │                 │
│       │         ┌──────────┐           │                 │
│       └──────── │  APPLY   │ ←─────────┘                 │
│                 │ 应用经验 │                              │
│                 └──────────┘                              │
│                                                          │
│  每次阀门设计任务完成后:                                  │
│  1. 提取: 这次任务学到了什么? (新约束/新经验/踩坑)       │
│  2. 归类: 经验属于哪个 Skill? 哪个公式?                  │
│  3. 写入: 自动追加到对应 SKILL.md 的 Pitfalls 节          │
│  4. 索引: 更新向量索引，让后续任务能检索到               │
│  5. 冷冻: 关键节点冻结为不可变快照，用于审计             │
└─────────────────────────────────────────────────────────┘
```

### 3.7 Nudge Engine — Hermes 的后台复盘

**借鉴 Hermes 的 Nudge Engine**: 不需要用户主动触发，Agent 在后台定时复盘。

```
Nudge 任务 (Cron 驱动, 借鉴 OpenClaw Cron):

每天 02:00: 复盘昨日所有设计任务 → 提炼可复用经验
每周一 09:00: 生成周报 → 本周设计趋势 + 经验积累 + 待改进项
每月1日: 审视所有 Skill 的 Pitfalls → 合并/清理/升级

Nudge 触发条件 (借鉴 Hermes):
- 某 Skill 执行成功率 < 80% → 自动触发深度分析
- 用户连续 3 次手动纠正同一类型的输出 → 记录为 Pitfall
- 发现新的有效设计模式 → 追加为成功案例
```

### 3.8 "动态图书馆"懒加载 — Hermes 的上下文效率

**问题**: 把所有 307 公式 + 21 材料 + 27 标准全塞进上下文 = Token 爆炸 + 模型注意力分散

**Hermes 方案**: 像图书馆一样，只取当前需要的书架

```python
class DynamicLibraryLoader:
    """
    借鉴 Hermes 的 "动态图书馆" 模式:
    不把所有知识提前注入 system prompt,
    而是根据当前任务动态检索加载
    """
    
    def load_for_task(self, task: str):
        # 步骤1: 意图识别 → 确定需要的知识域
        domains = self.intent_parser.get_domains(task)
        # "设计 10MPa 煤油减压阀" → domains: ['pressure_valve', 'fluid_dynamics', 'material']
        
        # 步骤2: 检索相关知识 (向量 + 图谱)
        relevant = self.retriever.search(
            domains=domains,
            constraints={'pressure': '10MPa', 'medium': '煤油'},
            top_k=15  # 最多加载 15 条相关知识
        )
        
        # 步骤3: 注入 Agent 上下文 (轻量!)
        context = self.format_context(relevant)
        # 包含: 减压阀设计公式(8条) + 煤油物性(1条) + 候选材料(3种)
        # 不包含: 弹簧/O形圈/CFD/非牛顿流体 等无关内容
        
        return context
```

**对比**:

| | 旧模式 (全量注入) | 新模式 (动态图书馆) |
|---|---|---|
| System Prompt 大小 | ~15KB (全部公式摘要) | ~2KB (仅任务相关) |
| Token 消耗 | 高，每次对话重复加载 | 低，按需动态检索 |
| 注意力精度 | 被无关信息分散 | 集中在当前问题 |
| 可扩展性 | 每增公式加重负担 | 总公式数量几乎不影响上下文 |

### 3.9 安全护栏 — Hermes 的自主行为约束

**Hermes 的关键设计**: Agent 能自我创建 Skills → 必须有安全护栏防止坏经验污染

```python
class SafetyGuard:
    """
    借鉴 Hermes 的安全机制:
    - 内容安全扫描: 防止提示词注入
    - Skill 安全扫描: 防止自主创建的 Skill 含危险指令
    """
    
    def validate_skill_update(self, new_content: str) -> bool:
        # 1. 内容安全: 检测提示词注入
        if self.contains_injection(new_content):
            return False
        
        # 2. 工程安全: 检测危险设计建议
        if self.contains_dangerous_recommendation(new_content):
            # 例如: "安全系数可以降低到 0.8" → 拒绝
            return False
        
        # 3. 事实校验: 交叉验证新的"经验"
        if not self.verify_against_known_standards(new_content):
            # 如果与已知标准冲突 → 标记待审核
            return 'pending_review'
        
        return True
```

---

## 四、多 Agent 协作矩阵

### 4.1 Agent 角色定义 (7+1)

```
                           ┌─────────────────────┐
                           │    🏗️  Orchestrator  │
                           │    总工程师/调度中枢   │
                           │    任务分解 · 元路由   │
                           │    冲突仲裁 · 质量把关 │
                           └──────────┬──────────┘
                                      │
          ┌───────────┬───────────────┼───────────────┬───────────┐
          │           │               │               │           │
    ┌─────▼─────┐ ┌──▼──────┐ ┌──────▼─────┐ ┌──────▼───┐ ┌────▼─────┐
    │🎨 设计专家│ │🌊 仿真师│ │🔬 材料学家│ │📋 标准官 │ │📚 研究员│
    │Design    │ │Simulate │ │Material   │ │Compliance│ │Knowledge│
    └─────┬─────┘ └──┬──────┘ └──────┬─────┘ └──────┬───┘ └────┬─────┘
          │           │               │               │           │
          └───────────┴───────────────┼───────────────┴───────────┘
                                      │
                               ┌──────▼──────┐
                               │🛡️ 质量审计官│
                               │  Quality    │
                               │  FMEA/Red Team│
                               └─────────────┘
```

### 4.2 协作模式 (4 种)

| 模式 | 描述 | 适用场景 | 来源思想 |
|------|------|---------|---------|
| **串行管道** | A→B→C→D 线性流 | 标准设计-仿真-合规流程 | ACP 工作流 |
| **并行分治** | 方案A/B/C 同时设计，最后对比 | 多方案概念设计 | OpenClaw Sub-agent |
| **辩论对抗** | Design ↔ Quality 红蓝对抗 | 安全关键设计评审 | Hermes Red Team |
| **层级委派** | Orchestrator→子Agent→Orchestrator | 复杂系统工程 | OpenClaw 委派模式 |

### 4.3 Agent-to-Agent 通信 (ACP 协议)

```
Design Agent                    Simulation Agent
     │                                │
     │  ACP: REQUEST                  │
     │  {                             │
     │    "type": "agent_request",    │
     │    "from": "design_agent",     │
     │    "to": "simulation_agent",   │
     │    "task": "验证方案B",         │
     │    "payload": {                │
     │      "design_params": {...}    │
     │    },                          │
     │    "priority": "high",         │
     │    "callback": "design_agent"  │
     │  }                             │
     ├────────────────────────────────►
     │                                 │
     │                    ACP: RESPONSE│
     │                    {            │
     │                      "status":  │
     │                        "done",  │
     │                      "result":{ │
     │                        "stress":│
     │                   "safety":2.8  │
     │                      }          │
     │                    }            │
     │◄────────────────────────────────┤
```

---

## 五、实施路线图 (融合版)

### Phase 1: 融合地基 (v2.0, 2026-Q3, 11周)

目标: 将 OpenClaw/Hermes/ACP 的核心模式植入现有平台

| # | 任务 | 融合思想 | 估时 |
|---|------|---------|------|
| 1.1 | **Bootstrap 文件系统** | OpenClaw: AGENTS.md/SOUL.md/USER.md/TOOLS.md + skills/ | 1周 |
| 1.2 | **Skills 仓库创建** | OpenClaw: 每个模块写 SKILL.md (标准流程) | 2周 |
| 1.3 | **PAOR 推理循环** | Hermes: Plan-Act-Observe-Reflect + 物理验证 | 2周 |
| 1.4 | **动态图书馆加载器** | Hermes: 按需检索公式/材料/标准, 不全量注入 | 1周 |
| 1.5 | **@mention 路由** | ACP: Gateway 解析 @agent_name → 路由到对应 Agent | 1周 |
| 1.6 | **MCP 工具标准化** | MCP + OpenClaw Tool: 全部工具注册为 MCP Tool | 2周 |
| 1.7 | **Agent Dashboard v1** | 可视化协作状态 + Chat UI | 2周 |
| | **小计** | | **11周** |

### Phase 2: 自进化引擎 (v3.0, 2026-Q4, 16周)

目标: Agent 能从任务中学习，越用越强

| # | 任务 | 融合思想 | 估时 |
|---|------|---------|------|
| 2.1 | **6 Agent 领域实现** | Design/Simulation/Material/Compliance/Knowledge/Quality | 5周 |
| 2.2 | **自进化学习闭环** | Hermes: 执行→观察→反思→应用 自动循环 | 2周 |
| 2.3 | **Nudge Engine** | Hermes + OpenClaw Cron: 定时后台复盘 | 2周 |
| 2.4 | **Skill 自动修补** | Hermes: Pitfalls 自动追加 + 安全扫描 | 2周 |
| 2.5 | **Agent-to-Agent 通信** | ACP: Design 自动请求 Simulation 验证 | 2周 |
| 2.6 | **记忆冻结快照** | Hermes: 关键节点不可变快照 + 审计链 | 1周 |
| 2.7 | **知识图谱 v1** | Neo4j: 阀门本体 + GraphRAG | 2周 |
| | **小计** | | **16周** |

### Phase 3: 超级阀门大脑 (v4.0, 2027-H1, 22周)

目标: 行业标杆级 AI 原生阀门研发平台

| # | 任务 | 融合思想 |
|---|------|---------|
| 3.1 | Agent 技能市场 | OpenClaw SkillHub: 第三方贡献阀门 Skills |
| 3.2 | 多物理场自主仿真 | ACP: 多个仿真 Agent 协同 |
| 3.3 | 数字孪生 | 实物↔虚拟模型实时同步 |
| 3.4 | 联邦经验共享 | 跨组织知识共享 (不泄露原始数据) |
| 3.5 | 语音/AR 交互 | 多模态 Agent 交互 |
| 3.6 | 完全自主设计 | Agent 从需求到详细设计全自动 |

---

## 六、继承 vs 新建 — 与现有系统的关系

### 现有资产在新架构中的位置

```
现有资产                    新架构角色              继承方式
────────────────────────────────────────────────────────
17个工程模块 API           → MCP Tool Server        全部保留, 加 MCP 壳
Flask Blueprint 路由       → Gateway 子路由          保留, 逐步迁移
307+ 公式计算引擎          → 动态图书馆知识源        全部保留, 加向量索引
21种材料数据库             → Material Agent 数据源   全部保留
QJ20156 标准合规工具       → Compliance Agent 核心   全部保留
CMS + 知识库(31400字)      → RAG 知识源              全部保留, embedding
JWT 认证系统               → Gateway Auth            保留并增强
index.html (SPA)           → Agent Dashboard v0      渐进改造为 React
ai_agent_engine.py (930行) → PAOR 循环起点           重构, 保留意图解析
sessions.json              → Session Manager         保留格式, 加 L2/L3
```

### 渐进式迁移 (不推倒重来)

```
Week 1-2: Bootstrap 文件 + Skills 仓库创建 (纯新增, 不影响现有)
Week 3-4: 动态图书馆 + PAOR 循环 (替换 ai_agent_engine.py, 旧 API 不变)
Week 5-6: MCP 工具标准化 (加 MCP 壳, 旧 REST API 保留)
Week 7-8: @mention 路由 + 新 Dashboard (新旧 UI 并存)
Week 9+:  多 Agent 逐个上线 (先内部测试, 再开放)
```

---

## 七、竞争力总结

### 为什么是"阀门大脑"？

| 维度 | 通用 Agent | 我们的阀门大脑 |
|------|-----------|--------------|
| **知识获取** | 从零学习 | 内建 307公式+21材料+27标准+60万字 |
| **知识进化** | 每次从零开始 | 自进化: 越用越懂阀门 |
| **上下文效率** | 全量注入, Token 浪费 | 动态图书馆: 只加载当前需要的 |
| **安全关键** | 无保障机制 | 物理验证+安全护栏+人机协同 |
| **协作模式** | 单人模式 | 7 Agent 矩阵: 设计/仿真/材料/标准/知识/质量/编排 |
| **记忆持久** | 关窗就忘 | L1(会话)+L2(快照)+L3(语义) 三层记忆 |
| **Agent 间通信** | 无 | ACP 协议: @mention + Agent-to-Agent |
| **可解释性** | 黑盒 | 每一步决策可追溯到公式/标准/材料 |
| **经验积累** | 无 | 自动提炼设计经验→修补 Skill→下次复用 |

---

## 八、关键决策待确认

| # | 决策项 | 选项 | 建议 |
|---|--------|------|------|
| 1 | LLM 选型 | Claude / GPT / DeepSeek / 国产模型 | 混合: 编排用 Claude, 计算用函数(非LLM), 检索用嵌入模型 |
| 2 | 部署环境 | Render (海外) / 国内云 (阿里/腾讯) | 国内云优先 (目标用户在国内) |
| 3 | 后端框架 | Flask (现状) / FastAPI (推荐) | v2.0 保留 Flask, v3.0 迁移 FastAPI |
| 4 | 开源策略 | 核心开源 / Skills 开源 / 完全闭源 | 核心引擎开源, 阀门 Skills 和数据集闭源 |
| 5 | 知识图谱 | Neo4j / 自研轻量图 | Neo4j AuraDB (托管, 免运维) |

---

*本文档为融合架构 v2.0, 深度吸纳 OpenClaw (平台思维) + Hermes (进化思维) + ACP (互联思维) 三大架构哲学*


## 九、批判性审查与风险管控

> 本章为 v2.0.1 审计新增，用批判性思维和系统思维审视架构的假设、漏洞与风险。
> 架构设计的本质不是画出完美的图，而是**诚实地承认什么可能出错**。

### 9.1 已验证的架构风险矩阵

| # | 风险 | 严重度 | 概率 | 被发现阶段 | 当前缓解 | 残余风险 |
|---|------|--------|------|------------|---------|---------|
| R1 | PLAN.md 与架构文档路线图冲突 | P0 | 已发生 | 审计 | 无 | **两个v2.0含义互斥** |
| R2 | 自进化与航空安全文化冲突 | P0 | 高 | 审计 | 安全护栏(3.9) | 护栏只能拦截显式违规，无法验证工程正确性 |
| R3 | 假阳性学习污染知识库 | P0 | 中 | Phase 2 | 无 | Agent错误被固化为"成功案例"后指数扩散 |
| R4 | Agent调用链级联故障 | P1 | 高 | Phase 2 | 无超时/重试/熔断 | 单一节点故障阻塞整个设计流程 |
| R5 | LLM成本失控 | P1 | 高 | Phase 2 | 无预算限制 | 一次设计8-12次LLM调用，无上限 |
| R6 | 技术栈过度膨胀 | P1 | 中 | Phase 1 | 无 | Neo4j+Qdrant+Docker对<1GB数据过度设计 |
| R7 | 自增强偏见固化 | P2 | 中 | Phase 3 | 无 | 成功案例正反馈削弱设计多样性 |
| R8 | Approval Bridge 单人悖论 | P2 | 已发生 | Phase 1 | 无 | 单人既是请求者又是审批者，失去意义 |
| R9 | 公式检索假阴性 | P2 | 低 | Phase 1 | 动态图书馆(3.8) | 语义检索<100%召回，遗漏关键公式 |
| R10 | Agent维护负担 | P3 | 高 | Phase 2 | 无 | 25+个SOUL.md/SKILL.md持续演化无人维护 |

### 9.2 自进化 vs 航空安全 — 根本矛盾及解决

**矛盾本质**：

```
航空安全哲学 (DO-178C / ARP4754):
  改一个参数 → 写分析报告 → 同行评审 → 测试验证(可能数周) → 审批 → 部署

自进化 Skills (Hermes 模式):
  Agent 发现模式 → 自动追加到 SKILL.md → 下次立即生效
  
这两者不可调和。航空领域不允许"先上线再验证"。
```

**解决方案：三阶段安全验证流水线**

```
                    ┌──────────────┐
  经验提取          │  STAGE 0     │
  (自动化)          │  原始观察    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
  自动验证          │  STAGE 1     │
  (自动化, <1min)   │  安全围栏    │
                    │  · 提示词注入检测         │
                    │  · 危险参数检测           │
                    │  · 标准冲突检测           │
                    │  · 物理合理性校验(量纲)   │
                    └──────┬───────┘
                           │ ✅ 通过
                    ┌──────▼───────┐
  回归测试          │  STAGE 2     │
  (自动化, ~5min)   │  测试验证    │
                    │  · 历史测试用例回放(≥20个)    │
                    │  · 安全系数边界测试            │
                    │  · 与已知标准的交叉验证        │
                    └──────┬───────┘
                           │ ✅ 通过
                    ┌──────▼───────┐
  人工审核          │  STAGE 3     │
  (人工, 按需)      │  专家评审    │
                    │  · 仅触达: 涉及安全系数/标准参数变更  │
                    │  · 自动跳过: 纯文本错误修正           │
                    │  · 审后: 批准/修订/拒绝 + 记录        │
                    └──────┬───────┘
                           │ ✅ 批准
                    ┌──────▼───────┐
                    │  合并并部署  │
                    └──────────────┘
```

**护栏分级**：

| Stage | 自动化 | 耗时 | 拦截什么 |
|-------|--------|------|---------|
| Stage 1 安全围栏 | 100% 自动 | <1min | 注入/危险参数/标准冲突 |
| Stage 2 回归测试 | 100% 自动 | ~5min | 历史用例失败/边界违规 |
| Stage 3 人工审核 | 按需触发 | 不定 | 关键安全变更的专家判断 |

> **底线原则**: 任何涉及安全系数降低、标准参数修改、材料替换的建设性更新，**自动进入 Stage 3 人工审核**，不可自动生效。

### 9.3 系统反馈回路分析

```
强化回路 (正反馈):
  ┌─────────────────────────────────────────────────┐
  │  更多设计 → 更多Pitfalls → 更好的Skill →        │
  │  更好的设计 → 更多使用 → 更多设计                │
  │  ⚠️ 风险: 若无多样性机制，收敛到局部最优          │
  └─────────────────────────────────────────────────┘

平衡回路 (负反馈):
  ┌─────────────────────────────────────────────────┐
  │  复杂度增加 → Bug增加 → 修复成本增加 →           │
  │  开发速度下降 → 复杂度增速放缓                   │
  │  ⚠️ 风险: 临界点后陷入维护沼泽                    │
  └─────────────────────────────────────────────────┘

危险回路 (必须打断):
  ┌─────────────────────────────────────────────────┐
  │  隐晦错误 → 被视为成功 → 记录为案例 →            │
  │  固化进Skill → 更多相同错误 → 错误常态化         │
  │  ⛔ 打断方式: Stage 2 回归测试 + 人工抽样审计    │
  └─────────────────────────────────────────────────┘
```

**自增强偏见对抗策略**：

| 策略 | 机制 | 成本 |
|------|------|------|
| Epsilon-Greedy 探索 | 每 20 次设计随机插入 1 次替代方案对比 | 低 |
| 负采样学习 | Nudge Engine 不仅记录成功案例，也记录被拒绝的方案及原因 | 低 |
| 周期性审计 | 每 50 次设计后自动审查 Skill 中固化经验的多样性 | 中 |
| 人类扰动 | 用户定期手动插入非常规设计参数验证 Agent 鲁棒性 | 零 |

---

## 十、系统工程质量保障

> 本章为 v2.0.1 审计新增。一个七 Agent 系统如果没有工程质量的保障，就是七倍的不可靠。

### 10.1 错误处理与韧性架构

**Agent 调用链韧性四件套**：

```
韧性 = 超时(Timeout) + 重试(Retry) + 降级(Degrade) + 熔断(Circuit Breaker)
```

| 机制 | 配置 | 为什么 |
|------|------|--------|
| **超时** | Orchestrator 30s / 计算 Agent 15s / 仿真 Agent 60s / 检索 Agent 5s | 防止级联等待 |
| **重试** | 最多 3 次, 指数退避 (1s→2s→4s), 仅重试 5xx 和网络错误 | 处理瞬时故障 |
| **降级** | CFD 仿真不可用 → 降级为经验公式估算 + 标注"未经仿真验证" | 不阻塞主流程 |
| **熔断** | 连续 5 次失败 → 停用该 Agent 5 分钟 → 半开探测 → 恢复或继续熔断 | 防止雪崩 |

```python
@resilient(timeout_ms=15000, retries=3, degrade=empirical_formula)
def call_simulation_agent(design_params):
    result = simulation_agent.run_cfd(design_params)
    if result.diverged:
        return degraded_response(design_params, reason="CFD发散")
    return result
```

**级联故障隔离**：

```
调用链: O → D → S → C
                ↓
              S 故障
                ↓
         ┌──────┴──────┐
         │  熔断器断开  │  → D 收到 "S暂不可用" (非超时)
         │  5分钟内不再 │
         │  调用 S      │
         └──────┬──────┘
                ↓
         D 降级: 用经验公式
         继续 → C 合规检查
         (标注: "方案未经仿真验证")
```

**死信队列**: 无法处理的任务进入死信队列 → 定时重试 → 超过阈值人工介入。

### 10.2 LLM 成本模型与预算控制

**调用量估算** (一次阀门设计):

```
Orchestrator 意图解析     1 次 (小模型, ~500 tokens)
Design Agent 方案生成     2-3 次 (大模型, ~2000 tokens/次)
Simulation Agent 结果解读 1 次 (小模型, ~800 tokens)
Compliance Agent 合规报告 1 次 (小模型, ~600 tokens)
Orchestrator 汇总         1 次 (小模型, ~1000 tokens)
─────────────────────────────────────────────
合计: 6-7 次 LLM 调用, ~8000-12000 tokens

成本 (以 DeepSeek v3 为例, $0.27/1M input, $1.10/1M output):
  单次设计: ~$0.01-0.02
  日 50 次: ~$0.50-1.00
  月 1500 次: ~$15-30
  年 18000 次: ~$180-360
```

**三层模型分派策略**:

| 层 | 任务 | 模型 | 成本/1M tokens |
|---|------|------|--------------|
| L0 函数层 | 公式计算、数据库查询、标准检查 | **无 LLM** (纯 Python) | $0.00 |
| L1 轻量层 | 意图解析、检索Query生成、结果格式化 | 小模型 (DeepSeek-Lite) | ~$0.14 |
| L2 深度层 | 方案推理、多约束优化、技术解释 | 大模型 (DeepSeek-V3) | ~$1.37 |

> **核心原则**: 能算的不推理。207 条公式、21 种材料、QJ20156 标准检查全部走 L0 函数层，不走 LLM。

**预算保护**:

```python
class CostGuard:
    daily_budget = 5.0      # 日预算 $5
    monthly_budget = 150.0  # 月预算 $150
    per_request_cap = 0.05  # 单次上限 $0.05
    
    def before_call(self, estimated_cost):
        if self.daily_spent + estimated_cost > self.daily_budget:
            raise BudgetExceeded("今日预算耗尽，请明天再试或联系管理员")
```

### 10.3 可观测性架构

**四层监控**：

```
L1: 基础设施
    · Flask 进程存活 (Heartbeat)
    · 内存/CPU/磁盘
    · LLM API 可用性
    · Docker 沙箱状态

L2: Agent 运行时
    · 每 Agent 的请求量/延迟/错误率
    · 熔断器状态 (开/半开/闭)
    · 死信队列深度
    · L0/L1/L2 调用比例

L3: 业务逻辑
    · 设计请求完成率
    · 安全系数分布直方图
    · 材料推荐分布
    · 用户纠正率 (Agent输出被人工修改的比例)

L4: 学习系统
    · Skill 更新频率
    · Pitfall 增长曲线
    · Nudge Engine 执行日志
    · 知识库版本快照
```

**Agent 决策审计日志** (每条设计决策的可追溯性):

```json
{
  "run_id": "run_20260612_125000_a1b2c3",
  "user_input": "设计 10MPa 煤油减压阀",
  "trace": [
    {"agent": "Orchestrator", "action": "intent_parse", "result": "design_pressure_valve", "time_ms": 230},
    {"agent": "Design",     "action": "formula_call", "formula": "PRV_critical_flow", "inputs": {...}, "outputs": {...}, "time_ms": 45},
    {"agent": "Design",     "action": "llm_reason",   "model": "deepseek-v3", "prompt_tokens": 1200, "completion_tokens": 500, "time_ms": 3100},
    {"agent": "Simulation", "action": "cfd_run",      "status": "failed", "reason": "mesh_divergence", "time_ms": 42000},
    {"agent": "Design",     "action": "degrade",      "fallback": "empirical_Pr", "time_ms": 15},
    {"agent": "Compliance", "action": "standard_check","standard": "QJ20156", "result": "pass", "time_ms": 80}
  ],
  "final_decision": {"design": "方案B", "safety_factor": 2.8, "confidence": 0.85}
}
```

### 10.4 技术栈降维 — 渐进复杂度路线

**问题**: 当前架构要求 Docker + Neo4j + Qdrant + PostgreSQL + Redis，但项目是个人/小团队规模。

```
数据量评估:
  207 公式 × 5 字段       = ~1000 条元数据
  60 万字知识库            = ~4000 段落
  21 种材料 × 30 属性     = ~630 条记录
  ─────────────────────────────────
  总数据 < 10MB (加载到内存)
```

**Phase 1 MVP 技术栈 (保持简单)**：

| 组件 | MVP 方案 | 满载方案 | 切换时机 |
|------|---------|---------|---------|
| 数据库 | SQLite (现状) | PostgreSQL | 并发写入 > 10 QPS 或数据 > 1GB |
| 向量存储 | ChromaDB 嵌入式 | Qdrant | 向量 > 10万条 或 需要分布式 |
| 知识图谱 | Python dict + JSON 文件 | Neo4j | 实体 > 1000 或 图遍历 > 3层深度 |
| 消息队列 | 内存队列 + SQLite 持久化 | Redis/RabbitMQ | Agent 间异步调用 > 100/min |
| 容器化 | 裸 Python 进程 (现状) | Docker Compose | 需要多服务编排或环境隔离 |

> **原则**: 先证明价值，再优化架构。如果 207 条公式用 JSON 文件就能服务好用户，就不要引入 Neo4j 的运维负担。

---

## 十一、降维实施路径 v2.0.1-pragmatic

> 本章为 v2.0.1 审计新增。将"十人团队三年愿景"降维为"两人+AI 助手"可执行的路线。

### 11.1 版本号重整

```
原混乱:
  PLAN.md:  v2.0 = 社区版 (公开注册/国际化)
  架构文档: v2.0 = AI原生融合架构

统一方案 (PLAN.md 纳管架构文档):
  v1.3 生产就绪 (当前进行中) → 完成 Docker/HTTPS/监控
  v2.0 AI 原生 MVP (2026-Q3)  → PAOR 循环 + Skills + 动态图书馆
  v2.5 自进化引擎 (2026-Q4)   → 学习闭环 + 多Agent + 知识图谱
  v3.0 社区版 (2027-Q1)       → 公开注册 + 国际化 + API开放
  v4.0 超级阀门大脑 (2027-H2) → 数字孪生 + 自主设计
```

### 11.2 MVP 核心交付 (8 周，非 11 周)

**砍掉什么**：
- ❌ Neo4j 知识图谱 → 推迟到 v2.5
- ❌ Qdrant 向量数据库 → ChromaDB 嵌入式替代
- ❌ 完整 ACP 协议栈 → 先用 REST API 模拟 Agent 间通信
- ❌ 7 个 Agent → Phase 1 只做 3 个 (Orchestrator + Design + Compliance)
- ❌ Agent Dashboard 改为简单的 Chat UI 升级

**保留什么**：
- ✅ PAOR 推理循环 — 这是核心差异化
- ✅ 动态图书馆加载 — 公式按需注入
- ✅ Skills 模块化 — 每模块写 SKILL.md
- ✅ Bootstrap 文件 — AGENTS.md/SOUL.md/USER.md
- ✅ L1 工作记忆 + 决策日志

**8 周 MVP 路线**：

| 周 | 交付 |
|----|------|
| W1-2 | Bootstrap 文件体系 + 3 个 SKILL.md |
| W3-4 | PAOR 循环 (替换 ai_agent_engine.py) |
| W5-6 | 动态图书馆 + ChromaDB 嵌入 |
| W7-8 | 3 Agent (编排+设计+合规) + Chat UI 升级 |

### 11.3 不做的事情 (明确排除)

| 原规划 | 决策 | 理由 |
|--------|------|------|
| Neo4j 知识图谱 (Phase 3) | **推迟** | 数据<10MB, JSON文件够用 |
| Qdrant (Phase 2) | **降级** | ChromaDB 嵌入式零运维 |
| ACP 完整协议栈 | **简化** | 单开发者不需要完整的 stdio JSON-RPC |
| 7 个独立 Agent | **合并** | Phase 1 只做 3 个 |
| 辩论对抗模式 | **推迟** | 需要 3+ Agent 且目前没有 Red Team 能力 |
| Agent 技能市场 | **推迟到 v4.0** | 需要社区和生态 |
| 语音/AR 交互 | **搁置** | 无明确用户需求 |

### 11.4 成功标准 (MVP)

```
MVP 完成 = 以下 5 个用例可通过:

1. "设计一个 5MPa 液氧电磁阀" 
   → Agent 自主选型+计算+输出方案+合规检查

2. "方案B的安全系数是多少？是否符合QJ20156？"
   → Agent 回溯设计历史+引用标准+给出结论

3. "为什么选了 TC4 而不是 Inconel718？"
   → Agent 列出材料对比+选择理由+引用成功案例

4. "这个设计有什么风险？"
   → Agent 引用 SKILL.md 中 Pitfalls + 历史失败案例

5. 相同输入两次 → 结果稳定 (非随机)
   → 温度、压力、介质相同 → 推荐方案一致
```

---

## 附录 A: 审计方法说明

### 批判性思维框架

| 维度 | 核心问题 | 在本架构中的应用 |
|------|---------|---------------|
| **清晰性** | 概念是否无歧义？ | 发现 v2.0 在 PLAN.md 和架构文档中含义不同 |
| **准确性** | 断言是否有证据？ | "越用越强" 缺乏工程验证闭环设计 |
| **精确性** | 是否足够细节？ | 错误处理/成本/可观测性完全缺失 |
| **相关性** | 解决的问题是真实问题吗？ | Neo4j 对 <10MB 数据过度 |
| **深度** | 是否触及根本？ | 自进化 vs 安全文化的矛盾触及航空工程伦理 |
| **广度** | 是否覆盖所有视角？ | 缺少运维视角 (谁维护 25+ 个 SKILL.md？) |
| **逻辑** | 推理是否自洽？ | "Session 隔离" vs "Agent 间自由调用" 存在张力 |

### 系统性思维框架

| 维度 | 核心问题 | 发现 |
|------|---------|------|
| **反馈回路** | 什么在自我强化/自我纠正？ | 3 个回路识别 (强化/平衡/危险) |
| **涌现特性** | 整体是否产生部分不具备的特性？ | 假阳性学习扩散、自增强偏见 |
| **边界** | 系统边界在哪里？什么被排除？ | 运维/安全/成本/部署边界模糊 |
| **杠杆点** | 哪里的小改变能产生大影响？ | PAOR 循环是最大杠杆点，Neo4j 是最小 |
| **延迟** | 因果之间的延迟多长？ | 错误固化的延迟 = 数周到数月 |

---

*本文档 v2.0.1 — 审计版。新增第十至十二章及附录 A，基于 2026-06-12 批判性+系统性审计。*
*审计原则: 架构设计的质量 = 能多诚实地承认可能出错。*
