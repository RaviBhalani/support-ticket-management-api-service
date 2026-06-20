from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.constants import Environment
from src.core.logging.constants import LogLevel, LogRenderer


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    environment: Environment
    server_host: str = "0.0.0.0"
    server_port: int = 8000


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_", extra="ignore")

    user: str
    password: str
    db: str
    host: str = "db"
    port: int = 5432

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.db}"
        )


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")

    host: str = "redis"
    port: int = 6379

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/0"


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    log_level: LogLevel = LogLevel.INFO
    log_renderer: LogRenderer = LogRenderer.CONSOLE
    log_timezone: str = "UTC"
    enable_colored_console_logs: bool = False
    enable_rich_traceback_formatter: bool = False


class CORSSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CORS_", extra="ignore")

    allowed_origins: list[str] = []
    allowed_methods: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    allowed_headers: list[str] = ["*"]
    allow_credentials: bool = True


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JWT_", extra="ignore")

    private_key: str
    public_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


class Settings:

    def __init__(self):
        self.server = ServerSettings()
        self.db = DatabaseSettings()
        self.redis = RedisSettings()
        self.logging = LoggingSettings()
        self.cors = CORSSettings()
        self.jwt = JWTSettings()


settings = Settings()
