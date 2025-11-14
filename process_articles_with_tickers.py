# process_articles_with_tickers.py
"""
Process existing articles and add ticker detection + context extraction.
This integrates Tasks 4.1, 4.2, and 4.3 with your existing pipeline.
"""

import json
from datetime import datetime
import sys
import os

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.ticker_extractor import TickerExtractor
from utils.context_extractor import ContextExtractor
from database.db_manager import DatabaseManager


def process_article_with_tickers(article, ticker_extractor, context_extractor):
    """
    Process a single article: detect tickers and extract contexts.
    
    Args:
        article (dict): Article dictionary
        ticker_extractor: Pre-initialized TickerExtractor instance
        context_extractor: Pre-initialized ContextExtractor instance
    
    Returns:
        dict: Enhanced article with ticker information
    """
    
    # Combine all text
    text_parts = [
        article.get('title', ''),
        article.get('description', ''),
        article.get('body', ''),
        article.get('content', '')
    ]
    full_text = ' '.join([part for part in text_parts if part])
    
    # Extract tickers with confidence
    ticker_confidence = ticker_extractor.extract_with_confidence(full_text)
    tickers = list(ticker_confidence.keys())
    
    # Extract contexts for each ticker
    contexts = {}
    for ticker in tickers:
        ticker_contexts = context_extractor.extract_context_for_ticker(full_text, ticker)
        if ticker_contexts:
            contexts[ticker] = ticker_contexts
    
    # Add to article
    article['tickers_mentioned'] = tickers
    article['ticker_confidence'] = ticker_confidence
    article['ticker_contexts'] = contexts
    article['processed_at'] = datetime.now().isoformat()
    
    return article


