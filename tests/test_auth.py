from datetime import datetime, timedelta, timezone
import pytest
from app.models import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import auth_service
from app.services.email_service import email_service


def test_signup_success(unauthed_client, db_session):
    payload = {
        "email": "newuser@example.com",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!",
    }
    res = unauthed_client.post("/auth/signup", json=payload)
    assert res.status_code == 201
    assert "Account created" in res.json()["message"]

    # User is in database as unverified
    user = UserRepository.get_by_email(db_session, "newuser@example.com")
    assert user is not None
    assert user.is_verified is False
    assert user.verification_token_hash is not None
    assert user.password_hash != "StrongPassword123!"

    # Email service captured token
    assert email_service.last_sent_email is not None
    assert email_service.last_sent_email["recipient"] == "newuser@example.com"
    assert "/verify?token=" in email_service.last_sent_email["link"]


def test_signup_password_mismatch(unauthed_client):
    payload = {
        "email": "mismatch@example.com",
        "password": "Password123!",
        "confirm_password": "DifferentPassword123!",
    }
    res = unauthed_client.post("/auth/signup", json=payload)
    assert res.status_code == 422


def test_signup_password_too_short(unauthed_client):
    payload = {
        "email": "short@example.com",
        "password": "short",
        "confirm_password": "short",
    }
    res = unauthed_client.post("/auth/signup", json=payload)
    assert res.status_code == 422


def test_signup_password_missing_number(unauthed_client):
    payload = {
        "email": "nonum@example.com",
        "password": "PasswordOnly!",
        "confirm_password": "PasswordOnly!",
    }
    res = unauthed_client.post("/auth/signup", json=payload)
    assert res.status_code == 422


def test_signup_password_missing_letter(unauthed_client):
    payload = {
        "email": "noletter@example.com",
        "password": "1234567890!@",
        "confirm_password": "1234567890!@",
    }
    res = unauthed_client.post("/auth/signup", json=payload)
    assert res.status_code == 422


def test_signup_password_missing_special_char(unauthed_client):
    payload = {
        "email": "nospecial@example.com",
        "password": "Password12345",
        "confirm_password": "Password12345",
    }
    res = unauthed_client.post("/auth/signup", json=payload)
    assert res.status_code == 422


def test_signup_duplicate_email(unauthed_client, test_user):
    payload = {
        "email": test_user.email,
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    res = unauthed_client.post("/auth/signup", json=payload)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]


def test_login_unverified_account(unauthed_client):
    signup_payload = {
        "email": "unverified@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    unauthed_client.post("/auth/signup", json=signup_payload)

    login_res = unauthed_client.post(
        "/auth/login",
        json={"email": "unverified@example.com", "password": "Password123!"},
    )
    assert login_res.status_code == 403
    assert "not verified" in login_res.json()["detail"]


def test_verify_email_success(unauthed_client):
    unauthed_client.post(
        "/auth/signup",
        json={
            "email": "verify_me@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    token = email_service.last_sent_email["token"]

    verify_res = unauthed_client.get(f"/auth/verify-email?token={token}")
    assert verify_res.status_code == 200
    assert "Email verified" in verify_res.json()["message"]

    login_res = unauthed_client.post(
        "/auth/login",
        json={"email": "verify_me@example.com", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()
    assert login_res.json()["token_type"] == "bearer"


def test_verify_email_invalid_token(unauthed_client):
    res = unauthed_client.get("/auth/verify-email?token=invalid-bogus-token-123")
    assert res.status_code == 400
    assert "Invalid or expired" in res.json()["detail"]


def test_verify_email_expired_token(unauthed_client, db_session):
    raw_token = "expired_raw_token_xyz"
    token_hash = auth_service.hash_token(raw_token)
    expired_time = datetime.now(timezone.utc) - timedelta(hours=1)

    user = User(
        email="expired@example.com",
        password_hash=auth_service.hash_password("Password123!"),
        is_verified=False,
        verification_token_hash=token_hash,
        verification_token_expires_at=expired_time,
    )
    db_session.add(user)
    db_session.commit()

    res = unauthed_client.get(f"/auth/verify-email?token={raw_token}")
    assert res.status_code == 400
    assert "expired" in res.json()["detail"]


def test_login_invalid_password(unauthed_client, test_user):
    res = unauthed_client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "WrongPassword123!"},
    )
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]


def test_login_nonexistent_email(unauthed_client):
    res = unauthed_client.post(
        "/auth/login",
        json={"email": "doesnotexist@example.com", "password": "Password123!"},
    )
    assert res.status_code == 401


def test_protected_routes_unauthenticated(unauthed_client):
    res1 = unauthed_client.get("/expenses")
    assert res1.status_code == 401

    res2 = unauthed_client.post("/expenses", json={"amount": 50, "category": "Food", "date": "2026-09-22"})
    assert res2.status_code == 401

    res3 = unauthed_client.get("/summary")
    assert res3.status_code == 401

    res4 = unauthed_client.get("/auth/me")
    assert res4.status_code == 401


def test_protected_routes_invalid_token(unauthed_client):
    unauthed_client.headers["Authorization"] = "Bearer invalid.jwt.token"
    res = unauthed_client.get("/expenses")
    assert res.status_code == 401


def test_get_current_user_profile(client, test_user):
    res = client.get("/auth/me")
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id
    assert data["is_verified"] is True


def test_user_data_isolation(db_session, test_user, auth_headers, unauthed_client):
    # Create second user
    user2 = User(
        email="user2@example.com",
        password_hash=auth_service.hash_password("Password123!"),
        is_verified=True,
    )
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user2)
    user2_token = auth_service.create_access_token(user_id=user2.id, email=user2.email)

    # User 1 client
    client_user1 = unauthed_client
    client_user1.headers.update(auth_headers)

    # User 1 posts an expense
    res1 = client_user1.post(
        "/expenses",
        json={"amount": 150.00, "category": "Travel", "date": "2026-09-10"},
    )
    assert res1.status_code == 201

    # User 2 headers
    client_user2 = client_user1
    client_user2.headers["Authorization"] = f"Bearer {user2_token}"

    # User 2 posts an expense
    res2 = client_user2.post(
        "/expenses",
        json={"amount": 50.00, "category": "Food", "date": "2026-09-10"},
    )
    assert res2.status_code == 201

    # User 2 lists expenses -> sees ONLY User 2's expense
    u2_expenses = client_user2.get("/expenses").json()
    assert u2_expenses["total"] == 1
    assert u2_expenses["items"][0]["category"] == "Food"
    assert u2_expenses["items"][0]["amount"] == 50.00

    # User 2 summary -> sees ONLY User 2's spending
    u2_summary = client_user2.get("/summary?year=2026&month=9").json()
    assert u2_summary["total_spend"] == 50.00
    assert u2_summary["transaction_count"] == 1
    assert "Food" in u2_summary["spend_by_category"]
    assert "Travel" not in u2_summary["spend_by_category"]

    # Switch back to User 1
    client_user1.headers.update(auth_headers)
    u1_expenses = client_user1.get("/expenses").json()
    assert u1_expenses["total"] == 1
    assert u1_expenses["items"][0]["category"] == "Travel"
    assert u1_expenses["items"][0]["amount"] == 150.00

    u1_summary = client_user1.get("/summary?year=2026&month=9").json()
    assert u1_summary["total_spend"] == 150.00
    assert u1_summary["transaction_count"] == 1
    assert "Travel" in u1_summary["spend_by_category"]
    assert "Food" not in u1_summary["spend_by_category"]
