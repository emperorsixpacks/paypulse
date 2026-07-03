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


# Bootstrap environment to find the correct .env file
_env_bootstrap = EnvironmentSettings()


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_bootstrap.get_env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )
    environment: ENVIRONMENT = Field(
        default=ENVIRONMENT.DEVELOPMENT,
        alias="ENVIRONMENT",
    )


class DatabaseConfig(ServerConfig):
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    database_uri: str | None = None
    db_driver: str = "postgresql+asyncpg"

    def get_uri(self) -> str:
        if self.database_uri:
            return self.database_uri
        return f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class RedisConfig(ServerConfig):
    redis_port: int
    redis_host: str
    redis_username: str | None = None
    redis_password: str | None = None


class NombaConfig(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")
    nomba_client_id: str
    nomba_client_secret: str
    nomba_account_id: str
    nomba_base_url: str = "https://api.nomba.com"
