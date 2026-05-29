"""航空航天阀门研发每日资讯模块"""
import json
import os
import re
from datetime import datetime
from flask import jsonify

NEWS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
NEWS_INDEX_FILE = os.path.join(NEWS_DIR, 'news_index.json')


def _ensure_dir():
    if not os.path.exists(NEWS_DIR):
        os.makedirs(NEWS_DIR)


def _clean(obj):
    """Recursively clean Infinity/NaN -> None"""
    import math
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
    return obj


def _get_index():
    """Get or create news index"""
    _ensure_dir()
    if os.path.exists(NEWS_INDEX_FILE):
        with open(NEWS_INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'entries': [], 'last_updated': None}


def _save_index(index):
    """Save news index"""
    _ensure_dir()
    with open(NEWS_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def get_latest_news(limit=10):
    """Get latest news entries"""
    index = _get_index()
    entries = index.get('entries', [])[:limit]
    return entries


def get_news_by_date(date_str):
    """Get news for a specific date (YYYY-MM-DD)"""
    index = _get_index()
    for entry in index.get('entries', []):
        if entry.get('date') == date_str:
            return entry
    return None


def get_all_dates():
    """Get all available news dates"""
    index = _get_index()
    return [e.get('date') for e in index.get('entries', [])]


def add_news_entry(news_data):
    """
    Add a news entry from cron job result.
    news_data: dict with keys: date (YYYY-MM-DD), title, items (list), source
    """
    _ensure_dir()
    index = _get_index()
    date_str = news_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Remove existing entry for same date if any
    index['entries'] = [e for e in index['entries'] if e.get('date') != date_str]
    
    # Add new entry at the beginning
    index['entries'].insert(0, {
        'date': date_str,
        'title': news_data.get('title', date_str + ' 航空航天阀门研发资讯'),
        'items': news_data.get('items', []),
        'source': news_data.get('source', '自动采集'),
        'created_at': datetime.now().isoformat()
    })
    
    index['last_updated'] = datetime.now().isoformat()
    _save_index(index)
    
    # Also save individual day file
    day_file = os.path.join(NEWS_DIR, 'news_' + date_str.replace('-', '') + '.json')
    with open(day_file, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    return True


def parse_markdown_news(file_path):
    """
    Parse a markdown news file saved by cron job and import into the system.
    Returns the parsed news_data dict.
    """
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    items = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('---') or line.startswith('*'):
            continue
        # Parse: 1. **Title** (Source, Date) -- Summary
        m = re.match(r'(\d+)\.\s+\*\*(.+?)\*\*[\(（](.+?)[）\)][—\-]\s*(.+)', line)
        if m:
            items.append({
                'index': int(m.group(1)),
                'title': m.group(2).strip(),
                'source': m.group(3).strip(),
                'summary': m.group(4).strip()
            })
    
    if not items:
        # Fallback: try simpler patterns
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('*'):
                continue
            if '**' in line and '. ' in line[:8] and len(line) > 10:
                parts = line.split('**')
                title = ''
                for p in parts:
                    if p.strip() and not p[0].isdigit() and not p.startswith('. '):
                        title = p.strip()
                        break
                if title:
                    items.append({
                        'index': len(items) + 1,
                        'title': title,
                        'source': '',
                        'summary': ''
                    })
    
    # Extract date from filename or content
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', file_path)
    if date_match:
        date_str = date_match.group(1) + '-' + date_match.group(2) + '-' + date_match.group(3)
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    return {
        'date': date_str,
        'title': date_str + ' 航空航天阀门研发资讯',
        'items': items,
        'source': '每日定时采集'
    }


def import_latest_markdown():
    """Find and import the latest news markdown file"""
    workspace = os.path.dirname(os.path.dirname(__file__))
    # Look for aerospace-valve-news-YYYY-MM-DD.md files
    for fname in sorted(os.listdir(workspace)):
        if fname.startswith('aerospace-valve-news-') and fname.endswith('.md'):
            parsed = parse_markdown_news(os.path.join(workspace, fname))
            if parsed and parsed.get('items'):
                add_news_entry(parsed)
                return parsed
    return None


def get_news_stats():
    """Get news statistics"""
    index = _get_index()
    return {
        'total_entries': len(index.get('entries', [])),
        'last_updated': index.get('last_updated'),
        'dates': get_all_dates()[:30]
    }
