const BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export async function getHealth() {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

export async function getSignal(symbol) {
  const res = await fetch(`${BASE}/signals/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol }),
  });
  return res.json();
}

export async function getPositions() {
  const res = await fetch(`${BASE}/paper/positions`);
  return res.json();
}

export async function getOrders() {
  const res = await fetch(`${BASE}/paper/orders`);
  return res.json();
}

export async function placeOrder(order) {
  const res = await fetch(`${BASE}/paper/order`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // BUG FIX: was sending { qty } — backend OrderIn model expects { quantity }
    body: JSON.stringify({
      symbol: order.symbol,
      side: order.side,
      quantity: order.qty ?? order.quantity,
    }),
  });
  return res.json();
}

export function wsConnect(onMessage) {
  // BUG FIX: was "/ws/stream" — backend only registers "/ws"
  const url = BASE.replace(/^http/, "ws") + "/ws";
  const ws = new WebSocket(url);
  ws.onmessage = (ev) => {
    try {
      const msg = JSON.parse(ev.data);
      onMessage?.(msg);
    } catch (e) {
      console.warn("WS parse error", e);
    }
  };
  ws.onerror = (e) => console.warn("WS error", e);
  return ws;
}

export async function getNews(symbol) {
  const res = await fetch(`${BASE}/news/${symbol}`);
  return res.json();
}

export async function getAnalytics() {
  // BUG FIX: was using window.BACKEND_URL (undefined in dev) instead of BASE
  const res = await fetch(`${BASE}/analytics/summary`);
  if (!res.ok) throw new Error("analytics fetch failed");
  return res.json();
}
