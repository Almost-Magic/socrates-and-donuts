"""
Configuration module for Peterman.

Loads configuration from environment variables with AMTL_PTR_ prefix.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get(key: str, default=None):
    """Get a configuration value from environment variables.
    
    Args:
        key: The configuration key (without AMTL_PTR_ prefix).
        default: Default value if key not found.
        
    Returns:
        The configuration value or default.
    """
    full_key = f"AMTL_PTR_{key.upper()}"
    return os.environ.get(full_key, default)


def get_required(key: str) -> str:
    """Get a required configuration value.
    
    Args:
        key: The configuration key (without AMTL_PTR_ prefix).
        
    Returns:
        The configuration value.
        
    Raises:
        ValueError: If the key is not found in environment.
    """
    full_key = f"AMTL_PTR_{key.upper()}"
    value = os.environ.get(full_key)
    if value is None:
        raise ValueError(f"Required configuration key not found: {full_key}")
    return value


# Export configuration as a module-like object
config = {
    # Core
    'PORT': int(get('PORT', 5008)),
    'SECRET_KEY': get('SECRET_KEY', 'dev-secret-key-change-in-production'),
    'DEBUG': get('DEBUG', 'False').lower() == 'true',
    'LOG_LEVEL': get('LOG_LEVEL', 'INFO'),
    
    # Database
    'DB_URL': get('DB_URL', 'postgresql://postgres:postgres@host.docker.internal:5433/peterman_flask'),
    'REDIS_URL': get('REDIS_URL', 'redis://localhost:6379/0'),
    
    # AI Engines
    'OLLAMA_URL': get('OLLAMA_URL', 'http://localhost:9000'),
    'CLAUDE_DESKTOP_SOCKET': get('CLAUDE_DESKTOP_SOCKET', ''),
    'OPENAI_API_KEY': get('OPENAI_API_KEY', ''),
    'ANTHROPIC_API_KEY': get('ANTHROPIC_API_KEY', ''),
    
    # Search
    'SEARXNG_URL': get('SEARXNG_URL', 'http://localhost:8888'),
    
    # Ecosystem
    'ELAINE_URL': get('ELAINE_URL', 'http://localhost:5000'),
    'WORKSHOP_URL': get('WORKSHOP_URL', 'http://localhost:5003'),
    
    # External
    'GSC_CREDENTIALS_PATH': get('GSC_CREDENTIALS_PATH', ''),
    'NTFY_TOPIC': get('NTFY_TOPIC', 'peterman-alerts'),
    
    # Budget
    'DEFAULT_WEEKLY_BUDGET_AUD': float(get('DEFAULT_WEEKLY_BUDGET_AUD', 50.00)),
}
