"""
Knowledge Graph Engine — Cross-reference graph for valve R&D platform

Sprint 7 | 2026-06-13

Architecture:
  - Builds a NetworkX DiGraph from existing platform data
  - Entities: Formulas, Materials, Knowledge Chapters, Design Modules, Standards
  - Edges: REFERENCES, USES_MATERIAL, APPEARS_IN, RELATES_TO, CITES_STANDARD
  - Query: neighbors, paths, subgraph, centrality

Design principles:
  - Phase 1: Python dict + JSON files (no Neo4j — data < 10MB)
  - Phase 2: NetworkX in-memory graph (current)  
  - Phase 3: Neo4j (when entities > 1000 or graph depth > 3)
"""

import json
import re
import math
import os
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
from dataclasses import dataclass, field

# Optional: NetworkX for graph algorithms
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None


# ============================================================
# Data types
# ============================================================

@dataclass
class Entity:
    """A node in the knowledge graph."""
    id: str
    type: str  # formula, material, knowledge_chapter, design_module, standard, parameter
    label: str  # human-readable name
    properties: Dict = field(default_factory=dict)

@dataclass  
class Edge:
    """A directed edge between two entities."""
    source: str
    target: str
    relation: str  # REFERENCES, USES_MATERIAL, APPEARS_IN, RELATES_TO, CITES_STANDARD, INPUT_OF, OUTPUT_OF
    weight: float = 1.0
    properties: Dict = field(default_factory=dict)


# ============================================================
# Graph Builder — Extracts entities and edges from platform data
# ============================================================

