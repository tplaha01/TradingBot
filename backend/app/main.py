from __future__ import annotations
from datetime import datetime
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    SignalRequest,
    SignalResponse,
    OrderIn,
    Order,
    Position,
    AnalyticsSummary,
    NewsItem,
)
from app.strategies.hybrid import hybrid_signal
from app.broker.paper import PaperBroker
from app.data.news import latest_news
from app.analytics import build_metrics_from_broker

app = FastAPI(title="Hybrid Trading Bot Backend", version="1.0.0")

# CORS — open during dev; lock down in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set to your frontend origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single in-memory paper broker instance
broker = PaperBroker()


# ---------- Health ----------
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ---------- Signals ----------
@app.post("/signals/generate", response_model=SignalResponse)
async def generate_signal(req: SignalRequest) -> SignalResponse:
    # hybrid_signal expected to return (signal_str, score_float)
    signal_str, score = hybrid_signal(req.symbol, lookback=req.lookback)
    # Normalize to BUY/SELL/HOLD
    signal = (signal_str or "HOLD").upper()
    if signal not in {"BUY", "SELL", " HOLD".replace(" ", "")}:
        signal = "HOLD"

    return SignalResponse(
        symbol=req.symbol,
        signal=signal,  # type: ignore
        score=float(score),
        timestamp=datetime.utcnow(),
    )


# ---------- Paper broker (positions/orders) ----------
@app.get("/paper/positions", response_model=List[Position])
async def get_positions() -> List[Position]:
    # broker.get_positions() should return list[dict] or list[Position]-like
    return [Position(**p) if not isinstance(p, Position) else p for p in broker.get_positions()]


@app.get("/paper/orders", response_model=List[Order])
async def get_orders() -> List[Order]:
    return [Order(**o) if not isinstance(o, Order) else o for o in broker.get_orders()]


@app.post("/paper/order", response_model=Order)
async def place_order(order: OrderIn) -> Order:
    # PaperBroker expected signature: place_order(symbol, side, qty) -> dict/Order-like
    created = broker.place_order(order.symbol, order.side, order.quantity)
    return Order(**created) if not isinstance(created, Order) else created


# ---------- News ----------
@app.get("/news/{symbol}", response_model=List[NewsItem])
async def get_news(symbol: str) -> List[NewsItem]:
    items = latest_news(symbol)
    # Coerce to models if needed
    out: List[NewsItem] = []
    for it in items:
        out.append(it if isinstance(it, NewsItem) else NewsItem(**it))
    return out


# ---------- Analytics ----------
@app.get("/analytics/summary", response_model=AnalyticsSummary)
async def analytics_summary() -> AnalyticsSummary:
    return build_metrics_from_broker(broker)


# ---------- WebSocket (simple echo placeholder) ----------
_connections: set[WebSocket] = set()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _connections.add(ws)
    try:
        while True:
            msg = await ws.receive_text()
            # For now we just echo; you can broadcast positions/PNL here
            await ws.send_text(f"echo: {msg}")
    except WebSocketDisconnect:
        _connections.discard(ws)
