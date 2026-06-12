"""
VectorStore — Sprint 6 Lightweight Semantic Search
===================================================
Pure-Python vector store using numpy TF-IDF + cosine similarity.
Designed for Phase 1 MVP data scale (< 10MB, < 5000 documents).
Zero external dependencies beyond numpy.
Upgradable to ChromaDB when Python >= 3.10 (sqlite 3.35.0+).

Collections:
  - knowledge: 15 chapters, ~4000 paragraphs from knowledge_base.py
  - formulas: 207 formulas with descriptions from fluid_mechanics_i18n.py
  - materials: 21 materials with full property descriptions
"""

import logging
import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Text Tokenizer — character n-grams for Chinese, word split for English
# ---------------------------------------------------------------------------

def _tokenize(text: str, ngram: int = 2) -> List[str]:
    """Tokenize mixed Chinese/English text into character n-grams.
    
    Chinese text uses character bigrams (overlapping).
    English words are kept whole and also split into prefixes.
    """
    tokens = []
    # Split into Chinese/non-Chinese segments
    segments = re.split(r'([\u4e00-\u9fff]+)', text.lower())
    
    for seg in segments:
        if not seg.strip():
            continue
        if re.match(r'[\u4e00-\u9fff]+', seg):
            # Chinese: use character n-grams
            cleaned = re.sub(r'\s+', '', seg)
            for i in range(len(cleaned) - ngram + 1):
                tokens.append(cleaned[i:i + ngram])
            # Also add single chars for better recall
            tokens.extend(list(cleaned))
        else:
            # English/numbers: use word-level + character n-grams
            words = re.findall(r'[a-z0-9]+', seg)
            tokens.extend(words)
            for w in words:
                if len(w) >= 3:
                    for i in range(len(w) - ngram + 1):
                        tokens.append(w[i:i + ngram])
    
    return tokens


# ---------------------------------------------------------------------------
# TF-IDF Vectorizer
# ---------------------------------------------------------------------------

class TfidfVectorizer:
    """Minimal TF-IDF vectorizer with L2 normalization."""
    
    def __init__(self, max_features: int = 5000):
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[int, float] = {}
        self.max_features = max_features
    
    def fit(self, documents: List[str]) -> 'TfidfVectorizer':
        """Build vocabulary and compute IDF from document collection."""
        # Tokenize all documents
        tokenized = [_tokenize(doc) for doc in documents]
        
        # Count document frequency
        df: Counter = Counter()
        for tokens in tokenized:
            unique = set(tokens)
            for t in unique:
                df[t] += 1
        
        N = len(documents)
        
        # Select top terms by DF
        top_terms = [t for t, _ in df.most_common(self.max_features)]
        self.vocab = {term: idx for idx, term in enumerate(top_terms)}
        
        # Compute IDF: log((N + 1) / (df + 1)) + 1
        for term, idx in self.vocab.items():
            self.idf[idx] = math.log((N + 1) / (df.get(term, 0) + 1)) + 1
        
        return self
    
    def transform(self, documents: List[str]) -> np.ndarray:
        """Transform documents to TF-IDF vectors."""
        V = len(self.vocab)
        result = np.zeros((len(documents), V), dtype=np.float32)
        
        for i, doc in enumerate(documents):
            tokens = _tokenize(doc)
            tf = Counter(tokens)
            if not tf:
                continue
            for term, count in tf.items():
                idx = self.vocab.get(term)
                if idx is not None:
                    result[i, idx] = count / len(tokens) * self.idf[idx]
            
            # L2 normalize
            norm = np.linalg.norm(result[i])
            if norm > 0:
                result[i] /= norm
        
        return result
    
    def transform_query(self, query: str) -> np.ndarray:
        """Transform a single query string."""
        return self.transform([query])[0]


# ---------------------------------------------------------------------------
# Vector Store
# ---------------------------------------------------------------------------

