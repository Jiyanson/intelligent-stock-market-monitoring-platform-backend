from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FINANCE_API_PROVIDER: str = "yfinance"  # default value

    class Config:
        env_file = ".env"

settings = Settings()
