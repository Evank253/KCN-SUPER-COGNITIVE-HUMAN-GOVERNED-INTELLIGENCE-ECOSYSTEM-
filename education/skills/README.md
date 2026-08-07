# Education System — Skills Registry

**Status:** Implemented (Phase 4 foundation)

## Purpose

A governed catalog of **skills** (capabilities) that agents and humans can invoke or develop.
Skills sit above raw tools: a skill may compose multiple tools and always carries governance metadata (`requires_human_approval`, `required_permissions`).

## Core Skills (seeded)

- Structured Reasoning
- Web Research
- Human Approval Workflow
- Truth & Evidence Verification
- Sandboxed Code Execution
- Federated Memory Recall
- Jarvis / Vibe Coaching

## Alignment

- Mirrors `Global-Intelligence/agent_runtime/tool_orchestration/tool_registry.py` style.
- Linked tool names match the Global-Intelligence tool registry where applicable.

## API

See `backend/app/routes/skills.py` — endpoints under `/api/v1/skills`.
