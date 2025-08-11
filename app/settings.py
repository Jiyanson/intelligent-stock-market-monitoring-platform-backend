from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    finance_api_provider: str = Field("yfinance", alias="FINANCE_API_PROVIDER")

    model_config = {
        "env_file": ".env",         # load from .env
        "extra": "ignore",          # ignore other unknown vars
        "populate_by_name": True    # allow setting by field name
    }

settings = Settings()
