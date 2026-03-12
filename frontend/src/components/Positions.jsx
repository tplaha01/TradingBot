import React from "react"

export default function Positions({ items }){
  return (
    <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-y-auto">
      <div className="font-semibold mb-2">Positions</div>
      <table className="w-full text-sm">
        <thead className="text-left opacity-60">
          <tr><th>Symbol</th><th>Qty</th><th>Avg</th><th>Last</th><th>Value</th><th>uPnL</th></tr>
        </thead>
        <tbody>
          {(items||[]).map((p,i)=> (
            <tr key={i} className="border-t">
              <td>{p.symbol}</td><td>{p.qty.toFixed(2)}</td><td>{p.avg_price.toFixed(2)}</td>
              <td>{p.market_price.toFixed(2)}</td><td>{p.market_value.toFixed(2)}</td><td>{p.unrealized_pnl.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
