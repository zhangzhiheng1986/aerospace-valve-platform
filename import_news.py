import sys, os
sys.path.insert(0, 'backend')
import importlib, news_feed
importlib.reload(news_feed)

workspace = r'C:\Users\Administrator\.qclaw\workspace'

for fn in sorted(os.listdir(workspace)):
    if fn.startswith('aerospace-valve-news-') and fn.endswith('.md'):
        fp = os.path.join(workspace, fn)
        r = news_feed.parse_markdown_news(fp)
        if r:
            print(fn, ':', r['date'], 'items:', len(r['items']))
            for it in r['items'][:2]:
                print('  [{}] {}'.format(it['index'], it['title'][:50]))
                print('      src:', it['source'][:30], '| sum:', it['summary'][:30])
            news_feed.add_news_entry(r)
            print('  -> saved')
        else:
            print(fn, ': NO RESULT')

print()
print('All dates:', news_feed.get_all_dates())
print('Stats:', news_feed.get_news_stats())