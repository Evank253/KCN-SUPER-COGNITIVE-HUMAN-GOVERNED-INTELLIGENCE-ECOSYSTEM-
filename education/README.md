# Education System

The Education System converts validated knowledge into structured learning experiences for humans.

## Purpose

Transform knowledge from the Knowledge Core into accessible learning paths, assessments, certifications, and skill development programs.

## Modules

| Module | Status |
|---|---|
| Learning Paths | Phase 4 |
| **Skill Development / Skills Registry** | **Implemented (foundation)** — see `skills/` |
| Assessments | Phase 4 |
| Certifications | Phase 4 |
| Knowledge Transfer | Phase 4 |

## Skills Registry (live)

- `skills/skills_registry.py` — governed skill catalog (reasoning, research, governance, verification, coding, memory, vibe)
- Linked to Global-Intelligence tool names where applicable
- Human-approval flags and permission requirements on every skill

API: `/api/v1/skills/*`

## Dependencies

- Knowledge Core (source of learning content)
- Analytics System (learning progress metrics)

## Expansion Points

- Adaptive learning algorithms
- External LMS integration
- Credential verification
- Skill progression tracking into Learning Database
