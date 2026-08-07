# Knowledge Core

The Knowledge Core stores and organizes information that has been validated by the Verification Core.

## Purpose

Preserve verified knowledge in a structured, queryable, and version-controlled form.

## Modules

| Module | Status |
|---|---|
| Knowledge Graph | Phase 3 |
| **Memory System** | **Implemented (foundation)** — see `memory/` |
| Documentation | Phase 1 (directory structure) |
| Research Archive | Phase 3 |
| Learning Database | Phase 4 |
| Version Control | Phase 3 |

## Memory System (live)

- `memory/vector_memory.py` — semantic store with provenance & governance flags
- `memory/session_memory.py` — working memory with TTL
- `memory/federated_memory.py` — unified service + federation adapters for Global-Intelligence, vibe-developer, singularity

API: `/api/v1/memory/*`

## Dependencies

- Verification Core (only accepts verified inputs)
- Security Core

## Expansion Points

- Graph database integration (Neo4j, etc.)
- Full-text search
- Knowledge versioning and provenance tracking
- Export to open formats
- Remote federation RPC against Global-Intelligence vector store
