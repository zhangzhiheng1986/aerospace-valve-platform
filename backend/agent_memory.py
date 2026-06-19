"""
agent_memory.py - Sprint 14.2: Agent Memory & Experience Distillation

Inspired by Hermes self-evolution: Agents persist learned patterns, decisions,
and outcomes into a long-term memory store. On future tasks, they query past
experience to inform new decisions.

Memory types:
- EXPERIENCE: A complete (input, decision, outcome) triplet from past tasks
- PATTERN: A reusable rule extracted from multiple experiences
- SNAPSHOT: A frozen design milestone for audit and roll-back

Stored as JSON files in backend/data/agent_memory/ for simplicity.
No external DB dependency (Hermes principle: keep it lightweight).
"""

import os
import json
import time
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

_MEMORY_DIR = os.path.join(os.path.dirname(__file__), 'data', 'agent_memory')
os.makedirs(_MEMORY_DIR, exist_ok=True)

EXPERIENCES_FILE = os.path.join(_MEMORY_DIR, 'experiences.jsonl')
PATTERNS_FILE = os.path.join(_MEMORY_DIR, 'patterns.json')
SNAPSHOTS_FILE = os.path.join(_MEMORY_DIR, 'snapshots.json')

_lock = threading.Lock()


# ============================================================================
# Experience recording
# ============================================================================

def record_experience(
    agent_role: str,
    task: str,
    decision: Dict,
    outcome: Dict,
    success: bool = True,
    duration_ms: float = 0.0,
    metadata: Optional[Dict] = None,
) -> str:
    """
    Append a single experience record to the JSONL store.

    Returns the experience_id (UUID).
    """
    exp_id = f"exp_{uuid.uuid4().hex[:12]}"
    record = {
        'experience_id': exp_id,
        'agent_role': agent_role,
        'task': task,
        'decision': decision,
        'outcome': outcome,
        'success': success,
        'duration_ms': duration_ms,
        'metadata': metadata or {},
        'created_at': datetime.now().isoformat(),
    }
    with _lock:
        with open(EXPERIENCES_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    return exp_id


def get_experiences(
    agent_role: Optional[str] = None,
    success: Optional[bool] = None,
    limit: int = 50,
) -> List[Dict]:
    """Load recent experiences, optionally filtered by agent_role and success."""
    if not os.path.exists(EXPERIENCES_FILE):
        return []
    records = []
    with open(EXPERIENCES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if agent_role and rec.get('agent_role') != agent_role:
                continue
            if success is not None and rec.get('success') != success:
                continue
            records.append(rec)
    # Most recent first
    records.sort(key=lambda r: r.get('created_at', ''), reverse=True)
    return records[:limit]


# ============================================================================
# Pattern extraction
# ============================================================================

def extract_patterns(agent_role: Optional[str] = None, min_count: int = 1) -> List[Dict]:
    """
    Distill reusable patterns from past experiences.

    A pattern emerges when >=min_count experiences share the same
    (tool_name, valve_type) tuple. We pick successful ones as the
    'best practice' and flag failure rates for warnings.
    """
    exps = get_experiences(agent_role=agent_role, limit=500)
    if not exps:
        return []

    # Group by (agent_role, decision_tool, outcome_valve_type)
    buckets: Dict[tuple, List[Dict]] = {}
    for e in exps:
        tool = e.get('decision', {}).get('tool', 'unknown')
        vtype = e.get('outcome', {}).get('valve_type', 'generic')
        key = (e.get('agent_role', 'unknown'), tool, vtype)
        buckets.setdefault(key, []).append(e)

    patterns = []
    for key, group in buckets.items():
        if len(group) < min_count:
            continue
        successes = sum(1 for e in group if e.get('success'))
        total = len(group)
        success_rate = successes / total if total else 0.0
        avg_duration = sum(e.get('duration_ms', 0) for e in group) / total
        # Sample decision fields to characterize pattern
        sample_decision = group[0].get('decision', {})
        patterns.append({
            'pattern_id': f"pat_{uuid.uuid4().hex[:8]}",
            'agent_role': key[0],
            'tool': key[1],
            'valve_type': key[2],
            'count': total,
            'success_rate': round(success_rate, 3),
            'avg_duration_ms': round(avg_duration, 1),
            'sample_decision_keys': list(sample_decision.keys())[:8],
            'confidence': min(1.0, total / 10.0),  # saturate at 10 experiences
            'recommendation': 'use' if success_rate >= 0.7 else 'avoid' if success_rate < 0.3 else 'review',
        })
    patterns.sort(key=lambda p: p['confidence'] * p['success_rate'], reverse=True)
    return patterns


def save_patterns(patterns: Optional[List[Dict]] = None) -> int:
    """Recompute and persist patterns. Returns count saved."""
    if patterns is None:
        patterns = extract_patterns()
    with _lock:
        with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'updated_at': datetime.now().isoformat(),
                'count': len(patterns),
                'patterns': patterns,
            }, f, ensure_ascii=False, indent=2)
    return len(patterns)


