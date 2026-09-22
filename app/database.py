import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Ensure sqlite directory exists if local file path is used
if settings.database_url.startswith("sqlite:///"):
    db_path = settings.database_url.replace("sqlite:///", "")
    if db_path and db_path != ":memory:":
        parent_dir = Path(db_path).parent
        parent_dir.mkdir(parents=True, exist_ok=True)

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    # Automatic migration for existing SQLite databases missing user_id
    if settings.database_url.startswith("sqlite"):
        with engine.connect() as conn:
            try:
                from sqlalchemy import text
                result = conn.execute(text("PRAGMA table_info(expenses)"))
                columns = [row[1] for row in result.fetchall()]
                if columns and "user_id" not in columns:
                    conn.execute(text("ALTER TABLE expenses ADD COLUMN user_id INTEGER DEFAULT 1 REFERENCES users(id) ON DELETE CASCADE"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_expenses_user_id ON expenses(user_id)"))
                    conn.commit()
            except Exception:
                pass
