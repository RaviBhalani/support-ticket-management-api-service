from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.constants import (
    Environment,
    SERVER_ENV_PREFIX,
    SERVER_DEFAULT_HOST,
    SERVER_DEFAULT_PORT,
    POSTGRES_ENV_PREFIX,
    DB_DEFAULT_HOST,
    DB_DEFAULT_PORT,
    DB_DRIVER,
    DB_ASYNC_DRIVER,
    REDIS_ENV_PREFIX,
    REDIS_DEFAULT_HOST,
    REDIS_DEFAULT_PORT,
    REDIS_DEFAULT_DB,
    REDIS_SCHEME,
    LOG_ENV_PREFIX,
    CORS_ENV_PREFIX,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_METHOD_PUT,
    HTTP_METHOD_PATCH,
    HTTP_METHOD_DELETE,
    HTTP_METHOD_OPTIONS,
    JWT_ENV_PREFIX,
    JWT_DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
    TIMEZONE_UTC,
)
from src.core.logging.constants import LogLevel, LogRenderer


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=SERVER_ENV_PREFIX, extra="ignore")

    environment: Environment
    host: str = SERVER_DEFAULT_HOST
    port: int = SERVER_DEFAULT_PORT


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=POSTGRES_ENV_PREFIX, extra="ignore")

    user: str
    password: str
    db: str
    host: str = DB_DEFAULT_HOST
    port: int = DB_DEFAULT_PORT

    @property
    def url(self) -> str:
        return (
            f"{DB_DRIVER}+{DB_ASYNC_DRIVER}://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.db}"
        )


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=REDIS_ENV_PREFIX, extra="ignore")

    host: str = REDIS_DEFAULT_HOST
    port: int = REDIS_DEFAULT_PORT

    @property
    def url(self) -> str:
        return f"{REDIS_SCHEME}://{self.host}:{self.port}/{REDIS_DEFAULT_DB}"


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=LOG_ENV_PREFIX, extra="ignore")

    level: LogLevel = LogLevel.INFO
    renderer: LogRenderer = LogRenderer.CONSOLE
    timezone: str = TIMEZONE_UTC
    enable_colored_console_logs: bool = False
    enable_rich_traceback_formatter: bool = False


class CORSSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=CORS_ENV_PREFIX, extra="ignore")

    allowed_origins: list[str] = []
    allowed_methods: list[str] = [
        HTTP_METHOD_GET,
        HTTP_METHOD_POST,
        HTTP_METHOD_PUT,
        HTTP_METHOD_PATCH,
        HTTP_METHOD_DELETE,
        HTTP_METHOD_OPTIONS,
    ]
    allowed_headers: list[str] = ["*"]
    allow_credentials: bool = True


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=JWT_ENV_PREFIX, extra="ignore")

    private_key: str
    public_key: str
    access_token_expire_minutes: int = JWT_DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_expire_days: int = JWT_DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS


class Settings:

    def __init__(self):
        self.server = ServerSettings()
        self.db = DatabaseSettings()
        self.redis = RedisSettings()
        self.logging = LoggingSettings()
        self.cors = CORSSettings()
        self.jwt = JWTSettings()


settings = Settings()
