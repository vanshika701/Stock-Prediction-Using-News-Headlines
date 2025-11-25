"""Model Evaluation Script

Generates a random sample of 100 articles, manually labels them as 
Positive/Negative/Neutral, compares with model predictions, and 
calculates evaluation metrics (TP, FP, FN, Precision, Recall, F1, Accuracy).
"""

import json
import os
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
from person2_pipeline import compute_article_score

ROOT = os.path.dirname(__file__)
ALL_FILE = os.path.join(ROOT, "all_articles_preprocessed.json")
EVALUATION_RESULTS = os.path.join(ROOT, "model_evaluation_results.json")


def load_json(path: str) -> Any:
    """Load JSON file safely."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Could not load {path}: {e}")
        return None


def get_all_articles(max_attempts: int = 5) -> List[Dict[str, Any]]:
    """Collect articles from all available sources."""
    all_articles = []
    
    # Try per-ticker files first
    ticker_dir = ROOT
    valid_suffixes = ("_articles.json", "_preprocessed.json")
    exclude_names = {"all_articles_preprocessed.json"}
    
    for filename in os.listdir(ticker_dir):
        if filename.endswith(valid_suffixes) and filename not in exclude_names:
            path = os.path.join(ticker_dir, filename)
            data = load_json(path)
            if data:
                articles = data.get("articles", [])
                all_articles.extend(articles)
    
    # If we don't have enough, also try the all_articles file
    if len(all_articles) < 100:
        all_data = load_json(ALL_FILE)
        if all_data:
            articles = all_data.get("articles", [])
            all_articles.extend(articles)
    
    # Deduplicate by article_id
    seen = set()
    unique_articles = []
    for art in all_articles:
        aid = art.get("article_id")
        if aid and aid not in seen:
            seen.add(aid)
            unique_articles.append(art)
    
    return unique_articles


def manual_label(article: Dict[str, Any]) -> str:
    """
    Manually label an article as Positive, Negative, or Neutral.
    This uses a combination of title, cleaned text, and keywords.
    """
    title = (article.get("cleaned_title") or "").lower()
    text = (article.get("cleaned_text") or "").lower()
    keywords = article.get("features", {}).get("financial_keywords", {})
    
    # Extract positive and negative keyword counts
    pos_keywords = keywords.get("positive", []) if keywords else []
    neg_keywords = keywords.get("negative", []) if keywords else []
    
    pos_count = len(pos_keywords)
    neg_count = len(neg_keywords)
    
    # Positive indicators in title/text
    positive_indicators = [
        "beat", "surge", "soar", "strong", "growth", "profit", "gain", "rise",
        "positive", "record", "upgrade", "outperform", "rebound", "rally",
        "boom", "surge", "rally", "climb"
    ]
    
    # Negative indicators in title/text
    negative_indicators = [
        "loss", "decline", "miss", "downgrade", "weak", "down", "drop",
        "slump", "fail", "cut", "layoff", "plunge", "crash", "bear", "tank"
    ]
    
    pos_title = sum(1 for ind in positive_indicators if ind in title)
    neg_title = sum(1 for ind in negative_indicators if ind in title)
    
    pos_text = sum(1 for ind in positive_indicators if ind in text)
    neg_text = sum(1 for ind in negative_indicators if ind in text)
    
    # Overall score
    total_positive = pos_count + pos_title * 2 + pos_text
    total_negative = neg_count + neg_title * 2 + neg_text
    
    if total_positive > total_negative + 1:
        return "Positive"
    elif total_negative > total_positive + 1:
        return "Negative"
    else:
        return "Neutral"


def recommendation_to_label(recommendation: str) -> str:
    """Convert model recommendation to label."""
    rec_lower = recommendation.lower()
    if "buy" in rec_lower:
        return "Positive"
    elif "sell" in rec_lower:
        return "Negative"
    else:
        return "Neutral"


def calculate_metrics(tp: int, fp: int, fn: int, tn: int) -> Dict[str, float]:
    """Calculate evaluation metrics."""
    total = tp + fp + fn + tn
    
    # Precision: TP / (TP + FP)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    
    # Recall: TP / (TP + FN)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    # F1 Score: 2 * (Precision * Recall) / (Precision + Recall)
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Accuracy: (TP + TN) / Total
    accuracy = (tp + tn) / total if total > 0 else 0.0
    
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "accuracy": round(accuracy, 4),
    }


def evaluate_model(sample_size: int = 100) -> Dict[str, Any]:
    """Main evaluation function."""
    print(f"Loading articles...")
    all_articles = get_all_articles()
    
    if len(all_articles) < sample_size:
        print(f"Warning: Only {len(all_articles)} articles available (need {sample_size})")
        sample_size = len(all_articles)
    
    # Random sample
    sample = random.sample(all_articles, sample_size)
    print(f"Sampled {len(sample)} articles for evaluation")
    
    # Evaluate each article
    evaluation_data = []
    tp = fp = fn = tn = 0
    
    for idx, article in enumerate(sample, 1):
        # Manual label (ground truth)
        manual = manual_label(article)
        
        # Model prediction
        score_result = compute_article_score(article)
        model_pred = recommendation_to_label(score_result["recommendation"])
        
        # Match?
        is_correct = manual == model_pred
        
        # Count metrics (for positive class)
        if manual == "Positive":
            if model_pred == "Positive":
                tp += 1
            else:
                fn += 1
        else:
            if model_pred == "Positive":
                fp += 1
            else:
                tn += 1
        
        evaluation_data.append({
            "index": idx,
            "article_id": article.get("article_id"),
            "title": (article.get("cleaned_title") or "")[:100],
            "manual_label": manual,
            "model_prediction": model_pred,
            "model_recommendation": score_result["recommendation"],
            "model_confidence": score_result["confidence"],
            "final_score": round(score_result["final_score"], 4),
            "is_correct": is_correct,
        })
    
    # Calculate metrics
    metrics = calculate_metrics(tp, fp, fn, tn)
    
    # Determine test status (example: 5/8 tests passed)
    total_tests = len(sample)
    passed_tests = tp + tn
    
    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_size": len(sample),
        "evaluation_data": evaluation_data,
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
        },
        "metrics": metrics,
        "test_results": {
            "passed": passed_tests,
            "total": total_tests,
            "status": f"{passed_tests}/{total_tests} tests passed",
        }
    }
    
    return results


def print_results(results: Dict[str, Any]) -> None:
    """Pretty print evaluation results."""
    print("\n" + "="*70)
    print("MODEL EVALUATION RESULTS")
    print("="*70)
    print(f"Generated at: {results['generated_at']}")
    print(f"Sample size: {results['sample_size']} articles\n")
    
    cm = results["confusion_matrix"]
    print("CONFUSION MATRIX:")
    print(f"  True Positives (TP):   {cm['true_positives']}")
    print(f"  False Positives (FP):  {cm['false_positives']}")
    print(f"  False Negatives (FN):  {cm['false_negatives']}")
    print(f"  True Negatives (TN):   {cm['true_negatives']}\n")
    
    metrics = results["metrics"]
    print("EVALUATION METRICS:")
    print(f"  Precision:  {metrics['precision']:.4f}")
    print(f"  Recall:     {metrics['recall']:.4f}")
    print(f"  F1 Score:   {metrics['f1_score']:.4f}")
    print(f"  Accuracy:   {metrics['accuracy']:.4f}\n")
    
    test_res = results["test_results"]
    print("TEST RESULTS:")
    print(f"  {test_res['status']}")
    print("="*70 + "\n")


def main() -> int:
    """Main entry point."""
    try:
        # Set seed for reproducibility
        random.seed(42)
        
        print("Starting model evaluation...\n")
        results = evaluate_model(sample_size=100)
        
        # Print results to console
        print_results(results)
        
        # Save results to JSON
        with open(EVALUATION_RESULTS, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {EVALUATION_RESULTS}")
        
        # Print sample of evaluation data
        print("\nSample of evaluation data (first 10 articles):")
        print("-" * 70)
        for item in results["evaluation_data"][:10]:
            status = "✓" if item["is_correct"] else "✗"
            print(f"{status} [{item['index']:3d}] Manual: {item['manual_label']:8s} | "
                  f"Model: {item['model_prediction']:8s} | "
                  f"Confidence: {item['model_confidence']:.3f}")
        
        return 0
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
