from __future__ import annotations
import asyncio
from datetime import datetime
from typing import Dict

from fastapi import WebSocket, WebSocketDisconnect
from app.config import get_settings
from app.data.market_data import FEED


WATCHLIST = ["AAPL", "MSFT", "NVDA", "SPY", "TSLA", "AMZN", "GOOGL", "META"]


class StreamManager:
    """
    Manages all active WebSocket connections.
    Broadcasts tick/signal/positions updates to every connected client.
    """
    def __init__(self):
        self.active: set[WebSocket] = set()
        self._tick_cache: Dict[str, dict] = {}

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.add(ws)
        # Send cached ticks immediately so new clients aren't blank
        if self._tick_cache:
            try:
                await ws.send_json({
                    "type": "tick_batch",
                    "data": list(self._tick_cache.values()),
                })
            except Exception:
                pass

    def disconnect(self, ws: WebSocket):
        self.active.discard(ws)

    async def broadcast(self, message: dict):
        if not self.active:
            return
        dead = []
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.disconnect(d)

    def update_tick(self, symbol: str, price: float):
        """Called by the Alpaca live feed callback to cache latest price."""
        self._tick_cache[symbol] = {
            "symbol": symbol,
            "price": price,
            "ts": datetime.utcnow().isoformat(),
        }


manager = StreamManager()


def _alpaca_tick_callback(symbol: str, price: float):
    """
    Registered with FEED.subscribe() at startup.
    Caches the tick so the polling loop picks it up without blocking.
    """
    manager.update_tick(symbol, price)


async def stream_loop():
    """
    Background coroutine started via asyncio.create_task() in main.py.

    Every WEBSOCKET_BROADCAST_INTERVAL seconds:
    1. Refreshes prices for any symbols not covered by Alpaca live feed
    2. Broadcasts a tick_batch to all connected clients
    3. Broadcasts a portfolio snapshot (positions + open PnL)
    """
    settings = get_settings()

    # Register live-price callback so Alpaca trades update the cache instantly
    FEED.subscribe(_alpaca_tick_callback)

    # Start Alpaca WebSocket stream in background thread
    FEED.start_stream(WATCHLIST)

    print(f"📡 Stream loop started — broadcasting every {settings.WEBSOCKET_BROADCAST_INTERVAL}s")

    while True:
        await asyncio.sleep(settings.WEBSOCKET_BROADCAST_INTERVAL)

        if not manager.active:
            continue

        try:
            # Build tick payload — use cached live prices, fallback to yfinance
            tick_data = []
            for sym in WATCHLIST:
                px = FEED.price(sym)
                if px and px > 0:
                    manager.update_tick(sym, px)
                    tick_data.append({
                        "symbol": sym,
                        "price": px,
                        "ts": datetime.utcnow().isoformat(),
                    })

            if tick_data:
                await manager.broadcast({
                    "type": "tick_batch",
                    "data": tick_data,
                    "ts": datetime.utcnow().isoformat(),
                })

            # Portfolio snapshot
            from app.core.context import broker
            positions = broker.list_positions(lambda s: FEED.price(s))
            if positions:
                await manager.broadcast({
                    "type": "positions_update",
                    "data": positions,
                    "ts": datetime.utcnow().isoformat(),
                })

        except Exception as e:
            print(f"⚠️ Stream loop error: {e}")
