import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt
import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User
from app.repositories.user_repository import UserRepository
from app.services.email_service import email_service
from app.schemas import UserSignupRequest, UserLoginRequest, TokenResponse


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "iat": now,
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode_access_token(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (jwt.InvalidTokenError, Exception):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @classmethod
    def signup(cls, db: Session, signup_data: UserSignupRequest) -> User:
        existing_user = UserRepository.get_by_email(db, signup_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists",
            )

        password_hash = cls.hash_password(signup_data.password)
        raw_token = secrets.token_urlsafe(32)
        token_hash = cls.hash_token(raw_token)
        token_expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.email_verification_token_expire_hours
        )

        user = UserRepository.create_user(
            db=db,
            email=signup_data.email,
            password_hash=password_hash,
            verification_token_hash=token_hash,
            verification_token_expires_at=token_expires_at,
            is_verified=False,
        )

        # Dispatch email asynchronously/synchronously
        email_service.send_verification_email(user.email, raw_token)
        return user

    @classmethod
    def verify_email(cls, db: Session, raw_token: str) -> User:
        if not raw_token or not raw_token.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token is required",
            )

        token_hash = cls.hash_token(raw_token.strip())
        user = UserRepository.get_by_verification_token_hash(db, token_hash)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        # Check expiration
        now = datetime.now(timezone.utc)
        expires_at = user.verification_token_expires_at
        if expires_at is not None:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if now > expires_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification token has expired",
                )

        user.is_verified = True
        user.verification_token_hash = None
        user.verification_token_expires_at = None
        UserRepository.update_user(db, user)
        return user

    @classmethod
    def login(cls, db: Session, login_data: UserLoginRequest) -> TokenResponse:
        user = UserRepository.get_by_email(db, login_data.email)
        if not user or not cls.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account email is not verified. Please verify your email before logging in.",
            )

        token = cls.create_access_token(user_id=user.id, email=user.email)
        return TokenResponse(access_token=token, token_type="bearer")


auth_service = AuthService()
