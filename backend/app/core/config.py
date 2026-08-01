"""
Application configuration — reads settings from environment variables.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file="../config/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "KCN-Ecosystem"
    app_version: str = "0.1.0"
    app_env: str = "development"
    app_debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # Security
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # GitHub OAuth (admin sign-in)
    github_client_id: str = ""
    github_client_secret: str = ""
    github_oauth_redirect_uri: str = "http://localhost:8000/api/v1/auth/github/callback"
    # Comma-separated list of GitHub usernames allowed to sign in as admin
    github_admin_usernames: str = "Evank253"
    # Where to send the browser back to after a successful/failed OAuth login
    frontend_url: str = "http://localhost:5173"
    # Short-lived signed state token, protects the OAuth redirect from CSRF
    oauth_state_expire_minutes: int = 10

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()
