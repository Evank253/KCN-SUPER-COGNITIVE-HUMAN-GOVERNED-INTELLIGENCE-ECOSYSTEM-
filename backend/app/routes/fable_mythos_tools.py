"""
KCN tools aligned with Claude Fable 5 / Mythos 5 *safe* control-plane features.

Fable 5 / Mythos 5 supported features (Anthropic docs):
  Effort, task budgets, memory tool, code execution, programmatic tool calling,
  context editing / tool-result clearing, compaction, vision, adaptive thinking,
  sub-agent style long-horizon work, refusal/fallback handling.

We implement the *product surface* under human governance.
We do NOT implement unrestricted offensive cyber capabilities (Mythos-only domains).
"""

from __future__ import annotations

import ast
import hashlib
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent")

_TRACK: list[dict[str, Any]] = []
_MEMORY: dict[str, dict[str, Any]] = {}  # session_id -> {key: value}
_BUDGETS: dict[str, dict[str, Any]] = {}
_SUBAGENTS: dict[str, dict[str, Any]] = {}


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(phase: str, status_s: str, detail: str, **extra: Any) -> dict[str, Any]:
    e = {"ts": _ts(), "phase": phase, "status": status_s, "detail": detail, **extra}
    _TRACK.append(e)
    logger.info("agent.track %s", e)
    return e


# ---- Schemas ----------------------------------------------------------------

class MemoryOp(BaseModel):
    session_id: str
    op: Literal["set", "get", "list", "delete", "clear"]
    key: str | None = None
    value: Any = None


class CodeExecRequest(BaseModel):
    code: str = Field(..., max_length=20_000)
    language: Literal["python"] = "python"
    sandboxed: bool = True
    network_enabled: bool = False
    human_approved: bool = False


class TaskBudget(BaseModel):
    session_id: str
    max_steps: int = Field(default=50, ge=1, le=10_000)
    max_tokens_est: int = Field(default=100_000, ge=100)
    max_wall_minutes: int = Field(default=60, ge=1, le=60 * 24 * 7)


class CompactRequest(BaseModel):
    session_id: str
    messages: list[dict[str, Any]]
    keep_last: int = Field(default=8, ge=1, le=200)


class ContextEditRequest(BaseModel):
    session_id: str
    messages: list[dict[str, Any]]
    clear_tool_results: bool = True
    clear_before_index: int | None = None


class SubAgentRequest(BaseModel):
    parent_session_id: str
    goal: str = Field(..., min_length=1, max_length=4000)
    role: Literal["researcher", "coder", "reviewer", "tester"] = "coder"


class SelfVerifyRequest(BaseModel):
    artifact: str = Field(..., min_length=1)
    criteria: list[str] = Field(default_factory=lambda: ["non_empty", "no_todo", "has_structure"])


class FallbackPolicy(BaseModel):
    """Fable-style refusal → safer model path (we map to local governed reply)."""

    risk_domains: list[str] = Field(
        default_factory=lambda: ["cyber_offensive", "bio_weapon", "model_distill"]
    )
    fallback_model: str = "kcn-safe-fallback"
    on_refusal: Literal["fallback", "block", "human"] = "human"


# ---- Catalog ----------------------------------------------------------------

FABLE_STYLE_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "memory",
            "description": "Persistent session memory (Fable/Mythos memory tool analogue).",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "op": {"type": "string", "enum": ["set", "get", "list", "delete", "clear"]},
                    "key": {"type": "string"},
                    "value": {},
                },
                "required": ["session_id", "op"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "code_execution",
            "description": "Sandboxed Python exec — requires sandbox=on, network=off (Fable code execution).",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "sandboxed": {"type": "boolean"},
                    "network_enabled": {"type": "boolean"},
                    "human_approved": {"type": "boolean"},
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_budget",
            "description": "Set/check task budgets for long-horizon agent runs (Fable task budgets).",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "max_steps": {"type": "integer"},
                    "max_tokens_est": {"type": "integer"},
                    "max_wall_minutes": {"type": "integer"},
                },
                "required": ["session_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compact_context",
            "description": "Compact long message history; keep recent turns (Fable compaction).",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "messages": {"type": "array"},
                    "keep_last": {"type": "integer"},
                },
                "required": ["session_id", "messages"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "context_edit",
            "description": "Clear old tool results from context (Fable context editing / tool-result clearing).",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "messages": {"type": "array"},
                    "clear_tool_results": {"type": "boolean"},
                },
                "required": ["session_id", "messages"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sub_agent_delegate",
            "description": "Spawn a governed sub-agent for a goal (long-horizon multi-agent pattern).",
            "parameters": {
                "type": "object",
                "properties": {
                    "parent_session_id": {"type": "string"},
                    "goal": {"type": "string"},
                    "role": {
                        "type": "string",
                        "enum": ["researcher", "coder", "reviewer", "tester"],
                    },
                },
                "required": ["parent_session_id", "goal"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "self_verify",
            "description": "Self-check an artifact against criteria (Fable tests-its-own-work pattern).",
            "parameters": {
                "type": "object",
                "properties": {
                    "artifact": {"type": "string"},
                    "criteria": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "refusal_fallback",
            "description": "Evaluate risk domain and apply Fable-style fallback/human escalation (not Mythos unrestricted).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "on_refusal": {"type": "string", "enum": ["fallback", "block", "human"]},
                },
                "required": ["query"],
            },
        },
    },
]


