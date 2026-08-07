"""Twin configuration — intentionally separate from real settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class TwinSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    app_name: str = "KCN-Security-Twin"
    app_version: str = "0.2.0-twin"
    api_prefix: str = "/api/v1"

    jwt_secret_key: str = "twin-only-not-for-production-change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 1
    jwt_issuer: str = "kcn-security-twin"

    # Login rate limit / lockout
    login_max_failures: int = 5
    login_lockout_seconds: int = 60
    login_window_seconds: int = 120

    # Request size limits (memory endpoints)
    memory_max_content_chars: int = 4096
    memory_max_tags: int = 20
    max_request_body_bytes: int = 65536  # 64 KiB

    log_level: str = "INFO"


@lru_cache
def get_settings() -> TwinSettings:
    return TwinSettings()


settings = get_settings()
