import unittest
import os
import json

from exports_for_person2 import person2_pipeline as pipeline


class TestPerson2Pipeline(unittest.TestCase):
    def test_positive_article_maps_to_buy(self):
        article = {
            "article_id": "t1",
            "cleaned_title": "Company posts record profits and strong growth",
            "cleaned_text": "Company posted record profits and strong growth this quarter",
            "tokens": {"lemmatized": ["company", "post", "record", "profit", "strong", "growth"]},
            "features": {"financial_keywords": {"positive": ["surged"], "negative": []}},
            "tickers_mentioned": ["TEST"]
        }

        sc = pipeline.compute_article_score(article)
        self.assertIn("final_score", sc)
        # expect a positive final score and BUY recommendation under tuned thresholds
        self.assertGreater(sc["final_score"], 0)
        self.assertEqual(sc["recommendation"], "BUY")

    def test_negative_article_maps_to_sell(self):
        article = {
            "article_id": "t2",
            "cleaned_title": "Company suffers heavy losses and layoffs",
            "cleaned_text": "Company reported heavy losses and announced layoffs",
            "tokens": {"lemmatized": ["company", "report", "heavy", "loss", "layoff"]},
            "features": {"financial_keywords": {"positive": [], "negative": ["loss"]}},
            "tickers_mentioned": ["TEST"]
        }

        sc = pipeline.compute_article_score(article)
        self.assertIn("final_score", sc)
        self.assertLess(sc["final_score"], 0)
        self.assertEqual(sc["recommendation"], "SELL")


if __name__ == "__main__":
    unittest.main()
