import React, { useState } from "react"

export default function TickerSearch({ value, onChange, onAnalyze }){
  const [inp, setInp] = useState(value || "AAPL")
  return (
    <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-y-auto">
      <input value={inp} onChange={e=>setInp(e.target.value.toUpperCase())} className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-y-auto " placeholder="Symbol"/>
      <button onClick={()=>{ onChange(inp); onAnalyze?.() }} className="px-3 py-2 rounded bg-green-600 text-white">Analyze</button>

    </div>
  )
}
