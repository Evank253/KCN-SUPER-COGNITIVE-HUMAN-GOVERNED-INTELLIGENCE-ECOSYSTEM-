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

## Vercel Deployment (Frontend)

The frontend is deployed from the repository root. The root `vercel.json` is the single source of truth for Vercel, while the actual Vite app remains in `frontend/`.

The Vercel CLI is included as a root dev dependency so deployments can be triggered from the monorepo root.

### Setup

```bash
# Install root deployment tooling (includes Vercel CLI)
npm install

# Log in to Vercel (one-time setup)
npx vercel login
```

### Deploy

```bash
# Deploy a preview (staging) build
npm run deploy:preview

# Deploy to production
npm run deploy
```

You can also run the CLI directly:

```bash
npx vercel          # preview deployment
npx vercel --prod   # production deployment
```

### Configuration

The `vercel.json` file at the repository root configures the deployment:

- **Framework**: Vite
- **Install command**: `npm --prefix frontend install --legacy-peer-deps`
- **Build command**: `npm --prefix frontend run build`
- **Output directory**: `frontend/dist`
- **Rewrites**: All routes fall back to `index.html` for SPA routing
- **Security headers**: `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`
- **Project root**: repository root (do not add a competing `frontend/vercel.json`)

### Environment Variables

Set any required environment variables in the [Vercel Dashboard](https://vercel.com/dashboard) under **Project → Settings → Environment Variables**, or via the CLI:

```bash
npx vercel env add VITE_API_URL
```

### Troubleshooting

- If the build fails due to a frontend lockfile mismatch, run `npm install --legacy-peer-deps` inside `frontend/` to regenerate `frontend/package-lock.json`, then re-deploy.
- If the root Vercel CLI install drifts, run `npm install` at the repository root to refresh the root `package-lock.json`.
- Ensure Node.js ≥ 20.19.0 is selected in Vercel project settings to match the `engines` field in the root `package.json`.

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
