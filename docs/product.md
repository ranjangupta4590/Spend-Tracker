# Spend Tracker — Product Requirements

## 1. Product Overview
Spend Tracker is a small, secure expense-management application that allows a user to record expenses, browse/filter them, and view spending summaries.

The implementation should be intentionally small, maintainable, testable, and production-minded without adding unnecessary features.

## 2. Goals
- Create and persist expenses in a real database.
- List expenses with category and date-range filters.
- Provide total spend, spend by category, and month-over-month change.
- Provide a minimal responsive frontend for end-to-end verification.
- Include automated tests for core business logic and important failure cases.
- Apply basic API security, validation, rate limiting, and idempotency where appropriate.
- Keep secrets/configuration outside source code.

## 3. Required API

### POST /expenses
Create an expense.

Request:
```json
{
  "amount": 450.50,
  "category": "Food",
  "note": "Lunch",
  "date": "2026-09-22"
}
```

Requirements:
- amount must be greater than zero.
- category is required and trimmed.
- note is optional.
- date must be a valid calendar date.
- Persist the record in the database.
- Return HTTP 201 on successful creation.
- Support an idempotency key so safe retries do not create duplicate expenses.

Recommended header:
`Idempotency-Key: <unique-client-generated-key>`

### GET /expenses
List expenses.

Supported query parameters:
- `category`
- `start_date`
- `end_date`
- sensible pagination parameters

Requirements:
- Validate date ranges.
- Return deterministic ordering.
- Do not load unbounded records into memory.

### GET /summary
Return:
- total spend for the current month
- spend by category for the current month
- previous month total
- month-over-month percentage change

If the previous month has zero spend, avoid division by zero and return a clearly documented null/appropriate representation.

## 4. Optional Enhancements
Only implement after all required functionality is complete:
- API-key authentication.
- Category-level insight when current-month spending increases by more than 20%.
- Public deployment.

## 5. Frontend
Provide a lightweight responsive UI:
- Add Expense form.
- Summary cards.
- Category breakdown.
- Recent expenses list.
- Loading, success, and error states.

Visual polish is secondary to correctness and usability.

## 6. Non-Functional Requirements
- Python backend.
- Real persistent database; SQLite is acceptable for this assignment.
- Strong input validation.
- Consistent HTTP error responses.
- Automated tests.
- Secure configuration through environment variables.
- No credentials, tokens, API keys, or security secrets committed to source.
- No unnecessary raw SQL strings in application code. Prefer SQLAlchemy models/query APIs.
- No in-memory-only persistence.
- No dead code, placeholder code, duplicated logic, or unnecessary comments.
- Avoid premature abstraction.

## 7. Acceptance Criteria
A reviewer must be able to:
1. Install dependencies.
2. Start the application.
3. Create an expense through the UI/API.
4. Retrieve and filter expenses.
5. View the summary.
6. Run automated tests successfully.
7. Understand setup and design decisions from README documentation.
