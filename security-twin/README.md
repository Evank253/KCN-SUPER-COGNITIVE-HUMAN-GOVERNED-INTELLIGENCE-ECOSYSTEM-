# KCN Security Twin

**DISPOSABLE · ISOLATED · AUTHORIZED TESTING ONLY**

Self-contained twin of the KCN Super Cognitive security-relevant surface.
Use this so external tools (e.g. HackerGPT) probe a controlled target instead of your real system.

All audit records are marked **TWIN TEST LOG — NOT PRODUCTION**.
They are evidence of activity against the twin only — not proof about the production system.

## Quick start

```bash
cd security-twin
docker compose up --build
```

- Twin: http://localhost:8100
- Docs: http://localhost:8100/docs

### Stub credentials (test only)

| Username     | Password              |
|--------------|-----------------------|
| `twin-admin` | `twin-pass-change-me` |
| `twin-user`  | `twin-user-pass`      |

## Audit / proof-of-test logs

Every request is recorded (JSONL on disk + in-memory).

| Endpoint | Auth | Purpose |
|----------|------|--------|
| `GET /api/v1/audit/summary` | admin token | Counts (auth success/fail, canary hits, top paths) |
| `GET /api/v1/audit/export` | admin token | Full event list (JSON) |
| `GET /api/v1/audit/export?format=jsonl` | admin token | Downloadable JSONL file |

### Example: export after a test session

```bash
# 1. Login as twin-admin
curl -s -X POST http://localhost:8100/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"twin-admin","password":"twin-pass-change-me"}'

# 2. Use the access_token
export TOKEN=...  # paste access_token from step 1

curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8100/api/v1/audit/summary

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8100/api/v1/audit/export?format=jsonl" \
  -o kcn-twin-audit.jsonl
```

Logs also live in the Docker volume `twin-logs` → `/logs/twin-audit.jsonl` inside the container.

## Safe exposure

1. Prefer local + temporary tunnel (ngrok / cloudflared) you can kill instantly.
2. Never put real secrets in the twin.
3. Watch logs live in the terminal.
4. When finished: `docker compose down -v`

## What these logs prove

They prove what was sent to **this disposable twin** and how the twin responded.
They do **not** prove the strength of the real KCN production system, and they do not support “best cybersecurity system ever” claims.

Use them as internal evidence of a controlled test session, then harden the real Security Core based on findings.
