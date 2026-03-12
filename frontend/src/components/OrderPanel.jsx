import React, { useState } from "react"

export default function OrderPanel({ symbol, onPlace }){
  const [side, setSide] = useState("buy")
  const [qty, setQty] = useState(1)
  return (
    <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-y-auto">
      <div className="font-semibold mb-2">Order Ticket</div>
      <div className="flex items-center gap-2">
        <select value={side} onChange={e=>setSide(e.target.value)} className="border px-3 py-2 rounded dark:bg-gray-800 transition-colors duration-300">
          <option value="buy">Buy</option>
          <option value="sell">Sell</option>
        </select>
        <input type="number" value={qty} min="0" step="1" onChange={e=>setQty(parseFloat(e.target.value))} className="border px-3 py-2 rounded w-28 dark:bg-gray-800 transition-colors duration-300"/>
        <button onClick={()=>onPlace({symbol, side, qty, type:"market"})} className="px-3 py-2 rounded bg-green-600 text-white">Submit</button>
      </div>
    </div>
  )
}
