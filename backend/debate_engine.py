"""
Multi-Agent Debate Engine with Voting Consensus
===============================================
Enables structured multi-round debates between specialized AI agents
with weighted voting and consensus detection for design decisions.

Architecture:
- DebateSession: Manages one debate (topic, participants, rounds)
- DebateAgent: Wraps an agent with its stance, arguments, and confidence
- VotingMechanism: Weighted voting with consensus detection
- DebateEngine: Orchestrates full debate lifecycle
"""

import json
import time
import math
import hashlib
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ============================================================
# Data Models
# ============================================================

class DebatePhase(Enum):
    SETUP = "setup"
    OPENING = "opening"
    REBUTTAL = "rebuttal"
    DELIBERATION = "deliberation"
    VOTING = "voting"
    CONSENSUS = "consensus"
    CLOSED = "closed"


class VoteOption(Enum):
    SUPPORT = "support"
    OPPOSE = "oppose"
    ABSTAIN = "abstain"
    CONDITIONAL_SUPPORT = "conditional_support"


@dataclass
class Argument:
    agent_name: str
    round_num: int
    content: str
    references: list = field(default_factory=list)
    confidence: float = 0.5
    timestamp: float = field(default_factory=time.time)


@dataclass
class Vote:
    agent_name: str
    option: VoteOption
    rationale: str = ""
    conditions: list = field(default_factory=list)
    weight: float = 1.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class ConsensusResult:
    achieved: bool
    level: str
    support_ratio: float
    total_weight: float
    majority_option: Optional[VoteOption] = None
    dissenting_agents: list = field(default_factory=list)
    summary: str = ""


# ============================================================
# DebateAgent
# ============================================================

class DebateAgent:
    """Wraps a domain agent for debate participation."""

    def __init__(self, name, expertise, personality="analytical",
                 default_stance="neutral", weight=1.0):
        self.name = name
        self.expertise = expertise
        self.personality = personality
        self.default_stance = default_stance
        self.weight = weight
        self.arguments = []
        self.current_stance = default_stance

    def to_dict(self):
        return {
            "name": self.name,
            "expertise": self.expertise,
            "personality": self.personality,
            "weight": self.weight,
            "current_stance": self.current_stance,
            "argument_count": len(self.arguments)
        }


# ============================================================
# VotingMechanism
# ============================================================

class VotingMechanism:
    """Weighted voting with multiple consensus detection strategies."""

    @staticmethod
    def tally_votes(votes):
        counts = {opt.value: 0.0 for opt in VoteOption}
        total = 0.0
        for v in votes:
            counts[v.option.value] += v.weight
            total += v.weight
        if total > 0:
            for k in counts:
                counts[k] = counts[k] / total
        return {"absolute": counts, "total_weight": total}

    @staticmethod
    def detect_consensus(votes, threshold=0.6):
        tally = VotingMechanism.tally_votes(votes)
        abs_counts = tally["absolute"]
        total = tally["total_weight"]

        if total == 0:
            return ConsensusResult(achieved=False, level="none",
                                   support_ratio=0.0, total_weight=0.0,
                                   summary="No votes cast.")

        support_ratio = abs_counts.get("support", 0) + abs_counts.get("conditional_support", 0)

        if support_ratio >= 0.85:
            level, achieved = "strong", True
        elif support_ratio >= 0.70:
            level, achieved = "moderate", True
        elif support_ratio >= threshold:
            level, achieved = "weak", True
        else:
            level, achieved = "none", False

        dissenting = [
            v.agent_name for v in votes
            if v.option in (VoteOption.OPPOSE, VoteOption.ABSTAIN)
        ]

        majority_opt_key = max(abs_counts, key=abs_counts.get)
        try:
            majority_opt = VoteOption(majority_opt_key)
        except ValueError:
            majority_opt = None

        summary = VotingMechanism._build_summary(level, support_ratio, dissenting)

        return ConsensusResult(
            achieved=achieved, level=level, support_ratio=support_ratio,
            total_weight=total, majority_option=majority_opt,
            dissenting_agents=dissenting, summary=summary
        )

    @staticmethod
    def _build_summary(level, ratio, dissenting):
        pct = int(ratio * 100)
        if level == "strong":
            msg = "Strong consensus ({}% support). ".format(pct)
            if dissenting:
                msg += "Minor dissenting: {}.".format(", ".join(dissenting))
            else:
                msg += "All agents aligned."
        elif level == "moderate":
            msg = "Moderate consensus ({}% support). ".format(pct)
            msg += "Dissenting: {}.".format(", ".join(dissenting)) if dissenting else ""
        elif level == "weak":
            msg = "Weak consensus ({}% support). ".format(pct)
            msg += "Significant opposition: {}. Further deliberation recommended.".format(", ".join(dissenting))
        else:
            msg = "No consensus ({}% support). ".format(pct)
            msg += "Deadlock detected. Consider external arbitration or scope narrowing."
        return msg