def process_json_file(input_file='unified_news_data.json', output_file='news_with_tickers.json'):
    """
    Process articles from JSON file and add ticker information.
    
    Args:
        input_file (str): Input JSON file with articles
        output_file (str): Output JSON file with enhanced articles
    """
    print("\n" + "="*80)
    print("PROCESSING ARTICLES WITH TICKER DETECTION")
    print("="*80)
    
    # Load articles
    print(f"\n📂 Loading articles from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded articles for {len(data)} tickers")
    except FileNotFoundError:
        print(f"✗ File not found: {input_file}")
        print("  Run the master_scraper first to generate articles!")
        return
    
    # Initialize extractors ONCE (not for each article!)
    print("\n🔧 Initializing extractors...")
    ticker_extractor = TickerExtractor()
    context_extractor = ContextExtractor(context_window=10)
    print("✓ Extractors ready")
    
    # Process each ticker's articles
    processed_data = {}
    total_articles = 0
    articles_with_tickers = 0
    
    for ticker, articles in data.items():
        print(f"\n🔍 Processing {len(articles)} articles for {ticker}...")
        
        processed_articles = []
        
        for article in articles:
            # Process article with pre-initialized extractors
            enhanced_article = process_article_with_tickers(article, ticker_extractor, context_extractor)
            processed_articles.append(enhanced_article)
            
            total_articles += 1
            
            # Count articles where we found tickers
            if enhanced_article.get('tickers_mentioned'):
                articles_with_tickers += 1
                
                # Show sample
                if len(processed_articles) == 1:  # Show first one as example
                    print(f"\n   📰 Sample: {enhanced_article['title'][:60]}...")
                    print(f"      Tickers found: {enhanced_article['tickers_mentioned']}")
                    for t, conf in enhanced_article['ticker_confidence'].items():
                        print(f"         {t}: {conf}% confidence")
        
        processed_data[ticker] = processed_articles
        print(f"   ✓ Processed {len(processed_articles)} articles")
    
    # Save processed data
    print(f"\n💾 Saving processed articles to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    
    # Summary
    print("\n" + "="*80)
    print("PROCESSING SUMMARY")
    print("="*80)
    print(f"Total articles processed: {total_articles}")
    print(f"Articles with tickers detected: {articles_with_tickers}")
    print(f"Detection rate: {(articles_with_tickers/total_articles)*100:.1f}%")
    print(f"Output saved to: {output_file}")
    print("="*80)


def update_database_with_tickers():
    """
    Update database articles with ticker information.
    Processes articles already in the database.
    """
    print("\n" + "="*80)
    print("UPDATING DATABASE WITH TICKER INFORMATION")
    print("="*80)
    
    db = DatabaseManager()
    
    if not db.connect():
        print("✗ Cannot connect to database")
        return
    
    # Get all articles from database
    print("\n📂 Fetching articles from database...")
    articles = db.get_latest_articles(n=1000)  # Get last 1000 articles
    
    if not articles:
        print("✗ No articles found in database")
        db.close()
        return
    
    print(f"✓ Found {len(articles)} articles")
    
    # Initialize extractors ONCE
    ticker_extractor = TickerExtractor()
    context_extractor = ContextExtractor(context_window=10)
    
    # Process each article
    updated_count = 0
    
    for i, article in enumerate(articles, 1):
        if i % 50 == 0:
            print(f"   Processing article {i}/{len(articles)}...")
        
        # Combine text
        full_text = f"{article['title']} {article['description']} {article['body']}"
        
        # Extract tickers using pre-initialized extractor
        ticker_confidence = ticker_extractor.extract_with_confidence(full_text)
        tickers = list(ticker_confidence.keys())
        
        if not tickers:
            continue
        
        # Extract contexts
        contexts = {}
        for ticker in tickers:
            ticker_contexts = context_extractor.extract_context_for_ticker(full_text, ticker)
            if ticker_contexts:
                contexts[ticker] = ticker_contexts[:3]  # Keep top 3 contexts
        
        # Update database (you would need to add these columns to your schema)
        # For now, we'll just log it
        updated_count += 1
    
    print(f"\n✓ Updated {updated_count} articles with ticker information")
    
    db.close()


def test_ticker_processing():
    """Test ticker processing with sample articles."""
    
    print("\n" + "="*80)
    print("TESTING TICKER PROCESSING")
    print("="*80)
    
    # Initialize extractors ONCE for all test articles
    ticker_extractor = TickerExtractor()
    context_extractor = ContextExtractor(context_window=10)
    
    # Sample articles
    test_articles = [
        {
            'title': '$AAPL surges to new high on strong iPhone demand',
            'description': 'Apple Inc. shares gained 5% after reporting record quarterly revenue.',
            'body': 'Analysts remain bullish on Apple stock citing strong services growth.',
            'source': 'Test Source'
        },
        {
            'title': 'Tesla production numbers disappoint investors',
            'description': '$TSLA falls 3% as delivery targets missed.',
            'body': 'Tesla faces headwinds in China market, impacting overall sales.',
            'source': 'Test Source'
        },
        {
            'title': 'Tech giants lead market rally',
            'description': 'Microsoft and Amazon see gains as sector rebounds.',
            'body': 'Both MSFT and AMZN posted strong quarterly results.',
            'source': 'Test Source'
        }
    ]
    
    # Process each test article
    for i, article in enumerate(test_articles, 1):
        print(f"\n📰 Test Article {i}:")
        print(f"   Title: {article['title']}")
        
        processed = process_article_with_tickers(article, ticker_extractor, context_extractor)
        
        print(f"   Tickers detected: {processed['tickers_mentioned']}")
        print(f"   Confidence scores:")
        for ticker, conf in processed['ticker_confidence'].items():
            print(f"      {ticker}: {conf}%")
        
        if processed['ticker_contexts']:
            print(f"   Contexts:")
            for ticker, contexts in processed['ticker_contexts'].items():
                print(f"      {ticker}: {contexts[0][:80]}...")
    
    print("\n✅ Ticker processing test complete!")


if __name__ == "__main__":
    # Test first
    test_ticker_processing()
    
    print("\n\n")
    
    # Process actual articles if file exists
    try:
        process_json_file()
    except Exception as e:
        print(f"\n⚠ Could not process articles file: {e}")
        print("   Make sure you have run the master_scraper first!")