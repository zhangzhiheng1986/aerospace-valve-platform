"""
News Blueprint: aerospace industry news feed (markdown-backed).
"""

from flask import Blueprint, request, render_template, jsonify
from app.utils.clean import prepare_json

news_bp = Blueprint('news', __name__)


@news_bp.route('/news')
def news_page():
    return render_template('news.html')


@news_bp.route('/api/news/latest')
def latest():
    from news_feed import get_latest_news
    limit = request.args.get('limit', 10, type=int)
    return jsonify(prepare_json(get_latest_news(limit=limit)))


@news_bp.route('/api/news/stats')
def stats():
    from news_feed import get_news_stats
    return jsonify(prepare_json(get_news_stats()))


@news_bp.route('/api/news/dates')
def dates():
    from news_feed import get_all_dates
    return jsonify(prepare_json(get_all_dates()))


@news_bp.route('/api/news/date/<date_str>')
def by_date(date_str):
    from news_feed import get_news_by_date
    return jsonify(prepare_json(get_news_by_date(date_str)))


@news_bp.route('/api/news/entry', methods=['POST'])
def add_entry():
    from news_feed import add_news_entry
    data = request.get_json() or {}
    result = add_news_entry(data)
    return jsonify(prepare_json(result))