from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.context import broker
from app.models import SignalRequest, OrderIn, Order, Position, NewsItem
from app.strategies.hybrid import hybrid_signal
from app.data.news import latest_news
from app.analytics import build_metrics_from_broker
from app.websocket.stream import manager, stream_loop

app = FastAPI(title="Hybrid Trading Bot Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    import asyncio
    asyncio.create_task(stream_loop())

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.post("/signals/generate")
async def generate_signal(req: SignalRequest) -> Dict[str, Any]:
    # Return the full rich dict so frontend gets subscores/weights/action
    return hybrid_signal(req.symbol)

@app.get("/paper/positions")
async def get_positions():
    from app.data.market_data import FEED
    return broker.list_positions(lambda s: FEED.price(s))

@app.get("/paper/orders")
async def get_orders():
    return broker.list_orders()

@app.post("/paper/order")
async def place_order(order: OrderIn):
    from app.data.market_data import FEED
    price = FEED.price(order.symbol)
    created = broker.submit_order(order.symbol, order.side, order.quantity, price)
    return {
        "id": created.id,
        "symbol": created.symbol,
        "side": created.side,
        "quantity": created.qty,
        "price": created.avg_price,
        "timestamp": created.created_at.isoformat(),
        "status": created.status,
    }

@app.get("/news/{symbol}")
async def get_news(symbol: str):
    items = latest_news(symbol)
    out = []
    for it in items:
        out.append({
            "symbol": it.get("symbol", symbol.upper()),
            "headline": it.get("headline", ""),
            "source": it.get("source", "Finnhub"),
            "url": it.get("url", ""),
            "published_at": it.get("published_at") or it.get("ts") or datetime.utcnow().isoformat(),
        })
    return out

@app.get("/analytics/summary")
async def analytics_summary() -> Dict[str, Any]:
    return build_metrics_from_broker(broker)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
