# Spend Tracker

## Overview

Spend Tracker is a lightweight, secure, and production-minded expense tracking web application. It enables users to record transactions with decimal-safe financial precision, filter and paginate expenses, and view real-time monthly summaries with month-over-month spending insights. The application is built with Python FastAPI, SQLAlchemy 2.x, SQLite, and a responsive modern dashboard served directly from the backend.

## Features

- **Expense Management**: Log, view, and manage expenses with strict decimal precision arithmetic.
- **Filtering & Pagination**: Search and filter ledger entries by category and date ranges with server-side pagination.
- **Monthly Spending Summary**: Automatic aggregation of total spend, transaction counts, and month-over-month (MoM) comparisons.
- **Category Spending Insights**: Automated flagging when spending in any category increases by more than 20% compared to the prior month.
- **JWT Authentication**: User registration, login, and token-based authentication with user data isolation and live password complexity validation.
- **Email Verification**: SMTP-driven email verification flow with secure, expiring activation tokens.
- **Transactional Idempotency**: Header-based idempotency (`Idempotency-Key`) preventing duplicate expense submissions.
- **Security & Protection**: In-process sliding-window rate limiting, request body size limits, and sanitized error responses.
- **Responsive Dashboard**: Dynamic UI with month-by-month navigation, category breakdowns, and a budget health gauge.
- **Automated Tests**: Comprehensive test coverage spanning authentication, security, business logic, and API validation.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Database & ORM**: SQLite, SQLAlchemy 2.x
- **Authentication**: JWT (PyJWT), bcrypt password hashing
- **Email Service**: Python standard library `smtplib` (TLS / HTML multipart)
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, Tailwind CSS
- **Testing**: pytest, httpx
- **Containerization**: Docker, Docker Compose

## Project Structure

```text
Spend-Tracker/
├── app/                  # FastAPI backend (routers, services, models, repositories)
├── frontend/             # Single-page dashboard, auth views, and static assets
├── tests/                # Automated test suite (49 unit and integration tests)
├── docs/                 # Product specifications, architecture, and design docs
├── data/                 # SQLite database persistence directory
├── .env.example          # Environment variables template
├── Dockerfile            # Container build definition
├── docker-compose.yml    # Multi-container orchestration & volumes
└── requirements.txt      # Pinned Python dependencies
```

## Local Setup

### Prerequisites
- Python 3.11 or higher
- Git

### Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Spend-Tracker
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

5. **Start the application**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Environment Configuration

Configure application behavior via the `.env` file. Use `.env.example` as the source of truth for available options:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `APP_ENV` | Runtime environment (`development`, `production`) | `development` |
| `DATABASE_URL` | SQLite database file connection string | `sqlite:///./data/spend_tracker.db` |
| `JWT_SECRET_KEY` | Secret key used for signing JWT tokens | (Set a strong secret) |
| `JWT_ALGORITHM` | JWT cryptographic algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan in minutes | `60` |
| `SMTP_HOST` | Outbound mail server hostname | `smtp.example.com` |
| `SMTP_PORT` | Outbound mail server port | `587` |
| `SMTP_USERNAME` | SMTP authentication username | `noreply@example.com` |
| `SMTP_PASSWORD` | SMTP authentication password | (Set your SMTP password) |
| `SMTP_FROM_EMAIL` | Sender address on outgoing verification emails | `noreply@example.com` |
| `SMTP_USE_TLS` | Enable TLS encryption for mail transport | `true` |
| `APP_BASE_URL` | Public base URL used in email activation links | `http://localhost:8000` |
| `RATE_LIMIT_REQUESTS` | Allowed requests per client within rate limit window | `100` |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit sliding window duration in seconds | `60` |
| `MAX_BODY_SIZE_BYTES` | Maximum accepted HTTP request body size in bytes | `1048576` (1 MB) |

> **Note**: Never commit real credentials, passwords, or production JWT secrets to version control.

## Docker

Run the entire application within an isolated Docker container with volume-backed persistence and hot-reload support:

```bash
# Build and start the service in the background
docker compose up --build -d

# View real-time container logs
docker compose logs -f

# Stop the application
docker compose down
```

## Running Tests

Run the full automated test suite using `pytest`:

```bash
# Run locally within your virtual environment
pytest -v

# Or run inside the Docker container
docker compose exec spend-tracker pytest -v
```

The test suite validates core expense operations, JWT authentication and user isolation, input boundary conditions, sliding-window rate limiting, transactional idempotency, and month-over-month category spending anomaly insights.

## Application URLs

When running locally, the following routes are available:

- **Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **Sign In**: [http://localhost:8000/login](http://localhost:8000/login)
- **Sign Up**: [http://localhost:8000/signup](http://localhost:8000/signup)
- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

## AI-Assisted Development

AI tools were utilized during the development of this project for:
- Requirements analysis and domain boundary modeling
- Implementation assistance across backend services and frontend controllers
- Debugging edge cases in database migrations and date-range filtering
- Test-case suggestions covering security and idempotency constraints
- Code review and refactoring suggestions

All AI-generated recommendations were human-reviewed. Suggestions that did not align with project requirements, introduced unnecessary dependencies, or added premature architectural complexity were modified or rejected.
