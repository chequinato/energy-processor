from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./energy.db"
    UVICORN_HOST: str = "127.0.0.1"
    UVICORN_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Redis é opcional: se estiver fora do ar, a API funciona sem cache
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL_SECONDS: int = 60

    CORS_ORIGINS: list[str] = ["http://localhost:8501"]

    UPLOAD_DIR: str = "data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10


settings = Settings()
