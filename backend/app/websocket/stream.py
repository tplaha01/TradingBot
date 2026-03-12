from __future__ import annotations
from fastapi import WebSocket, WebSocketDisconnect
from ..config import get_settings
from ..data.market_data import FEED
from ..strategies.hybrid import hybrid_signal
import asyncio, json, time

class StreamManager:
    def __init__(self):
        self.active = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.add(ws)

    def disconnect(self, ws: WebSocket):
        self.active.discard(ws)

    async def broadcast(self, message: dict):
        dead = []
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.disconnect(d)

manager = StreamManager()

async def stream_loop():
    settings = get_settings()
    symbols = ["AAPL", "MSFT", "NVDA", "SPY"]
    while True:
        payload = {"type": "tick_batch", "data": []}
        for s in symbols:
            px = FEED.price(s)
            sig = hybrid_signal(s)
            payload["data"].append({"symbol": s, "price": px, "signal": sig})
        await manager.broadcast(payload)
        await asyncio.sleep(settings.WEBSOCKET_BROADCAST_INTERVAL)
