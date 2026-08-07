# Installation Guide

This guide covers setting up the KCN Super Cognitive Human Governed Intelligence Ecosystem for local development.

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| Python | 3.12 | Required for backend |
| Node.js | 20.x LTS | Required for frontend |
| Docker | 24.x | Required for containerized setup |
| Docker Compose | 2.x | Required for multi-service setup |
| Git | 2.x | Required |

---

## Option 1 — Docker Compose (Recommended)

The fastest way to get a complete environment running:

```bash
# 1. Clone the repository
git clone https://github.com/Evank253/KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-.git
cd KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-

# 2. Copy environment configuration
cp config/.env.example config/.env

# 3. Review and update config/.env with your settings

# 4. Build and start all services
docker compose up --build

# 5. Verify services are running
docker compose ps
```

Services available after startup:

| Service | URL | Description |
|---|---|---|
| Backend API | http://localhost:8000 | FastAPI application |
| API Docs | http://localhost:8000/docs | OpenAPI (Swagger UI) |
| Frontend | http://localhost:3000 | React application |

---

## Option 2 — Manual Setup

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 5. Copy environment configuration
cp ../config/.env.example .env

# 6. Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev
```

---

## Environment Configuration

Copy `config/.env.example` to `config/.env` and configure:

```bash
# Application
APP_NAME=KCN-Ecosystem
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=change-me-to-a-secure-random-string

# API
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Security
JWT_SECRET_KEY=change-me-to-a-secure-random-string
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (Phase 2)
# DATABASE_URL=******localhost:5432/kcn

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**Important:** Never commit `.env` files with real credentials to version control.

---

## Running Tests

```bash
# Backend tests
cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# All tests via Docker
docker compose run --rm backend pytest tests/ -v
```

---

## Verifying Your Installation

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "0.1.0"}

# Check API docs are accessible
open http://localhost:8000/docs
```

---

## Troubleshooting

### Port already in use

```bash
# Find and stop the process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Docker build failures

```bash
# Clean Docker cache and rebuild
docker compose down --volumes
docker compose build --no-cache
docker compose up
```

### Python dependency conflicts

```bash
# Use a fresh virtual environment
deactivate
rm -rf backend/venv
python -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

---

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
- Read [CONTRIBUTING.md](CONTRIBUTING.md) to understand the development workflow
- See [API_REFERENCE.md](API_REFERENCE.md) for API documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions
