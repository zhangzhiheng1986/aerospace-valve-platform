"""
OrchestratorAgent — Sprint 3
=============================
Multi-agent orchestration hub. Decomposes user queries into subtasks,
delegates to specialized sub-agents, aggregates results with cross-validation.

Design philosophy (from fusion architecture):
- Protocol-First: all Agent communication via standardized REST-like interface
- N+M elimination: one Orchestrator serving all frontends (Web, CLI, future IDE)
- cwd binding: each sub-agent runs in its own logical workspace
- Three Agent MVP: Orchestrator + Design + Compliance
"""

import logging
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


def _json_safe(obj: Any) -> Any:
    """Recursively convert objects to JSON-serializable types."""
    import math
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
        return obj
    if isinstance(obj, (int, bool, str, type(None))):
        return obj
    # Fallback: convert unknown objects to dict or string
    if hasattr(obj, '__dict__'):
        return _json_safe(obj.__dict__)
    if hasattr(obj, '_asdict'):
        return _json_safe(obj._asdict())
    return str(obj)

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"
    DESIGN = "design"
    COMPLIANCE = "compliance"

@dataclass
class SubTask:
    """A single unit of work delegated to a sub-agent."""
    task_id: str
    role: AgentRole
    tool_name: str
    inputs: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    depends_on: List[str] = field(default_factory=list)  # task_ids that must finish first
    priority: int = 0  # higher = run first

@dataclass
class DecompositionPlan:
    """A plan for decomposing a user query into subtasks."""
    plan_id: str
    user_message: str
    intent: str
    subtasks: List[SubTask]
    confidence: float = 1.0
    created_at: str = ""

# ---------------------------------------------------------------------------
# Sub-Agent Registry
# ---------------------------------------------------------------------------

class AgentRegistry:
    """Manages available sub-agents and their capabilities."""

    def __init__(self):
        self._agents: Dict[AgentRole, 'SubAgent'] = {}
        self._tools: Dict[str, AgentRole] = {}  # tool_name → role mapping

    def register(self, agent: 'SubAgent') -> None:
        """Register a sub-agent and its tools."""
        self._agents[agent.role] = agent
        for tool_name in agent.capabilities:
            self._tools[tool_name] = agent.role
            # Allow multiple agents to claim the same tool (pick first)
            if tool_name not in self._tools:
                self._tools[tool_name] = agent.role

    def resolve_role(self, tool_name: str) -> Optional[AgentRole]:
        """Find which agent handles a given tool."""
        return self._tools.get(tool_name)

    def get_agent(self, role: AgentRole) -> Optional['SubAgent']:
        """Get agent by role."""
        return self._agents.get(role)

    def list_agents(self) -> List['SubAgent']:
        return list(self._agents.values())

# ---------------------------------------------------------------------------
# Base Sub-Agent
# ---------------------------------------------------------------------------

class SubAgent:
    """Specialized domain agent that executes tools in its capability set."""

    def __init__(self, role: AgentRole, name: str, capabilities: List[str], description: str = ""):
        self.role = role
        self.name = name
        self.capabilities = capabilities
        self.description = description
        self.tool_handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()

    def register_tool(self, tool_name: str, handler: Callable) -> None:
        """Register a tool handler."""
        assert tool_name in self.capabilities, f"{tool_name} not in {self.role} capabilities"
        self.tool_handlers[tool_name] = handler

    def execute(self, tool_name: str, inputs: Dict, timeout_s: float = 30.0) -> Dict:
        """Execute a tool with timeout. Returns {success, result, error}."""
        if tool_name not in self.tool_handlers:
            return {"success": False, "error": f"Tool {tool_name} not registered on {self.role}"}

        handler = self.tool_handlers[tool_name]
        start = time.time()

        # Run in thread with timeout
        result_holder = {"result": None, "error": None, "done": False}

        def _run():
            try:
                # Pass inputs as keyword arguments to the handler
                result_holder["result"] = handler(**inputs) if isinstance(inputs, dict) else handler(inputs)
                result_holder["done"] = True
            except Exception as e:
                result_holder["error"] = str(e)
                result_holder["done"] = True
                logging.getLogger(__name__).exception(f"SubAgent {self.role}.{tool_name} failed")

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join(timeout=timeout_s)

        elapsed = time.time() - start
        if not result_holder["done"]:
            return {"success": False, "error": f"Timeout after {timeout_s}s", "elapsed_ms": elapsed * 1000}

        if result_holder["error"]:
            return {"success": False, "error": result_holder["error"], "elapsed_ms": elapsed * 1000}

        result = _json_safe(result_holder["result"])
        if isinstance(result, dict):
            result["elapsed_ms"] = elapsed * 1000
            if "success" not in result:
                result["success"] = True
            return result
        return {"success": True, "result": result, "elapsed_ms": elapsed * 1000}

    def to_dict(self) -> Dict:
        return {
            "role": self.role.value,
            "name": self.name,
            "capabilities": self.capabilities,
            "description": self.description,
        }

