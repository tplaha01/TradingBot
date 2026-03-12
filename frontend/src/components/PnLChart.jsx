import React, { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

export default function PnLChart({ ticks, symbol }) {
  const [data, setData] = useState([])

  useEffect(() => {
    if (ticks && ticks[symbol]) {
      const { price, signal } = ticks[symbol]
      setData(prev => [
        ...prev.slice(-100),
        { ts: new Date().toLocaleTimeString(), price, score: signal.score }
      ])
    }
  }, [ticks, symbol])

  return (
    <div className="p-4 rounded-2xl shadow bg-white">
      <div className="font-semibold mb-2">Live Price & Signal</div>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="ts" tick={{ fontSize: 10 }} />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Line type="monotone" dataKey="price" stroke="#2563eb" dot={false} name="Price" />
          <Line type="monotone" dataKey="score" stroke="#f97316" dot={false} name="Signal Score" yAxisId={1}/>
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
