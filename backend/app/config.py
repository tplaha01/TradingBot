from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Hybrid Trading Bot"
    ENV: str = "dev"
    BROKER: str = "paper"          # paper | alpaca | ibkr
    DATA_MODE: str = "simulated"
    TECH_WEIGHT: float = 0.45
    FUND_WEIGHT: float = 0.25
    SENT_WEIGHT: float = 0.30
    WEBSOCKET_BROADCAST_INTERVAL: float = 1.0
    SECRET_KEY: str = "dev-secret"
    SQLITE_PATH: str = "trading.db"

    # --- Provider keys ---
    NEWSAPI_KEY: str | None = None
    FMP_KEY: str | None = None
    FINNHUB_KEY: str | None = None

    # --- Strategy tunables ---
    BUY_THRESHOLD: float = 0.25
    SELL_THRESHOLD: float = -0.25
    ATR_PERIOD: int = 14
    VOL_THRESHOLD: float = 0.03

    class Config:
        env_file = ".env"   # ✅ ensures backend/.env is read
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    return Settings()
