"""
Knowledge Graph Visualization Engine
=====================================
Backend data preparation layer that transforms the knowledge graph
into D3.js-compatible force-directed graph data.

Integrates with core/knowledge_graph.py for entity/relationship data.
"""

import sys
import os
import json
import math
from collections import Counter, defaultdict

# Attempt to import the knowledge graph
KG = None
try:
    _root = os.path.dirname(os.path.abspath(__file__))
    _core_path = os.path.join(os.path.dirname(_root), 'avis-platform', 'core')
    if os.path.isdir(_core_path) and _core_path not in sys.path:
        sys.path.insert(0, _core_path)
    from knowledge_graph import KnowledgeGraph
    KG = KnowledgeGraph
except ImportError:
    pass


# ============================================================
# Entity type -> color mapping (for D3 visualization)
# ============================================================

TYPE_COLORS = {
    "material": "#ff6b6b",
    "standard": "#51cf66",
    "design_parameter": "#ffd43b",
    "simulation_result": "#339af0",
    "valve_component": "#cc5de8",
    "failure_mode": "#f76707",
    "manufacturing_process": "#20c997",
    "test_method": "#e64980",
    "specification": "#748ffc",
    "property": "#38d9a9",
    "default": "#8899aa"
}


def entity_color(entity_type):
    """Get color for an entity type."""
    return TYPE_COLORS.get(entity_type, TYPE_COLORS["default"])


# ============================================================
# Graph Data Builders
# ============================================================

def build_force_graph(entities, relationships, entity_filter=None):
    """Build D3.js force-directed graph data from entities and relationships.

    Args:
        entities: list of entity dicts with id, name, type, properties
        relationships: list of relationship dicts with source, target, type, weight
        entity_filter: optional list of entity types to include

    Returns:
        dict with nodes and links arrays ready for D3 force simulation
    """
    # Filter entities
    if entity_filter:
        entities = [e for e in entities if e.get("type", "") in entity_filter]

    entity_ids = {e["id"] for e in entities}

    # Build node list
    nodes = []
    for e in entities:
        node_type = e.get("type", "default")
        # Node size based on degree (computed below) or property count
        prop_count = len(e.get("properties", {}))
        nodes.append({
            "id": e["id"],
            "label": e.get("name", e["id"])[:30],
            "group": node_type,
            "type": node_type,
            "size": max(5, min(20, 5 + prop_count * 2)),
            "color": entity_color(node_type),
            "properties": e.get("properties", {}),
            "description": e.get("description", "")[:200]
        })

    # Build link list (only if both endpoints exist in filtered entities)
    links = []
    for r in relationships:
        if r["source"] in entity_ids and r["target"] in entity_ids:
            links.append({
                "source": r["source"],
                "target": r["target"],
                "type": r.get("type", "related_to"),
                "weight": r.get("weight", 1),
                "label": r.get("type", "")[:30]
            })

    # Compute node degrees for sizing
    degree = defaultdict(int)
    for link in links:
        degree[link["source"]] += 1
        degree[link["target"]] += 1

    max_deg = max(degree.values()) if degree else 1
    for node in nodes:
        d = degree.get(node["id"], 0)
        node["degree"] = d
        node["size"] = max(5, min(30, 8 + (d / max(max_deg, 1)) * 20))

    return {
        "nodes": nodes,
        "links": links,
        "total_nodes": len(nodes),
        "total_links": len(links),
        "type_counts": dict(Counter(e.get("type", "default") for e in entities))
    }


def build_path_highlight(entities, relationships, path_entity_ids):
    """Build highlight data for a specific path in the graph.

    Returns graph data where nodes/links on the path are marked with 'highlight: true'.
    """
    base = build_force_graph(entities, relationships)
    path_set = set(path_entity_ids)

    for node in base["nodes"]:
        node["highlight"] = node["id"] in path_set
        if node["highlight"]:
            node["path_order"] = path_entity_ids.index(node["id"]) if node["id"] in path_entity_ids else -1

    for link in base["links"]:
        link["highlight"] = link["source"] in path_set and link["target"] in path_set

    base["path_length"] = len(path_entity_ids)
    base["path"] = path_entity_ids
    return base


