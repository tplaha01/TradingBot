import pandas as pd
import numpy as np
from ta.trend import ADXIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator
from ta.momentum import StochasticOscillator

def technical_score(df: pd.DataFrame, debug: bool = False) -> float | dict:
    c = df["close"]
    h = df["high"]
    l = df["low"]
    v = df["volume"]

    contrib = {}

    score = 0.0

    # === Trend ===
    # SMA(10) vs SMA(50)
    sma_fast = c.rolling(10).mean().iloc[-1]
    sma_slow = c.rolling(50).mean().iloc[-1]
    sma_contrib = 0.25 if sma_fast > sma_slow else -0.25
    score += sma_contrib
    contrib["SMA10>50"] = sma_contrib

    # ADX(14) — trend strength
    adx_val = ADXIndicator(h, l, c, window=14, fillna=True).adx().iloc[-1]
    adx_contrib = 0.15 if adx_val > 25 else -0.10
    score += adx_contrib
    contrib["ADX>25"] = adx_contrib

    # === Momentum ===
    # MACD
    ema_fast = c.ewm(span=12, adjust=False).mean()
    ema_slow = c.ewm(span=26, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_diff = macd_line.iloc[-1] - signal_line.iloc[-1]
    macd_contrib = 0.15 if macd_diff > 0 else -0.15
    score += macd_contrib
    contrib["MACD>Signal"] = macd_contrib

    # RSI(14)
    delta = c.diff()
    up = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    down = -delta.clip(upper=0).ewm(alpha=1/14, adjust=False).mean()
    rs = up / (down + 1e-9)
    rsi_val = 100 - (100 / (1 + rs)).iloc[-1]
    if rsi_val < 35:
        rsi_contrib = 0.15
    elif rsi_val > 65:
        rsi_contrib = -0.15
    else:
        rsi_contrib = 0.0
    score += rsi_contrib
    contrib["RSI"] = rsi_contrib

    # Stochastic Oscillator (fast K)
    so = StochasticOscillator(high=h, low=l, close=c, window=14, smooth_window=3, fillna=True)
    stoch = so.stoch().iloc[-1]
    if stoch < 20:
        stoch_contrib = 0.08
    elif stoch > 80:
        stoch_contrib = -0.08
    else:
        stoch_contrib = 0.0
    score += stoch_contrib
    contrib["Stoch"] = stoch_contrib

    # === Volatility ===
    # Bollinger Bands (20,2)
    bb = BollingerBands(close=c, window=20, window_dev=2)
    bb_pct = (c.iloc[-1] - bb.bollinger_lband().iloc[-1]) / (bb.bollinger_hband().iloc[-1] - bb.bollinger_lband().iloc[-1])
    if bb_pct < 0.05:
        boll_contrib = 0.10   # near lower band (potential bounce)
    elif bb_pct > 0.95:
        boll_contrib = -0.10  # near upper band (potential reversal)
    else:
        boll_contrib = 0.0
    score += boll_contrib
    contrib["BBands"] = boll_contrib

    # Bollinger bandwidth (squeeze signal)
    bandwidth = bb.bollinger_wband().iloc[-1]
    squeeze_contrib = 0.05 if bandwidth < 0.1 else 0.0
    score += squeeze_contrib
    contrib["BBSqueeze"] = squeeze_contrib

    # === Volume ===
    obv = OnBalanceVolumeIndicator(close=c, volume=v, fillna=True).on_balance_volume()
    obv_diff = obv.iloc[-1] - obv.iloc[-5]
    if obv_diff > 0:
        obv_contrib = 0.10
    else:
        obv_contrib = -0.05
    score += obv_contrib
    contrib["OBV"] = obv_contrib

    # === Final clamp ===
    final_score = float(np.clip(score, -1, 1))
    if debug:
        contrib["total"] = final_score
        contrib["raw_sum"] = score
        return contrib
    return final_score
