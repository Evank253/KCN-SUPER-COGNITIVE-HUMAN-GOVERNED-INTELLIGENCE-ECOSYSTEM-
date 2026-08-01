# API Reference

KCN Super Cognitive Human Governed Intelligence Ecosystem — REST API v1

Base URL: `http://localhost:8000/api/v1`

Interactive documentation (Swagger UI): `http://localhost:8000/docs`

Alternative documentation (ReDoc): `http://localhost:8000/redoc`

---

## Authentication

All protected endpoints require a ****** in the `Authorization` header:

```
Authorization: ******
```

Obtain a token via the `/auth/login` endpoint.

---

## Endpoints

### Health

#### `GET /health`

Check service health. No authentication required.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-08-01T00:00:00Z"
}
```

---

### Authentication

#### `POST /api/v1/auth/login`

Authenticate a user and receive access and refresh tokens.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response 200:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Response 401:**
```json
{
  "detail": "Invalid credentials"
}
```

---

#### `POST /api/v1/auth/refresh`

Refresh an access token using a valid refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response 200:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

#### `POST /api/v1/auth/logout`

Invalidate the current session. Requires authentication.

**Response 200:**
```json
{
  "message": "Logged out successfully"
}
```

---

### Governance

#### `GET /api/v1/governance/policies`

List all active governance policies. Requires `admin` or `governance_viewer` role.

**Response 200:**
```json
{
  "policies": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "enabled": true,
      "created_at": "2026-08-01T00:00:00Z",
      "updated_at": "2026-08-01T00:00:00Z"
    }
  ],
  "total": 0
}
```

---

#### `POST /api/v1/governance/approvals`

Submit a request for human approval. Requires authentication.

**Request Body:**
```json
{
  "action_type": "string",
  "description": "string",
  "data": {}
}
```

**Response 201:**
```json
{
  "id": "string",
  "status": "pending",
  "created_at": "2026-08-01T00:00:00Z"
}
```

---

### Intelligence

#### `POST /api/v1/intelligence/analyze`

Submit a request to the Intelligence Core for analysis. Requires authentication.

**Request Body:**
```json
{
  "query": "string",
  "context": {},
  "module": "analysis"
}
```

**Response 200:**
```json
{
  "id": "string",
  "status": "pending_verification",
  "result": null,
  "created_at": "2026-08-01T00:00:00Z"
}
```

---

### Verification

#### `GET /api/v1/verification/results/{result_id}`

Retrieve verification results for an intelligence output. Requires authentication.

**Path Parameters:**
- `result_id` (string): The ID of the intelligence result to verify.

**Response 200:**
```json
{
  "id": "string",
  "intelligence_result_id": "string",
  "status": "verified",
  "confidence_score": 0.95,
  "checks": [
    {
      "type": "logic_validation",
      "passed": true,
      "notes": "string"
    }
  ],
  "verified_at": "2026-08-01T00:00:00Z"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

| Status Code | Meaning |
|---|---|
| 400 | Bad Request — Invalid input |
| 401 | Unauthorized — Missing or invalid token |
| 403 | Forbidden — Insufficient permissions |
| 404 | Not Found — Resource does not exist |
| 422 | Unprocessable Entity — Validation error |
| 429 | Too Many Requests — Rate limit exceeded |
| 500 | Internal Server Error — Server-side error |

---

## Versioning

The API is versioned via URL prefix (`/api/v1/`, `/api/v2/`, etc.).

Breaking changes will always result in a new API version. Previous versions will be supported for a minimum of 6 months after a new version is released.

---

## Rate Limiting

Rate limiting is planned for Phase 2. Limits will be communicated via response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1722470400
```

---

## OpenAPI Specification

The full OpenAPI 3.1 specification is available at:
- JSON: `http://localhost:8000/openapi.json`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
