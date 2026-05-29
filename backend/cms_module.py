# -*- coding: utf-8 -*-
"""
CMS Module - Aerospace Valve R&D Platform
Professional content management system with SQLite backend.
"""

import sqlite3
import json
import os
import re
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'cms.db')


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db():
    conn = _get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL DEFAULT '',
            summary TEXT DEFAULT '',
            category_id INTEGER,
            tags TEXT DEFAULT '',
            status TEXT DEFAULT 'draft',
            author TEXT DEFAULT '',
            view_count INTEGER DEFAULT 0,
            is_pinned INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
        CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category_id);
        CREATE INDEX IF NOT EXISTS idx_articles_created ON articles(created_at DESC);
    ''')

    # Insert default categories if empty
    cur = conn.execute("SELECT COUNT(*) FROM categories")
    if cur.fetchone()[0] == 0:
        defaults = [
            ('1_block_foundation', '一、基础理论', '流体力学、热力学、材料科学等基础学科'),
            ('2_block_specialized', '二、专业技术', '阀门设计、材料选型、制造工艺、测试验证'),
            ('3_block_application', '三、工程应用', '航空应用、航天应用、推进系统、生命保障'),
            ('4_block_standards', '四、标准规范', '国军标、航天标准、国际标准解读与应用'),
            ('5_block_cases', '五、典型案例', '型号研制案例、故障分析与归零报告'),
            ('6_block_trends', '六、前沿动态', '新技术、新材料、新工艺发展动态'),
        ]
        conn.executemany(
            "INSERT INTO categories (slug, name, description) VALUES (?, ?, ?)",
            defaults
        )

    conn.commit()
    conn.close()


def _slugify(text):
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug or 'untitled'


def _clean(obj):
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_clean(v) for v in obj]
    elif isinstance(obj, float):
        if obj != obj or obj == float('inf') or obj == float('-inf'):
            return None
    return obj


# ============ Category CRUD ============

def get_categories():
    conn = _get_db()
    rows = conn.execute("SELECT * FROM categories ORDER BY sort_order, id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category(category_id):
    conn = _get_db()
    row = conn.execute("SELECT * FROM categories WHERE id=?", (category_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_category(name, description='', sort_order=0):
    conn = _get_db()
    slug = _slugify(name)
    try:
        conn.execute(
            "INSERT INTO categories (name, slug, description, sort_order) VALUES (?, ?, ?, ?)",
            (name, slug, description, sort_order)
        )
        conn.commit()
        cat_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        row = conn.execute("SELECT * FROM categories WHERE id=?", (cat_id,)).fetchone()
        conn.close()
        return {'success': True, 'category': dict(row)}
    except sqlite3.IntegrityError as e:
        conn.close()
        return {'success': False, 'error': f'分类名称或标识重复: {e}'}


def update_category(category_id, name=None, description=None, sort_order=None):
    conn = _get_db()
    existing = conn.execute("SELECT * FROM categories WHERE id=?", (category_id,)).fetchone()
    if not existing:
        conn.close()
        return {'success': False, 'error': '分类不存在'}

    updates = {}
    if name is not None:
        updates['name'] = name
        updates['slug'] = _slugify(name)
    if description is not None:
        updates['description'] = description
    if sort_order is not None:
        updates['sort_order'] = sort_order

    if not updates:
        conn.close()
        return {'success': True, 'category': dict(existing)}

    set_clause = ', '.join(f"{k}=?" for k in updates)
    values = list(updates.values()) + [category_id]
    try:
        conn.execute(f"UPDATE categories SET {set_clause} WHERE id=?", values)
        conn.commit()
        row = conn.execute("SELECT * FROM categories WHERE id=?", (category_id,)).fetchone()
        conn.close()
        return {'success': True, 'category': dict(row)}
    except sqlite3.IntegrityError as e:
        conn.close()
        return {'success': False, 'error': f'更新失败: {e}'}


def delete_category(category_id):
    conn = _get_db()
    existing = conn.execute("SELECT * FROM categories WHERE id=?", (category_id,)).fetchone()
    if not existing:
        conn.close()
        return {'success': False, 'error': '分类不存在'}
    conn.execute("DELETE FROM categories WHERE id=?", (category_id,))
    conn.commit()
    conn.close()
    return {'success': True, 'deleted': dict(existing)}


# ============ Article CRUD ============

def get_articles(status=None, category_id=None, search=None, limit=50, offset=0, pinned_first=True):
    conn = _get_db()
    conditions = []
    params = []

    if status:
        conditions.append("a.status = ?")
        params.append(status)
    if category_id:
        conditions.append("a.category_id = ?")
        params.append(category_id)
    if search:
        conditions.append("(a.title LIKE ? OR a.content LIKE ? OR a.tags LIKE ?)")
        q = f"%{search}%"
        params.extend([q, q, q])

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    order = "ORDER BY a.is_pinned DESC, a.created_at DESC" if pinned_first else "ORDER BY a.created_at DESC"

    query = f"""
        SELECT a.*, c.name as category_name, c.slug as category_slug
        FROM articles a
        LEFT JOIN categories c ON a.category_id = c.id
        {where}
        {order}
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()

    count_query = f"""
        SELECT COUNT(*) FROM articles a
        LEFT JOIN categories c ON a.category_id = c.id
        {where}
    """
    total = conn.execute(count_query, params[:-2]).fetchone()[0]

    conn.close()

    articles = []
    for r in rows:
        art = dict(r)
        art['tags_list'] = [t.strip() for t in art['tags'].split(',') if t.strip()] if art['tags'] else []
        articles.append(art)

    return {'articles': articles, 'total': total, 'limit': limit, 'offset': offset}


def get_article(article_id):
    conn = _get_db()
    row = conn.execute("""
        SELECT a.*, c.name as category_name, c.slug as category_slug
        FROM articles a
        LEFT JOIN categories c ON a.category_id = c.id
        WHERE a.id=?
    """, (article_id,)).fetchone()

    if row:
        # Increment view count
        conn.execute("UPDATE articles SET view_count = view_count + 1 WHERE id=?", (article_id,))
        conn.commit()

    conn.close()

    if row:
        art = dict(row)
        art['tags_list'] = [t.strip() for t in art['tags'].split(',') if t.strip()] if art['tags'] else []

        # Get prev/next articles
        conn2 = _get_db()
        cat_filter = "AND a.category_id = ?" if art['category_id'] else ""
        cat_params = (art['category_id'],) if art['category_id'] else ()

        prev = conn2.execute(
            f"SELECT id, title, slug FROM articles a WHERE a.status='published' AND a.created_at < ? {cat_filter} ORDER BY a.created_at DESC LIMIT 1",
            (art['created_at'],) + cat_params
        ).fetchone()

        next_ = conn2.execute(
            f"SELECT id, title, slug FROM articles a WHERE a.status='published' AND a.created_at > ? {cat_filter} ORDER BY a.created_at ASC LIMIT 1",
            (art['created_at'],) + cat_params
        ).fetchone()

        conn2.close()
        art['prev'] = dict(prev) if prev else None
        art['next_article'] = dict(next_) if next_ else None

        return _clean(art)

    return None


def create_article(title, content='', category_id=None, tags='', summary='', status='draft', author=''):
    conn = _get_db()
    slug_base = _slugify(title)
    slug = slug_base
    counter = 1
    while conn.execute("SELECT id FROM articles WHERE slug=?", (slug,)).fetchone():
        slug = f"{slug_base}-{counter}"
        counter += 1

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute(
        """INSERT INTO articles (title, slug, content, summary, category_id, tags, status, author, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (title, slug, content, summary, category_id, tags, status, author, now, now)
    )
    conn.commit()
    art_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    art = get_article(art_id)
    conn.close()
    return {'success': True, 'article': art}


def update_article(article_id, title=None, content=None, category_id=None, tags=None, summary=None, status=None, author=None, is_pinned=None):
    conn = _get_db()
    existing = conn.execute("SELECT * FROM articles WHERE id=?", (article_id,)).fetchone()
    if not existing:
        conn.close()
        return {'success': False, 'error': '文章不存在'}

    updates = {'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    if title is not None:
        updates['title'] = title
    if content is not None:
        updates['content'] = content
    if category_id is not None:
        updates['category_id'] = category_id
    if tags is not None:
        updates['tags'] = tags
    if summary is not None:
        updates['summary'] = summary
    if status is not None:
        updates['status'] = status
    if author is not None:
        updates['author'] = author
    if is_pinned is not None:
        updates['is_pinned'] = is_pinned

    set_clause = ', '.join(f"{k}=?" for k in updates)
    values = list(updates.values()) + [article_id]
    conn.execute(f"UPDATE articles SET {set_clause} WHERE id=?", values)
    conn.commit()
    conn.close()

    return {'success': True, 'article': get_article(article_id)}


def delete_article(article_id):
    conn = _get_db()
    existing = conn.execute("SELECT * FROM articles WHERE id=?", (article_id,)).fetchone()
    if not existing:
        conn.close()
        return {'success': False, 'error': '文章不存在'}
    conn.execute("DELETE FROM articles WHERE id=?", (article_id,))
    conn.commit()
    conn.close()
    return {'success': True, 'deleted': dict(existing)}


def get_tags():
    conn = _get_db()
    rows = conn.execute("SELECT tags FROM articles WHERE status='published' AND tags != ''").fetchall()
    conn.close()
    tag_set = set()
    for r in rows:
        for t in r[0].split(','):
            t = t.strip()
            if t:
                tag_set.add(t)
    return sorted(tag_set)


def get_stats():
    conn = _get_db()
    total = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    published = conn.execute("SELECT COUNT(*) FROM articles WHERE status='published'").fetchone()[0]
    drafts = conn.execute("SELECT COUNT(*) FROM articles WHERE status='draft'").fetchone()[0]
    total_views = conn.execute("SELECT COALESCE(SUM(view_count),0) FROM articles").fetchone()[0]
    cat_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    recent = conn.execute("SELECT id, title, slug, status, updated_at FROM articles ORDER BY updated_at DESC LIMIT 5").fetchall()
    conn.close()
    return {
        'total_articles': total,
        'published': published,
        'drafts': drafts,
        'total_views': total_views,
        'total_categories': cat_count,
        'recent_articles': [dict(r) for r in recent]
    }


# Initialize DB on import
_init_db()