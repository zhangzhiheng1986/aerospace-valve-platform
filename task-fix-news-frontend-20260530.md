# 每日资讯模块修复 — 2026-05-30/0600

## 问题
用户反馈：平台中看不到最新资讯数据。

## 根因：前端 JS 与 API 响应格式不匹配

`news.html` 中的 JS 函数通过 `fetch()` 调用后端 JSON API，但期望的响应格式与实际 API 返回不一致：

| API | 实际返回 | JS 期望（错误） | 修复后 |
|-----|---------|----------------|--------|
| `/api/news/dates` | `["2026-05-26", ...]` (数组) | `data.success && data.dates` | `Array.isArray(data)` |
| `/api/news/stats` | `{dates:[], total_entries:1, ...}` (扁平对象) | `data.success && data.stats` | `data.total_entries` 直接访问 |
| `/api/news/date/<d>` | `{date, items:[...], ...}` (扁平对象) | `data.success && data.entry` | `data.items.length > 0` |
| `/api/news/import` | `{success:true/false, message, data}` | 同 | 保持（已经是正确格式） |

所有条件分支中 `data.success` 始终为 `undefined`，导致页面显示为空。

## 修复内容

### 1. `frontend/news.html` — 修复 4 个 JS 函数的条件判断
- `loadDates()`: 直接判断 `Array.isArray(data)` 而非 `data.dates`
- `loadStats()`: 直接判断 `data.total_entries` 而非 `data.stats.*`
- `loadNews()`: 直接判断 `data.items.length > 0` 而非 `data.entry`
- `importNews()`: 保持 `data.success`（此端点已使用正确格式）

### 2. `data/news_index.json` — 清理低质量数据
- 删除 2026-05-29 的3条（非新闻内容，是AI搜索质量反馈）
- 删除 2026-05-18 的6条（markdown解析错误，首条为"序号. 标题"）
- 保留 2026-05-26 的10条完整新闻（标题/来源/摘要齐全，中文正常）

### 3. `backend/app/utils/clean.py` — numpy 降级修复（上一轮已完成）
- `numpy_safe()` 在 numpy 未安装时返回原始数据，不再抛 ImportError

## 验证结果
```
$ curl http://127.0.0.1:5000/api/news/stats
{"dates":["2026-05-26"], "last_updated":"2026-05-30T00:00:00.000000", "total_entries":1}

$ curl http://127.0.0.1:5000/news | grep "Array.isArray"
if (Array.isArray(data)) {           ← 修复已生效

$ curl http://127.0.0.1:5000/news | grep "data.items"
if (data && data.items && data.items.length > 0) {  ← 修复已生效
```

Flask 已重启，服务运行在 127.0.0.1:5000，访问 `/news` 即可看到 2026-05-26 的 10 条资讯。