"""
LLM-powered engineering result explainer.
Sprint 10: turn raw numbers (flow_area=15.33, Cv=0.32) into human-readable narrative.

Design: this layer NEVER generates numbers. It only describes the deterministic
output of the engineering modules. This is the safe way to use LLM in
safety-critical aerospace design.
"""
import json
import os
from typing import Dict, Any, Optional, List

from llm_client import get_llm_client


# System prompt is critical: lock down the LLM's role.
SYSTEM_PROMPT_BASE = """你是「张老师航空航天阀门研发平台」的工程结果解读助手。

## 你的角色
- 你**只负责解释**已经计算好的工程结果(由确定性 Python 模块产出)
- 你**绝对不能**编造、修改、质疑工具返回的数值
- 你的语气是**科普作家面向工程师**——专业但通俗,有比喻,偶尔金句

## 严格约束
1. 所有数字必须从"工具结果"中直接引用,不能推算、不能近似
2. 如果工具结果是失败的(error/skipped),你**只**能解释原因 + 给出 1-2 个备选方案
3. 你不能用"我认为""我觉得"等主观表达,改用"根据 X 标准/工况"等客观措辞
4. 输出长度 150-400 字,中文,可用 1-2 个 Markdown 粗体强调关键参数
5. 每次输出结尾,标注 **[基于 MiniMax 解读,数据由工程模块验证]**

## 输出模板
```
### 设计要点
- 关键参数 1: <值 + 单位 + 含义>
- 关键参数 2: <值 + 单位 + 含义>
- ...

### 设计取舍
<为什么选这个方案, 1-2 句话>

### 注意事项
<使用中需要留意的工程细节, 1-2 条>
```

严格遵守,不要自由发挥。"""


def build_explanation_prompt(tool_name: str, tool_result: Dict[str, Any],
                              user_query: str) -> str:
    """
    Build user prompt from deterministic tool output.
    Keep it compact to control token cost.
    """
    # Strip verbose internal fields
    clean = {k: v for k, v in tool_result.items()
             if k not in ("_tool", "_extraction_confidence", "_auto_selected",
                          "formulas", "raw_input", "input")}
    return f"""## 用户查询
{user_query}

## 工具调用
工具: `{tool_name}`
原始结果(JSON, 已脱敏):
```json
{json.dumps(clean, ensure_ascii=False, indent=2, default=str)[:3000]}
```

请按模板解读。如果结果包含 success=false, 请改用「诊断 + 建议」模式。"""


def explain_result(tool_name: str, tool_result: Dict[str, Any],
                   user_query: str, max_retries: int = 0) -> Dict[str, Any]:
    """
    Get LLM explanation of a deterministic tool result.
    Falls back gracefully if LLM unavailable.

    Returns dict with:
    - success: bool
    - explanation: str
    - source: 'llm' | 'fallback' | 'passthrough'
    - cost_usd: float
    - latency_ms: int
    """
    client = get_llm_client()
    if not client.enabled:
        return _deterministic_summary(tool_name, tool_result, user_query)

    user_prompt = build_explanation_prompt(tool_name, tool_result, user_query)
    result = client.chat(
        system=SYSTEM_PROMPT_BASE,
        user=user_prompt,
        temperature=0.3,
        max_tokens=600,
        metadata={"tool": tool_name, "user_query_len": len(user_query)},
    )

    if result["success"] and result["text"].strip():
        return {
            "success": True,
            "explanation": result["text"].strip(),
            "source": "llm",
            "cost_usd": result.get("cost_usd", 0.0),
            "latency_ms": result.get("latency_ms", 0),
            "model": result.get("model", "?"),
        }
    # Graceful fallback
    fallback = _deterministic_summary(tool_name, tool_result, user_query)
    fallback["llm_error"] = result.get("error", "unknown")
    return fallback


def _deterministic_summary(tool_name: str, result: Dict[str, Any],
                            user_query: str) -> Dict[str, Any]:
    """Fallback explanation when LLM is unavailable."""
    if not result.get("success", False):
        err = result.get("error", "unknown")
        return {
            "success": True,
            "explanation": f"### 诊断\n工具 `{tool_name}` 执行失败: `{err}`。\n\n"
                          f"### 建议\n请检查输入参数,或换一个等效材料/工况重试。",
            "source": "fallback",
            "cost_usd": 0.0,
            "latency_ms": 0,
            "model": "deterministic-fallback",
        }
    # Pick top 3 numeric keys for at-a-glance summary
    nums = []
    for k, v in result.items():
        if isinstance(v, (int, float)) and v != 0 and not k.startswith("_"):
            nums.append((k, v))
        elif isinstance(v, dict):
            for sk, sv in v.items():
                if isinstance(sv, (int, float)) and sv != 0 and not sk.startswith("_"):
                    nums.append((f"{k}.{sk}", sv))
    nums = nums[:5]
    if not nums:
        return {
            "success": True,
            "explanation": f"### 完成\n工具 `{tool_name}` 执行成功,具体结果请见上方面板。",
            "source": "passthrough",
            "cost_usd": 0.0,
            "latency_ms": 0,
            "model": "deterministic-fallback",
        }
    lines = ["### 关键参数 (LLM 暂不可用,以下是自动摘要)"]
    for k, v in nums:
        if isinstance(v, float):
            lines.append(f"- **{k}** = `{v:.4g}`")
        else:
            lines.append(f"- **{k}** = `{v}`")
    return {
        "success": True,
        "explanation": "\n".join(lines),
        "source": "fallback",
        "cost_usd": 0.0,
        "latency_ms": 0,
        "model": "deterministic-fallback",
    }


def explain_orchestration(synthesis: Dict[str, Any],
                          user_query: str) -> List[Dict[str, Any]]:
    """
    Generate explanations for all subtask results in a synthesis.
    Returns list of {tool, explanation, source, cost_usd} dicts.
    """
    out = []
    for tr in synthesis.get("task_results", []):
        tool = tr.get("tool", "?")
        result = tr.get("result", {})
        if not isinstance(result, dict):
            result = {"success": False, "error": "result not a dict"}
        exp = explain_result(tool, result, user_query)
        exp["tool"] = tool
        exp["role"] = tr.get("role", "?")
        out.append(exp)
    return out
