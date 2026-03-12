from __future__ import annotations
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

@dataclass
class PaperOrder:
    id: str
    symbol: str
    side: str
    qty: float
    avg_price: float
    status: str
    created_at: datetime

@dataclass
class PaperBroker:
    positions: Dict[str, Dict[str, float]] = field(default_factory=dict)  # symbol → {qty, avg_price}
    orders: List[PaperOrder] = field(default_factory=list)
    order_history: List[dict] = field(default_factory=list)  # ✅ new: raw dicts for analytics

    def submit_order(self, symbol: str, side: str, qty: float, price: float) -> PaperOrder:
        """Simulate market fill and update internal state."""
        oid = str(uuid.uuid4())[:8]
        status = "filled"

        # Update position
        pos = self.positions.get(symbol, {"qty": 0.0, "avg_price": 0.0})
        if side == "buy":
            new_qty = pos["qty"] + qty
            pos["avg_price"] = (
                (pos["avg_price"] * pos["qty"] + price * qty) / max(new_qty, 1e-9)
            )
            pos["qty"] = new_qty
        else:  # sell
            new_qty = pos["qty"] - qty
            pos["qty"] = new_qty
            if new_qty <= 1e-9:
                pos["avg_price"] = 0.0

        self.positions[symbol] = pos

        order = PaperOrder(
            id=oid,
            symbol=symbol,
            side=side,
            qty=qty,
            avg_price=price,
            status=status,
            created_at=datetime.now(timezone.utc),
        )

        # Track orders and history
        self.orders.append(order)
        self.order_history.append({
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "avg_price": price,
            "created_at": order.created_at.isoformat(),
        })

        return order

    def list_positions(self, price_lookup) -> List[dict]:
        """Return list of open positions with current valuation."""
        out = []
        for sym, p in self.positions.items():
            px = price_lookup(sym)
            mv = p["qty"] * px
            upnl = (px - p["avg_price"]) * p["qty"]
            out.append({
                "symbol": sym,
                "qty": p["qty"],
                "avg_price": p["avg_price"],
                "market_price": px,
                "market_value": mv,
                "unrealized_pnl": upnl,
            })
        return out

    def list_orders(self) -> List[dict]:
        """Return list of filled orders."""
        return [o.__dict__ for o in self.orders]
