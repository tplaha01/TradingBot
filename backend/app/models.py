from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# -------- Requests / Responses --------

class SignalRequest(BaseModel):
    symbol: str = Field(..., description="Ticker, e.g., AAPL")
    lookback: int = Field(150, ge=20, le=2000, description="Candles to analyze")


SignalLiteral = Literal["BUY", "SELL", "HOLD"]


class SignalResponse(BaseModel):
    symbol: str
    signal: SignalLiteral
    score: float
    timestamp: datetime


class OrderIn(BaseModel):
    symbol: str
    side: Literal["buy", "sell"]
    quantity: float = Field(..., gt=0)


class Order(BaseModel):
    id: int
    symbol: str
    side: Literal["buy", "sell"]
    quantity: float
    price: float
    timestamp: datetime
    status: Literal["filled", "pending", "cancelled"]


class Position(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    pnl: float


class AnalyticsSummary(BaseModel):
    total_pnl: float
    open_positions: int
    closed_trades: int
    win_rate: float
    avg_holding_time: Optional[float] = None  # minutes (optional)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NewsItem(BaseModel):
    symbol: str
    headline: str
    source: str
    url: str
    published_at: datetime
