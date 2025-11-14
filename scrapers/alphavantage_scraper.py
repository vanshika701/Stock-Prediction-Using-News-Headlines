# scrapers/alphavantage_scraper.py

import requests
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import ALPHAVANTAGE_KEY

# Rate limiting: Alpha Vantage allows 5 calls per minute
CALLS_PER_MINUTE = 5
CALL_INTERVAL = 60 / CALLS_PER_MINUTE  # 12 seconds between calls

last_call_time = 0


def rate_limit():
    """Ensure we don't exceed 5 calls per minute."""
    global last_call_time
    current_time = time.time()
    time_since_last_call = current_time - last_call_time
    
    if time_since_last_call < CALL_INTERVAL:
        wait_time = CALL_INTERVAL - time_since_last_call
        print(f"⏳ Rate limiting: waiting {wait_time:.1f} seconds...")
        time.sleep(wait_time)
    
    last_call_time = time.time()


def fetch_news_by_ticker(ticker, max_retries=3):
    """
    Fetch news for a specific ticker from Alpha Vantage.
    
    Args:
        ticker (str): Stock ticker symbol
        max_retries (int): Number of retry attempts
    
    Returns:
        list: List of articles or empty list if error
    """
    
    print(f"\n🔍 Alpha Vantage: Fetching news for {ticker}")
    
    # Check API key
    if not ALPHAVANTAGE_KEY or ALPHAVANTAGE_KEY == "your_alphavantage_key_here":
        print("✗ Error: Alpha Vantage API key not configured!")
        return []
    
    # Apply rate limiting
    rate_limit()
    
    # Alpha Vantage News API endpoint
    base_url = "https://www.alphavantage.co/query"
    
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': ticker,
        'apikey': ALPHAVANTAGE_KEY,
        'limit': 50  # Get up to 50 articles
    }
    
    # Retry logic
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API error messages
                if 'Note' in data:
                    print(f"✗ API Limit: {data['Note']}")
                    return []
                
                if 'Error Message' in data:
                    print(f"✗ Error: {data['Error Message']}")
                    return []
                
                # Extract articles from feed
                articles = data.get('feed', [])
                print(f"✓ Found {len(articles)} articles for {ticker}")
                
                return articles
            
            elif response.status_code == 429:
                print("✗ Rate limit exceeded!")
                return []
            
            else:
                print(f"✗ Error: Status code {response.status_code}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
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
    Convert Alpha Vantage article to standardized format.
    
    Args:
        article (dict): Raw article from Alpha Vantage
    
    Returns:
        dict: Standardized article format
    """
    
    # Alpha Vantage has different field names than NewsAPI
    return {
        'title': article.get('title', 'No title'),
        'description': article.get('summary', ''),
        'source': article.get('source', 'Unknown'),
        'author': article.get('authors', ['Unknown'])[0] if article.get('authors') else 'Unknown',
        'url': article.get('url', ''),
        'published_at': article.get('time_published', ''),
        'content': article.get('summary', ''),
        'sentiment_score': article.get('overall_sentiment_score', 0),
        'sentiment_label': article.get('overall_sentiment_label', 'Neutral')
    }


def test_alphavantage():
    """Test Alpha Vantage scraper with sample tickers."""
    
    print("\n" + "="*80)
    print("TESTING ALPHA VANTAGE SCRAPER")
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
            print(f"  Sentiment: {cleaned['sentiment_label']} ({cleaned['sentiment_score']})")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for ticker, articles in all_results.items():
        print(f"{ticker}: {len(articles)} articles")
    
    return all_results


if __name__ == "__main__":
    results = test_alphavantage()
    print(f"\n✓ Total articles: {sum(len(a) for a in results.values())}")