# Spend Tracker — Implementation Tasks

## Phase 0 — Project Setup
- [x] Initialize Git repository / workspace setup.
- [x] Create Python virtual environment.
- [x] Add FastAPI, SQLAlchemy, Pydantic Settings, Uvicorn, pytest, httpx.
- [x] Create `.gitignore`.
- [x] Create `.env.example`.
- [x] Confirm `.env` is ignored.
- [x] Create comprehensive README.

## Phase 1 — Configuration
- [x] Create environment-based configuration.
- [x] Configure database URL.
- [x] Configure CORS origins.
- [x] Configure rate-limit settings.
- [x] Configure environment/app mode.
- [x] Ensure no security values are hardcoded.

## Phase 2 — Database
- [x] Create SQLAlchemy base/database setup.
- [x] Create Expense model.
- [x] Create idempotency record model.
- [x] Add appropriate constraints.
- [x] Add useful indexes based on query patterns.
- [x] Implement transaction handling.
- [x] Avoid raw SQL strings.

## Phase 3 — Schemas
- [x] Create expense create schema.
- [x] Create expense response schema.
- [x] Create expense list/filter schema or validated query parameters.
- [x] Create summary response schemas.
- [x] Add field length/range validation.
- [x] Add date validation.
- [x] Ensure Decimal-safe money handling.

## Phase 4 — Expense API
- [x] Implement POST /expenses.
- [x] Implement GET /expenses.
- [x] Add category filtering.
- [x] Add start/end date filtering.
- [x] Add pagination.
- [x] Add deterministic ordering.
- [x] Add proper HTTP status codes.
- [x] Add safe error handling.

## Phase 5 — Idempotency
- [x] Accept `Idempotency-Key`.
- [x] Normalize/hash request payload.
- [x] Persist idempotency record transactionally.
- [x] Return original result for repeated identical requests.
- [x] Return 409 for same key with different payload.
- [x] Enforce unique key at database level.
- [x] Add tests for retries and conflicts.

## Phase 6 — Summary
- [x] Implement total current-month spend.
- [x] Implement spend by category.
- [x] Implement previous-month total.
- [x] Implement month-over-month percentage.
- [x] Handle previous-month zero safely.
- [x] Add optional category increase insight (>20%).

## Phase 7 — Rate Limiting & Security
- [x] Implement configurable rate limiting.
- [x] Apply appropriate limits to read/write endpoints.
- [x] Configure CORS from environment.
- [x] Add request validation limits.
- [x] Ensure no secrets are logged.
- [x] Ensure internal exceptions are not exposed.
- [x] Review dependency versions.
- [x] Add security-focused tests where practical.

## Phase 8 — Tests
- [x] Test valid expense creation.
- [x] Test zero/negative amount.
- [x] Test invalid category.
- [x] Test invalid date.
- [x] Test expense listing.
- [x] Test category filter.
- [x] Test date filter.
- [x] Test invalid date range.
- [x] Test pagination.
- [x] Test summary total.
- [x] Test category aggregation.
- [x] Test month-over-month calculation.
- [x] Test previous-month zero.
- [x] Test idempotent retry.
- [x] Test idempotency conflict.
- [x] Test rate-limit behavior.
- [x] Ensure tests use an isolated database.

## Phase 9 — Frontend
- [x] Create responsive layout.
- [x] Create Add Expense form.
- [x] Connect POST /expenses.
- [x] Display summary.
- [x] Display category breakdown.
- [x] Display recent expenses.
- [x] Add loading states.
- [x] Add empty states.
- [x] Add API error states.
- [x] Verify mobile layout.

## Phase 10 — Quality Review
- [x] Remove unused code/imports.
- [x] Remove unnecessary comments.
- [x] Check for duplicated logic.
- [x] Check for hardcoded secrets/config.
- [x] Check for raw SQL strings.
- [x] Check error responses.
- [x] Check database transactions.
- [x] Run full test suite (26/26 passed).
- [x] Manually test end-to-end flow.
- [x] Verify README documentation.

## Phase 11 — Optional Deployment
- [x] Add Dockerfile for containerized deployment.
- [x] Configure docker-compose.yml with persistent SQLite volume.
- [x] Verify docker compose build works cleanly.
- [x] Verify CORS and health check (/health).
- [x] Verify persistent database behavior.

## Phase 12 — JWT Authentication & Verification Flow
- [x] Revert API-key authentication method in favor of JWT Bearer tokens.
- [x] Add `pyjwt`, `bcrypt`, `email-validator` dependencies.
- [x] Implement User model with email verification fields and CASCADE foreign key on Expense.
- [x] Implement UserRepository with email lookup and verification token querying.
- [x] Implement AuthService with bcrypt hashing, constant-time verification, and JWT issuance/decoding.
- [x] Implement EmailService with SMTP dispatch and graceful dev/test mock fallback.
- [x] Implement `POST /auth/signup` with password confirmation and format validation.
- [x] Implement `POST /auth/login` requiring verified status.
- [x] Implement `GET /auth/verify-email` with single-use hashed token invalidation.
- [x] Implement `GET /auth/me` for authenticated user profile retrieval.
- [x] Strict user expense ownership and data isolation on `/expenses` and `/summary`.
- [x] Stitch-themed Login UI (`/login`) with eye show/hide password toggle.
- [x] Stitch-themed Signup UI (`/signup`) with eye show/hide password and confirm password toggles.
- [x] Stitch-themed Email Verification UI (`/verify`).
- [x] Dashboard route guard redirecting unauthenticated sessions to `/login`.
- [x] Header profile display and logout button.
- [x] Category spending increase insight (>20% MoM) in `/summary` response.
- [x] Division by zero safe handling when previous month is 0.
- [x] Strictly >20% threshold enforcement (exactly 20% is not flagged).
- [x] Automated test suite expanded to 46 tests (46/46 passed).

## Definition of Done
- [x] Required API endpoints work.
- [x] Data persists in SQLite with multi-user relational schema.
- [x] Validation works.
- [x] Filters work.
- [x] Summary is correct.
- [x] Idempotency works.
- [x] Rate limiting is configured.
- [x] JWT Bearer authentication implemented and verified.
- [x] SMTP email verification flow implemented and verified.
- [x] Login and Signup pages match Stitch design with password eye toggles.
- [x] Category spending insight implemented and verified (>20% threshold).
- [x] Automated tests pass (46/46 passed).
- [x] UI works end-to-end.
- [x] No secrets are committed.
- [x] No unnecessary raw SQL exists.
- [x] README explains setup and design decisions.
