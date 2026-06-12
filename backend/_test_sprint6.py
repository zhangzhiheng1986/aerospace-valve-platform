"""Comprehensive E2E test for Sprint 6: Vector Store + Semantic Search + Integration.

Tests:
  1. Vector store indexing (knowledge, formulas, materials)
  2. Semantic search API (POST + GET)
  3. PAOR engine vector search fallback
  4. tool_bridge semantic_search tool
  5. Orchestrator with semantic search capability
  6. AI agent /agent/chat integration
"""
import json
import urllib.request
import urllib.error
import urllib.parse
import time

BASE = "http://127.0.0.1:5000"
PASS, FAIL = 0, 0

def post(path, data):
    url = BASE + path
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def get(path):
    url = BASE + path
    # URL-encode if needed
    if any(ord(c) > 127 for c in path):
        parsed = urllib.parse.urlparse(url)
        encoded_query = urllib.parse.quote(parsed.query, safe='=&')
        url = urllib.parse.urlunparse(parsed._replace(query=encoded_query))
    resp = urllib.request.urlopen(url)
    return json.loads(resp.read())

def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} -- {detail}")

print("=" * 60)
print("Sprint 6: Vector Store + Semantic Search Integration Test")
print("=" * 60)

# ── 1. Vector Store Indexing ──────────────────────────────
print("\n[1] Vector Store Indexing")
stats = get("/api/search/stats")
check("API responds", stats.get("success"))
for name in ["knowledge", "formulas", "materials"]:
    s = stats.get("stats", {}).get(name, {})
    check(f"{name} built", s.get("built"), f"got {s}")
    check(f"{name} has documents", s.get("documents", 0) > 0, f"count={s.get('documents')}")

# ── 2. Semantic Search API (POST) ─────────────────────────
print("\n[2] Semantic Search API (POST)")
r = post("/api/search/semantic", {"query": "雷诺数计算水流管道", "top_k": 3})
check("POST returns success", r.get("success"))
check("Total > 0", r.get("total", 0) > 0, f"total={r.get('total')}")
top = r.get("results", [{}])[0]
check("Top result has _score", top.get("_score", 0) > 0, f"score={top.get('_score')}")
check("Top result has _source", top.get("_source", "") != "", f"source={top.get('_source')}")

# ── 3. Semantic Search API (GET) ──────────────────────────
print("\n[3] Semantic Search API (GET)")
r2 = get("/api/search/semantic?q=钛合金材料疲劳强度&top_k=3&source=materials")
check("GET returns success", r2.get("success"))
check("Source is materials", r2.get("source") == "materials")
check("At least 1 result", r2.get("total", 0) >= 1, f"total={r2.get('total')}")

# ── 4. Knowledge search ──────────────────────────────────
print("\n[4] Knowledge Base Semantic Search")
r3 = post("/api/search/semantic", {"query": "密封圈泄漏率计算标准", "source": "knowledge", "top_k": 3})
check("Knowledge search success", r3.get("success"))
check("Knowledge has results", r3.get("total", 0) > 0, f"total={r3.get('total')}")
top_kb = r3.get("results", [{}])[0]
check("Knowledge result type", top_kb.get("type", "").startswith("knowledge"), f"type={top_kb.get('type')}")

# ── 5. Formula semantic search ────────────────────────────
print("\n[5] Formula Semantic Search")
r4 = post("/api/search/semantic", {"query": "drag force coefficient aerodynamics", "source": "formulas", "top_k": 3})
check("Formula search success", r4.get("success"))
top_f = r4.get("results", [{}])[0]
check("Formula result", top_f.get("formula_id", "") != "", f"id={top_f.get('formula_id')}")

# ── 6. Cross-source unified search ────────────────────────
print("\n[6] Unified Cross-Source Search")
r5 = post("/api/search/semantic", {"query": "弹簧线圈设计 spring coil", "top_k": 5})
sources = set()
for res in r5.get("results", []):
    sources.add(res.get("_source"))
check("Multiple sources", len(sources) >= 2, f"sources={sources}")
check("Results ranked by score", all(
    r5["results"][i].get("_score", 0) >= r5["results"][i+1].get("_score", 0)
    for i in range(len(r5["results"])-1)
))