@router.get("/tools", summary="Fable/Mythos-style agent tools catalog")
async def catalog() -> dict[str, Any]:
    return {
        "tools": FABLE_STYLE_TOOLS,
        "source_models": ["claude-fable-5", "claude-mythos-5"],
        "notes": (
            "Implements safe control-plane analogues of Fable 5 features. "
            "Mythos unrestricted cyber/bio tooling is intentionally NOT provided; "
            "use human governance + refusal_fallback instead."
        ),
        "ts": _ts(),
    }


@router.post("/memory", summary="Memory tool")
async def memory_op(body: MemoryOp) -> dict[str, Any]:
    store = _MEMORY.setdefault(body.session_id, {})
    _log("track", "ok", f"memory {body.op}", session_id=body.session_id)
    if body.op == "set":
        if not body.key:
            raise HTTPException(400, "key required for set")
        store[body.key] = {"value": body.value, "updated_at": _ts()}
        return {"ok": True, "key": body.key}
    if body.op == "get":
        return {"ok": True, "entry": store.get(body.key or "")}
    if body.op == "list":
        return {"ok": True, "keys": list(store.keys())}
    if body.op == "delete":
        store.pop(body.key or "", None)
        return {"ok": True}
    if body.op == "clear":
        _MEMORY[body.session_id] = {}
        return {"ok": True}
    raise HTTPException(400, "unknown op")


@router.post("/code_execution", summary="Sandboxed code execution")
async def code_execution(body: CodeExecRequest) -> dict[str, Any]:
    _log("intake", "ok", "code_execution request")
    if not body.sandboxed or body.network_enabled:
        _log("verify", "fail", "sandbox/network policy")
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Requires sandboxed=true and network_enabled=false",
        )
    # Block obviously dangerous patterns
    banned = re.compile(
        r"\b(os\.system|subprocess|socket|requests|urllib|eval|exec|open\s*\(|__import__)\b"
    )
    if banned.search(body.code):
        _log("verify", "fail", "banned primitives")
        raise HTTPException(403, detail="Code uses blocked primitives")

    # Safe-ish eval: only allow AST of expressions/simple assigns via literal sandbox
    try:
        tree = ast.parse(body.code, mode="exec")
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.With, ast.AsyncFunctionDef)):
                raise TypeError("imports/with/async not allowed in sandbox")
        # Extremely limited: compute only if pure expression print targets
        # Prefer expression eval for single-line math-like scripts
        if len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr):
            result = ast.literal_eval(body.code.strip())  # type: ignore[arg-type]
            out = {"result": result, "mode": "literal_eval"}
        else:
            # structural accept only — no full exec of arbitrary code
            out = {
                "result": None,
                "mode": "structure_only",
                "message": "Script parsed OK; full exec disabled without human_approved + hardened runner",
                "human_approved": body.human_approved,
                "ast_nodes": len(list(ast.walk(tree))),
            }
            if body.human_approved:
                out["message"] = (
                    "human_approved=true noted — wire a hardened runner (nsjail/wasm) for real exec"
                )
    except Exception as exc:  # noqa: BLE001
        _log("complete", "fail", str(exc))
        return {"ok": False, "error": str(exc), "ts": _ts()}

    digest = hashlib.sha256(body.code.encode()).hexdigest()[:16]
    _log("complete", "ok", f"code_execution {digest}")
    return {"ok": True, "code_sha16": digest, "output": out, "ts": _ts()}


@router.post("/task_budget", summary="Task budgets")
async def task_budget(body: TaskBudget) -> dict[str, Any]:
    b = {
        "max_steps": body.max_steps,
        "max_tokens_est": body.max_tokens_est,
        "max_wall_minutes": body.max_wall_minutes,
        "steps_used": 0,
        "set_at": _ts(),
    }
    _BUDGETS[body.session_id] = b
    _log("track", "ok", "task_budget set", session_id=body.session_id)
    return {"ok": True, "budget": b}


@router.post("/task_budget/tick", summary="Consume one budget step")
async def task_budget_tick(session_id: str) -> dict[str, Any]:
    b = _BUDGETS.get(session_id)
    if not b:
        raise HTTPException(404, "no budget for session")
    b["steps_used"] = int(b.get("steps_used", 0)) + 1
    exhausted = b["steps_used"] >= b["max_steps"]
    _log("track", "ok" if not exhausted else "fail", f"tick {b['steps_used']}/{b['max_steps']}")
    return {"ok": not exhausted, "budget": b, "exhausted": exhausted}


