from datetime import datetime, timedelta
import requests
from app.config import get_settings

settings = get_settings()
FINNHUB_KEY = settings.FINNHUB_KEY

_cache: dict[str, dict] = {}


def latest_news(symbol: str, limit: int = 8):
    """
    Pull recent company news from Finnhub.
    BUG FIX: now returns dicts with source/url/published_at fields
    matching the NewsItem Pydantic model (was ts, missing source/url).
    """
    now = datetime.utcnow()

    if symbol in _cache and (now - _cache[symbol]["ts"]).seconds < 3600:
        return _cache[symbol]["data"]

    if not FINNHUB_KEY:
        return _cache.get(symbol, {}).get("data", _sample_news(symbol))

    try:
        url = (
            f"https://finnhub.io/api/v1/company-news?"
            f"symbol={symbol.upper()}"
            f"&from={(now - timedelta(days=2)).date()}"
            f"&to={now.date()}"
            f"&token={FINNHUB_KEY}"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Empty Finnhub response")

        parsed = [
            {
                "symbol": symbol.upper(),
                "headline": item.get("headline", ""),
                "source": item.get("source", "Finnhub"),
                "url": item.get("url", ""),
                "published_at": datetime.utcfromtimestamp(
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
        return _cache.get(symbol, {}).get("data", _sample_news(symbol))


def _sample_news(symbol: str):
    now = datetime.utcnow().isoformat()
    examples = [
        ("Company beats earnings expectations, raises guidance for next quarter", "Reuters"),
        ("Regulatory headwinds grow after new antitrust probe is announced", "Bloomberg"),
        ("Strong product launch drives record pre-orders, analysts turn bullish", "CNBC"),
        ("Supply chain disruptions expected to impact margins in near term", "WSJ"),
    ]
    return [
        {
            "symbol": symbol.upper(),
            "headline": h,
            "source": src,
            "url": "",
            "published_at": now,
        }
        for h, src in examples
    ]
