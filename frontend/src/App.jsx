import React, { useEffect, useState } from "react";
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

  useEffect(() => {
    getHealth().catch(console.warn);
    getPositions().then(setPositions).catch(console.warn);
    getOrders().then(setOrders).catch(console.warn);
    getSignal(symbol).then(setSignal).catch(console.warn);
    getNews(symbol).then(setNews).catch(console.warn);

    const ws = wsConnect((msg) => {
      if (msg.type === "tick_batch") {
        setTicks((prev) => {
          const map = { ...prev };
          msg.data.forEach((d) => (map[d.symbol] = d));
          return map;
        });
      }
    });

    // BUG FIX: was 200ms (hammering the backend) — correct cadence is 10s
    const refresh = setInterval(async () => {
      getPositions().then(setPositions).catch(console.warn);
      getOrders().then(setOrders).catch(console.warn);
    }, 10_000);

    return () => {
      clearInterval(refresh);
      ws?.close();
    };
  }, [symbol]);

  const current = ticks[symbol];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gradient-to-b dark:from-black dark:to-green-950 text-gray-900 dark:text-gray-100 transition-colors duration-500">
      <div className="max-w-7xl mx-auto p-4">
        <div className="flex items-center justify-between border-b border-gray-300 dark:border-gray-700 pb-3">
          <h1 className="text-2xl font-bold">Hybrid Trading Bot (Paper)</h1>
          <div className="flex items-center gap-4">
            <ThemeToggle />
          </div>
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
                  setPositions(await getPositions());
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
