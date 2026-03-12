const BASE = window.BACKEND_URL || "http://localhost:8000";

export async function getHealth() {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}
export async function getSignal(symbol){
  const res = await fetch(`${BASE}/signals/generate`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({symbol})
  });
  return res.json();
}
export async function getPositions(){
  const res = await fetch(`${BASE}/paper/positions`);
  return res.json();
}
export async function getOrders(){
  const res = await fetch(`${BASE}/paper/orders`);
  return res.json();
}
export async function placeOrder(order){
  const res = await fetch(`${BASE}/paper/order`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(order)
  });
  return res.json();
}
export function wsConnect(onMessage){
  const url = (BASE.replace("http","ws")) + "/ws/stream";
  const ws = new WebSocket(url);
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    onMessage?.(msg);
  };
  ws.onopen = () => ws.send("hi");
  return ws;
}
export async function getNews(symbol){
  const res = await fetch(`${BASE}/news/${symbol}`);
  return res.json();
}
export async function getAnalytics(){
  const res = await fetch(`${window.BACKEND_URL}/analytics/summary`);
  if(!res.ok) throw new Error("analytics fetch failed");
  return res.json();
}

