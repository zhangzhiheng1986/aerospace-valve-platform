# Phase 2: 共享设计系统迁移 — 三页面完成

**日期**: 2026-06-21 07:58–08:15
**状态**: ✅ 完成

## 迁移范围

将三个核心页面从"独立 CSS 副本"（~250 行 :root + body 在每页重复）迁移到共享设计系统。

### 1. index.html (仪表盘 v4) — 已迁移 ✅
- **之前**: ~550 行内联 CSS，500+ 行剩余
- **之后**: `<link bundle.css>` + 4 个共享 JS 模块 + 保留 ~120 行页面专属 CSS
- 页面专属样式：sidebar nav、chat container、agent cards、messages、input、external links
- 共享引用：5 个 (bundle.css, utils.js, toast.js, api.js, markdown.js)

### 2. index_classic.html (经典仪表盘) — 已迁移 ✅
- **之前**: 1120 行，全部内联 CSS/JS
- **之后**: `<link bundle.css>` + 4 个共享 JS 模块 + 保留 ~140 行页面专属 CSS
- 页面专属样式：collapsible nav-section、module-card、quick-stat、topbar、sidebar-user menu、mobile
- 共享引用：4 个 (bundle.css, utils.js, toast.js, api.js)
- 修复：`onclick="alert()"` → `Toast.info()`
- 修复：`fetch()` → `API.get()`/`API.post()`
- 修复：sidebar footer 链接从内联 style 提取为 `.sidebar-footer-link` 类

### 3. ai_agent.html (AI Co-Pilot) — 已迁移 ✅
- 变更：替换 `:root` + `*` + `body` → `<link bundle.css>`
- 变更：替换 `apiCall()` → `API.get()`/`API.post()`
- 变更：替换 `showToast()` → `Toast.info()`/`Toast.error()`
- 变更：替换 `formatText()` → `MD.render()`
- 变更：删除重复 `.toast` CSS（现由 shared toast.css 提供）
- 新增：4 个共享 JS 导入

## 迁移前后对比

| 页面 | 迁移前 CSS 行数 | 迁移后 CSS 行数 | CSS 缩减 | 共享引用 |
|------|----------------|----------------|---------|---------|
| index.html | ~550 | ~120 | 78% | 5 |
| index_classic.html | ~290 | ~140 | 52% | 4 |
| ai_agent.html | ~360 | ~280 | 22% | 5 |

## 共享模块使用统计

| 共享模块 | index.html | index_classic | ai_agent |
|---------|-----------|--------------|---------|
| bundle.css | ✅ | ✅ | ✅ |
| utils.js | ✅ | ✅ | ✅ |
| toast.js | ✅ | ✅ | ✅ |
| api.js | ✅ | ✅ | ✅ |
| markdown.js | ✅ | ❌ | ✅ |

## 验证
- `GET /` → HTTP 200, 23644 chars, 5 shared refs ✅
- `GET /classic` → HTTP 200, 53808 chars, 4 shared refs ✅
- `ai_agent.html` → 文件验证: 50054 chars, 5 shared refs ✅ (需登录)

## 待迁移
- 剩余 34 个独立模块 HTML 页面 (checkbox, cfd, thermal, structural, fluid_mechanics, materials, valve_metrics, qj20156, knowledge, knowledge_articles, cms_admin, templates, news, oring_design, spring_design, seal_design, solenoid, pressure_valve, docs, admin, login, avis, departments, projects, filesystem, cron, expert, multi-agent, product-structure, auto-optimizer, knowledge-graph, llm-status, safety-valve, login)
- 建议优先级：流体力学计算器 > 材料数据库 > 电磁阀 > 其余
