import React, { useEffect, useRef } from "react";

export default function TradingViewWidget({ symbol }) {
  const container = useRef();

  useEffect(() => {
    if (!window.TradingView) {
      const script = document.createElement("script");
      script.src = "https://s3.tradingview.com/tv.js";
      script.async = true;
      script.onload = () => createWidget();
      document.body.appendChild(script);
    } else {
      createWidget();
    }

    function createWidget() {
      if (container.current && typeof window.TradingView !== "undefined") {
        container.current.innerHTML = ""; // clear previous widget
        new window.TradingView.widget({
          autosize: true,
          loading_screen: { backgroundColor: "#000000" },
          symbol: symbol || "NASDAQ:AAPL",
          interval: "15",
          timezone: "America/Phoenix",
          theme: "dark",
          style: "1",
          locale: "en",
          enable_publishing: false,
          hide_top_toolbar: false,
          hide_legend: false,
          container_id: container.current.id,
        });
      }
    }
  }, [symbol]);

  return (
    <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-y-auto">
      <div className="font-semibold mb-2">Live Chart</div>
      <div id={`tv_chart_${symbol}`} ref={container} style={{ height: "400px" }}></div>
    </div>
  );
}