# ── 7. Vector Store Rebuild ──────────────────────────────
print("\n[7] Vector Store Rebuild")
r6 = post("/api/search/rebuild", {})
check("Rebuild success", r6.get("success"))
check("Stats returned", r6.get("stats") is not None)

# ── 8. PAOR Engine with vector search fallback ────────────
print("\n[8] PAOR Engine Vector Search Fallback")
try:
    import sys
    sys.path.insert(0, '.')
    from paor_engine import PAORPlanner
    # Test a query that won't match keyword rules
    fid, inputs = PAORPlanner._identify_formula("计算管道中的摩擦阻力系数")
    check("PAOR fallback found formula", fid is not None, f"fid={fid}")
    check("PAOR formula_id is valid string", bool(fid) and isinstance(fid, str), f"fid={fid}")
except Exception as e:
    check("PAOR import", False, str(e))

# ── 9. tool_bridge semantic_search ────────────────────────
print("\n[9] tool_bridge semantic_search Tool")
try:
    from tool_bridge import TOOL_BRIDGE, _semantic_search
    check("semantic_search in TOOL_BRIDGE", "semantic_search" in TOOL_BRIDGE)
    result = _semantic_search({"query": "电磁阀材料选择磁导率"})
    check("tool_bridge search success", result.get("success"))
    check("tool_bridge has results", result.get("total", 0) > 0, f"total={result.get('total')}")
except Exception as e:
    check("tool_bridge import", False, str(e))

# ── 10. Agent Chat with semantic search ───────────────────
print("\n[10] AI Agent Chat Integration")
# Login first
try:
    login_resp = post("/api/auth/login", {"username": "admin", "password": "admin123"})
    token = login_resp.get("data", {}).get("token") or login_resp.get("token", "")
    check("Login for chat test", bool(token), "Got token" if token else "NO TOKEN")
    if token:
        chat_url = "/api/agent/chat"
        body = json.dumps({
            "session_id": None,
            "message": "计算水在管道中流动的雷诺数，管径25mm，流速2m/s"
        }).encode('utf-8')
        req = urllib.request.Request(BASE + chat_url, data=body,
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})
        chat_resp = json.loads(urllib.request.urlopen(req).read())
        check("Chat success", chat_resp.get("success") or chat_resp.get("status") in ["ok", "success"], f"success={chat_resp.get('success')}")
        check("Chat has response", len(chat_resp.get("response", "")) > 0)
        check("Chat includes Re value or formula",
              any(kw in str(chat_resp).lower() for kw in ["reynolds", "re", "雷诺"]),
              "No Reynolds keyword in response")
except Exception as e:
    check("Chat endpoint", False, str(e)[:100])

# ── 11. Orchestrator multi-agent with semantic ────────────
print("\n[11] Orchestrator Multi-Agent + Semantic Search")
try:
    orch_body = json.dumps({
        "message": "设计一个钛合金弹簧用于高温高压阀门"
    }).encode('utf-8')
    orch_req = urllib.request.Request(BASE + "/api/agent/orchestrate", data=orch_body,
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})
    orch_resp = json.loads(urllib.request.urlopen(orch_req).read())
    check("Orchestrate success", orch_resp.get("success") or orch_resp.get("status") == "ok", f"success={orch_resp.get('success')}")
    check("Orchestrate has synthesis", len(orch_resp.get("synthesis", "")) > 0)
    check("Multi-agent orchestrated", orch_resp.get("orchestrated", False) or
          orch_resp.get("intent", "") in ["design_spring_system"],
          f"orchestrated={orch_resp.get('orchestrated')} intent={orch_resp.get('intent')}")
except Exception as e:
    check("Orchestrate endpoint", False, str(e)[:100])

# ── Summary ───────────────────────────────────────────────
print("\n" + "=" * 60)
total = PASS + FAIL
rate = PASS / total * 100 if total > 0 else 0
print(f"Results: {PASS} passed, {FAIL} failed ({total} total, {rate:.1f}%)")
print("=" * 60)

if FAIL > 0:
    exit(1)