class VectorStore:
    """Lightweight vector search with cosine similarity."""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.vectors: Optional[np.ndarray] = None
        self.documents: List[Dict[str, Any]] = []
        self._built = False
    
    def index(self, documents: List[Dict[str, Any]], text_field: str = "text") -> 'VectorStore':
        """Build index from a list of document dicts.
        
        Each document must have a 'text_field' key containing the searchable text.
        """
        self.documents = documents
        texts = [doc.get(text_field, "") for doc in documents]
        
        self.vectorizer = TfidfVectorizer()
        self.vectorizer.fit(texts)
        self.vectors = self.vectorizer.transform(texts)
        self._built = True
        
        _log.info(f"VectorStore[{self.name}]: indexed {len(documents)} docs, "
                  f"vocab={len(self.vectorizer.vocab)}, "
                  f"vectors.shape={self.vectors.shape}")
        return self
    
    def _cosine_similarity(self, query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and all documents."""
        # Both are already L2-normalized
        return np.dot(doc_vecs, query_vec)
    
    def search(self, query: str, top_k: int = 5, min_score: float = 0.0) -> List[Dict]:
        """Search for documents matching the query.
        
        Returns list of {score, document, index}.
        """
        if not self._built or self.vectorizer is None:
            return []
        
        qvec = self.vectorizer.transform_query(query)
        scores = self._cosine_similarity(qvec, self.vectors)
        
        # Get top-k indices
        if len(scores) == 0:
            return []
        
        top_indices = np.argsort(scores)[::-1][:top_k * 2]  # Get extra for filtering
        
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score < min_score:
                continue
            doc = dict(self.documents[int(idx)])
            doc["_score"] = round(score, 4)
            doc["_index"] = int(idx)
            results.append(doc)
            if len(results) >= top_k:
                break
        
        return results
    
    def search_multi(self, queries: List[str], top_k: int = 3) -> Dict[str, List[Dict]]:
        """Batch search: one result set per query."""
        return {q: self.search(q, top_k) for q in queries}
    
    def stats(self) -> Dict:
        """Return index statistics."""
        if not self._built:
            return {"name": self.name, "built": False, "documents": 0}
        return {
            "name": self.name,
            "built": True,
            "documents": len(self.documents),
            "vocabulary": len(self.vectorizer.vocab) if self.vectorizer else 0,
            "vector_dim": int(self.vectors.shape[1]) if self.vectors is not None else 0,
        }


# ---------------------------------------------------------------------------
# Knowledge Indexer — bridges the vector store to project modules
# ---------------------------------------------------------------------------

class KnowledgeIndexer:
    """Indexes knowledge base, formulas, and materials into vector stores."""
    
    def __init__(self):
        self.stores: Dict[str, VectorStore] = {}
    
    def build_knowledge_store(self) -> VectorStore:
        """Index knowledge base chapters and sections."""
        docs = []
        try:
            from knowledge_base import get_all_chapters, get_chapter_detail
            chapters = get_all_chapters()
            for ch in chapters:
                ch_id = ch["id"]
                ch_detail = get_chapter_detail(ch_id)
                if not ch_detail:
                    continue
                ch_title = ch_detail.get("title", ch_id)
                sections = ch_detail.get("sections", [])
                for section in sections:
                    sec_id = section.get("id", "")
                    title = section.get("title", sec_id)
                    content = section.get("content", "")
                    # Index the full section
                    docs.append({
                        "id": f"kb:{ch_id}:{sec_id}",
                        "text": f"{ch_title} {title} {content}",
                        "title": title,
                        "chapter": ch_title,
                        "chapter_id": ch_id,
                        "section_id": sec_id,
                        "type": "knowledge",
                    })
                    # Index paragraphs for fine-grained search
                    for pi, para in enumerate(content.split('\n')):
                        para = para.strip()
                        if len(para) > 20:
                            docs.append({
                                "id": f"kb:{ch_id}:{sec_id}:p{pi}",
                                "text": f"{ch_title} {title} {para}",
                                "title": title,
                                "chapter": ch_title,
                                "chapter_id": ch_id,
                                "section_id": sec_id,
                                "type": "knowledge_paragraph",
                                "snippet": para[:200],
                            })
        except ImportError:
            _log.warning("knowledge_base module not available, skipping knowledge index")
        
        store = VectorStore("knowledge")
        if docs:
            store.index(docs)
        else:
            _log.warning("No knowledge documents to index")
        self.stores["knowledge"] = store
        return store
    
    def build_formula_store(self) -> VectorStore:
        """Index fluid mechanics formulas with descriptions."""
        docs = []
        try:
            from fluid_mechanics_i18n import FORMULA_I18N, CATEGORY_I18N
            for fid, info in FORMULA_I18N.items():
                cat_id = info.get("category", "")
                cat_info = CATEGORY_I18N.get(cat_id, {})
                cat_name = cat_info.get("name_zh", cat_id)
                
                zh_name = info.get("name_zh", "")
                desc_zh = info.get("desc_zh", "")
                application = info.get("application_zh", "")
                inputs_info = info.get("inputs", {})
                
                # Build rich searchable text
                text_parts = [cat_name, zh_name, desc_zh, application]
                if isinstance(inputs_info, dict):
                    text_parts.append(" ".join(inputs_info.keys()))
                
                docs.append({
                    "id": f"formula:{fid}",
                    "text": " ".join(p for p in text_parts if p),
                    "formula_id": fid,
                    "name_zh": zh_name,
                    "desc_zh": desc_zh,
                    "category": cat_name,
                    "category_id": cat_id,
                    "application": application,
                    "type": "formula",
                })
        except ImportError:
            _log.warning("fluid_mechanics_i18n not available, skipping formula index")
        
        store = VectorStore("formulas")
        if docs:
            store.index(docs)
        self.stores["formulas"] = store
        return store
    
    def build_material_store(self) -> VectorStore:
        """Index materials database."""
        docs = []
        try:
            from materials_database import get_all_materials, get_material_detail
            materials = get_all_materials()
            for mat in materials:
                name = mat.get("name", "")
                category = mat.get("category", "")
                standard = mat.get("standard", "")
                
                # Get detailed properties
                detail = get_material_detail(name) if name else None
                if not detail:
                    # Fallback: use basic info only
                    docs.append({
                        "id": f"material:{name}",
                        "text": f"{name} {category} {standard}",
                        "material_id": name,
                        "name": name,
                        "category": category,
                        "standard": standard,
                        "type": "material",
                    })
                    continue
                
                # Build rich text from all available properties
                prop_parts = [name, category, standard]
                for key in ["density", "tensile_strength", "yield_strength", "elastic_modulus",
                           "thermal_expansion", "thermal_conductivity", "specific_heat",
                           "melting_point", "hardness", "poisson_ratio",
                           "fatigue_limit", "corrosion_resistance", "application"]:
                    val = detail.get(key)
                    if val is not None and val != "":
                        prop_parts.append(f"{key}:{val}")
                
                docs.append({
                    "id": f"material:{name}",
                    "text": " ".join(prop_parts),
                    "material_id": name,
                    "name": name,
                    "category": category,
                    "standard": standard,
                    "type": "material",
                })
        except ImportError:
            _log.warning("materials_database not available, skipping material index")
        
        store = VectorStore("materials")
        if docs:
            store.index(docs)
        self.stores["materials"] = store
        return store
    
    def build_all(self) -> Dict[str, VectorStore]:
        """Build all three indexes."""
        self.build_knowledge_store()
        self.build_formula_store()
        self.build_material_store()
        return self.stores
    
    def search_all(self, query: str, top_k: int = 5) -> Dict[str, List[Dict]]:
        """Search across all stores."""
        results = {}
        for name, store in self.stores.items():
            results[name] = store.search(query, top_k // 2)
        return results
    
    def unified_search(self, query: str, top_k: int = 8) -> List[Dict]:
        """Search across all stores and merge results by score."""
        all_hits = []
        for name, store in self.stores.items():
            hits = store.search(query, top_k // 2)
            for h in hits:
                h["_source"] = name
            all_hits.extend(hits)
        
        # Sort by score descending
        all_hits.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return all_hits[:top_k]


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_indexer: Optional[KnowledgeIndexer] = None


def get_indexer() -> KnowledgeIndexer:
    """Get or create the singleton KnowledgeIndexer."""
    global _indexer
    if _indexer is None:
        _indexer = KnowledgeIndexer()
        _log.info("KnowledgeIndexer created (lazy init — build_all() not yet called)")
    return _indexer


def get_search() -> KnowledgeIndexer:
    """Get fully-built indexer (builds if not yet done)."""
    global _indexer
    if _indexer is None or not _indexer.stores:
        _indexer = KnowledgeIndexer()
        _indexer.build_all()
        _log.info(f"KnowledgeIndexer built: { {k: v.stats() for k, v in _indexer.stores.items()} }")
    return _indexer


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time
    
    print("=== VectorStore Unit Tests ===\n")
    
    # Test 1: Basic tokenization
    print("[1] Tokenizer")
    tokens_cn = _tokenize("航空航天阀门减压阀设计")
    tokens_en = _tokenize("aerospace solenoid valve design")
    tokens_mix = _tokenize("TC4钛合金 fatigue strength 疲劳强度")
    print(f"  CN: {tokens_cn[:10]}...")
    print(f"  EN: {tokens_en[:10]}...")
    print(f"  MIX: {tokens_mix[:10]}...")
    assert len(tokens_cn) > 5, "Chinese tokenizer failed"
    assert "aerospace" in tokens_en, "English tokenizer failed"
    assert "tc4" in tokens_mix, "Mixed tokenizer failed"
    print("  PASS PASS\n")
    
    # Test 2: TF-IDF vectorizer
    print("[2] TF-IDF Vectorizer")
    docs = [
        "航空航天阀门电磁阀设计方法",
        "减压阀压力调节原理与计算",
        "O型密封圈泄漏率Roth模型",
        "钛合金TC4材料力学性能",
        "弹簧设计疲劳寿命校核",
    ]
    vec = TfidfVectorizer(max_features=200)
    vec.fit(docs)
    print(f"  Vocabulary size: {len(vec.vocab)}")
    vectors = vec.transform(docs)
    print(f"  Vectors shape: {vectors.shape}")
    assert vectors.shape[0] == 5
    assert vectors.shape[1] == len(vec.vocab)
    print("  PASS PASS\n")
    
    # Test 3: Cosine similarity search
    print("[3] Vector Store Search")
    store = VectorStore("test")
    store.index([{"id": f"doc{i}", "text": d} for i, d in enumerate(docs)])
    results = store.search("钛合金材料属性", top_k=2)
    for r in results:
        print(f"  score={r['_score']:.3f} | {r['text'][:50]}... (id={r['id']})")
    assert results[0]["_score"] > 0, "Top result should have positive score"
    assert results[0]["id"] == "doc3", f"Expected doc3 (TC4), got {results[0]['id']}"
    print("  PASS PASS\n")
    
    # Test 4: Batch search
    print("[4] Batch Search")
    batch = store.search_multi(["密封圈", "疲劳"], top_k=2)
    for q, res in batch.items():
        top = res[0] if res else None
        print(f"  '{q}' → {top['text'][:40]}... ({top['_score']:.3f})" if top else f"  '{q}' → no results")
    print("  PASS PASS\n")
    
    # Test 5: Knowledge Indexer integration
    print("[5] Knowledge Indexer (real data)")
    t0 = time.time()
    idx = get_search()
    elapsed = time.time() - t0
    for name, store in idx.stores.items():
        s = store.stats()
        print(f"  {name}: {s['documents']} docs, vocab={s['vocabulary']}, dim={s['vector_dim']}")
    print(f"  Built in {elapsed:.2f}s")
    print("  PASS PASS\n")
    
    # Test 6: Semantic search quality
    print("[6] Semantic Search Quality")
    queries = ["阀门密封泄漏", "雷诺数计算", "钛合金 TC4", "弹簧疲劳"]
    for q in queries:
        results = idx.unified_search(q, top_k=3)
        top_sources = [r.get("_source") for r in results]
        print("  {} -> sources={} top_score={:.3f}".format(
            q, top_sources, results[0]["_score"] if results else 0))
    
    print("\n=== All tests complete ===")
    print(f"Total index build time: {elapsed:.2f}s")
