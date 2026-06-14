import json, urllib.request, sys

def api(path, method='GET', body=None):
    url = 'http://127.0.0.1:5000' + path
    headers = {'Content-Type': 'application/json'}
    try:
        if body:
            data = json.dumps(body).encode()
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
        else:
            req = urllib.request.Request(url, headers=headers)
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}

def ok(v):
    return v if len(v) < 150 else v[:147] + '...'

checks = {
    'orchestrator_stats': api('/api/agent/orchestrator/stats'),
    'vector_stats': api('/api/search/stats'),
    'graph_stats': api('/api/graph/stats'),
}

for k, v in checks.items():
    if 'error' in v:
        print('{}: ERROR - {}'.format(k, v['error']))
    elif v.get('success'):
        print('{}: OK - {}'.format(k, ok(json.dumps(v, ensure_ascii=False))))
    else:
        print('{}: OK - {}'.format(k, ok(json.dumps(v, ensure_ascii=False))))
