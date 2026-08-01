# Contributing to KCN

Thank you for your interest in contributing to the KCN Super Cognitive Human Governed Intelligence Ecosystem. We welcome contributions from developers, researchers, security professionals, educators, and domain experts.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Security Issues](#security-issues)

---

## Code of Conduct

By participating in this project you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

---

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-.git
   cd KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-
   ```
3. Set up your development environment (see [INSTALLATION.md](INSTALLATION.md)).
4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Workflow

```
fork → branch → develop → test → lint → PR → review → merge
```

1. All changes should be made on a feature branch, never directly on `main`.
2. Branch naming convention: `feature/`, `fix/`, `docs/`, `refactor/`, `security/`
3. Commit messages should follow [Conventional Commits](https://www.conventionalcommits.org/).
4. Keep pull requests focused on a single change.

### Commit Message Format

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `security`

Examples:
```
feat(intelligence): add reasoning system stub
fix(security): correct RBAC role check logic
docs(api): update OpenAPI schema for v1 endpoints
```

---

## Coding Standards

### Python (Backend)

- Python 3.12+
- Type hints required on all function signatures
- Follow [PEP 8](https://pep8.org/) style
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Docstrings on all public functions and classes

```bash
# Format and lint
cd backend
pip install black ruff
black app/
ruff check app/
```

### TypeScript (Frontend)

- TypeScript strict mode enabled
- Use functional components and hooks
- No `any` types without explicit justification
- ESLint + Prettier enforced

```bash
cd frontend
npm run lint
npm run format
```

### General

- Every module has a single, clear responsibility
- No hardcoded secrets or credentials
- Input validation on all API endpoints
- Log structured JSON, never log sensitive data
- Tests required for all new logic

---

## Testing Requirements

All pull requests must include tests. We require:

| Type | Location | Framework |
|---|---|---|
| Unit tests | `tests/unit/` | Pytest (backend), Vitest (frontend) |
| Integration tests | `tests/integration/` | Pytest |
| E2E tests | `tests/e2e/` | Playwright (planned) |

Run tests before submitting:

```bash
# Backend tests
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

Minimum coverage: 80% for new modules.

---

## Pull Request Process

1. Ensure all tests pass locally.
2. Ensure linting passes without errors.
3. Update documentation if you are changing behavior or interfaces.
4. Open a pull request against the `main` branch.
5. Fill in the pull request template completely.
6. Request a review from at least one maintainer.
7. Address all review feedback before merge.

### Pull Request Checklist

- [ ] Tests added or updated
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Linting passes
- [ ] Follows coding standards
- [ ] Conventional commit messages

---

## Reporting Bugs

Please use the GitHub Issues tracker. Include:

1. A clear, descriptive title
2. Steps to reproduce the issue
3. Expected vs. actual behavior
4. Environment details (OS, Python version, Node version)
5. Relevant logs or screenshots

---

## Feature Requests

Open a GitHub Discussion or Issue with the `enhancement` label. Include:

1. The problem you want to solve
2. Your proposed solution
3. Alternative approaches considered
4. How this fits with the project design philosophy

---

## Security Issues

**Do not open public issues for security vulnerabilities.**

Please follow the responsible disclosure process in [SECURITY.md](SECURITY.md).

---

## Recognition

All contributors are recognized in the project. Thank you for helping build a trustworthy intelligence ecosystem.
