from unittest.mock import patch
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.middleware.rate_limit import reset_rate_limits


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rate_limiting(client):
    reset_rate_limits()
    original_limit = settings.rate_limit_requests
    settings.rate_limit_requests = 3
    settings.rate_limit_window_seconds = 60

    try:
        # 3 allowed requests
        for _ in range(3):
            res = client.get("/expenses")
            assert res.status_code == 200

        # 4th request must be rate limited
        res = client.get("/expenses")
        assert res.status_code == 429
        assert "Rate limit exceeded" in res.json()["detail"]
        assert "Retry-After" in res.headers
    finally:
        settings.rate_limit_requests = original_limit
        reset_rate_limits()


def test_request_body_size_limit(client):
    headers = {
        "Content-Length": str(settings.max_body_size_bytes + 100),
        "Content-Type": "application/json",
    }
    response = client.post("/expenses", content=b"{}", headers=headers)
    assert response.status_code == 413
    assert "Request payload exceeds allowed maximum size" in response.json()["detail"]


def test_internal_server_error_does_not_leak_stack_trace(auth_headers):
    # Use client with raise_server_exceptions=False to test production 500 handler
    with TestClient(app, raise_server_exceptions=False) as safe_client:
        safe_client.headers.update(auth_headers)
        with patch("app.services.summary_service.summary_service.get_summary", side_effect=RuntimeError("Secret database credentials /var/lib/db")):
            response = safe_client.get("/summary")
            assert response.status_code == 500
            data = response.json()
            assert data == {"detail": "An unexpected internal server error occurred."}
            # Verify no traceback or internal text is exposed
            assert "traceback" not in response.text.lower()
            assert "credentials" not in response.text.lower()