class KnowledgeGraphBuilder:
    """Builds a knowledge graph from the platform's existing data modules."""
    
    # Keywords that indicate material usage in formula names/descriptions
    MATERIAL_KEYWORDS = {
        'tc4': 'TC4 (Ti-6Al-4V)', 'ti-6al-4v': 'TC4 (Ti-6Al-4V)',
        'ti6al4v': 'TC4 (Ti-6Al-4V)', '钛合金': 'Titanium Alloy',
        'inconel': 'Inconel 718', 'inconel718': 'Inconel 718', 'inconel 718': 'Inconel 718',
        '304': '304 Stainless Steel', '304ss': '304 Stainless Steel', 
        '316': '316 Stainless Steel', '316l': '316L Stainless Steel',
        '50crva': '50CrVA', 'swp-a': 'SWP-A',
        'steel': 'Steel', '钢': 'Steel', '不锈钢': 'Stainless Steel',
        'aluminum': 'Aluminum', '铝合金': 'Aluminum Alloy', '铝': 'Aluminum',
        'copper': 'Copper', '铜': 'Copper',
        'elgiloy': 'Elgiloy', 'nitinol': 'Nitinol',
        'ptfe': 'PTFE', 'teflon': 'PTFE', '聚四氟乙烯': 'PTFE',
        'epdm': 'EPDM', 'nbr': 'NBR', 'fkm': 'FKM', 'viton': 'FKM',
        'silicone': 'Silicone', '硅橡胶': 'Silicone',
        '陶瓷': 'Ceramic', 'ceramic': 'Ceramic',
        'carbon': 'Carbon Fiber', '碳纤维': 'Carbon Fiber',
        'dt4c': 'DT4C', 'dt4': 'DT4C', '电工纯铁': 'DT4C',
    }
    
    # Keywords that indicate standard references
    STANDARD_KEYWORDS = {
        'qj 20156': 'QJ 20156', 'qj20156': 'QJ 20156',
        'hb 6455': 'HB 6455-2014', 'hb6455': 'HB 6455-2014',
        'qj 1142': 'QJ 1142A-2008', 'qj1142': 'QJ 1142A-2008',
        'sae as568': 'SAE AS568F', 'as568': 'SAE AS568F',
        'iso 3601': 'ISO 3601-2', 'iso3601': 'ISO 3601-2',
        'gb/t': 'GB/T Standard', 'gjb': 'GJB Standard',
        'mil-std': 'MIL-STD', 'milstd': 'MIL-STD',
    }
    
    # Design module → formulas connections (fluid mechanics formulas only)
    MODULE_FORMULA_LINKS = {
        'cfd_analyzer': ['reynolds', 'mach', 'lift_force', 'drag_force', 'reynolds_nu', 
                         'reynolds_stress_uv', 'bluff_body_drag', 'cylinder_force', 'cylinder_velocity'],
        'pressure_reducing_valve': ['darcy_dp', 'bernoulli_total_pressure', 'bernoulli_dp', 
                                     'darcy_hf', 'Kv_to_Cv', 'Cv_to_Kv', 'valve_Cv', 
                                     'valve_authority', 'valve_dp_from_Cv'],
        'check_valve': ['valve_Cv', 'valve_authority', 'valve_dp_from_Cv', 'darcy_dp'],
    }
    
    # Module → Knowledge chapter mappings
    MODULE_KNOWLEDGE_LINKS = {
        'solenoid_optimizer': 'electromagnetic_valve',
        'spring_design': 'spring_design',
        'oring_design': 'seal_design',
        'seal_design': 'seal_design',
        'thermal_analyzer': 'thermal_analysis',
        'structural_analyzer': 'structural_analysis',
        'cfd_analyzer': 'cfd_simulation',
        'pressure_reducing_valve': 'pressure_reducing_valve',
        'check_valve': 'check_valve',
        'qj20156': 'compliance_verification',
        'materials_database': 'aerospace_materials',
    }
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.edges: List[Edge] = []
        self._built = False
    
    def build(self) -> int:
        """Build the complete knowledge graph. Returns edge count."""
        self.entities.clear()
        self.edges.clear()
        
        self._add_formula_entities()
        self._add_material_entities()
        self._add_knowledge_entities()
        self._add_module_entities()
        
        self._link_formulas_to_materials()
        self._link_formulas_to_standards()
        self._link_knowledge_to_formulas()
        self._link_modules_to_formulas()
        self._link_formula_io_chains()
        
        self._built = True
        return len(self.edges)
    
    # ── Entity builders ────────────────────────────────────
    
    def _add_formula_entities(self):
        from fluid_mechanics_calc import get_all_formulas
        from fluid_mechanics_i18n import FORMULA_I18N
        
        formulas = get_all_formulas()
        self._formula_data = {}  # Store for later linking
        
        for cat_id, cat_data in formulas.items():
            cat_name = cat_data.get('name', cat_id)
            for f in cat_data.get('formulas', []):
                fid = f.get('id', '')
                fname = f.get('name', fid)
                i18n = FORMULA_I18N.get(fid, {})
                
                entity = Entity(
                    id=f'formula:{fid}',
                    type='formula',
                    label=f'{fname} ({fid})',
                    properties={
                        'category_id': cat_id,
                        'category_name': cat_name,
                        'equation': f.get('eq', ''),
                        'inputs': f.get('inputs', []),
                        'output': f.get('output', ''),
                        'name_zh': i18n.get('name_zh', ''),
                        'application_zh': i18n.get('application_zh', ''),
                    }
                )
                self.entities[entity.id] = entity
                self._formula_data[fid] = entity
    
    def _add_material_entities(self):
        from materials_database import get_all_materials
        
        materials = get_all_materials()
        self._material_data = {}  # Store for linking
        
        for idx, m in enumerate(materials):
            name = m.get('name', '')
            # Use index + ASCII slug for stable, URL-safe IDs
            ascii_slug = re.sub(r'[^a-zA-Z0-9_]', '_', re.sub(r'[^\x00-\x7F]', '', name))
            mid = f'mat_{idx}' if not ascii_slug.strip('_') else f'mat_{ascii_slug}'
            
            entity = Entity(
                id=f'material:{mid}',
                type='material',
                label=name,
                properties={
                    'category': m.get('category', ''),
                    'standard': m.get('standard', ''),
                    'raw_data': {k: v for k, v in m.items() if k not in ['name', 'category', 'standard']}
                }
            )
            self.entities[entity.id] = entity
            self._material_data[name.lower()] = entity
    
    def _add_knowledge_entities(self):
        from knowledge_base import get_all_chapters
        
        chapters = get_all_chapters()
        self._knowledge_data = {}
        
        for ch in chapters:
            ch_id = ch.get('id', '')
            entity = Entity(
                id=f'knowledge:{ch_id}',
                type='knowledge_chapter',
                label=ch.get('title', ch_id),
                properties={
                    'icon': ch.get('icon', ''),
                    'section_count': ch.get('section_count', 0),
                }
            )
            self.entities[entity.id] = entity
            self._knowledge_data[ch_id] = entity
    
    def _add_module_entities(self):
        modules = {
            'solenoid_optimizer': '电磁阀优化设计',
            'pressure_reducing_valve': '减压阀设计',
            'check_valve': '单向阀设计',
            'spring_design': '弹簧设计',
            'oring_design': 'O形密封圈设计',
            'seal_design': '密封副设计',
            'cfd_analyzer': 'CFD流体仿真',
            'thermal_analyzer': '热力学分析',
            'structural_analyzer': '结构强度分析',
            'qj20156': 'QJ 20156标准合规',
            'materials_database': '材料数据库',
            'valve_metrics': '阀门性能指标',
            'knowledge_base': '知识库',
            'template_library': '研发模板库',
            'fluid_mechanics': '流体力学计算器',
        }
        for mid, mname in modules.items():
            entity = Entity(
                id=f'module:{mid}',
                type='design_module',
                label=mname,
                properties={'module_id': mid}
            )
            self.entities[entity.id] = entity
    
    # ── Edge builders (relationships) ──────────────────────
    
    def _link_formulas_to_materials(self):
        """Link formulas to materials based on keyword matching in formula metadata."""
        for fid, fentity in self._formula_data.items():
            # Collect all text to search for material keywords
            props = fentity.properties
            text = ' '.join([
                fid, fentity.label,
                props.get('equation', ''),
                props.get('name_zh', ''),
                props.get('application_zh', ''),
                ' '.join(props.get('inputs', [])),
                props.get('output', ''),
            ]).lower()
            
            for keyword, mat_label in self.MATERIAL_KEYWORDS.items():
                if keyword in text:
                    # Find matching material entity
                    for mname, mentity in self._material_data.items():
                        if mat_label.lower() in mname or mname in mat_label.lower():
                            self.edges.append(Edge(
                                source=f'formula:{fid}',
                                target=mentity.id,
                                relation='USES_MATERIAL',
                                weight=0.7,
                                properties={'matched_keyword': keyword}
                            ))
                            # Bidirectional
                            self.edges.append(Edge(
                                source=mentity.id,
                                target=f'formula:{fid}',
                                relation='USED_IN_FORMULA',
                                weight=0.7
                            ))
    
    def _link_formulas_to_standards(self):
        """Link formulas to standards based on keyword matching."""
        for fid, fentity in self._formula_data.items():
            props = fentity.properties
            text = ' '.join([
                fid, props.get('application_zh', ''),
                props.get('name_zh', ''),
                props.get('category_name', ''),
            ]).lower()
            
            for keyword, std_name in self.STANDARD_KEYWORDS.items():
                if keyword in text:
                    std_id = f'standard:{std_name.lower().replace(" ", "_").replace("/", "_")}'
                    # Create standard entity if not exists
                    if std_id not in self.entities:
                        self.entities[std_id] = Entity(
                            id=std_id, type='standard', label=std_name
                        )
                    self.edges.append(Edge(
                        source=f'formula:{fid}',
                        target=std_id,
                        relation='CITES_STANDARD',
                        weight=0.5
                    ))
    
    def _link_knowledge_to_formulas(self):
        """Link knowledge chapters to formulas via keyword overlap."""
        from fluid_mechanics_i18n import FORMULA_I18N
        
        for ch_id, chentity in self._knowledge_data.items():
            ch_text = f'{ch_id} {chentity.label}'.lower()
            
            for fid in self._formula_data:
                i18n = FORMULA_I18N.get(fid, {})
                ftext = f'{fid} {i18n.get("name_zh", "")} {i18n.get("application_zh", "")}'.lower()
                
                # Check overlap: if knowledge chapter title words appear in formula text
                ch_words = set(re.findall(r'\w+', ch_text))
                f_words = set(re.findall(r'\w+', ftext))
                overlap = ch_words & f_words
                
                if len(overlap) >= 2:  # At least 2 shared words
                    self.edges.append(Edge(
                        source=f'knowledge:{ch_id}',
                        target=f'formula:{fid}',
                        relation='REFERENCES',
                        weight=min(1.0, len(overlap) * 0.3),
                    ))
    
    def _link_modules_to_formulas(self):
        """Link design modules to fluid mechanics formulas."""
        for mod_id, formula_ids in self.MODULE_FORMULA_LINKS.items():
            mod_entity_id = f'module:{mod_id}'
            if mod_entity_id not in self.entities:
                continue
            for fid in formula_ids:
                formula_entity_id = f'formula:{fid}'
                if formula_entity_id in self.entities:
                    self.edges.append(Edge(
                        source=mod_entity_id,
                        target=formula_entity_id,
                        relation='REFERENCES',
                        weight=1.0,
                    ))
        # Also link modules to knowledge chapters
        for mod_id, ch_id in self.MODULE_KNOWLEDGE_LINKS.items():
            mod_entity_id = f'module:{mod_id}'
            knowledge_entity_id = f'knowledge:{ch_id}'
            if mod_entity_id in self.entities and knowledge_entity_id in self.entities:
                self.edges.append(Edge(
                    source=mod_entity_id,
                    target=knowledge_entity_id,
                    relation='REFERENCES',
                    weight=0.9,
                ))
        # Keyword-based module → material linking
        module_material_keywords = {
            'solenoid_optimizer': ['DT4C', 'Copper', '35WW300', 'MnZn', '1K107', 'Kapton', 'QZY', 'Nomex', 'Cr20Ni80'],
            'spring_design': ['50CrVA', 'SWP-A', 'Inconel', 'TC4', '1Cr18Ni9', 'C17200'],
            'oring_design': ['Viton', 'PTFE', 'Silastic', 'EPDM', 'NBR', 'FKM'],
            'seal_design': ['TC4', 'PTFE', '1Cr18Ni9', '2A12', 'Ceramic', 'Carbon'],
            'thermal_analyzer': ['TC4', 'Inconel', 'Ceramic', 'Stainless Steel'],
            'structural_analyzer': ['TC4', '2A12', '1Cr18Ni9', 'Inconel', 'Carbon'],
            'cfd_analyzer': ['TC4', 'Aluminum', 'Stainless Steel'],
            'pressure_reducing_valve': ['TC4', 'Stainless Steel', 'PTFE', '1Cr18Ni9'],
            'check_valve': ['TC4', 'Stainless Steel', 'Aluminum'],
            'qj20156': ['TC4', 'Stainless Steel', 'Aluminum'],
        }
        for mod_id, mat_keywords in module_material_keywords.items():
            mod_entity_id = f'module:{mod_id}'
            if mod_entity_id not in self.entities:
                continue
            for kw in mat_keywords:
                kw_lower = kw.lower()
                for mname, mentity in self._material_data.items():
                    if kw_lower in mname:
                        self.edges.append(Edge(
                            source=mod_entity_id,
                            target=mentity.id,
                            relation='USES_MATERIAL',
                            weight=0.6,
                        ))
                        break
    
    def _link_formula_io_chains(self):
        """Link formulas whose output becomes another formula's input."""
        output_to_formulas = defaultdict(list)
        input_to_formulas = defaultdict(list)
        
        for fid, fentity in self._formula_data.items():
            output = fentity.properties.get('output', '')
            if output:
                output_to_formulas[output].append(fid)
            for inp in fentity.properties.get('inputs', []):
                input_to_formulas[inp].append(fid)
        
        for param, producers in output_to_formulas.items():
            for consumer in input_to_formulas.get(param, []):
                for producer in producers:
                    if producer != consumer:
                        self.edges.append(Edge(
                            source=f'formula:{producer}',
                            target=f'formula:{consumer}',
                            relation='INPUT_OF',
                            weight=0.8,
                            properties={'parameter': param}
                        ))
    
    def to_dict(self) -> Dict:
        """Serialize graph to JSON-compatible dict."""
        return {
            'entities': {eid: {
                'type': e.type, 'label': e.label, 'properties': e.properties
            } for eid, e in self.entities.items()},
            'edges': [{
                'source': ed.source,
                'target': ed.target,
                'relation': ed.relation,
                'weight': ed.weight,
            } for ed in self.edges],
            'stats': self.get_stats(),
        }
    
    def get_stats(self) -> Dict:
        """Return graph statistics."""
        entity_types = defaultdict(int)
        relation_types = defaultdict(int)
        for e in self.entities.values():
            entity_types[e.type] += 1
        for ed in self.edges:
            relation_types[ed.relation] += 1
        return {
            'total_entities': len(self.entities),
            'total_edges': len(self.edges),
            'entity_types': dict(entity_types),
            'relation_types': dict(relation_types),
        }


