from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User


class UserRepository:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_verification_token_hash(db: Session, token_hash: str) -> Optional[User]:
        return db.query(User).filter(User.verification_token_hash == token_hash).first()

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password_hash: str,
        verification_token_hash: Optional[str] = None,
        verification_token_expires_at: Optional[datetime] = None,
        is_verified: bool = False,
    ) -> User:
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            is_verified=is_verified,
            verification_token_hash=verification_token_hash,
            verification_token_expires_at=verification_token_expires_at,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user: User) -> User:
        db.commit()
        db.refresh(user)
        return user
