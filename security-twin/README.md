# KCN Security Twin

**DISPOSABLE · ISOLATED · AUTHORIZED TESTING ONLY**

This is a self-contained twin of the KCN Super Cognitive security-relevant surface.
It exists so you can point external tools (e.g. HackerGPT) at a controlled target
instead of your real system.

## What it contains

- Auth (login / refresh / logout) with stub users
- Governance approval stubs
- Memory (vector + session) stubs
- Skills registry stubs
- Heavy request logging + audit trail
- Clear `X-KCN-Twin: true` header and response banners on every reply

## What it deliberately does NOT contain

- Real secrets or production JWT keys
- Real user data or databases
- GitHub OAuth (disabled)
- Any connection to the real KCN backend, frontend, or knowledge stores

## Quick start (local only — recommended)

```bash
cd security-twin
docker compose up --build
```

Twin will be available at: http://localhost:8100

Docs: http://localhost:8100/docs

### Default stub credentials (test only)

| Username | Password |
|----------|----------|
| twin-admin | twin-pass-change-me |
| twin-user  | twin-user-pass     |

## Safe exposure (optional)

If you must give an external tool a reachable URL:

1. Prefer a temporary tunnel (ngrok, cloudflared, etc.) that you can kill instantly.
2. Do **not** put real secrets in the twin.
3. Watch the logs in real time.
4. Destroy the container when finished: `docker compose down -v`

## Logs

All requests are logged with method, path, client, headers (redacted), and status.
Audit events are written to stdout in structured JSON.

## Destroy when done

```bash
docker compose down -v
```

This twin is intentionally simple and disposable. Treat any findings as feedback
for hardening the real Security Core, not as a production system.
