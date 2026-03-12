from __future__ import annotations
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Dict

class YahooFeed:
    """Fetches live & historical stock data from Yahoo Finance."""
    def __init__(self):
        self.cache: Dict[str, float] = {}

    def price(self, symbol: str) -> float:
        """Fetches latest market price."""
        try:
            data = yf.Ticker(symbol)
            price = float(data.fast_info["last_price"])
            self.cache[symbol] = price
            return price
        except Exception:
            # fallback: last cached or 0
            return self.cache.get(symbol, 0.0)

    def history(self, symbol: str, bars: int = 200) -> pd.DataFrame:
        """Fetches historical bars (daily)."""
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False, auto_adjust=True)
            df = df.tail(bars).reset_index()
            df.rename(columns={
                "Date": "ts",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            }, inplace=True)
            return df
        except Exception:
            return pd.DataFrame(columns=["ts", "open", "high", "low", "close", "volume"])

FEED = YahooFeed()
