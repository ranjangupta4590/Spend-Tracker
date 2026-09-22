from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import (
    UserSignupRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def signup(
    signup_data: UserSignupRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user and send an email verification link.
    """
    auth_service.signup(db, signup_data)
    return MessageResponse(
        message="Account created successfully. Please check your email to verify your account."
    )


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return a JWT access token.
    Account email must be verified.
    """
    return auth_service.login(db, login_data)


@router.get("/verify-email", response_model=MessageResponse)
def verify_email(
    token: str = Query(..., description="Email verification token"),
    db: Session = Depends(get_db),
):
    """
    Verify user email using the single-use token sent via email.
    """
    auth_service.verify_email(db, token)
    return MessageResponse(message="Email verified successfully. You may now log in.")


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve authenticated user's profile.
    """
    return current_user
