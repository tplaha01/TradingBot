import React from "react"
import SignalCard from "./SignalCard"

export default function Dashboard({ symbol, signal, tick }) {
  const weights = signal?.weights ?? {}
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300">
        <div className="text-sm opacity-70">Symbol</div>
        <div className="text-3xl font-semibold">{symbol}</div>
        <div className="mt-2 text-xl">
          {tick ? `$${tick.price.toFixed(2)}` : "—"}
        </div>
        {tick?.signal?.action && (
          <div className="mt-1 text-xs opacity-50 uppercase tracking-wide">
            WS signal: {tick.signal.action}
          </div>
        )}
      </div>

      <SignalCard signal={signal} />

      <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300">
        <div className="text-sm opacity-70 mb-1">Signal weights</div>
        {signal ? (
          <ul className="space-y-1 text-sm">
            <li>Technical: <b>{(weights.technical ?? 0).toFixed(2)}</b></li>
            <li>Fundamental: <b>{(weights.fundamental ?? 0).toFixed(2)}</b></li>
            <li>Sentiment: <b>{(weights.sentiment ?? 0).toFixed(2)}</b></li>
            <li className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
              Score: <b>{(signal.score ?? 0).toFixed(3)}</b> → <b>{(signal.action ?? "hold").toUpperCase()}</b>
            </li>
          </ul>
        ) : (
          <div className="text-sm opacity-50">No signal yet</div>
        )}
      </div>
    </div>
  )
}
