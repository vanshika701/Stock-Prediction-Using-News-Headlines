# scrapers/finnhub_scraper.py

import requests
from datetime import datetime, timedelta
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FINNHUB_KEY


def get_date_range():
    """Get date range for last 7 days in YYYY-MM-DD format."""
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    
    # Finnhub wants dates as YYYY-MM-DD
    from_date = seven_days_ago.strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    return from_date, to_date


def fetch_news_by_ticker(ticker, max_retries=3):
    """
    Fetch company news from Finnhub.
    
    Args:
        ticker (str): Stock ticker symbol
        max_retries (int): Number of retry attempts
    
    Returns:
        list: List of articles or empty list if error
    """
    
    print(f"\n🔍 Finnhub: Fetching news for {ticker}")
    
    # Check API key
    if not FINNHUB_KEY or FINNHUB_KEY == "your_finnhub_key_here":
        print("✗ Error: Finnhub API key not configured!")
        return []
    
    # Get date range
    from_date, to_date = get_date_range()
    
    # Finnhub API endpoint
    base_url = "https://finnhub.io/api/v1/company-news"
    
    params = {
        'symbol': ticker,
        'from': from_date,
        'to': to_date,
        'token': FINNHUB_KEY
    }
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                articles = response.json()
                
                # Finnhub returns a list directly
                if isinstance(articles, list):
                    print(f"✓ Found {len(articles)} articles for {ticker}")
                    return articles
                else:
                    print(f"✗ Unexpected response format")
                    return []
            
            elif response.status_code == 401:
                print("✗ Invalid API key!")
                return []
            
            elif response.status_code == 429:
                print("✗ Rate limit exceeded!")
                return []
            
            else:
                print(f"✗ Error: Status code {response.status_code}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                return []
        
        except requests.exceptions.Timeout:
            print(f"✗ Timeout (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return []
        
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection error (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return []
        
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return []
    
    return []


def extract_article_info(article):
    """
    Convert Finnhub article to standardized format.
    
    Args:
        article (dict): Raw article from Finnhub
    
    Returns:
        dict: Standardized article format
    """
    
    # Finnhub uses Unix timestamp, convert to readable format
    timestamp = article.get('datetime', 0)
    published_at = datetime.fromtimestamp(timestamp).isoformat() if timestamp else ''
    
    return {
        'title': article.get('headline', 'No title'),
        'description': article.get('summary', ''),
        'source': article.get('source', 'Unknown'),
        'author': 'Unknown',  # Finnhub doesn't provide author
        'url': article.get('url', ''),
        'published_at': published_at,
        'content': article.get('summary', ''),
        'image': article.get('image', ''),
        'category': article.get('category', 'general')
    }


def test_finnhub():
    """Test Finnhub scraper with sample tickers."""
    
    print("\n" + "="*80)
    print("TESTING FINNHUB SCRAPER")
    print("="*80)
    
    test_tickers = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"]
    all_results = {}
    
    for ticker in test_tickers:
        articles = fetch_news_by_ticker(ticker)
        all_results[ticker] = articles
        
        if articles:
            print(f"\nSample article for {ticker}:")
            cleaned = extract_article_info(articles[0])
            print(f"  Title: {cleaned['title'][:80]}...")
            print(f"  Source: {cleaned['source']}")
            print(f"  Published: {cleaned['published_at']}")
        
        # Be nice to API - wait 1 second between requests
        if ticker != test_tickers[-1]:
            time.sleep(1)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for ticker, articles in all_results.items():
        print(f"{ticker}: {len(articles)} articles")
    
    return all_results


if __name__ == "__main__":
    results = test_finnhub()
    print(f"\n✓ Total articles: {sum(len(a) for a in results.values())}")