import React, { useEffect, useState, useRef } from "react";
import {
  getHealth,
  getSignal,
  getPositions,
  getOrders,
  placeOrder,
  wsConnect,
  getNews,
} from "./api";
import Dashboard from "./components/Dashboard";
import TickerSearch from "./components/TickerSearch";
import OrderPanel from "./components/OrderPanel";
import Positions from "./components/Positions";
import NewsFeed from "./components/NewsFeed";
import TradingViewWidget from "./components/TradingViewWidget";
import ThemeToggle from "./components/ThemeToggle";
import StrategyDashboard from "./components/StrategyDashboard";

export default function App() {
  const [symbol, setSymbol] = useState("AAPL");
  const [signal, setSignal] = useState(null);
  const [positions, setPositions] = useState([]);
  const [orders, setOrders] = useState([]);
  const [ticks, setTicks] = useState({});
  const [news, setNews] = useState([]);
  const [wsStatus, setWsStatus] = useState("connecting"); // connecting | live | disconnected
  const wsRef = useRef(null);

  // Initial load
  useEffect(() => {
    getHealth().catch(console.warn);
    getPositions().then(setPositions).catch(console.warn);
    getOrders().then(setOrders).catch(console.warn);
  }, []);

  // Symbol-dependent loads
  useEffect(() => {
    getSignal(symbol).then(setSignal).catch(console.warn);
    getNews(symbol).then(setNews).catch(console.warn);
  }, [symbol]);

  // WebSocket — reconnects on disconnect
  useEffect(() => {
    let dead = false;

    function connect() {
      if (dead) return;
      setWsStatus("connecting");
      const ws = wsConnect((msg) => {
        if (msg.type === "tick_batch") {
          setTicks((prev) => {
            const map = { ...prev };
            msg.data.forEach((d) => (map[d.symbol] = d));
            return map;
          });
          setWsStatus("live");
        }
        // Phase 2: server pushes position updates after trades / on interval
        if (msg.type === "positions_update") {
          setPositions(msg.data);
        }
      });

      ws.onopen = () => setWsStatus("live");
      ws.onclose = () => {
        setWsStatus("disconnected");
        if (!dead) setTimeout(connect, 3000); // auto-reconnect
      };
      ws.onerror = () => setWsStatus("disconnected");

      wsRef.current = ws;
    }

    connect();

    // REST fallback polling — only for orders (positions come via WS now)
    const poll = setInterval(() => {
      getOrders().then(setOrders).catch(console.warn);
    }, 10_000);

    return () => {
      dead = true;
      clearInterval(poll);
      wsRef.current?.close();
    };
  }, []);

  const current = ticks[symbol];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gradient-to-b dark:from-black dark:to-green-950 text-gray-900 dark:text-gray-100 transition-colors duration-500">
      <div className="max-w-7xl mx-auto p-4">
        <div className="flex items-center justify-between border-b border-gray-300 dark:border-gray-700 pb-3">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">Hybrid Trading Bot</h1>
            {/* Live WS status indicator */}
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              wsStatus === "live"
                ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400"
                : wsStatus === "connecting"
                ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-400"
                : "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400"
            }`}>
              {wsStatus === "live" ? "● LIVE" : wsStatus === "connecting" ? "◌ connecting" : "○ disconnected"}
            </span>
          </div>
          <ThemeToggle />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
          <div className="lg:col-span-2 space-y-4">
            <TickerSearch
              value={symbol}
              onChange={setSymbol}
              onAnalyze={() => {
                getSignal(symbol).then(setSignal).catch(console.warn);
                getNews(symbol).then(setNews).catch(console.warn);
              }}
            />

            <Dashboard symbol={symbol} signal={signal} tick={current} />
            <TradingViewWidget symbol={symbol} />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <OrderPanel
                symbol={symbol}
                onPlace={async (o) => {
                  await placeOrder(o);
                  // Positions will update via WS push; orders need REST
                  setOrders(await getOrders());
                }}
              />
              <Positions items={positions} />
            </div>
            <StrategyDashboard />
          </div>

          <div className="lg:col-span-1 h-full sticky top-4">
            <NewsFeed symbol={symbol} items={news} />
          </div>
        </div>
      </div>
    </div>
  );
}
