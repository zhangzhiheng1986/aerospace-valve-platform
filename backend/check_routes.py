import sys
sys.path.insert(0, r'C:\Users\Administrator\.qclaw\workspace\aerospace-valve-platform\backend')
from app import create_app
app = create_app()
rules = list(app.url_map.iter_rules())
api_rules = [r for r in rules if '/api/' in r.rule]
print(f"Total routes: {len(rules)}, API routes: {len(api_rules)}")
for r in sorted(api_rules, key=lambda x: x.rule):
    methods = ','.join(sorted(r.methods - {'OPTIONS', 'HEAD'}))
    print(f"  {methods:6s} {r.rule}")
