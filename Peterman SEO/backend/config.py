"""
Peterman V4.1 — Configuration
Almost Magic Tech Lab
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "peterman-dev-key")
    DEBUG = False

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:peterman2026@localhost:5433/peterman"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ollama — routed through Supervisor (port 9000)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:9000")
    OLLAMA_PRIMARY_MODEL = os.getenv("OLLAMA_PRIMARY_MODEL", "gemma2:27b")
    OLLAMA_FAST_MODEL = os.getenv("OLLAMA_FAST_MODEL", "gemma2:27b")
    OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    # SearXNG
    SEARXNG_BASE_URL = os.getenv("SEARXNG_BASE_URL", "http://localhost:8888")

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Paid APIs
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

    # Snitcher
    SNITCHER_API_KEY = os.getenv("SNITCHER_API_KEY", "")

    # Elaine
    ELAINE_BASE_URL = os.getenv("ELAINE_BASE_URL", "http://localhost:5000")

    # Slack
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

    # App
    APP_NAME = "Peterman"
    APP_VERSION = "4.1.0"
    APP_PORT = int(os.getenv("FLASK_PORT", 5008))

    # Vector dimensions (nomic-embed-text = 768)
    EMBED_DIMENSIONS = 768

    # Scan settings
    SCAN_CACHE_DAYS = 7
    MAX_CONCURRENT_SCANS = 3
    DEFAULT_SCAN_DEPTH = "standard"  # standard | deep | crisis


class DevelopmentConfig(Config):
    DEBUG = False


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
