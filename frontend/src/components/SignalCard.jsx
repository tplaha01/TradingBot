import React from "react"

export default function SignalCard({ signal }){
  if(!signal) return <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-y-auto">No signal yet.</div>
  const sub = signal.subscores
  return (
    <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-y-auto">
      <div className="text-sm opacity-70 mb-2">Hybrid Signal</div>
      <div className="grid grid-cols-3 gap-3 text-sm">
        <div>
          <div className="opacity-60">Technical</div>
          <div className="text-xl font-semibold">{sub.technical.toFixed(2)}</div>
        </div>
        <div>
          <div className="opacity-60">Fundamental</div>
          <div className="text-xl font-semibold">{sub.fundamental.toFixed(2)}</div>
        </div>
        <div>
          <div className="opacity-60">Sentiment</div>
          <div className="text-xl font-semibold">{sub.sentiment.toFixed(2)}</div>
        </div>
      </div>
      <div className="mt-3">
        <div className="opacity-60 text-sm">Composite</div>
        <div className="text-2xl font-bold">{signal.score.toFixed(3)} → {signal.action.toUpperCase()}</div>
      </div>
    </div>
  )
}