def get_patterns(agent_role: Optional[str] = None, min_confidence: float = 0.0) -> List[Dict]:
    """Load saved patterns, optionally filtered."""
    if not os.path.exists(PATTERNS_FILE):
        return []
    try:
        with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    patterns = data.get('patterns', [])
    if agent_role:
        patterns = [p for p in patterns if p.get('agent_role') == agent_role]
    if min_confidence:
        patterns = [p for p in patterns if p.get('confidence', 0) >= min_confidence]
    return patterns


# ============================================================================
# Snapshots (frozen design milestones)
# ============================================================================

def create_snapshot(
    design_id: str,
    design_type: str,
    state: Dict,
    note: str = '',
) -> str:
    """Freeze a design state for audit/rollback."""
    snap_id = f"snap_{uuid.uuid4().hex[:8]}"
    snap = {
        'snapshot_id': snap_id,
        'design_id': design_id,
        'design_type': design_type,
        'state': state,
        'note': note,
        'frozen_at': datetime.now().isoformat(),
    }
    with _lock:
        snapshots = []
        if os.path.exists(SNAPSHOTS_FILE):
            try:
                with open(SNAPSHOTS_FILE, 'r', encoding='utf-8') as f:
                    snapshots = json.load(f)
            except (json.JSONDecodeError, OSError):
                snapshots = []
        snapshots.append(snap)
        # Keep last 200 snapshots
        snapshots = snapshots[-200:]
        with open(SNAPSHOTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(snapshots, f, ensure_ascii=False, indent=2)
    return snap_id


def get_snapshots(design_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """List snapshots, optionally filtered by design_id."""
    if not os.path.exists(SNAPSHOTS_FILE):
        return []
    try:
        with open(SNAPSHOTS_FILE, 'r', encoding='utf-8') as f:
            snapshots = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    if design_id:
        snapshots = [s for s in snapshots if s.get('design_id') == design_id]
    return snapshots[-limit:][::-1]  # most recent first


# ============================================================================
# Reflection — synthesize guidance from past experience
# ============================================================================

def reflect_for_task(task: str, agent_role: Optional[str] = None) -> Dict:
    """
    Query memory for guidance on a new task.
    Returns: {patterns: [...], recent_similar: [...], recommendation: str}
    """
    patterns = get_patterns(agent_role=agent_role, min_confidence=0.2)
    # Pick top 3 patterns as guidance
    guidance_patterns = patterns[:3]
    # Find recent similar experiences
    recent = get_experiences(agent_role=agent_role, limit=10)
    # Build recommendation
    if not patterns:
        recommendation = 'No prior experience — proceed with default rules'
    else:
        top = patterns[0]
        if top.get('success_rate', 0) >= 0.7:
            recommendation = f"Use {top['tool']} for {top['valve_type']} (success rate {top['success_rate']*100:.0f}%)"
        else:
            recommendation = f"Cautious: best pattern {top['tool']} has only {top['success_rate']*100:.0f}% success"
    return {
        'task': task,
        'agent_role': agent_role or 'any',
        'guidance_patterns': guidance_patterns,
        'recent_experiences': recent[:5],
        'recommendation': recommendation,
    }


# ============================================================================
# Stats / admin
# ============================================================================

def get_memory_stats() -> Dict:
    """Aggregate stats for admin dashboards."""
    exps = get_experiences(limit=10000)
    patterns = get_patterns()
    snapshots = get_snapshots(limit=10000)
    by_role = {}
    for e in exps:
        r = e.get('agent_role', 'unknown')
        by_role[r] = by_role.get(r, 0) + 1
    by_tool = {}
    for e in exps:
        t = e.get('decision', {}).get('tool', 'unknown')
        by_tool[t] = by_tool.get(t, 0) + 1
    success_count = sum(1 for e in exps if e.get('success'))
    return {
        'experiences_total': len(exps),
        'experiences_by_role': by_role,
        'experiences_by_tool': by_tool,
        'success_rate': round(success_count / len(exps), 3) if exps else 0.0,
        'patterns_total': len(patterns),
        'snapshots_total': len(snapshots),
        'memory_dir': _MEMORY_DIR,
    }
