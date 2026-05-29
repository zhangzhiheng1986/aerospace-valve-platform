"""Import existing news markdown files into the news system"""
import sys
sys.path.insert(0, 'backend')
from news_feed import parse_markdown_news, add_news_entry, get_latest_news, get_all_dates
import os

workspace = os.path.dirname(__file__)

for fname in sorted(os.listdir(workspace)):
    if fname.startswith('aerospace-valve-news-') and fname.endswith('.md'):
        filepath = os.path.join(workspace, fname)
        print(f'Parsing: {fname}')
        parsed = parse_markdown_news(filepath)
        if parsed and parsed.get('items'):
            add_news_entry(parsed)
            print(f'  -> Imported {len(parsed["items"])} items for {parsed["date"]}')
        else:
            print(f'  -> No items found')

print(f'\nAll dates: {get_all_dates()}')
print(f'Latest: {get_latest_news(1)}')