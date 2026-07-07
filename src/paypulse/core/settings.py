import os
from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.paypulse.core.utils import return_base_dir


class ENVIRONMENT(StrEnum):
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class EnvironmentSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file_encoding="utf-8")
    environment: ENVIRONMENT = Field(
        default=ENVIRONMENT.DEVELOPMENT,
        alias="ENVIRONMENT",
    )

    @property
    def get_env_file_path(self) -> str:
        filename = (
            ".env"
            if self.environment == ENVIRONMENT.DEVELOPMENT
            else f".env.{self.environment.value}"
        )
        return os.path.join(return_base_dir(), "config", filename)


_env_bootstrap = EnvironmentSettings()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_bootstrap.get_env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "Paypulse"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DATABASE_URL: str | None = None
    DB_DRIVER: str = "postgresql+asyncpg"

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_URL: str | None = None

    # ARQ Workers (Redis Streams)
    ARQ_QUEUE_NAME: str = "arq:queue:paypulse"
    ARQ_STREAM_NAME: str = "arq:stream:paypulse"
    ARQ_MAX_JOBS: int = 10
    ARQ_JOB_TIMEOUT: int = 300
    ARQ_KEEP_RESULT: int = 3600
    ARQ_MAX_TRIES: int = 3

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Nomba
    NOMBA_BASE_URL: str = "https://sandbox.nomba.com"
    NOMBA_CLIENT_ID: str = ""
    NOMBA_CLIENT_SECRET: str = ""
    NOMBA_ACCOUNT_ID: str = ""

    # Checkout
    CHECKOUT_BASE_URL: str = "http://localhost:8000/checkout"

    # Resend
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "billing@paypulse.dev"

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def get_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def nomba_base_url(self) -> str:
        return self.NOMBA_BASE_URL

    @property
    def nomba_client_id(self) -> str:
        return self.NOMBA_CLIENT_ID

    @property
    def nomba_client_secret(self) -> str:
        return self.NOMBA_CLIENT_SECRET

    @property
    def nomba_account_id(self) -> str:
        return self.NOMBA_ACCOUNT_ID


class NombaConfig:
    def __init__(
        self,
        NOMBA_BASE_URL: str = "https://sandbox.nomba.com",
        NOMBA_CLIENT_ID: str = "",
        NOMBA_CLIENT_SECRET: str = "",
        NOMBA_ACCOUNT_ID: str = "",
    ) -> None:
        self.NOMBA_BASE_URL = NOMBA_BASE_URL
        self.NOMBA_CLIENT_ID = NOMBA_CLIENT_ID
        self.NOMBA_CLIENT_SECRET = NOMBA_CLIENT_SECRET
        self.NOMBA_ACCOUNT_ID = NOMBA_ACCOUNT_ID

    @property
    def nomba_base_url(self) -> str:
        return self.NOMBA_BASE_URL

    @property
    def nomba_client_id(self) -> str:
        return self.NOMBA_CLIENT_ID

    @property
    def nomba_client_secret(self) -> str:
        return self.NOMBA_CLIENT_SECRET

    @property
    def nomba_account_id(self) -> str:
        return self.NOMBA_ACCOUNT_ID


settings = Settings()

