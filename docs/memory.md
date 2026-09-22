# Spend Tracker — Project Context & Progress

## Project Purpose

This repository implements a small Spend Tracker application for a coding assignment.

The primary evaluation areas are:
- backend/API correctness
- database usage
- validation
- business logic
- testing
- code quality
- basic security
- end-to-end frontend integration

The application should remain intentionally small.

## Current Technical Direction

Backend:
- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic/Pydantic Settings
- pytest

Frontend:
- Vanilla HTML/CSS/JavaScript
- Responsive light UI

## Core Requirements

1. POST /expenses
2. GET /expenses
3. GET /summary
4. SQLite persistence
5. Validation
6. Automated tests
7. Minimal UI
8. README

## Security Requirements

- Environment-based configuration.
- `.env` never committed.
- `.env.example` contains placeholders only.
- No hardcoded credentials or security keys.
- Configurable rate limiting.
- Idempotent expense creation.
- Safe error responses.
- No secret logging.
- Explicit CORS.
- Reasonable request/input limits.

## Database Requirements

Use SQLAlchemy rather than handwritten SQL.

Do not hardcode SQL queries into application code.

Use database constraints for important invariants.

Money must be handled with Decimal-safe logic.

## Idempotency Contract

`POST /expenses` accepts:

`Idempotency-Key`

Same key + same request:
- return the original successful response.

Same key + different request:
- return HTTP 409.

The database must enforce uniqueness.

## Summary Definition

Summary defaults to the current calendar month.

It contains:
- total current-month spend
- current-month spend by category
- previous-month total
- month-over-month percentage change

If previous-month spend is zero, percentage change must not cause division by zero.

## Current Progress

Status: Complete and verified.

### Completed
- [x] Requirements defined.
- [x] Architecture defined.
- [x] Coding/security rules defined.
- [x] UI/UX direction defined.
- [x] Implementation task list defined.
- [x] Backend implementation (FastAPI, Pydantic v2, layered services).
- [x] Database implementation (SQLAlchemy 2.x, SQLite, Decimal-safe currency handling).
- [x] API implementation (POST /expenses, GET /expenses, GET /summary, GET /health).
- [x] Idempotency (database-backed, transactionally secured with unique constraint).
- [x] Rate limiting (configurable in-process sliding-window limiter).
- [x] Automated tests (26/26 tests passing covering creation, listing, summary, idempotency, security).
- [x] Frontend integration (responsive Stitch UI wired to live backend API, XSS safe, real CSV export).
- [x] Basic API-key authentication reverted and replaced by industry-standard JWT authentication.
- [x] Category spending insight when spending increases >20% MoM with zero-division safety.
- [x] User registration with password hashing (bcrypt), confirm password validation, and SHA-256 tokenized email verification.
- [x] SMTP email dispatch service with graceful local/testing mock handling.
- [x] Dedicated Stitch-themed Login (`/login`), Signup (`/signup`), and Email Verification (`/verify`) pages with eye show/hide password toggles.
- [x] Strict user expense ownership and data isolation across all expense listing and summary analytics queries.
- [x] Automated test suite expanded to 46 comprehensive tests (100% passing across auth, expenses, summary, idempotency, security, and bonus insights).
- [x] Frontend dashboard route guard and header user profile/logout controls.

## Working Rules for Future Agents

Before changing code:
1. Read `product.md`.
2. Read `architecture.md`.
3. Read `rules.md`.
4. Check `tasks.md` and `memory.md`.
5. Inspect existing implementation before creating new files.
6. Do not rewrite working code without a concrete reason.
7. Do not introduce a new dependency unless it solves a real requirement.
8. Do not add speculative features.
9. Keep changes focused and test them.

After implementation:
1. Update `tasks.md`.
2. Update the progress section of this file.
3. Run tests.
4. Perform a security/configuration review.
5. Confirm no secrets or generated artifacts were accidentally committed.

## Important Non-Goals

Do not turn this into a large enterprise system.

Avoid:
- unnecessary microservices
- unnecessary repositories/abstractions
- complex frontend frameworks
- excessive dependencies
- over-engineered event systems
- unnecessary background workers
- hardcoded configuration
- raw SQL embedded in business code
- comments that merely restate the code

## Future Production Direction

If this application grows beyond the assignment:
- PostgreSQL for persistent multi-user production workloads.
- Alembic for schema migrations.
- Redis for distributed rate limiting/idempotency if required.
- Proper authentication/authorization.
- Structured logging and monitoring.
- CI/CD.
- Containerized deployment.
- Automated security/dependency scanning.

These should remain future improvements unless the assignment explicitly requires them.