def build_subgraph_tree(entities, relationships, root_id, max_depth=2):
    """Build a hierarchical tree rooted at root_id for tree visualization.

    BFS traversal up to max_depth, returns nested node structure.
    """
    entity_map = {e["id"]: e for e in entities}

    # Build adjacency list
    adj = defaultdict(list)
    for r in relationships:
        adj[r["source"]].append((r["target"], r.get("type", "related_to"), r.get("weight", 1)))
        adj[r["target"]].append((r["source"], r.get("type", "related_to"), r.get("weight", 1)))

    visited = set()
    root = entity_map.get(root_id, {"id": root_id, "name": root_id, "type": "unknown"})

    def _build(id_, depth):
        if id_ in visited or depth > max_depth:
            return None
        visited.add(id_)
        entity = entity_map.get(id_, {"id": id_, "name": id_, "type": "unknown"})

        children = []
        for neighbor, rel_type, weight in adj.get(id_, []):
            child = _build(neighbor, depth + 1)
            if child:
                child["_relationship"] = {"type": rel_type, "weight": weight}
                children.append(child)

        return {
            "id": entity["id"],
            "name": entity.get("name", entity["id"]),
            "type": entity.get("type", "default"),
            "color": entity_color(entity.get("type", "default")),
            "properties": entity.get("properties", {}),
            "children": children if children else None
        }

    tree = _build(root["id"], 0) or {
        "id": root["id"],
        "name": root.get("name", root["id"]),
        "type": root.get("type", "default"),
        "color": "#8899aa",
        "children": None
    }
    return tree


def compute_statistics(entities, relationships):
    """Compute graph statistics for the dashboard panel."""
    n_nodes = len(entities)
    n_links = len(relationships)

    # Degree distribution
    degree = defaultdict(int)
    for r in relationships:
        degree[r["source"]] += 1
        degree[r["target"]] += 1

    if degree:
        degrees = list(degree.values())
        avg_degree = sum(degrees) / max(len(degrees), 1)
        max_degree = max(degrees)
        min_degree = min(degrees)
    else:
        avg_degree = max_degree = min_degree = 0

    # Type distribution
    type_counts = Counter(e.get("type", "default") for e in entities)
    rel_type_counts = Counter(r.get("type", "related_to") for r in relationships)

    # Connectivity
    density = (2 * n_links) / max(n_nodes * (n_nodes - 1), 1) if n_nodes > 1 else 0

    # Top hubs
    hubs = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:10]
    node_map = {e["id"]: e.get("name", e["id"]) for e in entities}
    top_hubs = [{"id": h[0], "name": node_map.get(h[0], h[0]), "degree": h[1]} for h in hubs]

    return {
        "total_nodes": n_nodes,
        "total_links": n_links,
        "density": round(density, 4),
        "avg_degree": round(avg_degree, 2),
        "max_degree": max_degree,
        "min_degree": min_degree,
        "entity_types": {k: v for k, v in type_counts.most_common()},
        "relationship_types": {k: v for k, v in rel_type_counts.most_common()},
        "top_hubs": top_hubs
    }


# ============================================================
# Seed Data (for standalone use without knowledge_graph.py)
# ============================================================