# ============================================================
# Preset Agent Definitions
# ============================================================

PRESET_AGENTS = {
    "design_engineer": {
        "name": "Design Engineer",
        "expertise": "Valve structural design, material selection, FEA",
        "personality": "pragmatic",
        "default_stance": "neutral",
        "weight": 1.2
    },
    "compliance_officer": {
        "name": "Compliance Officer",
        "expertise": "QJ 20156, HB 6455, ISO standards compliance",
        "personality": "cautious",
        "default_stance": "neutral",
        "weight": 1.0
    },
    "materials_scientist": {
        "name": "Materials Scientist",
        "expertise": "Aerospace materials, fatigue, corrosion, thermal properties",
        "personality": "analytical",
        "default_stance": "neutral",
        "weight": 1.1
    },
    "simulation_analyst": {
        "name": "Simulation Analyst",
        "expertise": "CFD, thermal analysis, structural FEA simulation",
        "personality": "analytical",
        "default_stance": "neutral",
        "weight": 1.0
    },
    "systems_engineer": {
        "name": "Systems Engineer",
        "expertise": "System integration, requirements flow-down, trade studies",
        "personality": "pragmatic",
        "default_stance": "neutral",
        "weight": 1.15
    },
    "reliability_engineer": {
        "name": "Reliability Engineer",
        "expertise": "FMECA, reliability prediction, lifetime analysis",
        "personality": "cautious",
        "default_stance": "neutral",
        "weight": 1.05
    },
    "manufacturing_engineer": {
        "name": "Manufacturing Engineer",
        "expertise": "DFM, machining, additive manufacturing, cost estimation",
        "personality": "pragmatic",
        "default_stance": "neutral",
        "weight": 0.9
    },
    "innovation_architect": {
        "name": "Innovation Architect",
        "expertise": "Novel mechanisms, topology optimization, emerging technologies",
        "personality": "innovative",
        "default_stance": "neutral",
        "weight": 0.85
    }
}

# Debate templates with default agent rosters
DEBATE_TEMPLATES = {
    "valve_design_decision": {
        "name": "Valve Design Decision",
        "description": "Evaluate design alternatives for a valve configuration",
        "default_agents": ["design_engineer", "simulation_analyst", "systems_engineer",
                          "manufacturing_engineer", "innovation_architect"],
        "topics": [
            "Poppet vs. ball sealing mechanism for cryogenic LOX valve",
            "Direct-acting vs. pilot-operated solenoid for 30MPa helium valve",
            "Additive manufactured vs. traditionally machined valve body for satellite propulsion"
        ]
    },
    "material_selection": {
        "name": "Material Selection",
        "description": "Debate optimal material choices for given design constraints",
        "default_agents": ["design_engineer", "materials_scientist", "compliance_officer",
                          "manufacturing_engineer", "reliability_engineer"],
        "topics": [
            "Inconel 718 vs. Ti-6Al-4V for high-temperature oxidizer valve body",
            "PTFE vs. PCTFE vs. PEEK for cryogenic seal applications",
            "440C vs. 17-4PH for high-pressure hydraulic valve spools"
        ]
    },
    "safety_margin_debate": {
        "name": "Safety Margin Debate",
        "description": "Discuss appropriate safety factors for critical components",
        "default_agents": ["design_engineer", "compliance_officer", "reliability_engineer",
                          "systems_engineer", "simulation_analyst"],
        "topics": [
            "Proof factor: QJ 20156 minimum 1.5x vs. desired 2.0x for manned mission application",
            "Burst factor: 2.0x minimum vs. 3.0x for composite overwrapped pressure vessels",
            "Fatigue life margin: 4x required life vs. 10x for single-use launch vehicle components"
        ]
    },
    "compliance_interpretation": {
        "name": "Compliance Interpretation",
        "description": "Resolve conflicting standard requirements or interpretation disagreements",
        "default_agents": ["compliance_officer", "systems_engineer", "design_engineer",
                          "reliability_engineer"],
        "topics": [
            "QJ 20156 thermal-vacuum cycle requirement: 6 cycles sufficient vs. 10 cycles conservative",
            "HB 6455 check valve cracking pressure tolerance interpretation for cryogenic service",
            "Conflict between weight optimization targets and ISO 3601 O-ring groove design constraints"
        ]
    }
}


