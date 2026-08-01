# Intelligence Core

The Intelligence Core performs research, reasoning, planning, analysis, creative work, engineering support, and learning assistance.

## Purpose

Produce structured outputs that support human decision-making. All outputs must pass through the Verification Core before entering the Knowledge Core.

## Modules

| Module | Status | Description |
|---|---|---|
| Research Agents | Phase 2 | Gather, synthesize, and summarize information |
| Reasoning Systems | Phase 2 | Apply logical inference and structured thinking |
| Planning Systems | Phase 2 | Generate action plans and decision trees |
| Creative Systems | Phase 2 | Produce novel ideas and creative outputs |
| Engineering Systems | Phase 2 | Support software design and code generation |
| Analysis Systems | Phase 1 (stub) | Evaluate data and produce structured insights |
| Learning Systems | Phase 2 | Track progress and adapt to user context |

## Dependencies

- Verification Core (all outputs go through verification)
- Security Core (authentication and authorization)

## Interfaces

- `POST /api/v1/intelligence/analyze` — submit analysis request

## Expansion Points

- Async processing with task queues
- Model provider abstraction layer
- Output caching and deduplication
- Multi-agent coordination
