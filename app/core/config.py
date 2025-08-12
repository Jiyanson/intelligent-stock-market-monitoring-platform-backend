from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://fastapi:fastapi@db:5432/fastapi_db"
    REDIS_URL: str = "redis://redis:6379/0"
    FINANCE_API_PROVIDER: str = Field(default="yfinance", alias="FINANCE_API_PROVIDER")

    class Config:
        env_file = ".env"
        extra = "ignore"  # This allows extra fields to be ignored instead of causing errors
        populate_by_name = True

settings = Settings()