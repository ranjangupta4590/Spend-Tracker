# Spend Tracker — Project Architecture

## 1. Architecture Style

Use a small layered architecture:

```text
Frontend
   |
   | HTTP/JSON
   v
FastAPI Routers
   |
   v
Application/Service Layer
   |
   v
SQLAlchemy Repository/Data Access
   |
   v
SQLite
```

Keep HTTP concerns, business rules, and persistence concerns separated.

## 2. Recommended Structure

```text
spend-tracker/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── middleware/
│   │   └── rate_limit.py
│   ├── routers/
│   │   ├── expenses.py
│   │   └── summary.py
│   ├── services/
│   │   ├── expense_service.py
│   │   └── summary_service.py
│   └── repositories/
│       └── expense_repository.py
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── tests/
│   ├── conftest.py
│   ├── test_expenses.py
│   ├── test_summary.py
│   └── test_security.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The exact structure may be simplified if a smaller implementation remains clean. Do not create files merely to satisfy the structure.

## 3. Technology Choices

Backend:
- Python 3.11+ or the project's explicitly supported Python version.
- FastAPI.
- Pydantic/Pydantic Settings.
- SQLAlchemy 2.x.
- SQLite for local/assignment persistence.
- Uvicorn.

Testing:
- pytest.
- FastAPI TestClient/httpx.

Frontend:
- Plain HTML/CSS/JavaScript unless an existing frontend stack is already required.

## 4. Database

Primary entity:

```text
Expense
- id
- amount
- category
- note
- expense_date
- created_at
- updated_at
```

For idempotency:

```text
IdempotencyRecord
- id
- key
- request_hash
- response_status
- response_body
- created_at
```

The idempotency key must have a unique database constraint.

Use SQLAlchemy ORM/query expressions. Do not embed ad-hoc SQL strings in application code.

## 5. Money Handling

Do not perform business calculations using binary floating-point values.

Use a database numeric/decimal representation and Decimal in Python for monetary calculations. API serialization should produce predictable numeric values.

## 6. Request Flow

POST /expenses:

```text
Request
 -> validation
 -> rate-limit check
 -> idempotency check
 -> service validation/business rules
 -> repository/database transaction
 -> response
```

GET /expenses:

```text
Request
 -> query parameter validation
 -> rate-limit check
 -> repository query
 -> pagination
 -> response
```

GET /summary:

```text
Request
 -> rate-limit check
 -> service
 -> aggregate database queries
 -> Decimal-safe calculations
 -> response
```

## 7. Transactions

Expense creation and its idempotency record must be handled transactionally so a successful response cannot leave inconsistent state.

Avoid committing multiple unrelated partial transactions for one operation.

## 8. Security

- Read configuration from environment variables.
- Never commit `.env`.
- Provide `.env.example` containing placeholders only.
- Never hardcode API keys, passwords, signing secrets, or tokens.
- Validate and constrain all user-controlled input.
- Rate-limit write and read endpoints.
- Avoid exposing stack traces or internal database errors to clients.
- Return generic production-safe errors while logging useful server-side diagnostics.
- Do not log secrets or sensitive request headers.
- Configure CORS explicitly from environment configuration rather than allowing arbitrary origins in production.
- Restrict request body size where practical.
- Use secure HTTP deployment configuration when deployed publicly.

## 9. Idempotency

POST /expenses should accept `Idempotency-Key`.

Rules:
- Key must be non-empty and have a reasonable maximum length.
- Store a hash of the normalized request body with the key.
- Same key + same request should return the original result.
- Same key + different request should return HTTP 409.
- The uniqueness constraint must be enforced by the database.
- Idempotency records should have a documented retention strategy.

## 10. Rate Limiting

Use a simple, maintainable rate limiter appropriate to the deployment.

For a single-process assignment deployment, an in-process limiter may be acceptable.

For multi-instance production deployment, use a shared store such as Redis.

Do not pretend an in-memory limiter provides distributed protection.

Rate-limit configuration must come from environment variables.

## 11. Observability

Use Python logging rather than print statements.

Log:
- request failures
- unexpected server errors
- important security events

Do not log:
- API keys
- authorization headers
- secrets
- full sensitive payloads

## 12. Deployment Evolution

SQLite is acceptable for this assignment.

For production multi-instance deployment:
- PostgreSQL
- Redis for distributed rate limiting if needed
- Alembic for migrations
- HTTPS/reverse proxy
- centralized logs/metrics

Do not implement this infrastructure unless required.