SEED_ENTITIES = [
    {"id": "inconel_718", "name": "Inconel 718", "type": "material",
     "properties": {"density_gcc": 8.19, "yield_mpa": 1034, "max_temp_c": 700},
     "description": "Nickel-based superalloy, excellent high-temperature strength and oxidation resistance."},
    {"id": "ti6al4v", "name": "Ti-6Al-4V", "type": "material",
     "properties": {"density_gcc": 4.43, "yield_mpa": 880, "max_temp_c": 400},
     "description": "Titanium alloy, high strength-to-weight ratio, widely used in aerospace."},
    {"id": "316l_ss", "name": "316L Stainless Steel", "type": "material",
     "properties": {"density_gcc": 8.0, "yield_mpa": 290, "max_temp_c": 870},
     "description": "Austenitic stainless steel, excellent corrosion resistance."},
    {"id": "ptfe", "name": "PTFE (Teflon)", "type": "material",
     "properties": {"density_gcc": 2.2, "yield_mpa": 23, "max_temp_c": 260},
     "description": "Low friction polymer, excellent chemical resistance."},
    {"id": "qj20156", "name": "QJ 20156", "type": "standard",
     "properties": {"proof_factor": 1.5, "burst_factor": 2.0, "life_cycles": 20000},
     "description": "Chinese aerospace standard for solenoid valves."},
    {"id": "hb6455", "name": "HB 6455-2014", "type": "standard",
     "properties": {"category": "check_valve"},
     "description": "Chinese aviation standard for check valves."},
    {"id": "iso3601", "name": "ISO 3601-2", "type": "standard",
     "properties": {"category": "oring_groove"},
     "description": "International standard for O-ring groove dimensions."},
    {"id": "solenoid_valve", "name": "Solenoid Valve", "type": "valve_component",
     "properties": {"typical_pressure_mpa": 35, "typical_flow_lps": 5},
     "description": "Electromagnetically actuated valve for fluid control."},
    {"id": "check_valve", "name": "Check Valve", "type": "valve_component",
     "properties": {"cracking_pressure_mpa": 0.05, "typical_diameter_mm": 10},
     "description": "One-way flow valve preventing reverse flow."},
    {"id": "pressure_reducing_valve", "name": "Pressure Reducing Valve", "type": "valve_component",
     "properties": {"regulation_accuracy_percent": 5},
     "description": "Maintains constant downstream pressure regardless of upstream variations."},
    {"id": "oring_groove", "name": "O-Ring Groove", "type": "design_parameter",
     "properties": {"compression_ratio": 0.15, "fill_ratio": 0.75},
     "description": "Groove dimensions for O-ring sealing systems."},
    {"id": "spring_design", "name": "Valve Spring", "type": "design_parameter",
     "properties": {"spring_index": 8, "safety_factor": 1.2},
     "description": "Helical compression spring design for valve actuation."},
    {"id": "leak_rate", "name": "Leak Rate", "type": "property",
     "properties": {"unit": "Pa m3/s", "typical_range": "1e-7 to 1e-12"},
     "description": "Gas leakage rate through seal interfaces."},
    {"id": "proof_test", "name": "Proof Pressure Test", "type": "test_method",
     "properties": {"factor": 1.5, "duration_min": 5},
     "description": "Pressure test at 1.5x rated pressure to verify structural integrity."},
    {"id": "thermal_vacuum", "name": "Thermal Vacuum Cycling", "type": "test_method",
     "properties": {"cycles": 6, "temp_range": "-40C to +80C"},
     "description": "Thermal cycling under vacuum to simulate space environment."},
    {"id": "fatigue_failure", "name": "Fatigue Failure", "type": "failure_mode",
     "properties": {"primary_cause": "cyclic loading"},
     "description": "Progressive failure under cyclic stress below yield strength."},
    {"id": "corrosion", "name": "Corrosion", "type": "failure_mode",
     "properties": {"primary_cause": "chemical attack"},
     "description": "Material degradation due to chemical reaction with environment."},
    {"id": "additive_manufacturing", "name": "Additive Manufacturing", "type": "manufacturing_process",
     "properties": {"surface_roughness_um": 6.3, "min_wall_mm": 0.5},
     "description": "3D printing of metal components, enables complex geometries."},
    {"id": "precision_machining", "name": "Precision Machining", "type": "manufacturing_process",
     "properties": {"tolerance_mm": 0.01, "surface_roughness_um": 0.8},
     "description": "Traditional subtractive manufacturing with tight tolerances."},
    {"id": "cryogenic_valve_spec", "name": "Cryogenic Valve Spec", "type": "specification",
     "properties": {"temp_range": "-253C to -150C", "medium": "LH2/LOX"},
     "description": "Specification for valves operating at cryogenic temperatures."},
    {"id": "high_pressure_spec", "name": "High Pressure Spec", "type": "specification",
     "properties": {"pressure_range_mpa": "30 to 70", "medium": "Helium/Nitrogen"},
     "description": "Specification for high-pressure gas valve systems."},
]

