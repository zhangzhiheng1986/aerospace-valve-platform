## 每日资讯模块 - 任务总结 (2026-05-30/0530)

### 目标
完成航空航天阀门研发平台的「每日资讯」模块，实现定时任务自动搜索新闻 → 自动导入平台 → 用户随时浏览。

### 完成事项

**1. `backend/news_feed.py` — 后端数据层**
- Markdown格式新闻解析与JSON存储
- 支持按日期查询、最新新闻拉取、统计信息
- `import_latest_markdown()` 自动扫描workspace根目录下的 `aerospace-valve-news*.md` 文件并导入

**2. `backend/app/blueprints/news.py` — Flask Blueprint**
- 已有端点：`/api/news/latest|stats|dates|date/<date>|entry(POST)`
- 新增端点：`/api/news/import` (POST) — 从markdown自动导入
- 对应HTML页面：`/news` → `news.html`

**3. `frontend/news.html` — 前端页面**
- 深色主题，侧边栏日期导航 + 内容面板
- JS fetch调用全部API端点，事件委托处理交互
- "导入最新"按钮调用 POST `/api/news/import`

**4. `frontend/index.html` — 导航入口**
- 侧边栏已添加「📰 每日资讯」链接

**5. `backend/app/utils/clean.py` — numpy降级修复**
- `numpy_safe()` 函数在numpy未安装时返回原始数据（不再报ImportError）
- 这对资讯模块是必需的（纯Python数据类型，无numpy依赖）

**6. `backend/app/__init__.py` — 启动自动导入**
- `_auto_import_news()` — 应用启动时扫描新markdown文件并自动导入
- 异常静默处理（日志warning），不影响其他模块启动

**7. 定时任务更新**
- 任务名「每日航空航天阀门研发新闻推送」(d78fdf86)已更新
- 新增步骤5: 保存为 `aerospace-valve-news-YYYY-MM-DD.md`
- 新增步骤6: 运行 `curl -s -X POST http://127.0.0.1:5000/api/news/import` 自动导入

**8. HEARTBEAT.md 更新**
- 新增心跳检查第5项：定期调用 `/api/news/import`，确保新闻文件始终同步

**9. `backend/app.py` — 新建启动入口**
- 使用Flask app factory模式，设置sys.path后创建应用

### 当前数据
- 已导入3期：2026-05-18 (6条)、2026-05-26 (10条)、2026-05-29 (3条)
- Flask运行在 127.0.0.1:5000，全部新闻API端点200 OK

### 修复的问题
- `numpy_safe()` 在无numpy环境下报 `ModuleNotFoundError: No module named 'numpy'` → 修复为优雅降级
- `backend/app.py` 入口文件不存在 → 新建（使用app factory，非v2的 `app/__init__.py`）

### 数据流架构
```
Cron Job (每天08:00)
  → 搜索新闻 → 保存 .md 文件
  → curl POST /api/news/import
  → news_feed.parse_markdown_news()
  → data/news/YYYY-MM-DD.json

Flask 启动时
  → _auto_import_news()
  → 扫描 *.md 文件 → 导入 → JSON

心跳检查
  → curl POST /api/news/import
  → 增量导入新文件
```

### 变更文件
| 文件 | 操作 |
|------|------|
| backend/news_feed.py | 修改 |
| backend/app/blueprints/news.py | 修改（新增 /api/news/import） |
| backend/app/utils/clean.py | 修改（numpy降级） |
| backend/app/__init__.py | 修改（启动自动导入） |
| backend/app.py | 新建（启动入口） |
| frontend/news.html | 已存在 |
| frontend/index.html | 已修改 |
| import_news.py | 修改 |
| rewrite_news_feed.py | 已删除（不再需要） |
| data/news/*.json | 已生成（3期数据） |
| HEARTBEAT.md | 已修改 |
| 定时任务 d78fdf86 | 已更新 |
