import React, { useEffect, useState } from "react";
import { getNews } from "../api";
import { SentimentIntensityAnalyzer } from "vader-sentiment";

export default function NewsFeed({ symbol }) {
  const [items, setItems] = useState([]);
  const [avgSentiment, setAvgSentiment] = useState(0);

  // Fetch news and refresh every minute
  useEffect(() => {
    const fetchNews = async () => {
      const data = await getNews(symbol);
      setItems(data || []);
    };
    fetchNews();
    const interval = setInterval(fetchNews, 60000);
    return () => clearInterval(interval);
  }, [symbol]);

  // Calculate average sentiment score
  useEffect(() => {
    if (!items.length) return;
    const scores = items.map((n) =>
      SentimentIntensityAnalyzer.polarity_scores(n.headline || "").compound
    );
    const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
    setAvgSentiment(avg);
  }, [items]);

  const getSentimentLabel = () => {
    if (avgSentiment > 0.2) return "Bullish";
    if (avgSentiment < -0.2) return "Bearish";
    return "Neutral";
  };

  const getSentimentColor = () => {
    if (avgSentiment > 0.2) return "bg-green-500";
    if (avgSentiment < -0.2) return "bg-red-500";
    return "bg-yellow-400";
  };

  return (
    <div className="p-4 rounded-2xl shadow bg-white/80 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200 dark:border-gray-700 transition-all duration-300 h-[calc(100vh-100px)] overflow-y-auto">
      <div className="font-semibold mb-3 text-lg flex items-center gap-2">
        📰 Live Market News
        <span className="text-xs opacity-70">({symbol})</span>
      </div>

      {/* 📊 Sentiment Meter */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span>Overall Sentiment: {getSentimentLabel()}</span>
          <span>{(avgSentiment * 100).toFixed(1)}%</span>
        </div>
        <div className="w-full h-2 bg-gray-300 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`${getSentimentColor()} h-2 transition-all duration-700`}
            style={{ width: `${Math.min(100, Math.abs(avgSentiment) * 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Headlines list */}
      <ul className="space-y-3">
        {(items || []).length === 0 && (
          <li className="text-sm opacity-70">No recent headlines available.</li>
        )}
        {(items || []).map((n, i) => {
          const score =
            SentimentIntensityAnalyzer.polarity_scores(n.headline || "").compound;
          const color =
            score > 0.2
              ? "text-green-500"
              : score < -0.2
              ? "text-red-500"
              : "text-yellow-400";

          return (
            <li
              key={i}
              className="text-sm border-b border-gray-200 dark:border-gray-700 pb-2 hover:bg-gray-100/60 dark:hover:bg-gray-700/40 rounded transition-colors"
            >
              <div className="flex justify-between items-center">
                <span className="text-xs opacity-60">
                  {new Date(n.ts).toLocaleTimeString()}
                </span>
                <span className={`text-xs font-semibold ${color}`}>
                  {score > 0.2 ? "Bullish" : score < -0.2 ? "Bearish" : "Neutral"}
                </span>
              </div>
              <div className="mt-1">{n.headline}</div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
