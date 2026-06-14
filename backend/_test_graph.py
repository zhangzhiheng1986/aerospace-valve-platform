import json, urllib.request, urllib.parse, urllib.error, sys
BASE = 'http://127.0.0.1:5000'

def api_get(path, expect_error=False):
    try:
        return json.loads(urllib.request.urlopen(BASE + path).read())
    except urllib.error.HTTPError as e:
        if expect_error:
            return {'_http_error': e.code}
        raise

def api_post(path, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=body,
        headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req).read())

passed = 0
failed = 0

def check(name, cond, msg=""):
    global passed, failed
    if cond:
        passed += 1
        print("  PASS " + name)
    else:
        failed += 1
        print("  FAIL " + name + (": " + msg if msg else ""))

# === Stats & Entity ===
r = api_get('/api/graph/stats')
check("GET /stats: 255 entities", r['success'] and r['total_entities'] == 255)
check("GET /stats: 900+ edges", r['total_edges'] >= 900)

r = api_get('/api/graph/entity/formula:reynolds')
check("GET /entity/formula:reynolds", r['success'] and r['entity']['type'] == 'formula')

r = api_get('/api/graph/entity/material:mat_TC4')
check("GET /entity/material:mat_TC4", r['success'] and r['entity']['type'] == 'material')

r = api_get('/api/graph/entity/nonexistent', expect_error=True)
check("GET /entity/nonexistent => 404", r.get('_http_error') == 404)

# === Search ===
r = api_get('/api/graph/search?q=reynolds&type=formula&limit=5')
check("GET /search reynolds (>=3)", r['success'] and r['total'] >= 3)

r = api_get('/api/graph/search?q=TC4&type=material')
check("GET /search TC4 (>=1)", r['success'] and r['total'] >= 1)

r = api_get('/api/graph/search?q=thermal&type=design_module')
check("GET /search thermal (>=1)", r['success'] and r['total'] >= 1)

# === Neighbors ===
r = api_get('/api/graph/neighbors/module:cfd_analyzer?dir=out')
check("GET /neighbors CFD out (>=8)", r['success'] and r['total'] >= 8)

r = api_get('/api/graph/neighbors/material:mat_TC4?relation=USES_MATERIAL&dir=in')
check("GET /neighbors TC4 USES_MATERIAL in (>=5)", r['success'] and r['total'] >= 5)

r = api_get('/api/graph/neighbors/formula:reynolds?relation=INPUT_OF&dir=in')
check("GET /neighbors reynolds INPUT_OF in (>=10)", r['success'] and r['total'] >= 10)

# === Path ===
r = api_get('/api/graph/path?from=module:cfd_analyzer&to=formula:reynolds')
check("GET /path CFD->Reynolds (length=1)", r['success'] and r['length'] == 1)

r = api_get('/api/graph/path?from=formula:gas_density_ideal&to=formula:reynolds')
check("GET /path gas_density->reynolds (length=1)", r['success'] and r['length'] == 1)

r = api_get('/api/graph/path?from=', expect_error=True)
check("GET /path missing params => 400", r.get('_http_error') == 400)

r = api_get('/api/graph/path?from=formula:density&to=material:mat_T2&max_depth=3')
check("GET /path unreachable => length=0", r['success'] and r['length'] == 0)

# === Subgraph ===
r = api_post('/api/graph/subgraph', {'entity_ids': ['material:mat_TC4'], 'depth': 1})
check("POST /subgraph TC4 depth=1 (>=9 entities)", r['success'] and len(r['entities']) >= 9)
check("POST /subgraph TC4 depth=1 (>=8 edges)", len(r['edges']) >= 8)

r = api_post('/api/graph/subgraph', {'entity_ids': ['formula:reynolds', 'formula:mach'], 'depth': 2})
check("POST /subgraph Reynolds+Mach depth=2", r['success'] and len(r['entities']) >= 2)

try:
    r = api_post('/api/graph/subgraph', {})
    check("POST /subgraph no ids => 400", False, "Expected HTTP 400")
except urllib.error.HTTPError as e:
    check("POST /subgraph no ids => 400", e.code == 400)

# === Centrality ===
r = api_get('/api/graph/centrality?top_k=5')
check("GET /centrality top_k=5 (top>50 degree)", r['success'] and len(r['results']) == 5 and r['results'][0]['degree'] > 50)

r = api_get('/api/graph/centrality?top_k=20')
check("GET /centrality top_k=20", r['success'] and len(r['results']) == 20)

print("")
print("=== Knowledge Graph API: " + str(passed) + "/" + str(passed + failed) + " PASSED ===")
if failed > 0:
    sys.exit(1)
