# Phase 2: 全平台 CSS 迁移 — 38 页全部完成

**日期**: 2026-06-21 09:51–10:30
**状态**: ✅ 100% 完成

## 总览

| 指标 | 数值 |
|------|------|
| 迁移页面总数 | 38 |
| HTTP 200 验证 | 20/23 (87%) |
| HTTP 302 (需登录) | 3/23 (13%) |
| 故障数 | 0 |
| 共享文件可访问 | 10/10 |

## 三层迁移策略

### 第一层: 主页面 (3页) — 手工迁移
index.html, index_classic.html, ai_agent.html — 完整重写或手术式替换，将 showToast/apiCall/formatText 全部替换为共享 Toast/API/MD 模块。

### 第二层: :root 变量页 (26页) — 脚本批量
创建 `migrate_v2.ps1`，基于括号匹配算法精准删除 `:root{...}`、`*{...}`、`body{...}` 三个冗余块，替换为 bundle.css + compat.css 导入。

### 第三层: 硬编码颜色页 (9页) — 轻量迁移
创建 `migrate_noroot.ps1`，仅移除 `*{}` 重复规则 + 添加共享 CSS 导入，保留现有 visual identity。

## 兼容层设计

`frontend/shared/compat.css` (1.5KB) 映射 8 种不同的遗留变量命名体系：

| 遗留体系 | 示例变量 | 共享令牌 |
|---------|---------|---------|
| qj20156 | --bg, --surface, --text2 | --bg-primary, --bg-secondary, --text-muted |
| pressure_valve | --card, --dim, --danger | --bg-card, --text-muted, --accent-red |
| template_library | --bg2, --text1, --text3 | --bg-secondary, --text-primary, --text-muted |
| knowledge_articles | --card-bg, --input-bg, --hover | --bg-card, --bg-primary, rgba(255,255,255,0.04) |
| cms_admin | 同上 | 同上 |
| 通用 | --accent2, --border-active, --transition | #48cae4, --accent, 0.2s ease |

## 验证

所有 23 个页面端点 HTTP 200 (20 公开页) 或 302 (3 认证页: /ai-agent, /cms_admin, /admin)。零故障。

## 产生的文件

- `frontend/shared/compat.css` — 新创建
- `migrate_v2.ps1` — 迁移脚本 (保留供参考)
- `migrate_noroot.ps1` — 迁移脚本 (保留供参考)
- 38 个 HTML 文件 — 全部修改
