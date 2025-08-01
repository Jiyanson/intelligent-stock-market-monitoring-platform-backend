from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://fastapi:fastapi@db:5432/fastapi_db"
    REDIS_URL: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()