# Knowledge Core — Memory System

**Status:** Implemented (Phase 3 foundation)

## Components

| Module | Role |
|--------|------|
| `vector_memory.py` | Semantic embedding store with provenance + governance flags |
| `session_memory.py` | Short-term working memory (TTL sessions, turns, context) |
| `federated_memory.py` | Unified service + cross-repo federation adapter registry |

## Design

- Only **verified** / **human-approved** content should be persisted long-term (enforced by callers and API defaults).
- Patterns aligned with `Global-Intelligence/data_fabric/knowledge_storage/vector_memory.py`.
- Federation adapters are registered for Global-Intelligence, vibe-developer, and KCN_SINGULARITY_MASTER so remote sync can be added without changing the public interface.

## Usage (Python)

```python
from knowledge.memory import FederatedMemoryService, memory_service

# or use the shared singleton
mem = memory_service

sid = mem.open_session(user_id="human-1", agent_id="jarvis")
mem.add_turn(sid, "user", "What is the governance policy?")
mem.remember([0.1, 0.2, ...], {"text": "Policy X..."}, verified=True, human_approved=True)
results = mem.recall([0.1, 0.2, ...], require_verified=True)
```

## API

See `backend/app/routes/memory.py` — endpoints under `/api/v1/memory`.
