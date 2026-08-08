# KCN Launch — Python-3

**Date:** 2026-08-08  
**Branch:** `Python-3`  
**Owner:** Evank253  
**Issue:** #30

## Maturity

**L2 — internal scaffold / launch sync.**  
Not L3. L3 requires an unaffiliated evaluator to reproduce and falsify sealed claims.

## What shipped on Python-3 (S-Class spine)

| Module | Path | Notes |
|--------|------|-------|
| Self-mod / governance lock | `backend/governance/engine.py`, `backend/kcn_core/governance_lock/` | Human acceptance required |
| Human-AI watchdog | `backend/kcn_core/human_ai/watchdog.py` | Kill/freeze; **agent resume → 403** |
| Human-AI Twin | `backend/kcn_core/human_ai/twin.py` | Ecosystem twin, not chat UI |
| Discovery sandbox | `backend/kcn_core/discovery/sandbox.py` | Propose free; **promote needs human** |
| Judgment bridge | `backend/kcn_core/judgment/bridge.py` | Recommendations only |
| Authority routes | `backend/app/routes/authority.py` | F13 acceptance, F14 resume |
| Boundary tests | `backend/tests/test_authority_boundary.py` | Agent 403 cases |
| Control Deck / Jarvis / sound | prior push | As in issue #30 |

## Principle

**Humans govern. Agents execute. No self-change without human acceptance.**

Valid BBS/VC/ZK proof + agent JWT does **not** authorize acceptance or watchdog resume → **HTTP 403**.

## Related repos

- [vibe-developer](https://github.com/Evank253/vibe-developer)
- [kcn-preflight](https://github.com/Evank253/kcn-preflight)

## Run (local)

```bash
cd backend && pip install -r requirements.txt
# Ensure PYTHONPATH includes backend/
uvicorn app.main:app --reload --port 8000
pytest backend/tests/test_authority_boundary.py -q
```

## Issue #30 closure criteria (this push)

- [x] Watchdog module on branch
- [x] Twin module on branch
- [x] Discovery sandbox on branch
- [x] Judgment bridge on branch
- [x] Authority routes with agent 403
- [x] Boundary unit tests
- [ ] Full admin chat / award UI polish (follow-up issues)
- [ ] Independent L3 evaluation package execution
