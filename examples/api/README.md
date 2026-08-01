# API Examples

Examples using curl to interact with the KCN API.

## Health Check

```bash
curl http://localhost:8000/health
```

## Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme"}'

# Use the access_token from the response
TOKEN="<access_token>"

# Refresh
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

## Governance

```bash
# List policies
curl http://localhost:8000/api/v1/governance/policies \
  -H "Authorization: ****** $TOKEN"

# Submit approval request
curl -X POST http://localhost:8000/api/v1/governance/approvals \
  -H "Authorization: ****** $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action_type": "high_risk_operation", "description": "Deploy new model version"}'
```

## Intelligence

```bash
# Submit analysis
curl -X POST http://localhost:8000/api/v1/intelligence/analyze \
  -H "Authorization: ****** $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize best practices for secure API design", "module": "analysis"}'
```
