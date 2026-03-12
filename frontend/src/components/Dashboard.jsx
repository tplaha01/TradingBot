import React from "react"
import SignalCard from "./SignalCard"

export default function Dashboard({ symbol, signal, tick }){
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-y-auto">
        <div className="text-sm opacity-70">Symbol</div>
        <div className="text-3xl font-semibold">{symbol}</div>
        <div className="mt-2 text-xl">{tick ? tick.price.toFixed(2) : "—"}</div>
      </div>
      <SignalCard signal={signal} />
      <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-y-auto">
        <div className="text-sm opacity-70 mb-1">Weights</div>
        {signal ? (
          <ul className="space-y-1 text-sm">
            <li>T: {signal.weights.technical}</li>
            <li>F: {signal.weights.fundamental}</li>
            <li>S: {signal.weights.sentiment}</li>
            <li className="mt-2">Score: <b>{signal.score.toFixed(3)}</b> → <b>{signal.action.toUpperCase()}</b></li>
          </ul>
        ) : "No signal yet"}
      </div>
    </div>
  )
}
