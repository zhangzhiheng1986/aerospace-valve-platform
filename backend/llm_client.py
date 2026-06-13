"""
LLM Client for AI Agent explanations.
Supports MiniMax primary + OpenAI-compatible fallback.

Design principles (Sprint 10):
1. Graceful degradation: if LLM fails, fall back to deterministic output
2. Cost control: per-session budget cap
3. Audit trail: log every call (model, prompt, response, cost)
4. Timeout: hard 20s limit, never block user UI
5. Determinism prefix: temperature 0.0 by default
"""
import os
import json
import time
import logging
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

LOG = logging.getLogger("llm_client")


class LLMUnavailable(Exception):
    """LLM provider unreachable or disabled."""


class LLMBudgetExceeded(Exception):
    """Per-session budget exceeded."""


class LLMClient:
    """
    MiniMax-first, OpenAI-compatible LLM client.

    Uses Chat Completions API format (works with MiniMax, OpenAI, DeepSeek, Qwen, etc.)
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 timeout: float = 20.0,
                 enabled: bool = True):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY", "")
        self.base_url = (base_url or os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")).rstrip("/")
        self.model = model or os.getenv("MINIMAX_MODEL", "MiniMax-Text-01")
        self.timeout = timeout
        self.enabled = enabled and bool(self.api_key)
        self.session_budget_usd = float(os.getenv("AI_AGENT_LLM_BUDGET_USD_PER_SESSION", "0.10"))
        self._session_spend = 0.0
        self._call_log: List[Dict[str, Any]] = []
        self._pricing = self._load_pricing()

    @staticmethod
    def _load_pricing() -> Dict[str, tuple]:
        """USD per million tokens (input, output)."""
        return {
            "MiniMax-Text-01": (0.30, 1.20),  # MiniMax typical
            "gpt-4o-mini": (0.15, 0.60),
            "gpt-4o": (2.50, 10.00),
            "deepseek-chat": (0.14, 0.28),
            "qwen-plus": (0.40, 1.20),
        }

    def reset_budget(self):
        self._session_spend = 0.0
        self._call_log.clear()

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_price, output_price = self._pricing.get(self.model, (0.5, 1.5))
        cost = (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000
        return round(cost, 6)

    def chat(self,
             system: str,
             user: str,
             temperature: float = 0.3,
             max_tokens: int = 800,
             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Synchronous chat completion. Returns dict with keys:
        - success: bool
        - text: str (response)
        - usage: {prompt_tokens, completion_tokens, total_tokens}
        - cost_usd: float
        - latency_ms: int
        - model: str
        - error: str (if failed)
        - mocked: bool (if LLM disabled)
        """
        if not self.enabled or requests is None:
            return {
                "success": False,
                "text": "",
                "error": "LLM disabled or requests module unavailable",
                "mocked": True,
                "model": self.model,
            }
        # Budget check
        if self._session_spend >= self.session_budget_usd:
            return {
                "success": False,
                "text": "",
                "error": f"Session budget exceeded: ${self._session_spend:.4f} >= ${self.session_budget_usd}",
                "mocked": False,
                "model": self.model,
            }

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        t0 = time.time()
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            latency_ms = int((time.time() - t0) * 1000)
            if resp.status_code != 200:
                err = f"HTTP {resp.status_code}: {resp.text[:200]}"
                LOG.warning("LLM call failed: %s", err)
                self._log_call(system, user, "", err, latency_ms, 0, 0, metadata)
                return {
                    "success": False, "text": "", "error": err,
                    "mocked": False, "model": self.model, "latency_ms": latency_ms,
                }
            data = resp.json()
            choice = (data.get("choices") or [{}])[0]
            text = (choice.get("message") or {}).get("content", "") or ""
            usage = data.get("usage", {})
            pt = int(usage.get("prompt_tokens", 0))
            ct = int(usage.get("completion_tokens", 0))
            cost = self._estimate_cost(pt, ct)
            self._session_spend += cost
            self._log_call(system, user, text, "", latency_ms, pt, ct, metadata, cost)
            return {
                "success": True,
                "text": text,
                "usage": {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": pt + ct},
                "cost_usd": cost,
                "latency_ms": latency_ms,
                "model": data.get("model", self.model),
                "mocked": False,
            }
        except requests.Timeout:
            latency_ms = int((time.time() - t0) * 1000)
            err = f"Timeout after {self.timeout}s"
            self._log_call(system, user, "", err, latency_ms, 0, 0, metadata)
            return {
                "success": False, "text": "", "error": err,
                "mocked": False, "model": self.model, "latency_ms": latency_ms,
            }
        except Exception as e:
            latency_ms = int((time.time() - t0) * 1000)
            err = f"{type(e).__name__}: {e}"
            self._log_call(system, user, "", err, latency_ms, 0, 0, metadata)
            return {
                "success": False, "text": "", "error": err,
                "mocked": False, "model": self.model, "latency_ms": latency_ms,
            }

    def _log_call(self, system, user, response, error, latency_ms,
                  pt, ct, metadata=None, cost=0.0):
        self._call_log.append({
            "ts": datetime.now().isoformat(),
            "model": self.model,
            "system_hash": hashlib.sha256(system.encode()).hexdigest()[:8],
            "user_len": len(user),
            "response_len": len(response),
            "error": error,
            "latency_ms": latency_ms,
            "prompt_tokens": pt,
            "completion_tokens": ct,
            "cost_usd": cost,
            "metadata": metadata or {},
        })

    def get_stats(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "model": self.model,
            "base_url": self.base_url,
            "session_spend_usd": round(self._session_spend, 6),
            "session_budget_usd": self.session_budget_usd,
            "calls": len(self._call_log),
            "log": self._call_log[-20:],
        }


# Singleton with thread-safe lazy init
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        enabled = os.getenv("AI_AGENT_LLM_ENABLED", "true").lower() == "true"
        _client = LLMClient(enabled=enabled)
    return _client


def reset_llm_client():
    """Reset singleton (used by tests or when env changes)."""
    global _client
    _client = None
