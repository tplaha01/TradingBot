import React, { useEffect, useState } from "react";
import { getAnalytics } from "../api";

export default function StrategyDashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const load = async () => setData(await getAnalytics());
    load();
    const id = setInterval(load, 10000); // refresh every 10s
    return () => clearInterval(id);
  }, []);

  if (!data) {
    return (
      <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700">
        Loading strategy metrics…
      </div>
    );
  }

  const {
    total_trades, closed_trades, wins, losses, win_rate,
    realized_pnl, avg_pnl, best_trade, worst_trade, max_drawdown, recent_trades
  } = data;

  return (
    <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300">
      <div className="flex items-center justify-between mb-3">
        <div className="font-semibold text-lg">🤖 Strategy Dashboard</div>
      </div>

      {/* Summary grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
        <Metric label="Total Trades" value={total_trades} />
        <Metric label="Closed Trades" value={closed_trades} />
        <Metric label="Wins" value={wins} accent="text-green-400" />
        <Metric label="Losses" value={losses} accent="text-red-400" />
        <Metric label="Win Rate" value={`${win_rate.toFixed(1)}%`} />
        <Metric label="Realized PnL" value={`$${realized_pnl.toFixed(2)}`} accent={realized_pnl>=0?"text-green-400":"text-red-400"} />
        <Metric label="Avg PnL" value={`$${avg_pnl.toFixed(2)}`} />
        <Metric label="Max Drawdown" value={`$${max_drawdown.toFixed(2)}`} accent="text-red-400" />
        <Metric label="Best Trade" value={`$${best_trade.toFixed(2)}`} accent="text-green-400" />
        <Metric label="Worst Trade" value={`$${worst_trade.toFixed(2)}`} accent="text-red-400" />
      </div>

      {/* Recent trades table */}
      <div className="mt-4">
        <div className="text-sm font-semibold mb-2">Recent Round Trips</div>
        <table className="w-full text-xs">
          <thead className="text-left opacity-70 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th className="py-1">Closed</th>
              <th>Symbol</th>
              <th>Qty</th>
              <th>Buy</th>
              <th>Sell</th>
              <th>PnL</th>
            </tr>
          </thead>
          <tbody>
            {(recent_trades || []).map((t, i) => (
              <tr key={i} className="border-b border-gray-100 dark:border-gray-800">
                <td className="py-1">{new Date(t.close_ts).toLocaleTimeString()}</td>
                <td>{t.symbol}</td>
                <td>{t.qty}</td>
                <td>${t.buy.toFixed(2)}</td>
                <td>${t.sell.toFixed(2)}</td>
                <td className={t.pnl>=0 ? "text-green-400" : "text-red-400"}>${t.pnl.toFixed(2)}</td>
              </tr>
            ))}
            {(!recent_trades || recent_trades.length===0) && (
              <tr><td colSpan="6" className="py-2 opacity-60">No closed trades yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Metric({ label, value, accent }) {
  return (
    <div className="p-3 rounded-xl bg-white/70 dark:bg-gray-900/40 border border-gray-200 dark:border-gray-700">
      <div className="text-xs opacity-70">{label}</div>
      <div className={`mt-1 text-base font-semibold ${accent||""}`}>{value}</div>
    </div>
  );
}
