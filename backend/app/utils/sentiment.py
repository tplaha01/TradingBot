from __future__ import annotations
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

def sentiment_score(texts: list[str]) -> float:
    if not texts:
        return 0.0
    scores = []
    for t in texts:
        s = _analyzer.polarity_scores(t)["compound"]
        scores.append(s)
    # average to [-1, 1]
    return float(sum(scores) / max(len(scores), 1))
