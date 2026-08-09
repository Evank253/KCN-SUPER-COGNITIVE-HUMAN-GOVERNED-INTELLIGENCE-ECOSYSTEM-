# Deployment Guide

This document describes how to deploy the KCN Super Cognitive Human Governed Intelligence Ecosystem to production environments.

---

## Deployment Environments

| Environment | Branch | Purpose |
|---|---|---|
| Development | `feature/*` | Local developer testing |
| Staging | `develop` | Integration testing |
| Production | `main` | Live system |

---

## Prerequisites

- Docker 24.x and Docker Compose 2.x installed on the deployment host
- Access to a container registry (e.g., GitHub Container Registry)
- Configured secrets and environment variables (see below)
- Domain name with TLS certificate (production)

---

## Environment Variables

Copy `config/.env.example` to your deployment environment secrets manager. Required variables for production:

```bash
APP_ENV=production
APP_DEBUG=false
APP_SECRET_KEY=<strong-random-secret>

JWT_SECRET_KEY=<strong-random-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

LOG_LEVEL=INFO
LOG_FORMAT=json

# Phase 2+
# DATABASE_URL=******db-host:5432/kcn
# REDIS_URL=redis://redis-host:6379
```

**Never store production secrets in the repository.** Use your deployment platform's secrets manager (GitHub Secrets, Vault, AWS Secrets Manager, etc.).

---

## Docker Deployment

### Build Images

```bash
# Build backend image
docker build -t kcn-backend:latest ./backend

# Build frontend image
docker build -t kcn-frontend:latest ./frontend
```

### Run with Docker Compose

```bash
# Production deployment
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

---

## CI/CD Pipeline

The repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that:

1. Runs on every push and pull request to `main`
2. Lints backend Python code (Ruff)
3. Type-checks backend Python code (mypy)
4. Runs backend unit tests (Pytest)
5. Lints frontend TypeScript code (ESLint)
6. Runs frontend unit tests (Vitest)
7. Builds Docker images to verify build integrity

### Extending CI/CD for Deployment

To add deployment stages, extend `.github/workflows/ci.yml`:

```yaml
deploy:
  needs: [test-backend, test-frontend]
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Deploy to production
      # Add your deployment steps here
```

---

## Public Demo (GitHub Pages)

A static preview of `public-demo/` is deployed automatically via `.github/workflows/pages.yml` on every push to `main`, `develop`, and `copilot/kcn-super-cognitive-ecosystem`. It requires GitHub Pages to be enabled once per repo:

1. Repo Settings → Pages → Build and deployment → Source: **GitHub Actions**
2. Push to a tracked branch (or run the workflow manually via `workflow_dispatch`)
3. Live at `https://<owner>.github.io/<repo>/`

This is a static demo only — it does not run the FastAPI backend. Use the Docker deployment above for the full stack.

---

## Health Checks

The backend exposes health check endpoints:

```bash
# Basic health check
GET /health
# Response: {"status": "healthy", "version": "0.1.0"}

# Readiness check (Phase 2+)
GET /health/ready
# Response: {"status": "ready", "dependencies": {"database": "ok"}}
```

Configure your load balancer or orchestrator to use `/health` for liveness probes.

---

## Logging

All services emit structured JSON logs. In production:

- Logs are written to stdout/stderr (12-factor app pattern)
- Log aggregation (ELK stack, Loki, etc.) is recommended
- Log level is controlled by `LOG_LEVEL` environment variable
- Sensitive data must never appear in logs

---

## Monitoring (Planned — Phase 6)

The following monitoring integrations are planned:

- Prometheus metrics endpoint
- Grafana dashboards
- Alerting via PagerDuty or similar
- Distributed tracing (OpenTelemetry)

---

## Security Considerations for Production

- [ ] TLS 1.3 enforced for all external traffic
- [ ] Secrets managed via secrets manager (not environment files)
- [ ] Container images scanned for vulnerabilities before deployment
- [ ] Network policies restrict inter-service traffic
- [ ] `APP_DEBUG=false` in production
- [ ] Access logs enabled and retained per compliance requirements
- [ ] Backup strategy defined for persistent data

---

## Rollback Procedure

```bash
# Roll back to a previous Docker image version
docker compose down
docker tag kcn-backend:previous kcn-backend:latest
docker compose up -d
```

For Git-based rollback:

```bash
git revert <commit-hash>
git push origin main
# CI/CD will rebuild and redeploy automatically
```

---

## Further Reading

- [INSTALLATION.md](INSTALLATION.md) — Local setup
- [ARCHITECTURE.md](ARCHITECTURE.md) — System design
- [SECURITY.md](SECURITY.md) — Security policy
