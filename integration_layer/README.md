# KCN Integration Layer (Phase 11)

Cross-cutting fabric that connects every subsystem of the KCN Singularity Master ecosystem.

## Packages

| Package | Purpose |
|---------|---------|
| `service_mesh` | Subsystem registry, discovery, message routing, health monitoring |
| `identity_federation` | Unified identity, credential exchange, permission bridging |
| `event_orchestration` | Global event bus, mission pipeline, workflow scheduler |
| `data_fabric` | Artifact sync, knowledge sync, **provenance sync** |
| `ai_control_plane` | Agent registry, model router, memory coordinator, swarm manager |

## Quick start

```bash
pip install -e .
pytest tests/ -v
```

## Design principles

- Thin plumbing – no domain logic
- Content-addressed provenance for every significant object
- Human-governance first (identity + permission bridge)
- Observable by default (health, events, evidence packages)
