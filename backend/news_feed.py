# -*- coding: utf-8 -*-

import json, os, re, math
from datetime import datetime
from flask import jsonify

NEWS_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
NEWS_INDEX_FILE = os.path.join(NEWS_DIR, "news_index.json")

# Pattern 1: N. **[Title](URL)**（Source, Date）—Summary
_PAT_WITH_URL = re.compile(r'(\d+)\.\s+\*\*\[(.+?)\]\((.+?)\)\*\*\s*[（(](.+?)[）)]\s*[—–-]\s*(.+)')
# Pattern 2: N. **Title**（Source, Date）—Summary (legacy, no URL)
_PAT_NO_URL = re.compile(r'(\d+)\.\s+\*\*(.+?)\*\*\s*[（(](.+?)[）)]\s*[—–-]\s*(.+)')

NL = chr(10)

def _ensure_dir():
    if not os.path.exists(NEWS_DIR):
        os.makedirs(NEWS_DIR)


def _get_index():
    _ensure_dir()
    if os.path.exists(NEWS_INDEX_FILE):
        with open(NEWS_INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"entries": [], "last_updated": None}


def _save_index(idx):
    _ensure_dir()
    with open(NEWS_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)


def get_latest_news(limit=10):
    return _get_index().get("entries", [])[:limit]


def get_news_by_date(date_str):
    for e in _get_index().get("entries", []):
        if e.get("date") == date_str:
            return e
    return None


def get_all_dates():
    return [e.get("date") for e in _get_index().get("entries", [])]


def add_news_entry(nd):
    _ensure_dir()
    idx = _get_index()
    ds = nd.get("date", datetime.now().strftime("%Y-%m-%d"))
    idx["entries"] = [e for e in idx["entries"] if e.get("date") != ds]
    idx["entries"].insert(0, {
        "date": ds,
        "title": nd.get("title", ds),
        "items": nd.get("items", []),
        "source": nd.get("source", "auto"),
        "created_at": datetime.now().isoformat()
    })
    idx["last_updated"] = datetime.now().isoformat()
    _save_index(idx)
    return True


def parse_markdown_news(filepath):
    """Parse news markdown file into news_data dict.
    
    Supported formats:
      N. **[Title](URL)**（Source, Date）—Summary
      N. **Title**（Source, Date）—Summary (legacy, no URL)
    """
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    items = []
    for line in text.split(NL):
        line = line.strip()
        if not line or line[0] in "#*-=":
            continue
        # Try URL pattern first
        m = _PAT_WITH_URL.match(line)
        if m:
            src = m.group(4).strip()
            if src.endswith(",") or src.endswith(";"):
                src = src[:-1]
            items.append({
                "index": int(m.group(1)),
                "title": m.group(2).strip(),
                "url": m.group(3).strip(),
                "source": src,
                "summary": m.group(5).strip()
            })
            continue
        # Fall back to no-URL pattern
        m = _PAT_NO_URL.match(line)
        if m:
            src = m.group(3).strip()
            if src.endswith(",") or src.endswith(";"):
                src = src[:-1]
            items.append({
                "index": int(m.group(1)),
                "title": m.group(2).strip(),
                "url": "",
                "source": src,
                "summary": m.group(4).strip()
            })
    if not items:
        for line in text.split(NL):
            line = line.strip()
            if "**" in line and len(line) > 10:
                parts = line.split("**")
                if len(parts) >= 3:
                    items.append({
                        "index": len(items) + 1,
                        "title": parts[1].strip(),
                        "url": "",
                        "source": "",
                        "summary": ""
                    })
    dm = re.search(r"(\d{4})-(\d{2})-(\d{2})", filepath)
    ds = dm.group(1) + "-" + dm.group(2) + "-" + dm.group(3) if dm else datetime.now().strftime("%Y-%m-%d")
    return {"date": ds, "title": ds, "items": items, "source": "auto"}


def import_latest_markdown():
    ws = os.path.dirname(os.path.dirname(__file__))
    imported = None
    for fn in sorted(os.listdir(ws)):
        if fn.startswith("aerospace-valve-news-") and fn.endswith(".md"):
            p = parse_markdown_news(os.path.join(ws, fn))
            if p and p.get("items"):
                add_news_entry(p)
                imported = p
    return imported


def get_news_stats():
    idx = _get_index()
    return {
        "total_entries": len(idx.get("entries", [])),
        "last_updated": idx.get("last_updated"),
        "dates": get_all_dates()[:30]
    }