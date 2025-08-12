from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://fastapi:fastapi@db:5432/fastapi_db"
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Alpha Vantage API Configuration
    ALPHA_VANTAGE_API_KEY: str = Field(default="demo", description="Alpha Vantage API Key")
    FINANCE_API_PROVIDER: str = Field(default="alpha_vantage", description="Finance API Provider")
    
    # API Rate Limiting
    API_REQUEST_TIMEOUT: int = Field(default=30, description="API request timeout in seconds")
    ALPHA_VANTAGE_BASE_URL: str = Field(default="https://www.alphavantage.co/query", description="Alpha Vantage base URL")

    class Config:
        env_file = ".env"
        extra = "ignore"
        populate_by_name = True

settings = Settings()