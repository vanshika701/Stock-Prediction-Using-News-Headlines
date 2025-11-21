"""Person2 pipeline

Loads preprocessed articles (all and per-ticker), computes a simple sentiment
score per article using lemmatized tokens + provided financial keywords, maps
to Buy/Sell/Hold recommendations with confidence scores, and aggregates per
ticker across recent articles (up to 50). Writes results to
`exports_for_person2/person2_results.json`.

This is a lightweight, local implementation so Person 2 can iterate quickly.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from math import exp
from typing import List, Dict, Any, Tuple

ROOT = os.path.dirname(__file__)
ALL_FILE = os.path.join(ROOT, "all_articles_preprocessed.json")
RESULTS_FILE = os.path.join(ROOT, "person2_results.json")

# Small token sentiment lexicon (lightweight, adjustable)
# Tuned lexicon: expanded with common financial terms; adjust as needed.
POSITIVE_WORDS = {
    "surge",
    "surged",
    "soar",
    "soared",
    "beat",
    "beats",
    "outperform",
    "upgrade",
    "upgraded",
    "growth",
    "strong",
    "gain",
    "gained",
    "up",
    "rise",
    "positive",
    "record",
    "increase",
    "profit",
    "profits",
    "rebound",
    "beat",
}

NEGATIVE_WORDS = {
    "loss",
    "losses",
    "decline",
    "declined",
    "miss",
    "missed",
    "downgrade",
    "downgraded",
    "down",
    "drop",
    "negative",
    "cut",
    "layoff",
    "weak",
    "fail",
    "slump",
    "slumped",
}

# Tunable thresholds and weights
THRESHOLD_BUY = 0.25  # lowered slightly for sensitivity
THRESHOLD_SELL = -0.25

# Weights for combining evidence: if external model available, prefer it
WEIGHT_MODEL = 0.5
WEIGHT_TOKENS = 0.3
WEIGHT_KEYWORDS = 0.2


def sigmoid(x: float) -> float:
    return 1 / (1 + exp(-x))


def score_tokens(tokens: List[str]) -> float:
    """Compute a simple lexicon-based token score in range [-1,1]."""
    if not tokens:
        return 0.0
    pos = sum(1 for t in tokens if t in POSITIVE_WORDS)
    neg = sum(1 for t in tokens if t in NEGATIVE_WORDS)
    return (pos - neg) / (pos + neg + 1)


def score_keywords(keywords: Dict[str, List[str]]) -> Tuple[float, int, int]:
    """Return keyword score and counts (positive, negative).

    Score formula: (pos - neg)/(pos + neg + 1)
    """
    pos = len(keywords.get("positive", [])) if keywords else 0
    neg = len(keywords.get("negative", [])) if keywords else 0
    if pos == 0 and neg == 0:
        return 0.0, pos, neg
    return (pos - neg) / (pos + neg + 1), pos, neg


def compute_article_score(article: Dict[str, Any]) -> Dict[str, Any]:
    # tokens: try to use lemmatized tokens
    tokens = []
    try:
        tokens = article.get("tokens", {}).get("lemmatized") or []
    except Exception:
        tokens = []

    token_score = score_tokens(tokens)

    keyword_score, pos_count, neg_count = score_keywords(
        article.get("features", {}).get("financial_keywords", {})
    )

    # Try to use an external sentiment analyzer (VADER) if available.
    model_score = 0.0
    used_model = False
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        analyzer = SentimentIntensityAnalyzer()
        text = article.get("cleaned_text") or " ".join(tokens)
        vs = analyzer.polarity_scores(text)
        # compound is in [-1,1]
        model_score = float(vs.get("compound", 0.0))
        used_model = True
    except Exception:
        # Vader not available; continue with lexicon-only approach
        model_score = 0.0
        used_model = False

    if used_model:
        final_score = (
            model_score * WEIGHT_MODEL
            + token_score * WEIGHT_TOKENS
            + keyword_score * WEIGHT_KEYWORDS
        )
    else:
        # Combine scores: tokens and keywords only
        final_score = (token_score * 0.7) + (keyword_score * 0.3)

    # Confidence: depends on keyword evidence, model availability and magnitude
    evidence = pos_count + neg_count
    evidence_factor = min(1.0, evidence / 5) if evidence > 0 else 0.4
    model_factor = 1.0 if used_model else 0.8
    confidence = min(1.0, abs(final_score) * 0.9 + 0.1) * evidence_factor * model_factor

    # Recommendation thresholds
    if final_score >= THRESHOLD_BUY:
        rec = "BUY"
    elif final_score <= THRESHOLD_SELL:
        rec = "SELL"
    else:
        rec = "HOLD"

    return {
        "final_score": final_score,
        "token_score": token_score,
        "keyword_score": keyword_score,
        "positive_keyword_count": pos_count,
        "negative_keyword_count": neg_count,
        "recommendation": rec,
        "confidence": round(confidence, 3),
    }


def aggregate_ticker(articles: List[Dict[str, Any]], max_articles: int = 50) -> Dict[str, Any]:
    """Aggregate recent articles for a ticker. Assumes `articles` is in
    chronological order; we'll take the last `max_articles` as most recent.
    """
    if not articles:
        return {"n_articles": 0, "aggregate_score": 0.0, "recommendation": "HOLD", "confidence": 0.0}

    subset = articles[-max_articles:]
    n = len(subset)

    # Weighted average: weight recent articles higher (linear ramp)
    weights = [i + 1 for i in range(n)]  # older->smaller, recent->larger
    total_weight = sum(weights)

    scores = []
    confidences = []
    for art in subset:
        sc = compute_article_score(art)
        scores.append(sc["final_score"])
        confidences.append(sc["confidence"])

    weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight

    # Aggregate confidence: weighted average of article confidences
    agg_conf = sum(c * w for c, w in zip(confidences, weights)) / total_weight

    # Map to recommendation using same thresholds
    if weighted_score >= 0.4:
        rec =  "STRONG BUY"
    elif weighted_score >= 0.25:
        rec = "BUY"
    elif weighted_score >= 0.1:
        rec = "WEAK BUY"
    elif weighted_score >= -0.1:
        rec = "HOLD"
    elif weighted_score >= -0.25:
        rec = "WEAK SELL"
    elif weighted_score >= -0.4:
        rec = "SELL"
    else:
        rec = "STRONG SELL"
    return {
        "n_articles": n,
        "aggregate_score": round(weighted_score, 4),
        "recommendation": rec,
        "confidence": round(min(1.0, agg_conf), 3),
    }


def load_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Could not load {path}: {e}")
        return None


from datetime import datetime, timezone

def main() -> int:

    results: Dict[str, Any] = {"generated_at": datetime.now(timezone.utc).isoformat()}

    all_data = load_json(ALL_FILE)
    per_article_out = []

    # Try to use per-ticker files where possible (prefer them for recency grouping)
    ticker_dir = ROOT
    # Consider both per-ticker article files and per-ticker preprocessed files
    # e.g. `APH_articles.json`, `aph_preprocessed.json`. Exclude the combined
    # `all_articles_preprocessed.json`, the results file and this script.
    valid_suffixes = ("_articles.json", "_preprocessed.json")
    exclude_names = {"all_articles_preprocessed.json", os.path.basename(RESULTS_FILE), os.path.basename(__file__)}
    ticker_files = [
        f
        for f in os.listdir(ticker_dir)
        if f.endswith(valid_suffixes) and f not in exclude_names
    ]

    per_ticker_aggregates: Dict[str, Any] = {}

    if ticker_files:
        for tf in ticker_files:
            path = os.path.join(ticker_dir, tf)
            data = load_json(path)
            if not data:
                continue
            # Use rsplit to keep everything before the last underscore as the ticker
            # (handles tickers with dots or hyphens like `brk.b_articles.json`).
            ticker = tf.rsplit("_", 1)[0].upper()
            articles = data.get("articles") or []

            # compute per-article scores and store brief info
            for art in articles:
                sc = compute_article_score(art)
                per_article_out.append(
                    {
                        "article_id": art.get("article_id"),
                        "title": (art.get("cleaned_title") or "")[:180],
                        "tickers_mentioned": art.get("tickers_mentioned", []),
                        "final_score": round(sc["final_score"], 4),
                        "recommendation": sc["recommendation"],
                        "confidence": sc["confidence"],
                    }
                )

            per_ticker_aggregates[ticker] = aggregate_ticker(articles, max_articles=50)

    else:
        # Fallback: group from all_articles_preprocessed.json
        articles = (all_data or {}).get("articles", [])
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for art in articles:
            sc = compute_article_score(art)
            per_article_out.append(
                {
                    "article_id": art.get("article_id"),
                    "title": (art.get("cleaned_title") or "")[:180],
                    "tickers_mentioned": art.get("tickers_mentioned", []),
                    "final_score": round(sc["final_score"], 4),
                    "recommendation": sc["recommendation"],
                    "confidence": sc["confidence"],
                }
            )
            for t in art.get("tickers_mentioned", []) or []:
                grouped.setdefault(t.upper(), []).append(art)

        for t, arts in grouped.items():
            per_ticker_aggregates[t] = aggregate_ticker(arts, max_articles=50)

    results["per_article"] = per_article_out
    results["per_ticker"] = per_ticker_aggregates

    # Write results
    try:
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Wrote results to: {RESULTS_FILE}")
    except Exception as e:
        print(f"Failed to write results: {e}")
        return 2

    # Print short summary: top 10 tickers by number of articles
    summary = sorted(
        per_ticker_aggregates.items(), key=lambda kv: kv[1].get("n_articles", 0), reverse=True
    )[:10]

    print("Top ticker summaries:")
    for ticker, agg in summary:
        print(f"{ticker}: n={agg['n_articles']}, score={agg['aggregate_score']}, rec={agg['recommendation']}, conf={agg['confidence']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
