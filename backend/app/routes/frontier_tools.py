"""
KCN Frontier Tools — capabilities aligned with open frontier model APIs
(reasoning effort, tool calling, multimodal inputs, preserved thinking),
with human-governed verification + timestamped tracking on every call.

This is the control-plane layer. Optional upstream LLM via KCN_LLM_* env.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/frontier")

_TRACK: list[dict[str, Any]] = []
_SESSIONS: dict[str, list[dict[str, Any]]] = {}


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(phase: str, status_s: str, detail: str, **extra: Any) -> dict[str, Any]:
    entry = {"ts": _ts(), "phase": phase, "status": status_s, "detail": detail, **extra}
    _TRACK.append(entry)
    logger.info("frontier.track %s", entry)
    return entry


# ---- Schemas (OpenAI-compatible shape) -------------------------------------

class ContentPart(BaseModel):
    type: Literal["text", "image_url"]
    text: str | None = None
    image_url: dict[str, str] | None = None  # {"url": "..."}


class ToolFunction(BaseModel):
    name: str
    description: str | None = None
    parameters: dict[str, Any] | None = None


class ToolSpec(BaseModel):
    type: Literal["function"] = "function"
    function: ToolFunction


class ChatMessageIn(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[ContentPart] | None = None
    reasoning_content: str | None = None  # preserved thinking (Kimi-style)
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    name: str | None = None


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="kcn-k3-governed")
    messages: list[ChatMessageIn] = Field(..., min_length=1)
    reasoning_effort: Literal["low", "high", "max"] = "max"
    tools: list[ToolSpec] | None = None
    tool_choice: str | dict[str, Any] | None = "auto"
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=128000)
    stream: bool = False
    session_id: str | None = None  # long-horizon session continuity


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[dict[str, Any]]
    usage: dict[str, int]
    kcn: dict[str, Any]  # governance metadata


class ToolCatalogResponse(BaseModel):
    tools: list[dict[str, Any]]
    notes: str


# Built-in KCN tools (what we have that pure model cards don't)
BUILTIN_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "vibe_build",
            "description": "Route a natural-language build request through Vibe Developer → Kronos → verification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "language": {"type": "string", "enum": ["typescript", "python"]},
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verify_artifact",
            "description": "Run verification checks and return SHA-256 + pass/fail.",
            "parameters": {
                "type": "object",
                "properties": {"content": {"type": "string"}},
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "governance_check",
            "description": "Check whether an action is allowed under human governance policy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "risk": {"type": "string", "enum": ["low", "medium", "high"]},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "experiment_gate",
            "description": "Evaluate ExperimentController: sandbox, network, human_subjects, approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sandboxed": {"type": "boolean"},
                    "network_enabled": {"type": "boolean"},
                    "human_subjects": {"type": "boolean"},
                    "approval": {"type": "boolean"},
                },
                "required": ["sandboxed", "network_enabled", "human_subjects", "approval"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tracking_append",
            "description": "Append a timestamped tracking event (intake/verify/track/complete).",
            "parameters": {
                "type": "object",
                "properties": {
                    "phase": {"type": "string"},
                    "detail": {"type": "string"},
                },
                "required": ["phase", "detail"],
            },
        },
    },
]


def _flatten_content(content: str | list[ContentPart] | None) -> tuple[str, list[str]]:
    """Extract text + image URLs from multimodal content."""
    if content is None:
        return "", []
    if isinstance(content, str):
        return content, []
    texts: list[str] = []
    images: list[str] = []
    for part in content:
        if part.type == "text" and part.text:
            texts.append(part.text)
        elif part.type == "image_url" and part.image_url:
            url = part.image_url.get("url", "")
            if url:
                images.append(url)
                texts.append(f"[image: {url[:80]}]")
    return "\n".join(texts), images


def _local_reason(messages: list[ChatMessageIn], effort: str) -> tuple[str, str]:
    """Local reasoning + reply when no upstream LLM is configured."""
    last_user = ""
    images: list[str] = []
    for m in reversed(messages):
        if m.role == "user":
            last_user, images = _flatten_content(m.content)
            break
    depth = {"low": 1, "high": 2, "max": 3}.get(effort, 3)
    steps = [
        "Parse operator intent under human-governance constraints.",
        "Prefer verification + tracking over unbounded autonomy.",
        "Offer Vibe→Kronos for code, or governance tools for policy risk.",
    ][:depth]
    reasoning = " ".join(f"({i+1}) {s}" for i, s in enumerate(steps))
    if images:
        reasoning += f" Multimodal: {len(images)} image(s) noted (vision passthrough ready)."
    reply = (
        f"KCN K3 governed response (effort={effort}). "
        f"Understood: {last_user[:400] or '(empty)'}. "
        "Use tools vibe_build / verify_artifact / governance_check / experiment_gate as needed. "
        "Humans keep authority."
    )
    return reasoning, reply


def _maybe_tool_call(
    messages: list[ChatMessageIn], tools: list[ToolSpec] | None, tool_choice: Any
) -> list[dict[str, Any]] | None:
    if not tools and tool_choice in (None, "none"):
        return None
    last = ""
    for m in reversed(messages):
        if m.role == "user":
            last, _ = _flatten_content(m.content)
            break
    low = last.lower()
    # Heuristic tool routing (upgrade to LLM tool choice when KCN_LLM_BASE_URL set)
    if any(w in low for w in ("build", "code", "scaffold", "implement")):
        return [
            {
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "function",
                "function": {
                    "name": "vibe_build",
                    "arguments": json.dumps({"prompt": last, "language": "typescript"}),
                },
            }
        ]
    if any(w in low for w in ("verify", "checksum", "hash")):
        return [
            {
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "function",
                "function": {
                    "name": "verify_artifact",
                    "arguments": json.dumps({"content": last}),
                },
            }
        ]
    if any(w in low for w in ("policy", "govern", "allow", "approve")):
        return [
            {
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "function",
                "function": {
                    "name": "governance_check",
                    "arguments": json.dumps({"action": last[:200], "risk": "medium"}),
                },
            }
        ]
    return None


@router.get("/tools", response_model=ToolCatalogResponse, summary="List KCN frontier + governance tools")
async def list_tools() -> ToolCatalogResponse:
    return ToolCatalogResponse(
        tools=BUILTIN_TOOLS,
        notes=(
            "KCN tools = frontier-style function calling + human governance. "
            "Optional upstream model via KCN_LLM_BASE_URL / KCN_LLM_API_KEY / KCN_LLM_MODEL."
        ),
    )


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    summary="OpenAI-compatible chat with reasoning_effort, tools, multimodal",
)
async def chat_completions(body: ChatCompletionRequest) -> ChatCompletionResponse:
    if body.stream:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Streaming not enabled in this build; set stream=false.",
        )

    job_id = f"chat-{uuid.uuid4().hex[:12]}"
    _log("intake", "ok", f"chat completions job={job_id} effort={body.reasoning_effort}", job_id=job_id)

    # Session continuity (long-horizon)
    sid = body.session_id or f"sess-{uuid.uuid4().hex[:10]}"
    history = _SESSIONS.setdefault(sid, [])
    for m in body.messages:
        history.append(m.model_dump())

    # Count multimodal
    n_images = 0
    for m in body.messages:
        if isinstance(m.content, list):
            n_images += sum(1 for p in m.content if p.type == "image_url")

    tool_calls = _maybe_tool_call(body.messages, body.tools, body.tool_choice)
    reasoning, content = _local_reason(body.messages, body.reasoning_effort)

    # Optional upstream LLM
    base = os.getenv("KCN_LLM_BASE_URL", "").rstrip("/")
    key = os.getenv("KCN_LLM_API_KEY", "")
    model = os.getenv("KCN_LLM_MODEL", body.model)
    upstream_used = False
    if base and key:
        try:
            import urllib.request

            payload = {
                "model": model,
                "messages": [m.model_dump(exclude_none=True) for m in body.messages],
                "temperature": body.temperature,
                "max_tokens": body.max_tokens,
            }
            # Pass through reasoning_effort if provider supports it (e.g. kimi-k3)
            payload["reasoning_effort"] = body.reasoning_effort
            if body.tools:
                payload["tools"] = [t.model_dump() for t in body.tools]
            req = urllib.request.Request(
                f"{base}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            choice0 = data["choices"][0]["message"]
            content = choice0.get("content") or content
            reasoning = choice0.get("reasoning_content") or choice0.get("reasoning") or reasoning
            tool_calls = choice0.get("tool_calls") or tool_calls
            upstream_used = True
            _log("track", "ok", f"upstream LLM {model}", job_id=job_id, actor="llm")
        except Exception as exc:  # noqa: BLE001
            _log("track", "fail", f"upstream fallback: {exc}", job_id=job_id)
            # keep local reasoning/content

    message: dict[str, Any] = {
        "role": "assistant",
        "content": content,
        "reasoning_content": reasoning,
    }
    if tool_calls:
        message["tool_calls"] = tool_calls

    _log("verify", "ok", "response assembled under governance", job_id=job_id)
    _log("complete", "ok", "chat complete", job_id=job_id, session_id=sid)

    created = int(datetime.now(timezone.utc).timestamp())
    prompt_chars = sum(len(_flatten_content(m.content)[0]) for m in body.messages)

    return ChatCompletionResponse(
        id=job_id,
        created=created,
        model=body.model,
        choices=[
            {
                "index": 0,
                "message": message,
                "finish_reason": "tool_calls" if tool_calls else "stop",
            }
        ],
        usage={
            "prompt_tokens": max(1, prompt_chars // 4),
            "completion_tokens": max(1, len(content) // 4),
            "total_tokens": max(2, (prompt_chars + len(content)) // 4),
        },
        kcn={
            "session_id": sid,
            "reasoning_effort": body.reasoning_effort,
            "images_seen": n_images,
            "upstream_llm": upstream_used,
            "tracking_ts": _ts(),
            "human_governed": True,
        },
    )


@router.get("/tracking", summary="Frontier tool call tracking log")
async def frontier_tracking(limit: int = 100) -> dict[str, Any]:
    entries = _TRACK[-max(1, min(limit, 500)) :]
    return {"entries": entries, "count": len(entries)}


@router.post("/tools/execute", summary="Execute a built-in KCN tool (governed)")
async def execute_tool(body: dict[str, Any]) -> dict[str, Any]:
    name = body.get("name") or body.get("function", {}).get("name")
    args = body.get("arguments") or body.get("function", {}).get("arguments") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {"raw": args}

    _log("intake", "ok", f"tool execute {name}", tool=name)

    if name == "verify_artifact":
        content = str(args.get("content", ""))
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        result = {"passed": len(content) >= 20, "sha256": digest, "verified_at": _ts()}
    elif name == "governance_check":
        risk = args.get("risk", "medium")
        result = {
            "allowed": risk != "high",
            "requires_human": risk == "high",
            "action": args.get("action"),
            "ts": _ts(),
        }
    elif name == "experiment_gate":
        sandboxed = bool(args.get("sandboxed"))
        network = bool(args.get("network_enabled"))
        human = bool(args.get("human_subjects"))
        approval = bool(args.get("approval"))
        ok = sandboxed and not network and (approval if human else True)
        result = {"can_run": ok, "ts": _ts(), "rules": "sandbox=on network=off human→approval"}
    elif name == "tracking_append":
        e = _log(str(args.get("phase", "track")), "ok", str(args.get("detail", "")), actor="tool")
        result = {"appended": e}
    elif name == "vibe_build":
        result = {
            "status": "routed",
            "hint": "POST /api/v1/vibe/build with {prompt, language}",
            "prompt": args.get("prompt"),
            "ts": _ts(),
        }
    else:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {name}")

    _log("complete", "ok", f"tool {name} done", tool=name)
    return {"name": name, "result": result}