@router.post("/compact", summary="Context compaction")
async def compact(body: CompactRequest) -> dict[str, Any]:
    msgs = body.messages
    if len(msgs) <= body.keep_last:
        return {"ok": True, "messages": msgs, "compacted": False}
    dropped = msgs[: -body.keep_last]
    summary = {
        "role": "system",
        "content": f"[KCN compact] Dropped {len(dropped)} earlier messages at {_ts()}.",
    }
    new_msgs = [summary] + msgs[-body.keep_last :]
    _log("track", "ok", f"compacted {len(dropped)} msgs", session_id=body.session_id)
    return {"ok": True, "messages": new_msgs, "compacted": True, "dropped": len(dropped)}


@router.post("/context_edit", summary="Clear tool results from context")
async def context_edit(body: ContextEditRequest) -> dict[str, Any]:
    out: list[dict[str, Any]] = []
    cleared = 0
    for i, m in enumerate(body.messages):
        if (
            body.clear_before_index is not None
            and i < body.clear_before_index
            and (m.get("role") == "tool" or m.get("tool_calls"))
        ):
            cleared += 1
            continue
        if body.clear_tool_results and m.get("role") == "tool":
            cleared += 1
            out.append({**m, "content": "[tool result cleared]"})
        else:
            out.append(m)
    _log("track", "ok", f"cleared {cleared}", session_id=body.session_id)
    return {"ok": True, "messages": out, "cleared": cleared}


@router.post("/sub_agent", summary="Delegate to sub-agent")
async def sub_agent(body: SubAgentRequest) -> dict[str, Any]:
    aid = f"sub-{uuid.uuid4().hex[:10]}"
    rec = {
        "id": aid,
        "parent": body.parent_session_id,
        "goal": body.goal,
        "role": body.role,
        "status": "queued",
        "created_at": _ts(),
        "plan": [
            f"Understand goal as {body.role}",
            "Propose steps under governance",
            "Self-verify outputs",
            "Return summary to parent",
        ],
    }
    _SUBAGENTS[aid] = rec
    _log("track", "ok", f"sub_agent {aid}", parent=body.parent_session_id)
    return {"ok": True, "agent": rec}


@router.get("/sub_agent/{agent_id}", summary="Sub-agent status")
async def sub_agent_status(agent_id: str) -> dict[str, Any]:
    a = _SUBAGENTS.get(agent_id)
    if not a:
        raise HTTPException(404, "unknown sub-agent")
    return a


@router.post("/self_verify", summary="Self-verify artifact")
async def self_verify(body: SelfVerifyRequest) -> dict[str, Any]:
    checks = []
    art = body.artifact
    for c in body.criteria:
        if c == "non_empty":
            checks.append({"criterion": c, "passed": bool(art.strip())})
        elif c == "no_todo":
            checks.append({"criterion": c, "passed": "TODO" not in art and "FIXME" not in art})
        elif c == "has_structure":
            checks.append(
                {
                    "criterion": c,
                    "passed": any(x in art for x in ("def ", "function", "class ", "{", "export")),
                }
            )
        else:
            checks.append({"criterion": c, "passed": c.lower() in art.lower()})
    passed = all(x["passed"] for x in checks)
    _log("verify", "ok" if passed else "fail", "self_verify")
    return {
        "passed": passed,
        "checks": checks,
        "sha256": hashlib.sha256(art.encode()).hexdigest(),
        "ts": _ts(),
    }


@router.post("/refusal_fallback", summary="Fable-style risk + fallback policy")
async def refusal_fallback(body: dict[str, Any]) -> dict[str, Any]:
    query = str(body.get("query", "")).lower()
    on_refusal = body.get("on_refusal", "human")
    # Conservative domain flags — escalate to human, never open offensive tooling
    flags = []
    if re.search(r"\b(rce|zero[- ]day|exploit kit|ransomware)\b", query):
        flags.append("cyber_offensive")
    if re.search(r"\b(weaponize|pathogen design|select agent)\b", query):
        flags.append("bio_risk")
    if re.search(r"\b(distill weights|exfiltrate model)\b", query):
        flags.append("model_distill")

    if not flags:
        return {"refusal": False, "action": "continue", "ts": _ts()}

    action = on_refusal if on_refusal in ("fallback", "block", "human") else "human"
    _log("verify", "fail", f"refusal domains={flags}", action=action)
    return {
        "refusal": True,
        "domains": flags,
        "action": action,
        "fallback_model": "kcn-safe-fallback",
        "message": "Routed under human governance — Mythos-unrestricted paths are not available in KCN.",
        "ts": _ts(),
    }


@router.get("/tracking", summary="Agent tool tracking log")
async def tracking(limit: int = 100) -> dict[str, Any]:
    return {"entries": _TRACK[-max(1, min(limit, 500)) :], "count": len(_TRACK)}
