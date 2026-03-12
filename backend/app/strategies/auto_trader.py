from datetime import datetime
import asyncio
from ..strategies.hybrid import hybrid_signal
from ..broker.paper import PaperBroker
from ..data.market_data import FEED
from ..config import get_settings
from ..core.context import broker
from ..websocket.stream import manager

settings = get_settings()

WATCHLIST = ["AAPL", "MSFT", "NVDA", "SPY", "TSLA"]
TRADE_INTERVAL = 10     # seconds between scans
STOP_LOSS_PCT = -0.02   # -2%
TAKE_PROFIT_PCT = 0.05  # +5%

def position_size(score: float, base_size: float = 1.0, max_size: float = 3.0) -> float:
    """Scale size by confidence buckets."""
    conf = min(1.0, max(0.0, abs(score)))
    if conf < 0.30:
        mul = 0.5
    elif conf < 0.60:
        mul = 1.0
    else:
        mul = 2.0
    return min(max_size, base_size * mul)

def manage_positions():
    """Check open positions for stop-loss / take-profit."""
    for pos in broker.list_positions(lambda s: FEED.price(s)):
        qty = pos["qty"]
        if qty <= 0:
            continue
        avg = pos["avg_price"]
        px = pos["market_price"]
        change = (px - avg) / avg
        if change <= STOP_LOSS_PCT:
            broker.submit_order(pos["symbol"], "sell", qty, px)
            print(f"🔴 Stop-loss hit on {pos['symbol']} at {px:.2f} ({change:.1%})")
        elif change >= TAKE_PROFIT_PCT:
            broker.submit_order(pos["symbol"], "sell", qty, px)
            print(f"🟢 Take-profit on {pos['symbol']} at {px:.2f} ({change:.1%})")

async def auto_trading_loop():
    """Background task: scan, trade, and manage risk every interval."""
    print(f"🚀 Auto-trading loop started at {datetime.utcnow().isoformat()}")
    while True:
        print("────────────────────────────")
        print(f"⏰ Cycle start: {datetime.utcnow().strftime('%H:%M:%S UTC')}")
        for sym in WATCHLIST:
            sig = hybrid_signal(sym)
            action = sig["action"]
            score = sig["score"]
            vol = sig.get("volatility", None)
            price = FEED.price(sym)

            # Diagnostic: print raw signal info
            print(f"{sym}: action={action.upper()}  score={score:.3f}  vol={vol if vol is not None else 'N/A'}  price={price:.2f}")

            # Only act on explicit buy/sell
            if action == "buy":
                qty = position_size(score)
                broker.submit_order(sym, "buy", qty, price)
                await broadcast_positions()

                print(f"🟢 EXECUTED BUY  {sym} x{qty} @ {price:.2f}  (score={score:.3f})")
            elif action == "sell":
                qty = position_size(score)
                broker.submit_order(sym, "sell", qty, price)
                await broadcast_positions()

                print(f"🔴 EXECUTED SELL {sym} x{qty} @ {price:.2f}  (score={score:.3f})")
            else:
                print(f"⚪ HOLD — score={score:.3f}")

        # After scanning all symbols, enforce stops
        manage_positions()
        await broadcast_positions()

        print(f"✅ Cycle complete. Sleeping {TRADE_INTERVAL}s\n")
        await asyncio.sleep(TRADE_INTERVAL)

async def broadcast_positions():
    positions = broker.list_positions(lambda s: FEED.price(s))
    await manager.broadcast({"type": "positions", "data": positions})