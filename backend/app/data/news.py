from datetime import datetime, timedelta
import requests
from ..config import get_settings

settings = get_settings()
FINNHUB_KEY = settings.FINNHUB_KEY

# in-memory cache {symbol: {"ts": datetime, "data": [...]}}
_cache: dict[str, dict] = {}

def latest_news(symbol: str, limit: int = 8):
    """
    Pull recent company news from Finnhub.
    Falls back to last successful cached headlines if API fails or is rate-limited.
    """
    now = datetime.utcnow()

    # return cached news if it's less than 1 hour old
    if symbol in _cache and (now - _cache[symbol]["ts"]).seconds < 3600:
        return _cache[symbol]["data"]

    if not FINNHUB_KEY:
        print("⚠️ No FINNHUB_KEY set — using cached/sample news.")
        return _cache.get(symbol, {}).get("data", _sample_news(symbol))

    try:
        url = (
            f"https://finnhub.io/api/v1/company-news?"
            f"symbol={symbol.upper()}&from={(now - timedelta(days=2)).date()}&to={now.date()}&token={FINNHUB_KEY}"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Empty Finnhub response")

        parsed = [
            {
                "symbol": symbol.upper(),
                "headline": item.get("headline"),
                "summary": item.get("summary"),
                "ts": datetime.utcfromtimestamp(
                    item.get("datetime", now.timestamp())
                ).isoformat(),
            }
            for item in data[:limit]
            if item.get("headline")
        ]

        _cache[symbol] = {"ts": now, "data": parsed}
        return parsed


    except Exception as e:
        print(f"⚠️ Finnhub news fetch failed for {symbol}: {e}")
        # fallback to last good cache or sample
        return _cache.get(symbol, {}).get("data", _sample_news(symbol))


def _sample_news(symbol: str):
    """Fallback headlines for offline or first-run mode."""
    now = datetime.utcnow()
    examples = [
        "Company beats earnings expectations, raises guidance for next quarter",
        "Regulatory headwinds grow after new antitrust probe is announced",
        "Strong product launch drives record pre-orders, analysts turn bullish",
        "Supply chain disruptions expected to impact margins in the near term",
    ]
    return [
        {"symbol": symbol.upper(), "headline": h, "summary": None, "ts": now.isoformat()}
        for h in examples
    ]
