# Secure Env Rotation · Audit Verification · Tracking

## 1. Secure env rotation process

Handoff secrets in `SECURE_ENV_AND_KEYS/.env.secure` are **not** production credentials.

### Rotate before production

1. Generate a new JWT secret (≥32 random bytes, hex or base64).
2. Set a strong admin bootstrap password (or disable bootstrap after first real user).
3. Replace Discord invite only if the server changes.
4. Update deployment secrets (GitHub Actions repo/environment secrets, Docker host env vars) — never commit real secrets.
5. Restart services so new values load.
6. Log the rotation event with ISO-8601 timestamp (see Tracking phase).

### Template fields

```
KCN_ENV=production
KCN_SANDBOX=true
KCN_NETWORK_ENABLED=false
KCN_JWT_SECRET=<rotate>
KCN_ADMIN_BOOTSTRAP_USER=admin
KCN_ADMIN_BOOTSTRAP_PASS=<rotate>
KCN_DISCORD_INVITE=https://discord.gg/ZtYmsQRcR
```

`experiment_controller` still requires: sandboxed=True, network_enabled=False, human_subjects → approval=True.

## 2. Audit log verification methods

1. **Checksum chain** — `sha256sum -c CHECKSUMS.sha256` on export packages.
2. **Event ledger** — each verification step appends `{ts, phase, actor, status, detail}`.
3. **Signature (optional)** — sign ledger entries with auditor key; verify with public key.
4. **Replay** — re-run `verify_bundle` / `verify_manifest` against stored hashes.
5. **API** — `GET /api/v1/verification/tracking` returns timestamped phase log.

Everything that ships or deploys **must** pass the verification process and a tracking phase; both are logged with timestamps.

## 3. Sandbox size discrepancy

Original campaign machines held large benchmark runs (~25MB source section, ~138MB results section).
This rebuild environment only had ~5MB of attachment payloads, so complete-build ZIPs are smaller (≈4MB / ≈8MB).
All files that **existed** in the sandbox were included; missing bulk is absent source data, not omitted packaging.

## 4. Tracking phase (required)

Every build / deploy / secret rotation / vibe job:

| Phase | Logged fields |
|-------|----------------|
| `intake` | ts, request_id, actor |
| `verify` | ts, checks[], passed |
| `track` | ts, pipeline stage |
| `complete` | ts, artifact_ref, status |

Timestamps are UTC ISO-8601.
