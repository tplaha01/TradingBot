from __future__ import annotations
from datetime import datetime
import pandas as pd
from ..config import get_settings
from ..data.market_data import FEED
from ..data.fundamentals import get_fundamentals
from ..data.news import latest_news
from ..indicators.technical import technical_score
from ..utils.sentiment import sentiment_score
from ..utils.common import clamp

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close  = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=period).mean()

def hybrid_signal(symbol: str) -> dict:
    settings = get_settings()

    # Configurable knobs (with safe defaults)
    BUY_THR  = getattr(settings, "BUY_THRESHOLD",  0.25)
    SELL_THR = getattr(settings, "SELL_THRESHOLD", -0.25)
    ATR_N    = getattr(settings, "ATR_PERIOD", 14)
    VOL_CAP  = getattr(settings, "VOL_THRESHOLD", 0.03)  # 3%

    # History
    hist = FEED.history(symbol, bars=200)
    if hist is None or len(hist) < max(60, ATR_N + 2) or hist[["close","high","low"]].isna().any().any():
        return {
            "symbol": symbol.upper(),
            "timestamp": datetime.utcnow().isoformat(),
            "subscores": {"technical": 0.0, "fundamental": 0.0, "sentiment": 0.0},
            "weights": {"technical": settings.TECH_WEIGHT, "fundamental": settings.FUND_WEIGHT, "sentiment": settings.SENT_WEIGHT},
            "score": 0.0, "action": "hold", "volatility": None
        }

    # Technical / Fundamental / Sentiment
    t_score = technical_score(hist)

    f = get_fundamentals(symbol)
    f_score = 0.0
    f_score += min(f.get("revenue_growth", 0.0), 0.3) * (1/0.3) * 0.35
    f_score += min(f.get("gross_margin",   0.0), 0.7) * (1/0.7) * 0.35
    f_score += min(f.get("oper_margin",    0.0), 0.5) * (1/0.5) * 0.30
    f_score -= min(f.get("debt_to_equity", 1.0)/3.0, 1.0) * 0.25
    f_score -= min(f.get("pe",            20.0)/60.0, 1.0) * 0.25
    f_score = clamp(f_score)

    news   = latest_news(symbol)
    texts  = [n["headline"] for n in news]
    s_score= clamp(sentiment_score(texts))

    wT, wF, wS = settings.TECH_WEIGHT, settings.FUND_WEIGHT, settings.SENT_WEIGHT
    score = clamp(wT*t_score + wF*f_score + wS*s_score)

    # Volatility filter
    try:
        atr_series = atr(hist, ATR_N)
        # grab scalars directly via .iloc
        atr_val = float(atr_series.iloc[-1].item())
        px      = float(hist["close"].iloc[-1].item())
        vol_ratio = atr_val / px if px != 0.0 else 0.0



        if vol_ratio > VOL_CAP:
            action = "hold"
        else:
            action = "buy" if score > BUY_THR else ("sell" if score < SELL_THR else "hold")
    except Exception as e:
        print(f"⚠️ ATR calc failed for {symbol}: {e}")
        vol_ratio = None
        action = "hold"

    return {
        "symbol": symbol.upper(),
        "timestamp": datetime.utcnow().isoformat(),
        "subscores": {"technical": t_score, "fundamental": f_score, "sentiment": s_score},
        "weights": {"technical": wT, "fundamental": wF, "sentiment": wS},
        "score": score,
        "action": action,
        "volatility": vol_ratio
    }
