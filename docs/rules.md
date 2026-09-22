# Spend Tracker — Coding Rules

## General
1. Write clean, small, readable production-quality code.
2. Prefer straightforward solutions over clever abstractions.
3. Do not add functionality that is not required.
4. Do not leave dead code, unused imports, placeholders, or debugging statements.
5. Do not duplicate business logic.
6. Avoid unnecessary comments. Code should explain itself; comment only non-obvious decisions.

## Python
1. Follow PEP 8.
2. Use type hints for public functions and important internal functions.
3. Prefer explicit names over abbreviations.
4. Keep functions focused on one responsibility.
5. Avoid broad `except Exception` unless it is at a deliberate application boundary and the error is logged safely.
6. Never use `print()` for application logging.
7. Use structured/standard logging.
8. Do not silently swallow exceptions.

## FastAPI
1. Use Pydantic schemas for request and response validation.
2. Keep routers thin.
3. Business logic belongs in services.
4. Database access belongs in repositories/data-access functions.
5. Use appropriate HTTP status codes.
6. Return consistent error structures.
7. Never expose stack traces in API responses.

## Database
1. Use SQLAlchemy ORM/query APIs.
2. Do not hardcode raw SQL query strings in application code.
3. Use database constraints for invariants such as uniqueness.
4. Use transactions for multi-step writes.
5. Avoid N+1 query patterns.
6. Never construct SQL by string concatenation from user input.
7. Add indexes only where justified by actual query patterns.
8. Use migrations if the project introduces schema migration tooling.

## Security
1. No secrets in source code.
2. No API keys, passwords, JWT secrets, database credentials, or private tokens in Git.
3. Read security-sensitive configuration from environment variables.
4. `.env` must be ignored by Git.
5. `.env.example` must contain placeholders, not real credentials.
6. Validate all external input.
7. Apply reasonable length/range limits.
8. Do not trust client-provided identifiers or metadata.
9. Do not return internal exception messages to clients.
10. Do not log secrets.
11. Configure CORS explicitly.
12. Use rate limiting.
13. Use idempotency for expense creation.
14. Protect against duplicate database writes with database constraints, not only application checks.

## API Design
1. Use RESTful endpoint semantics.
2. POST creates resources.
3. GET is read-only.
4. Use query parameters for filtering.
5. Validate date ranges.
6. Paginate list endpoints.
7. Return deterministic ordering.
8. Document edge cases.

## Money
1. Never use float arithmetic for financial calculations.
2. Use Decimal in Python.
3. Store money in a suitable database numeric representation.
4. Define rounding behavior explicitly.

## Testing
1. Test core business logic.
2. Test validation failures.
3. Test filtering.
4. Test summary calculations.
5. Test zero previous-month spending.
6. Test idempotency.
7. Test conflicting idempotency keys.
8. Test rate limiting behavior where practical.
9. Tests must not depend on the production database.
10. Tests must be deterministic.

## Frontend
1. Keep the frontend lightweight.
2. Do not duplicate backend business rules.
3. Never place secrets in frontend JavaScript.
4. Handle loading and API errors.
5. Validate basic form input client-side for UX, but always rely on backend validation for security.
6. Avoid unnecessary dependencies.

## Git
1. Small, meaningful commits.
2. Never commit `.env`, databases containing sensitive data, caches, virtual environments, or build artifacts.
3. Keep README setup instructions reproducible.
