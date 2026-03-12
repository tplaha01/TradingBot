from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Hybrid Trading Bot"
    ENV: str = "dev"
    BROKER: str = "paper"           # paper | alpaca
    DATA_MODE: str = "live"
    TECH_WEIGHT: float = 0.45
    FUND_WEIGHT: float = 0.25
    SENT_WEIGHT: float = 0.30
    WEBSOCKET_BROADCAST_INTERVAL: float = 2.0
    SECRET_KEY: str = "dev-secret"

    # Provider keys
    NEWSAPI_KEY: str | None = None
    FMP_KEY: str | None = None
    FINNHUB_KEY: str | None = None

    # Alpaca (Phase 2)
    ALPACA_API_KEY: str | None = None
    ALPACA_SECRET_KEY: str | None = None
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"
    ALPACA_FEED: str = "iex"        # iex (free) | sip (paid)

    # Strategy tunables
    BUY_THRESHOLD: float = 0.25
    SELL_THRESHOLD: float = -0.25
    ATR_PERIOD: int = 14
    VOL_THRESHOLD: float = 0.03

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
