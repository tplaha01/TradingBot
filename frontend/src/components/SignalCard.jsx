import React from "react"

const ACTION_COLORS = {
  buy:  "text-green-500",
  sell: "text-red-500",
  hold: "text-yellow-500",
}

export default function SignalCard({ signal }) {
  if (!signal) return (
    <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300">
      No signal yet.
    </div>
  )

  // BUG FIX: old SignalResponse model stripped subscores/weights/action.
  // Backend now returns the full hybrid_signal dict directly.
  const sub = signal.subscores ?? {}
  const action = signal.action ?? signal.signal ?? "hold"
  const score = signal.score ?? 0

  return (
    <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300">
      <div className="text-sm opacity-70 mb-2">Hybrid Signal</div>
      <div className="grid grid-cols-3 gap-3 text-sm">
        <div>
          <div className="opacity-60">Technical</div>
          <div className="text-xl font-semibold">{(sub.technical ?? 0).toFixed(2)}</div>
        </div>
        <div>
          <div className="opacity-60">Fundamental</div>
          <div className="text-xl font-semibold">{(sub.fundamental ?? 0).toFixed(2)}</div>
        </div>
        <div>
          <div className="opacity-60">Sentiment</div>
          <div className="text-xl font-semibold">{(sub.sentiment ?? 0).toFixed(2)}</div>
        </div>
      </div>
      <div className="mt-3">
        <div className="opacity-60 text-sm">Composite</div>
        <div className={`text-2xl font-bold ${ACTION_COLORS[action.toLowerCase()] ?? ""}`}>
          {score.toFixed(3)} → {action.toUpperCase()}
        </div>
      </div>
      {signal.volatility != null && (
        <div className="mt-2 text-xs opacity-50">
          Volatility (ATR/px): {(signal.volatility * 100).toFixed(2)}%
        </div>
      )}
    </div>
  )
}
