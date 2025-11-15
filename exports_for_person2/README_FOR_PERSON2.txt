
================================================================================
PREPROCESSED ARTICLES FOR SENTIMENT ANALYSIS
================================================================================

Export Date: 2025-11-15 01:16:26
Total Articles: 832
Tickers: 60

================================================================================
FILES IN THIS EXPORT
================================================================================

1. all_articles_preprocessed.json
   - Contains ALL 832 preprocessed articles
   - Organized with metadata and ticker summary

2. Individual ticker files (e.g., aapl_preprocessed.json)
   - Articles filtered by specific ticker
   - 60 ticker-specific files

================================================================================
DATA STRUCTURE
================================================================================

Each article contains:

{
  "article_id": "unique_id",
  "cleaned_title": "lowercase title without html",
  "cleaned_body": "cleaned article text",
  "cleaned_text": "full cleaned text",
  
  "tokens": {
    "original": ["Apple", "reports", "earnings"],
    "filtered": ["Apple", "reports", "earnings"],  # Stop words removed
    "lemmatized": ["apple", "report", "earning"]   # USE THIS FOR YOUR MODEL
  },
  
  "features": {
    "entities": {
      "ORGANIZATION": ["Apple Inc.", "Wall Street"],
      "PERSON": ["Tim Cook"],
      "GPE": ["California"]
    },
    
    "financial_keywords": {
      "positive": ["surged", "beat", "growth", "strong"],
      "negative": ["loss", "decline", "miss"],
      "neutral": ["reported", "announced"]
    },
    
    "numbers": ["25%", "$180B", "Q4"],
    "dates": ["November 2024"]
  },
  
  "tickers_mentioned": ["AAPL"],
  "ticker_contexts": {
    "AAPL": ["context around **$AAPL** mention"]
  },
  
  "text_stats": {
    "word_count": 250,
    "sentence_count": 12
  }
}

================================================================================
HOW TO USE THIS DATA
================================================================================

1. LOAD THE DATA:

   import json
   
   with open('all_articles_preprocessed.json', 'r') as f:
       data = json.load(f)
   
   articles = data['articles']

2. ACCESS PREPROCESSED TOKENS (Recommended):

   for article in articles:
       # Use lemmatized tokens - already cleaned and normalized
       tokens = article['tokens']['lemmatized']
       
       # Your sentiment analysis here
       sentiment = analyze_sentiment(tokens)

3. USE FINANCIAL KEYWORDS AS FEATURES:

   keywords = article['features']['financial_keywords']
   positive_count = len(keywords['positive'])
   negative_count = len(keywords['negative'])
   
   # Simple sentiment score
   sentiment_ratio = (positive_count - negative_count) / 
                     (positive_count + negative_count + 1)

4. FILTER BY TICKER:

   # Load ticker-specific file
   with open('aapl_preprocessed.json', 'r') as f:
       aapl_data = json.load(f)
   
   aapl_articles = aapl_data['articles']

================================================================================
WHAT'S ALREADY DONE
================================================================================

✓ HTML/URLs removed
✓ Text normalized (lowercase)
✓ Contractions expanded ("can't" → "cannot")
✓ Tokenized (words split properly)
✓ Stop words removed (kept financial terms)
✓ Lemmatized (base word forms: "running" → "run")
✓ Named entities extracted
✓ Financial keywords identified (positive/negative/neutral)
✓ Duplicates removed (17% deduplication rate)
✓ Tickers detected with confidence scores

================================================================================
WHAT YOU NEED TO DO
================================================================================

✗ Sentiment scoring (your model!)
✗ Buy/Sell/Hold recommendations
✗ Confidence scores for predictions
✗ Aggregate analysis across multiple articles

================================================================================
RECOMMENDED APPROACH
================================================================================

1. Use 'tokens.lemmatized' as input to your model
2. Use 'features.financial_keywords' as additional features
3. Consider 'ticker_contexts' for ticker-specific sentiment
4. Aggregate sentiment across 20-50 articles per ticker
5. Weight recent articles higher than older ones

================================================================================
EXAMPLE CODE
================================================================================

import json

# Load data
with open('all_articles_preprocessed.json', 'r') as f:
    data = json.load(f)

articles = data['articles']

# Analyze sentiment
for article in articles:
    # Get preprocessed tokens
    tokens = article['tokens']['lemmatized']
    
    # Get financial keywords
    keywords = article['features']['financial_keywords']
    positive = len(keywords['positive'])
    negative = len(keywords['negative'])
    
    # Your model here
    sentiment_score = your_model.predict(tokens)
    
    # Combine with keyword analysis
    keyword_score = (positive - negative) / (positive + negative + 1)
    final_score = (sentiment_score * 0.7) + (keyword_score * 0.3)
    
    print(f"{article['cleaned_title'][:50]}: {final_score:.2f}")

================================================================================
TICKER SUMMARY
================================================================================

TSLA: 155 articles
MSFT: 119 articles
AAPL: 87 articles
NVDA: 82 articles
FB: 24 articles
GOOG: 20 articles
AMD: 19 articles
TXN: 19 articles
BRK-B: 18 articles
TGT: 13 articles
AXP: 12 articles
ORCL: 12 articles
RIVN: 10 articles
TSM: 9 articles
COIN: 9 articles
IBM: 7 articles
MS: 7 articles
BAC: 7 articles
META: 7 articles
AVGO: 6 articles

================================================================================
NEED HELP?
================================================================================

Contact: Person 1 (News Scraper Team)

Questions? Issues? Need different format?
- More tickers
- Different preprocessing
- Additional features
- API access instead of files

We're here to help! 🚀

================================================================================