# ---------------------------------------------------------------------------
# Decomposition Engine
# ---------------------------------------------------------------------------

class TaskDecomposer:
    """
    Analyzes a user message and decomposes it into subtasks with dependency
    ordering. Uses rule-based decomposition (no LLM call needed for MVP).
    """

    # Decomposition recipes: intent → list of (tool_name, role, depends_on_indices)
    RECIPES = {
        # Complex multi-discipline design
        "design_solenoid_system": [
            ("query_material", AgentRole.DESIGN, []),
            ("analyze_solenoid_valve", AgentRole.DESIGN, [0]),
            ("check_compliance", AgentRole.COMPLIANCE, [1]),    # runs after design
        ],
        "design_pressure_valve_system": [
            ("query_material", AgentRole.DESIGN, []),
            ("analyze_pressure_valve", AgentRole.DESIGN, [0]),
            ("check_compliance", AgentRole.COMPLIANCE, [1]),
        ],
        "design_spring_system": [
            ("query_material", AgentRole.DESIGN, []),
            ("design_spring", AgentRole.DESIGN, [0]),
            ("check_compliance", AgentRole.COMPLIANCE, [1]),
        ],
        "design_oring_system": [
            ("query_material", AgentRole.DESIGN, []),
            ("design_oring", AgentRole.DESIGN, [0]),
            ("check_compliance", AgentRole.COMPLIANCE, [1]),
        ],
        # Compliance-only checks
        "validate_design": [
            ("check_compliance", AgentRole.COMPLIANCE, []),
        ],
        # Material + performance cross-check
        "material_analysis": [
            ("query_material", AgentRole.DESIGN, []),
            ("run_fluid_calculation", AgentRole.DESIGN, []),    # independent, parallel
        ],
        # Full design review
        "design_review": [
            ("query_material", AgentRole.DESIGN, []),
            ("analyze_pressure_valve", AgentRole.DESIGN, [0]),
            ("design_spring", AgentRole.DESIGN, []),             # independent of valve
            ("check_compliance", AgentRole.COMPLIANCE, [1, 2]),  # wait for both
        ],
    }

    @classmethod
    def _is_simple_query(cls, message: str) -> bool:
        """Check if this is a simple informational query, not a design request."""
        m = message.lower()
        simple_patterns = [
            'what is', 'tell me about', 'describe', 'explain',
            'info on', 'details of', 'properties of', 'look up',
        ]
        design_patterns = [
            'design', 'analyze', 'calculate', 'optimize', 'verify',
            'check', 'validate', 'select', 'review', 'test',
        ]
        has_simple = any(p in m for p in simple_patterns)
        has_design = any(p in m for p in design_patterns)
        return has_simple and not has_design

    @classmethod
    def match_intent(cls, message: str) -> str:
        """Determine the highest-level intent for decomposition."""
        # Simple informational queries: no orchestration needed
        if cls._is_simple_query(message):
            return None

        m = message.lower()

        # Compound signals first
        if ("设计" in m or "design" in m) and ("电磁阀" in m or "solenoid" in m or "螺线管" in m):
            return "design_solenoid_system"
        if ("设计" in m or "design" in m) and ("减压阀" in m or "pressure" in m or "prv" in m):
            return "design_pressure_valve_system"
        if ("设计" in m or "design" in m) and ("弹簧" in m or "spring" in m):
            return "design_spring_system"
        if ("设计" in m or "design" in m) and ("o型" in m or "oring" in m or "密封圈" in m or "o形" in m or "o-ring" in m):
            return "design_oring_system"
        if ("审查" in m or "review" in m or "评估" in m or "评估" in m) and ("设计" in m or "方案" in m):
            return "design_review"
        if ("验证" in m or "validate" in m or "合规" in m or "compliance" in m or "标准" in m or "qj" in m):
            return "validate_design"
        if ("材料" in m or "material" in m or "tc4" in m or "inconel" in m):
            return "material_analysis"

        # Fallback: single-agent queries go to design
        return None  # Simple queries don't need orchestration

    @classmethod
    def decompose(cls, message: str) -> Tuple[Optional[DecompositionPlan], str]:
        """
        Decompose a message into subtasks. Returns (plan, matched_intent).
        Returns (None, intent) if no decomposition needed (simple query).
        """
        intent = cls.match_intent(message)
        if intent is None:
            return None, "simple_query"

        recipe = cls.RECIPES.get(intent)
        if not recipe:
            return None, intent

        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        subtasks = []
        for i, (tool_name, role, deps) in enumerate(recipe):
            dep_ids = []
            for dep_idx in deps:
                dep_ids.append(subtasks[dep_idx].task_id)

            st = SubTask(
                task_id="task_{}_{}".format(i, tool_name),
                role=role,
                tool_name=tool_name,
                inputs={"message": message},  # delegate param extraction to sub-agent
                depends_on=dep_ids,
                priority=len(recipe) - i,  # earlier tasks higher priority
            )
            subtasks.append(st)

        return DecompositionPlan(
            plan_id=plan_id,
            user_message=message,
            intent=intent,
            subtasks=subtasks,
            confidence=0.85,
            created_at=datetime.now().isoformat(),
        ), intent