# ============================================================
# Graph Queries — Fast in-memory lookups
# ============================================================

class GraphQuery:
    """Query interface for the knowledge graph."""
    
    def __init__(self, builder: KnowledgeGraphBuilder):
        self.builder = builder
        self._edge_index = defaultdict(list)  # source → [edge]
        self._reverse_index = defaultdict(list)  # target → [edge]
        self._build_indices()
    
    def _build_indices(self):
        for edge in self.builder.edges:
            self._edge_index[edge.source].append(edge)
            self._reverse_index[edge.target].append(edge)
    
    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get entity by ID."""
        e = self.builder.entities.get(entity_id)
        if not e:
            return None
        return {'id': e.id, 'type': e.type, 'label': e.label, 'properties': e.properties}
    
    def search_entity(self, query: str, entity_type: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Search entities by label fuzzy match."""
        results = []
        q = query.lower()
        for eid, e in self.builder.entities.items():
            if entity_type and e.type != entity_type:
                continue
            score = 0
            # Exact match in label
            if q in e.label.lower():
                score = 1.0
            elif q in eid.lower():
                score = 0.8
            else:
                # Partial word match
                label_words = set(re.findall(r'\w+', e.label.lower()))
                query_words = set(re.findall(r'\w+', q))
                overlap = label_words & query_words
                if overlap:
                    score = min(1.0, len(overlap) / max(len(query_words), 1) * 0.7)
            
            if score > 0:
                results.append((eid, e, score))
        
        results.sort(key=lambda x: -x[2])
        return [{
            'id': eid, 'type': e.type, 'label': e.label,
            'properties': e.properties, 'score': round(score, 3)
        } for eid, e, score in results[:limit]]
    
    def get_neighbors(self, entity_id: str, relation: Optional[str] = None, 
                      direction: str = 'both', limit: int = 50) -> List[Dict]:
        """Get neighbor entities of a node."""
        if entity_id not in self.builder.entities:
            return []
        
        neighbors = []
        seen = set()
        
        # Outgoing
        if direction in ('out', 'both'):
            for edge in self._edge_index.get(entity_id, []):
                if relation and edge.relation != relation:
                    continue
                target_id = edge.target
                if target_id in seen:
                    continue
                seen.add(target_id)
                target = self.builder.entities.get(target_id)
                if target:
                    neighbors.append({
                        'entity': {'id': target.id, 'type': target.type, 'label': target.label},
                        'relation': edge.relation,
                        'direction': 'outgoing',
                        'weight': edge.weight,
                    })
        
        # Incoming
        if direction in ('in', 'both'):
            for edge in self._reverse_index.get(entity_id, []):
                if relation and edge.relation != relation:
                    continue
                source_id = edge.source
                if source_id in seen:
                    continue
                seen.add(source_id)
                source = self.builder.entities.get(source_id)
                if source:
                    neighbors.append({
                        'entity': {'id': source.id, 'type': source.type, 'label': source.label},
                        'relation': edge.relation,
                        'direction': 'incoming',
                        'weight': edge.weight,
                    })
        
        return neighbors[:limit]
    
    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> List[Dict]:
        """Find shortest path between two entities using BFS."""
        if source_id not in self.builder.entities or target_id not in self.builder.entities:
            return []
        
        # BFS
        visited = {source_id}
        queue = [(source_id, [])]
        
        while queue:
            current, path = queue.pop(0)
            if len(path) >= max_depth:
                continue
            
            for edge in self._edge_index.get(current, []):
                next_id = edge.target
                if next_id == target_id:
                    new_path = path + [{
                        'from': current,
                        'to': next_id,
                        'relation': edge.relation,
                    }]
                    return new_path
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [{
                        'from': current,
                        'to': next_id,
                        'relation': edge.relation,
                    }]))
        
        return []
    
    def get_subgraph(self, entity_ids: List[str], depth: int = 1) -> Dict:
        """Extract a subgraph around given entities."""
        entities = {}
        edges = []
        visited = set(entity_ids)
        frontier = set(entity_ids)
        
        for d in range(depth):
            new_frontier = set()
            for eid in frontier:
                if eid in self.builder.entities:
                    entities[eid] = self.get_entity(eid)
                # Outgoing
                for edge in self._edge_index.get(eid, []):
                    edges.append({
                        'source': edge.source,
                        'target': edge.target,
                        'relation': edge.relation,
                    })
                    if edge.target not in visited:
                        visited.add(edge.target)
                        new_frontier.add(edge.target)
                # Incoming
                for edge in self._reverse_index.get(eid, []):
                    edges.append({
                        'source': edge.source,
                        'target': edge.target,
                        'relation': edge.relation,
                    })
                    if edge.source not in visited:
                        visited.add(edge.source)
                        new_frontier.add(edge.source)
            frontier = new_frontier
        
        # Add remaining entities
        for eid in visited:
            if eid not in entities and eid in self.builder.entities:
                entities[eid] = self.get_entity(eid)
        
        return {'entities': entities, 'edges': edges}
    
    def get_centrality(self, top_k: int = 20) -> List[Dict]:
        """Get most central entities by degree."""
        degrees = defaultdict(int)
        for edge in self.builder.edges:
            degrees[edge.source] += 1
            degrees[edge.target] += 1
        
        sorted_entities = sorted(degrees.items(), key=lambda x: -x[1])[:top_k]
        results = []
        for eid, deg in sorted_entities:
            e = self.builder.entities.get(eid)
            if e:
                results.append({
                    'id': eid, 'type': e.type, 'label': e.label,
                    'degree': deg
                })
        return results


# ============================================================
# Singleton accessor (lazy build)
# ============================================================

_knowledge_graph: Optional[KnowledgeGraphBuilder] = None
_graph_query: Optional[GraphQuery] = None

def get_knowledge_graph() -> KnowledgeGraphBuilder:
    """Get or build the knowledge graph singleton."""
    global _knowledge_graph, _graph_query
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraphBuilder()
        edge_count = _knowledge_graph.build()
        _graph_query = GraphQuery(_knowledge_graph)
        print(f"[knowledge_graph] Built: {len(_knowledge_graph.entities)} entities, {edge_count} edges")
    return _knowledge_graph

def get_graph_query() -> GraphQuery:
    """Get or build the graph query interface."""
    global _graph_query
    if _graph_query is None:
        get_knowledge_graph()  # Triggers build
    return _graph_query
