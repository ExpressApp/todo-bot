"""App settings for development stage."""

from pydantic import Field, PostgresDsn, RedisDsn

from app.settings.environments.base import AppSettings


class DevAppSettings(AppSettings):
    """Application settings with override params for dev environment."""

    # base kwargs
    DEBUG: bool = True
    SQL_DEBUG: bool = True

    # storages
    DATABASE_URL: PostgresDsn = Field(
        "postgres://postgres:postgres@localhost/postgres", env="DB_CONNECTION"
    )
    REDIS_DSN: RedisDsn = "redis://localhost/0"

    class Config(AppSettings.Config):  # noqa: WPS431
        env_file = ".env"