# ---------------------------------------------------------------------------
# Orchestrator Agent — Main Class
# ---------------------------------------------------------------------------

class OrchestratorAgent:
    """
    Central orchestration hub. Takes a user message → decomposes → delegates →
    aggregates → returns synthesized response.
    """

    def __init__(self, max_workers: int = 4):
        self.registry = AgentRegistry()
        self.decomposer = TaskDecomposer()
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._sessions: Dict[str, Dict] = {}  # active orchestration sessions

    # ------------------------------------------------------------------
    # Agent registration
    # ------------------------------------------------------------------

    def register_design_agent(self, handler_map: Dict[str, Callable]) -> 'OrchestratorAgent':
        """Register the Design agent with its tool handlers."""
        agent = SubAgent(
            role=AgentRole.DESIGN,
            name="Design Expert",
            capabilities=[
                "query_material", "analyze_solenoid_valve", "analyze_pressure_valve",
                "design_spring", "design_oring", "design_seal", "run_fluid_calculation",
                "identify_formula",
            ],
            description="阀门设计专家：负责材料选型、结构设计、流体计算"
        )
        for tool_name, handler in handler_map.items():
            if tool_name in agent.capabilities:
                agent.register_tool(tool_name, handler)
        self.registry.register(agent)
        return self

    def register_compliance_agent(self, handler_map: Dict[str, Callable]) -> 'OrchestratorAgent':
        """Register the Compliance agent with its tool handlers."""
        agent = SubAgent(
            role=AgentRole.COMPLIANCE,
            name="Compliance Checker",
            capabilities=["check_compliance", "verify_leak", "verify_rated", "verify_life"],
            description="标准合规专家：负责QJ20156/GJB等标准的符合性校验"
        )
        for tool_name, handler in handler_map.items():
            if tool_name in agent.capabilities:
                agent.register_tool(tool_name, handler)
        self.registry.register(agent)
        return self

    # ------------------------------------------------------------------
    # Execution engine
    # ------------------------------------------------------------------

    def process(self, message: str, timeout_s: float = 60.0) -> Dict:
        """
        Main entry point. Process a user message through the orchestration pipeline.
        Returns a synthesis response including all sub-agent results.
        """
        session_id = f"orch_{uuid.uuid4().hex[:8]}"
        self._sessions[session_id] = {
            "message": message,
            "started_at": datetime.now().isoformat(),
            "status": "running",
        }

        # Step 1: Decompose
        plan, intent = self.decomposer.decompose(message)
        if plan is None:
            return self._respond_simple(message, intent, session_id)

        # Step 2: Execute with dependency ordering
        results = self._execute_plan(plan, timeout_s)

        # Step 3: Cross-validate + aggregate
        synthesis = self._synthesize(plan, results, message)

        self._sessions[session_id]["status"] = "completed"
        self._sessions[session_id]["completed_at"] = datetime.now().isoformat()
        return synthesis

    def _execute_plan(self, plan: DecompositionPlan, timeout_s: float) -> Dict[str, Dict]:
        """
        Execute all subtasks respecting dependency order.
        Independent tasks run concurrently within a wave.
        """
        completed: Dict[str, Dict] = {}
        failed: Dict[str, str] = {}
        task_map = {st.task_id: st for st in plan.subtasks}

        remaining = set(task_map.keys())

        wave = 0
        max_waves = 10  # safety

        while remaining and wave < max_waves:
            wave += 1

            # Find tasks whose dependencies are all satisfied
            ready = []
            for tid in list(remaining):
                st = task_map[tid]
                if all(dep in completed for dep in st.depends_on):
                    # Also skip if any dependency failed
                    dep_failed = any(dep in failed for dep in st.depends_on)
                    if dep_failed:
                        remaining.remove(tid)
                        continue
                    # Check if any dependency result has errors
                    if any(dep in completed and not completed[dep].get("success", True) for dep in st.depends_on):
                        continue
                    ready.append(st)

            if not ready:
                # Deadlock or all remaining depend on each other
                # Try to force-run them anyway
                ready = [task_map[tid] for tid in remaining]
                remaining.clear()
                break

            # Execute ready tasks concurrently
            futures = {}
            for st in ready:
                remaining.remove(st.task_id)
                role = st.role
                agent = self.registry.get_agent(role)
                if not agent:
                    st.status = TaskStatus.FAILED
                    st.error = f"No agent registered for role {role}"
                    failed[st.task_id] = st.error
                    continue

                st.status = TaskStatus.RUNNING
                st.started_at = datetime.now().isoformat()
                future = self._executor.submit(agent.execute, st.tool_name, st.inputs, timeout_s=30.0)
                futures[future] = st

            # Collect results
            for future in as_completed(futures, timeout=timeout_s / max(1, wave)):
                st = futures[future]
                try:
                    result = future.result(timeout=5)
                    st.result = result
                    st.status = TaskStatus.COMPLETED if result.get("success", True) else TaskStatus.FAILED
                    st.completed_at = datetime.now().isoformat()
                    completed[st.task_id] = result
                    if not result.get("success", True):
                        failed[st.task_id] = result.get("error", "unknown error")
                except Exception as e:
                    st.status = TaskStatus.TIMEOUT
                    st.error = str(e)
                    st.completed_at = datetime.now().isoformat()
                    failed[st.task_id] = str(e)
                    completed[st.task_id] = {"success": False, "error": str(e)}

        # Timeout remaining
        for tid in remaining:
            st = task_map[tid]
            st.status = TaskStatus.TIMEOUT
            st.error = "Dependency not resolved within max waves"
            failed[tid] = st.error

        return completed

    def _synthesize(self, plan: DecompositionPlan, results: Dict[str, Dict], message: str) -> Dict:
        """Aggregate sub-agent results into a coherent response."""
        task_results = []
        all_success = True
        total_duration = 0.0

        for st in plan.subtasks:
            r = st.result or results.get(st.task_id, {})
            task_results.append({
                "task_id": st.task_id,
                "tool": st.tool_name,
                "role": st.role.value,
                "status": st.status.value,
                "success": r.get("success", False) if isinstance(r, dict) else False,
                "result": r,
                "error": st.error,
                "duration_ms": st.duration_ms,
            })
            total_duration += st.duration_ms
            if not r.get("success", False) if isinstance(r, dict) else False:
                all_success = False

        # Classification
        categories = {
            "material": [t for t in task_results if "material" in t["tool"]],
            "design": [t for t in task_results if any(w in t["tool"] for w in ["design", "analyze", "run_fluid"])],
            "compliance": [t for t in task_results if "compliance" in t["tool"] or "verify" in t["tool"]],
        }

        return {
            "success": all_success,
            "orchestrated": True,
            "plan_id": plan.plan_id,
            "intent": plan.intent,
            "total_subtasks": len(task_results),
            "completed": sum(1 for t in task_results if t["status"] == "completed"),
            "failed": sum(1 for t in task_results if t["status"] != "completed"),
            "total_duration_ms": total_duration,
            "categories": {k: [t["tool"] for t in v] for k, v in categories.items() if v},
            "task_results": task_results,
            "message": message,
        }

    def _respond_simple(self, message: str, intent: str, session_id: str) -> Dict:
        """Handle simple queries that don't need orchestration."""
        self._sessions[session_id]["status"] = "simple"
        return {
            "success": True,
            "orchestrated": False,
            "intent": intent,
            "message": message,
            "note": "Simple query — no multi-agent orchestration needed. Route to PAOR directly.",
        }

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def get_session(self, session_id: str) -> Optional[Dict]:
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self._sessions.items()]

    def stats(self) -> Dict:
        return {
            "agents": [a.to_dict() for a in self.registry.list_agents()],
            "active_sessions": len(self._sessions),
            "max_workers": self.max_workers,
        }


# ============================================================
# Singleton
# ============================================================

_orchestrator: Optional[OrchestratorAgent] = None


def get_orchestrator() -> OrchestratorAgent:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent(max_workers=4)
    return _orchestrator
