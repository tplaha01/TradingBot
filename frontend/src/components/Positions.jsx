import React from "react"

export default function Positions({ items }) {
  return (
    <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-y-auto">
      <div className="font-semibold mb-2">Positions</div>
      {(!items || items.length === 0) ? (
        <div className="text-sm opacity-50">No open positions.</div>
      ) : (
        <table className="w-full text-sm">
          <thead className="text-left opacity-60">
            {/* BUG FIX: was p.quantity — broker returns qty; market_price/market_value/unrealized_pnl now match */}
            <tr><th>Symbol</th><th>Qty</th><th>Avg</th><th>Last</th><th>Value</th><th>uPnL</th></tr>
          </thead>
          <tbody>
            {items.map((p, i) => (
              <tr key={i} className="border-t border-gray-100 dark:border-gray-700">
                <td className="py-1">{p.symbol}</td>
                <td>{(p.qty ?? p.quantity ?? 0).toFixed(2)}</td>
                <td>{(p.avg_price ?? 0).toFixed(2)}</td>
                <td>{(p.market_price ?? p.current_price ?? 0).toFixed(2)}</td>
                <td>{(p.market_value ?? 0).toFixed(2)}</td>
                <td className={(p.unrealized_pnl ?? 0) >= 0 ? "text-green-500" : "text-red-500"}>
                  {(p.unrealized_pnl ?? 0).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