# ============================================================
# DebateEngine
# ============================================================

class DebateEngine:
    """Orchestrates multi-round agent debates with voting consensus."""

    def __init__(self, max_rounds=5, consensus_threshold=0.6):
        self.max_rounds = max_rounds
        self.consensus_threshold = consensus_threshold
        self.sessions = {}
        self._voting = VotingMechanism()

    # -- Session Management --

    def create_session(self, topic, description="", design_params=None,
                       agent_names=None, custom_agents=None):
        session_id = self._make_id(topic)
        agents = {}
        names = agent_names or list(PRESET_AGENTS.keys())[:5]

        for name in names:
            if name in PRESET_AGENTS:
                p = PRESET_AGENTS[name]
                agents[name] = DebateAgent(
                    name=p["name"], expertise=p["expertise"],
                    personality=p["personality"],
                    default_stance=p["default_stance"],
                    weight=p["weight"]
                )

        if custom_agents:
            for ca in custom_agents:
                key = ca.get("name", "").lower().replace(" ", "_")
                if key and key not in agents:
                    agents[key] = DebateAgent(
                        name=ca["name"],
                        expertise=ca.get("expertise", "General"),
                        personality=ca.get("personality", "analytical"),
                        weight=ca.get("weight", 1.0)
                    )

        session = {
            "id": session_id,
            "topic": topic,
            "description": description,
            "design_params": design_params or {},
            "agents": agents,
            "rounds": [],
            "votes": [],
            "phase": DebatePhase.SETUP.value,
            "consensus": None,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        self.sessions[session_id] = session
        return self._summary(session)

    def start_debate(self, session_id):
        session = self._get(session_id)
        session["phase"] = DebatePhase.OPENING.value
        session["updated_at"] = time.time()
        return self._summary(session)

    # -- Argument Submission --

    def submit_argument(self, session_id, agent_key, content,
                        references=None, confidence=0.7):
        session = self._get(session_id)

        if agent_key not in session["agents"]:
            return {"error": "Agent '{}' not in this debate.".format(agent_key)}

        if session["phase"] in (DebatePhase.CONSENSUS.value, DebatePhase.CLOSED.value):
            return {"error": "Debate is in {} phase.".format(session["phase"])}

        agent = session["agents"][agent_key]

        # Create new round if needed
        if not session["rounds"] or \
           len(session["rounds"][-1].get("arguments", [])) >= len(session["agents"]):
            session["rounds"].append({
                "number": len(session["rounds"]) + 1,
                "arguments": [],
                "phase": session["phase"]
            })

        arg = Argument(
            agent_name=agent.name,
            round_num=len(session["rounds"]),
            content=content,
            references=references or [],
            confidence=confidence
        )
        agent.arguments.append(arg)
        session["rounds"][-1]["arguments"].append({
            "agent": agent.name,
            "agent_key": agent_key,
            "content": content,
            "references": references or [],
            "confidence": confidence,
            "timestamp": arg.timestamp
        })
        session["updated_at"] = time.time()
        self._auto_advance(session)
        return self._summary(session)

    # -- Voting --

    def cast_vote(self, session_id, agent_key, option, rationale="", conditions=None):
        session = self._get(session_id)

        if agent_key not in session["agents"]:
            return {"error": "Agent '{}' not in debate.".format(agent_key)}

        if session["phase"] not in (DebatePhase.VOTING.value, DebatePhase.DELIBERATION.value):
            return {"error": "Voting not open. Phase: {}.".format(session["phase"])}

        # Remove previous vote from same agent
        agent_name = session["agents"][agent_key].name
        session["votes"] = [v for v in session["votes"] if v.agent_name != agent_name]

        try:
            vote_opt = VoteOption(option)
        except ValueError:
            return {"error": "Invalid option: {}. Valid: {}.".format(
                option, [o.value for o in VoteOption])}

        vote = Vote(
            agent_name=agent_name, option=vote_opt,
            rationale=rationale, conditions=conditions or [],
            weight=session["agents"][agent_key].weight
        )
        session["votes"].append(vote)
        session["updated_at"] = time.time()

        # Check if all voted
        if len(session["votes"]) >= len(session["agents"]):
            consensus = self._voting.detect_consensus(
                session["votes"], self.consensus_threshold)
            session["consensus"] = {
                "achieved": consensus.achieved,
                "level": consensus.level,
                "support_ratio": consensus.support_ratio,
                "summary": consensus.summary,
                "dissenting_agents": consensus.dissenting_agents
            }
            if consensus.achieved:
                session["phase"] = DebatePhase.CONSENSUS.value
            elif len(session["rounds"]) < self.max_rounds:
                session["phase"] = DebatePhase.DELIBERATION.value
                session["rounds"].append({
                    "number": len(session["rounds"]) + 1,
                    "arguments": [],
                    "phase": DebatePhase.DELIBERATION.value
                })

        return self._summary(session)

    def force_phase(self, session_id, phase):
        session = self._get(session_id)
        try:
            session["phase"] = DebatePhase(phase).value
        except ValueError:
            return {"error": "Invalid phase: {}.".format(phase)}
        session["updated_at"] = time.time()
        return self._summary(session)

    # -- Query --

    def get_session(self, session_id):
        return self._summary(self._get(session_id))

    def list_sessions(self):
        return [{
            "id": sid, "topic": s["topic"], "phase": s["phase"],
            "agent_count": len(s["agents"]), "rounds": len(s["rounds"]),
            "votes_cast": len(s["votes"]),
            "consensus": s["consensus"]["level"] if s.get("consensus") else None,
            "created_at": s["created_at"]
        } for sid, s in self.sessions.items()]

    def close_session(self, session_id):
        session = self._get(session_id)
        session["phase"] = DebatePhase.CLOSED.value
        session["updated_at"] = time.time()
        session["final_report"] = self._build_report(session)
        return self._summary(session)

    def get_templates(self):
        return {k: {
            "name": v["name"], "description": v["description"],
            "default_agents": v["default_agents"], "topics": v["topics"]
        } for k, v in DEBATE_TEMPLATES.items()}

    # -- Internal --

    def _get(self, session_id):
        if session_id not in self.sessions:
            raise ValueError("Session '{}' not found.".format(session_id))
        return self.sessions[session_id]

    def _auto_advance(self, session):
        rounds = len(session["rounds"])
        phase = session["phase"]
        if phase == DebatePhase.OPENING.value and rounds >= 1:
            session["phase"] = DebatePhase.REBUTTAL.value
        elif phase == DebatePhase.REBUTTAL.value and rounds >= 2:
            session["phase"] = DebatePhase.DELIBERATION.value
        elif phase == DebatePhase.DELIBERATION.value and rounds >= 3:
            session["phase"] = DebatePhase.VOTING.value

    def _summary(self, session):
        result = {
            "id": session["id"], "topic": session["topic"],
            "description": session["description"],
            "design_params": session["design_params"],
            "phase": session["phase"],
            "agents": {k: a.to_dict() for k, a in session["agents"].items()},
            "rounds": [{
                "number": r["number"],
                "phase": r.get("phase", ""),
                "arguments": r["arguments"]
            } for r in session["rounds"]],
            "votes": [{
                "agent": v.agent_name, "option": v.option.value,
                "rationale": v.rationale, "conditions": v.conditions,
                "weight": v.weight
            } for v in session["votes"]],
            "consensus": session.get("consensus"),
            "created_at": session["created_at"],
            "updated_at": session["updated_at"]
        }
        if session.get("final_report"):
            result["final_report"] = session["final_report"]
        return result

    def _build_report(self, session):
        all_refs = []
        for r in session["rounds"]:
            for arg in r["arguments"]:
                all_refs.extend(arg.get("references", []))

        from collections import Counter
        ref_counts = Counter(all_refs).most_common(5)

        return {
            "topic": session["topic"],
            "total_rounds": len(session["rounds"]),
            "total_arguments": sum(len(r["arguments"]) for r in session["rounds"]),
            "total_votes": len(session["votes"]),
            "consensus": session.get("consensus"),
            "participants": [a.to_dict() for a in session["agents"].values()],
            "key_references": [{"term": r[0], "count": r[1]} for r in ref_counts],
            "duration_seconds": time.time() - session["created_at"]
        }

    @staticmethod
    def _make_id(topic):
        raw = "{}:{}".format(topic, time.time())
        return hashlib.md5(raw.encode()).hexdigest()[:12]


# ============================================================
# Singleton
# ============================================================

debate_engine = DebateEngine(max_rounds=5, consensus_threshold=0.6)