SEED_RELATIONSHIPS = [
    {"source": "inconel_718", "target": "cryogenic_valve_spec", "type": "recommended_for", "weight": 1},
    {"source": "ti6al4v", "target": "high_pressure_spec", "type": "recommended_for", "weight": 1},
    {"source": "316l_ss", "target": "pressure_reducing_valve", "type": "used_in", "weight": 1},
    {"source": "ptfe", "target": "oring_groove", "type": "used_as", "weight": 1},
    {"source": "qj20156", "target": "solenoid_valve", "type": "governs", "weight": 1},
    {"source": "qj20156", "target": "proof_test", "type": "requires", "weight": 1},
    {"source": "qj20156", "target": "thermal_vacuum", "type": "requires", "weight": 1},
    {"source": "hb6455", "target": "check_valve", "type": "governs", "weight": 1},
    {"source": "iso3601", "target": "oring_groove", "type": "specifies", "weight": 1},
    {"source": "solenoid_valve", "target": "spring_design", "type": "has_component", "weight": 1},
    {"source": "check_valve", "target": "spring_design", "type": "has_component", "weight": 1},
    {"source": "pressure_reducing_valve", "target": "spring_design", "type": "has_component", "weight": 1},
    {"source": "oring_groove", "target": "leak_rate", "type": "affects", "weight": 1},
    {"source": "solenoid_valve", "target": "leak_rate", "type": "must_meet", "weight": 1},
    {"source": "check_valve", "target": "leak_rate", "type": "must_meet", "weight": 1},
    {"source": "proof_test", "target": "fatigue_failure", "type": "detects", "weight": 1},
    {"source": "thermal_vacuum", "target": "corrosion", "type": "can_accelerate", "weight": 0.5},
    {"source": "additive_manufacturing", "target": "inconel_718", "type": "processes", "weight": 1},
    {"source": "precision_machining", "target": "316l_ss", "type": "processes", "weight": 1},
    {"source": "precision_machining", "target": "ti6al4v", "type": "processes", "weight": 1},
    {"source": "inconel_718", "target": "cryogenic_valve_spec", "type": "meets", "weight": 1},
    {"source": "cryogenic_valve_spec", "target": "qj20156", "type": "references", "weight": 1},
    {"source": "high_pressure_spec", "target": "qj20156", "type": "references", "weight": 1},
    {"source": "fatigue_failure", "target": "spring_design", "type": "affects", "weight": 1},
    {"source": "corrosion", "target": "oring_groove", "type": "affects", "weight": 0.5},
    {"source": "additive_manufacturing", "target": "solenoid_valve", "type": "can_produce", "weight": 0.8},
    {"source": "precision_machining", "target": "pressure_reducing_valve", "type": "can_produce", "weight": 0.9},
    {"source": "inconel_718", "target": "proof_test", "type": "validated_by", "weight": 1},
    {"source": "316l_ss", "target": "corrosion", "type": "resistant_to", "weight": 1},
    {"source": "ptfe", "target": "cryogenic_valve_spec", "type": "suitable_for", "weight": 0.8},
    {"source": "ti6al4v", "target": "high_pressure_spec", "type": "meets", "weight": 1},
    {"source": "leak_rate", "target": "qj20156", "type": "regulated_by", "weight": 1},
]


def get_kg_instance():
    """Try to get the real knowledge graph instance, fall back to seed data."""
    if KG is not None:
        try:
            return KG(), False  # (instance, is_seed)
        except Exception:
            pass
    return None, True


def get_all_entities():
    """Get all entities from knowledge graph or seed data."""
    kg, is_seed = get_kg_instance()
    if kg and not is_seed:
        try:
            return kg.get_all_entities()
        except Exception:
            pass
    return SEED_ENTITIES


def get_all_relationships():
    """Get all relationships from knowledge graph or seed data."""
    kg, is_seed = get_kg_instance()
    if kg and not is_seed:
        try:
            return kg.get_all_relationships()
        except Exception:
            pass
    return SEED_RELATIONSHIPS
