"""Twin configuration — intentionally separate from real settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class TwinSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    app_name: str = "KCN-Security-Twin"
    app_version: str = "0.1.0-twin"
    api_prefix: str = "/api/v1"

    jwt_secret_key: str = "twin-only-not-for-production-change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 1

    log_level: str = "INFO"


@lru_cache
def get_settings() -> TwinSettings:
    return TwinSettings()


settings = get_settings()
