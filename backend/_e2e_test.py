# E2E test suite — Sprint 9: bug fix validation + full platform health
import json, urllib.request, sys

BASE = 'http://127.0.0.1:5000'
passed = 0; failed = 0
token = None

def api(path, method='GET', body=None, auth=False):
    url = BASE + path
    data = None
    if body is not None:
        data = json.dumps(body).encode()
    hdrs = {'Content-Type': 'application/json'} if data else {}
    if auth and token:
        hdrs['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        r = urllib.request.urlopen(req, timeout=15)
        code = r.getcode()
        raw = r.read()
        try: resp = json.loads(raw)
        except: resp = {'_html': True, '_len': len(raw)}
        return code, resp
    except urllib.error.HTTPError as e:
        return e.code, {'error': str(e)}
    except Exception as e:
        return 0, {'error': str(e)}

def chk(name, cond, detail=''):
    global passed, failed
    if cond: passed += 1; print('  PASS  {}'.format(name))
    else: failed += 1; print('  FAIL  {}  {}'.format(name, detail))

print('=' * 60)
print('E2E TEST SUITE')
print('=' * 60)

# 1. Platform health
print('\n--- 1. Platform health ---')
for label, path in [('Root page', '/'), ('Login page', '/login'), ('AI Agent', '/ai-agent')]:
    c, r = api(path)
    chk(label, c == 200, 'code={}'.format(c))

# 2. Auth
print('\n--- 2. Auth ---')
c, r = api('/api/auth/login', 'POST', {'username': 'admin', 'password': 'admin123'})
tok = r.get('data', {}).get('token', '') or r.get('token', '')
chk('Login', bool(tok) or r.get('success'), 'resp={}'.format(str(r)[:80]))
token = tok

# 3. Core modules
print('\n--- 3. Core modules ---')
for path in ['/api/materials/list', '/api/fluid_mechanics/formulas',
             '/api/qj20156/info', '/api/knowledge/chapters', '/api/cms/articles']:
    c, r = api(path)
    chk('GET {}'.format(path), c == 200, 'code={}'.format(c))

# 4. Fluid mechanics
print('\n--- 4. Fluid mechanics ---')
c, r = api('/api/fluid_mechanics/search-index')
cnt = len(r) if isinstance(r, list) else len(r.get('results', []))
chk('Search index >100', c == 200 and cnt > 100, 'code={} cnt={}'.format(c, cnt))

c, r = api('/api/fluid_mechanics/compute', 'POST',
          {'formula_id': 'reynolds', 'inputs': {'rho': 1000, 'v': 10, 'L': 0.01, 'mu': 0.001}})
chk('Reynolds compute', c == 200 and r.get('error') is None, 'code={}'.format(c))
if r.get('error') is None:
    v = r.get('results', {}).get('Re', 0) or r.get('result', r.get('value', 0))
    chk('Re ~ 100000', abs(float(v) - 100000) < 1000, 'got={}'.format(v))

# 5. Design tools
print('\n--- 5. Orchestrator ---')
for msg in ['Design a spring wire_diameter=3 mean_diameter=20 n_coils=8 material=50CrVA',
            'Design an O-ring shaft_diameter=100 pressure=30']:
    c, r = api('/api/agent/orchestrate', 'POST', {'message': msg}, auth=True)
    chk('Orch: {}'.format(msg[:30]), c in (200, 401), 'code={}'.format(c))

# 6. AI Agent tools
print('\n--- 6. AI Agent ---')
c, r = api('/api/agent/tools', auth=True)
chk('Tools list', c == 200, 'code={}'.format(c))

c, r = api('/api/agent/execute', 'POST',
          {'tool': 'query_material', 'params': {'material': 'TC4'}}, auth=True)
chk('Material query', c == 200 and r.get('success'), 'code={}'.format(c))

c, r = api('/api/agent/execute', 'POST',
          {'tool': 'run_fluid_calculation',
           'params': {'formula_id': 'reynolds_number', 'inputs': {'rho': 1000, 'v': 10, 'L': 0.01, 'mu': 0.001}}}, auth=True)
chk('Fluid calc via tool', c == 200 and r.get('success'), 'code={}'.format(c))

# 7. Vector search
print('\n--- 7. Vector search ---')
c, r = api('/api/search/stats')
chk('Vector stats', c == 200 and r.get('success'), 'code={}'.format(c))
c, r = api('/api/search/semantic', 'POST', {'query': 'Reynolds number'})
chk('Semantic search', c == 200 and r.get('success'),
    'code={} hits={}'.format(c, len(r.get('results', []))))

# 8. Knowledge graph
print('\n--- 8. Knowledge graph ---')
c, r = api('/api/graph/stats')
chk('Graph stats', c == 200 and r.get('success'), 'code={}'.format(c))
c, r = api('/api/graph/search?query=TC4')
chk('Graph search', c == 200 and r.get('success'),
    'code={} hits={}'.format(c, len(r.get('results', []))))
c, r = api('/api/graph/entity/formula:reynolds')
chk('Graph entity', c == 200 and r.get('success'), 'code={}'.format(c))
c, r = api('/api/graph/neighbors/formula_reynolds_number')
chk('Graph neighbors', c == 200 and r.get('success'),
    'code={} n={}'.format(c, len(r.get('neighbors', []))))

# --- 9. Search knowledge integration ---
print('--- 9. Search knowledge integration ---')

# Test via PAOR chat that uses search_knowledge
c, r = api('/api/agent/chat', 'POST', {'message': 'what is reynolds number'}, auth=True)
chk('PAOR chat with knowledge', c == 200 and r.get('success'),
    'code={}'.format(c))
if r.get('success'):
    text = r.get('response', {}).get('text', '')
    chk('Knowledge results in response',
        'Knowledge' in text and len(text) > 100,
        'text_len={} has_knowledge={}'.format(len(text), 'Knowledge' in text))
else:
    print('  FAIL  PAOR chat with knowledge  error={}'.format(r.get('error', '??')[:100]))

total = passed + failed
print('\n' + '=' * 60)
print('RESULTS: {}/{} passed ({:.1f}%)'.format(passed, total, 100*passed/total if total else 0))
print('=' * 60)
sys.exit(0 if failed == 0 else 1)
