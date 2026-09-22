from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./data/spend_tracker.db"
    cors_origins: Union[str, List[str]] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    max_body_size_bytes: int = 1048576
    # JWT Settings
    jwt_secret_key: str = "spend-tracker-dev-jwt-secret-key-32charsmin!"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # SMTP Settings
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@spendtracker.local"
    smtp_use_tls: bool = True
    email_verification_token_expire_hours: int = 24
    app_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
