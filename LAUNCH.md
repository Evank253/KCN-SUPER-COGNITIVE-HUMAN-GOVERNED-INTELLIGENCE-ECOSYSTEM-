# KCN Launch — Python-3

**Date:** 2026-08-07  
**Branch:** `Python-3`  
**Owner:** Evank253

## What shipped

Human-governed S-Class spine with **bounded autonomy**:

- Dual cyber watchdog + killswitch (Human-AI)
- Human-AI **Twin** (ecosystem counterpart ≠ chat companion)
- Sealed **Discovery sandbox** (transparent; promote needs human)
- **Self-modification lock** — no self-change without human acceptance
- Judgment bridge + Learning + Jarvis (toggleable)
- Award-tier admin UI, Control Deck (Jarvis + Sound on/off)

## Related repos

- [vibe-developer](https://github.com/Evank253/vibe-developer) — builder platform
- [kcn-preflight](https://github.com/Evank253/kcn-preflight) — quality gate (replaces vibe coder gate)
- [Kronos-Vibe-Coder](https://github.com/Evank253/Kronos-Vibe-Coder)

## Run (local)

```bash
# backend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000

# admin console
cd frontend/admin-console && npm i && npm run dev
```

## Principle

Humans govern. Agents execute. Nothing rewrites the system without human acceptance.
