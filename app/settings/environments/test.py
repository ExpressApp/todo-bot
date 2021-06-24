"""App settings for test stage."""
from pathlib import Path
from typing import Any

from pydantic import Field, PostgresDsn, RedisDsn

from app.settings.environments.base import AppSettings


class TestAppSettings(AppSettings):
    """Application settings with override params for test environment."""

    # base kwargs
    DEBUG: bool = True
    SQL_DEBUG: bool = True
    BOT_CREDENTIALS: Any = "cts.example.com@secret@123e4567-e89b-12d3-a456-426655440000"
    FILE_STORAGE_PATH: Path = Path("/tmp")  # noqa: S108

    # storages
    DATABASE_URL: PostgresDsn = Field(
        "postgres://postgres:postgres@localhost/postgres", env="TEST_DB_CONNECTION"
    )
    REDIS_DSN: RedisDsn = "redis://localhost/0"

    # db up-time can be more that 25
    RETRY_TIMEOUT: int = 25
    # use local db for tests
    DB: bool = False

    class Config(AppSettings.Config):  # noqa: WPS431
        env_file = ".env"
