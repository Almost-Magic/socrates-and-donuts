"""Touchstone — Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:peterman2026@localhost:5433/touchstone_db"
    app_name: str = "Touchstone"
    app_version: str = "0.1.0"
    app_port: int = 8200
    cors_origins: str = "*"
    secret_key: str = "change-me-in-production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
