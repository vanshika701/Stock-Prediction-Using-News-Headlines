# scrapers/master_scraper.py

import json
import hashlib
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all scrapers
from scrapers import newsapi_scraper
from scrapers import alphavantage_scraper
from scrapers import finnhub_scraper
from scrapers import rss_scraper

# Source priority (higher = more reliable)
SOURCE_PRIORITY = {
    'newsapi': 3,
    'alphavantage': 2,
    'finnhub': 2,
    'rss': 1
}


def generate_article_id(title, url):
    """
    Generate unique ID for an article based on title and URL.
    
    Args:
        title (str): Article title
        url (str): Article URL
    
    Returns:
        str: Unique article ID (hash)
    """
    # Combine title and URL
    content = f"{title}|{url}".encode('utf-8')
    # Create SHA256 hash
    return hashlib.sha256(content).hexdigest()[:16]


def standardize_article(article, source_name, ticker=None):
    """
    Convert any article format to unified standard format.
    
    Args:
        article (dict): Raw article from any source
        source_name (str): Which scraper this came from
        ticker (str): Stock ticker (if available)
    
    Returns:
        dict: Standardized article format
    """
    
    # Extract common fields
    title = article.get('title', 'No title')
    url = article.get('url', article.get('link', ''))
    
    # Create standardized article
    standardized = {
        'article_id': generate_article_id(title, url),
        'title': title,
        'description': article.get('description', article.get('summary', '')),
        'body': article.get('content', article.get('summary', '')),
        'source': article.get('source', 'Unknown'),
        'source_api': source_name,
        'source_priority': SOURCE_PRIORITY.get(source_name, 1),
        'url': url,
        'author': article.get('author', 'Unknown'),
        'published_at': article.get('published_at', ''),
        'scraped_at': datetime.now().isoformat(),
        'ticker': ticker,
        'raw_text': f"{title} {article.get('description', '')} {article.get('content', '')}",
        
        # Extra fields from specific sources
        'sentiment_score': article.get('sentiment_score'),
        'sentiment_label': article.get('sentiment_label'),
        'image': article.get('image'),
        'category': article.get('category')
    }
    
    return standardized


def remove_duplicates(articles):
    """
    Remove duplicate articles based on article_id.
    Keep the one from the highest priority source.
    
    Args:
        articles (list): List of standardized articles
    
    Returns:
        list: Deduplicated articles
    """
    
    seen = {}  # article_id -> article
    
    for article in articles:
        article_id = article['article_id']
        
        # If we haven't seen this article, add it
        if article_id not in seen:
            seen[article_id] = article
        else:
            # We've seen it - keep the one with higher priority
            existing_priority = seen[article_id]['source_priority']
            new_priority = article['source_priority']
            
            if new_priority > existing_priority:
                seen[article_id] = article
    
    return list(seen.values())


def fetch_all_news_for_ticker(ticker):
    """
    Fetch news for a ticker from ALL sources and unify.
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        list: Unified list of articles from all sources
    """
    
    print(f"\n{'='*80}")
    print(f"FETCHING ALL NEWS FOR: {ticker}")
    print(f"{'='*80}")
    
    all_articles = []
    
    # 1. Fetch from NewsAPI
    print("\n1️⃣ Fetching from NewsAPI...")
    try:
        newsapi_articles = newsapi_scraper.fetch_news_by_ticker(ticker)
        for article in newsapi_articles:
            cleaned = newsapi_scraper.extract_article_info(article)
            standardized = standardize_article(cleaned, 'newsapi', ticker)
            all_articles.append(standardized)
        print(f"✓ Added {len(newsapi_articles)} from NewsAPI")
    except Exception as e:
        print(f"✗ NewsAPI error: {e}")
    
    # 2. Fetch from Alpha Vantage
    print("\n2️⃣ Fetching from Alpha Vantage...")
    try:
        av_articles = alphavantage_scraper.fetch_news_by_ticker(ticker)
        for article in av_articles:
            cleaned = alphavantage_scraper.extract_article_info(article)
            standardized = standardize_article(cleaned, 'alphavantage', ticker)
            all_articles.append(standardized)
        print(f"✓ Added {len(av_articles)} from Alpha Vantage")
    except Exception as e:
        print(f"✗ Alpha Vantage error: {e}")
    
    # 3. Fetch from Finnhub
    print("\n3️⃣ Fetching from Finnhub...")
    try:
        finnhub_articles = finnhub_scraper.fetch_news_by_ticker(ticker)
        for article in finnhub_articles:
            cleaned = finnhub_scraper.extract_article_info(article)
            standardized = standardize_article(cleaned, 'finnhub', ticker)
            all_articles.append(standardized)
        print(f"✓ Added {len(finnhub_articles)} from Finnhub")
    except Exception as e:
        print(f"✗ Finnhub error: {e}")
    
    # 4. Remove duplicates (keep highest priority)
    print(f"\n4️⃣ Removing duplicates...")
    print(f"   Before deduplication: {len(all_articles)} articles")
    all_articles = remove_duplicates(all_articles)
    print(f"   After deduplication: {len(all_articles)} articles")
    
    return all_articles


def fetch_all_news_for_multiple_tickers(tickers):
    """
    Fetch news for multiple tickers from all sources.
    
    Args:
        tickers (list): List of stock ticker symbols
    
    Returns:
        dict: Dictionary with ticker as key and list of articles as value
    """
    
    print("\n" + "🚀"*40)
    print("MASTER SCRAPER - COLLECTING FROM ALL SOURCES")
    print("🚀"*40)
    
    all_results = {}
    
    for i, ticker in enumerate(tickers):
        print(f"\n[{i+1}/{len(tickers)}] Processing: {ticker}")
        articles = fetch_all_news_for_ticker(ticker)
        all_results[ticker] = articles
        
        print(f"✓ Total unique articles for {ticker}: {len(articles)}")
    
    return all_results


def save_unified_data(data, filename='unified_news_data.json'):
    """
    Save unified data to JSON file.
    
    Args:
        data (dict): Dictionary with ticker -> articles mapping
        filename (str): Output filename
    """
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        total_articles = sum(len(articles) for articles in data.values())
        print(f"\n✅ Saved {total_articles} articles to {filename}")
        
        # Print summary by source
        source_counts = {}
        for articles in data.values():
            for article in articles:
                source_api = article['source_api']
                source_counts[source_api] = source_counts.get(source_api, 0) + 1
        
        print("\n📊 Articles by source:")
        for source, count in sorted(source_counts.items()):
            print(f"   {source}: {count} articles")
        
    except Exception as e:
        print(f"✗ Error saving data: {e}")


def test_master_scraper():
    """Test the master scraper with sample tickers."""
    
    # Test with these tickers
    test_tickers = ["AAPL", "TSLA", "MSFT"]
    
    # Fetch all news
    results = fetch_all_news_for_multiple_tickers(test_tickers)
    
    # Save to file
    save_unified_data(results)
    
    # Print summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    for ticker, articles in results.items():
        print(f"{ticker}: {len(articles)} unique articles")
    print("="*80)
    
    return results


if __name__ == "__main__":
    results = test_master_scraper()
    print("\n🎉 Master scraper test complete!")