# Sprint 7: Knowledge Graph — Completion Report

**Date**: 2026-06-13 04:58 GMT+8
**Commit**: 8532022
**Status**: ✅ COMPLETE (21/21 API tests, pushed to Render)

## What Was Built

A full knowledge graph engine using NetworkX plus a REST API Blueprint:

### Core Engine (`backend/knowledge_graph.py`, ~450 lines)
- **Entity types**: formula (204), material (21), knowledge_chapter (15), design_module (15)
- **Edge types**: INPUT_OF (866), REFERENCES (22), USES_MATERIAL (28)
- **Total**: 255 entities, 916 edges
- **I/O linking**: Formula output→input chains built from `fluid_mechanics_calc.get_all_formulas()` data
- **Module linking**: Design modules → formulas (via correct formula IDs from engine), modules → knowledge chapters, modules → materials (keyword-based)

### REST API Blueprint (`backend/app/blueprints/graph.py`, 7 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/graph/stats` | GET | Graph statistics |
| `/api/graph/entity/<id>` | GET | Single entity lookup |
| `/api/graph/search?q=&type=&limit=` | GET | Entity search |
| `/api/graph/neighbors/<id>?relation=&dir=&limit=` | GET | Neighbor traversal |
| `/api/graph/path?from=&to=&max_depth=` | GET | Shortest path (BFS) |
| `/api/graph/subgraph` | POST | Subgraph extraction |
| `/api/graph/centrality?top_k=` | GET | Degree centrality ranking |

### Test Results: 21/21 PASSED
- Entity lookup: formulas, materials, 404 for nonexistent
- Search: by type (formula/material/design_module), multi-result
- Neighbors: CFD module (≥8 neighbors), TC4 material (≥5, USES_MATERIAL), Reynolds (≥10, INPUT_OF)
- Path: CFD→Reynolds (1 hop), gas_density_ideal→reynolds (1 hop), missing params→400, unreachable→length=0
- Subgraph: TC4 extraction (≥9 entities + ≥8 edges), multi-node extraction, validation errors
- Centrality: top-5 (top>50 degree), top-20

## Key Fixes During Build
1. **Blueprint url_prefix**: Initial registration missing `/api/graph` prefix → added in `app/__init__.py`
2. **Material ID garbling**: Chinese names with `.lower().replace()` produced garbage → switched to index+ASCII slug pattern (`mat_TC4`, `mat_DT4C`, etc.)
3. **Formula ID mismatch**: Original MODULE_FORMULA_LINKS used guessed IDs → replaced with actual IDs from `fluid_mechanics_calc.get_all_formulas()`
4. **I/O naming gap**: Formula engine uses both symbol names (rho, Re) and label names (density) as outputs — I/O chains only match identical strings, so some chains are disconnected. This is a data consistency issue in the formula engine, not a graph bug.

## Architecture Notes
- **Graph**: In-memory NetworkX graph, lazy-built, singleton via `get_knowledge_graph()`
- **Query**: `GraphQuery` class wraps NetworkX for all traversals
- **BFS path finding**: Not Dijkstra (no edge weights yet), = shortest hop count
- **Centrality**: Simple degree centrality (= number of incident edges)

## Next Steps
- Sprint 8: Chat UI upgrade (integrate graph/vector search into AI Agent)
- Explore: Graph visualization (D3.js force layout), Weighted traversal (formula importance), Real-time graph updates
