# scrapers/newsapi_scraper.py

# IMPORT SECTION
# These are tools/libraries we need
import requests  # To make HTTP requests to APIs
from datetime import datetime, timedelta  # To work with dates
import time  # To add delays between requests
import json  # To work with JSON data
import sys
import os

# Add the parent directory to path so we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import NEWSAPI_KEY  # Import your API key


# COMPANY TICKER MAPPING
# This dictionary maps stock tickers to company names
# Why? Because some articles say "Apple" and some say "AAPL"
TICKER_TO_COMPANY = {
    "AAPL": "Apple Inc",
    "TSLA": "Tesla",
    "GOOGL": "Alphabet Google",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "META": "Meta Platforms",
    "NFLX": "Netflix",
    "AMD": "Advanced Micro Devices",
    "INTC": "Intel"
}

# FINANCIAL NEWS DOMAINS
# Only scrape from these trusted financial news sources
FINANCIAL_DOMAINS = [
    "bloomberg.com",
    "reuters.com",
    "wsj.com",
    "cnbc.com",
    "marketwatch.com",
    "forbes.com",
    "ft.com",
    "barrons.com",
    "seekingalpha.com",
    "fool.com",
    "investing.com",
    "benzinga.com",
    "thestreet.com",
    "finance.yahoo.com",
    "investopedia.com"
]

# FINANCIAL KEYWORDS
# Articles must contain at least one of these to be considered financial
FINANCIAL_KEYWORDS = [
    "stock", "shares", "market", "trading", "investor", "investment",
    "earnings", "revenue", "profit", "quarter", "financial", "price",
    "wall street", "nasdaq", "dow jones", "s&p 500", "analyst",
    "forecast", "valuation", "dividend", "shareholder", "ipo"
]


def is_financial_article(article):
    """
    Check if an article is finance-related based on domain and content.
    
    Args:
        article (dict): Raw article from NewsAPI
    
    Returns:
        bool: True if article is financial, False otherwise
    """
    # Get article URL and convert to lowercase
    url = article.get('url', '').lower()
    
    # Check if article is from a financial domain
    is_from_financial_domain = any(domain in url for domain in FINANCIAL_DOMAINS)
    
    # Get text content to search for keywords
    title = (article.get('title') or '').lower()
    description = (article.get('description') or '').lower()
    content = (article.get('content') or '').lower()
    
    # Combine all text
    full_text = f"{title} {description} {content}"
    
    # Check if article contains financial keywords
    contains_financial_keywords = any(keyword in full_text for keyword in FINANCIAL_KEYWORDS)
    
    # Article must be from financial domain OR contain financial keywords
    return is_from_financial_domain or contains_financial_keywords


def get_date_range():
    """
    Calculate date range for the last 7 days.
    
    Why? NewsAPI needs dates in format: YYYY-MM-DD
    We want news from the last 7 days for better sentiment analysis data.
    
    Returns:
        tuple: (from_date, to_date) both as strings like "2024-01-15"
    """
    # Get today's date
    today = datetime.now()
    
    # Subtract 7 days to get the start date
    seven_days_ago = today - timedelta(days=7)
    
    # Convert to string format that API wants: "2024-01-15"
    from_date = seven_days_ago.strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    # Print so you can see what dates we're using
    print(f"Fetching news from {from_date} to {to_date} (Last 7 days)")
    
    return from_date, to_date


def fetch_news_by_ticker(ticker):
    """
    Fetch news articles for a specific stock ticker from NewsAPI.
    
    Args:
        ticker (str): Stock ticker symbol like "AAPL", "TSLA"
    
    Returns:
        list: List of article dictionaries, or empty list if error
    """
    
    # STEP 1: Get the date range (last 24 hours)
    from_date, to_date = get_date_range()
    
    # STEP 2: Get company name for this ticker
    company_name = TICKER_TO_COMPANY.get(ticker, ticker)
    print(f"\nSearching for: {ticker} ({company_name})")
    
    # STEP 3: Build the search query with financial keywords
    # We search for ticker/company AND add financial context
    search_query = f"({ticker} OR {company_name}) AND (stock OR shares OR market OR trading OR earnings)"
    
    # STEP 4: Build the complete API URL
    base_url = "https://newsapi.org/v2/everything"
    
    # These are the parameters we send to the API
    params = {
        'q': search_query,           # What to search for
        'from': from_date,            # Start date
        'to': to_date,                # End date
        'language': 'en',             # Only English articles
        'sortBy': 'publishedAt',      # Newest first
        'apiKey': NEWSAPI_KEY         # Your API key
    }
    
    print(f"Making request to NewsAPI...")
    
    # STEP 5: Make the API request
    try:
        # Send GET request to NewsAPI
        response = requests.get(base_url, params=params, timeout=10)
        
        # Check if request was successful (status code 200 = OK)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Get the articles from the response
            articles = data.get('articles', [])
            total_results = data.get('totalResults', 0)
            
            print(f"✓ Success! Found {total_results} total articles")
            
            # FILTER: Only keep financial articles
            financial_articles = [article for article in articles if is_financial_article(article)]
            
            print(f"✓ Filtered to {len(financial_articles)} financial articles")
            
            return financial_articles
            
        elif response.status_code == 429:
            # Rate limit exceeded
            print("✗ Error: Rate limit exceeded. You've made too many requests.")
            print("  Free tier allows 100 requests per day.")
            return []
            
        elif response.status_code == 401:
            # Invalid API key
            print("✗ Error: Invalid API key. Check your .env file.")
            return []
            
        else:
            # Some other error
            print(f"✗ Error: API returned status code {response.status_code}")
            print(f"  Message: {response.text}")
            return []
    
    except requests.exceptions.Timeout:
        print("✗ Error: Request timed out. API took too long to respond.")
        return []
    
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to NewsAPI. Check your internet.")
        return []
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return []


def extract_article_info(article):
    """
    Extract relevant information from a raw NewsAPI article.
    
    Args:
        article (dict): Raw article from NewsAPI
    
    Returns:
        dict: Cleaned article with standardized fields
    """
    
    # Extract fields from the article
    # .get() is safe - returns None if field doesn't exist
    
    cleaned_article = {
        'title': article.get('title', 'No title'),
        'description': article.get('description', ''),
        'source': article.get('source', {}).get('name', 'Unknown'),
        'author': article.get('author', 'Unknown'),
        'url': article.get('url', ''),
        'published_at': article.get('publishedAt', ''),
        'content': article.get('content', '')
    }
    
    return cleaned_article


def print_article_summary(article, index):
    """
    Print a nice summary of an article.
    
    Args:
        article (dict): Article dictionary
        index (int): Article number
    """
    print(f"\n{'='*80}")
    print(f"Article #{index + 1}")
    print(f"{'='*80}")
    print(f"Title:       {article['title']}")
    print(f"Source:      {article['source']}")
    print(f"Published:   {article['published_at']}")
    print(f"URL:         {article['url']}")
    print(f"Description: {article['description'][:150]}...")  # First 150 chars
    print(f"{'='*80}")


def save_to_json(all_results, filename='news_data.json'):
    """
    Save all scraped articles to a JSON file.
    
    Args:
        all_results (dict): Dictionary with ticker as key and list of articles as value
        filename (str): Name of the JSON file to save to
    """
    
    # Save directly in root directory (no subdirectory)
    filepath = filename
    
    # Prepare data for saving
    # Extract clean article info for each article
    cleaned_results = {}
    for ticker, articles in all_results.items():
        cleaned_results[ticker] = [extract_article_info(article) for article in articles]
    
    # Save to JSON file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cleaned_results, f, indent=4, ensure_ascii=False)
        
        print(f"\n✓ Saved all articles to: {filepath}")
        
        # Calculate total articles
        total_articles = sum(len(articles) for articles in cleaned_results.values())
        print(f"✓ Total articles saved: {total_articles}")
        
    except Exception as e:
        print(f"\n✗ Error saving to JSON: {e}")


def test_newsapi():
    """
    Test function to verify NewsAPI is working.
    This will fetch news for all 5 tickers and display results.
    """
    
    print("\n" + "="*80)
    print("TESTING NEWSAPI SCRAPER (FINANCIAL NEWS ONLY)")
    print("="*80)
    
    # List of tickers to test - ALL TICKERS FROM YOUR ORIGINAL CODE
    test_tickers = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", "NVDA", "META", "NFLX", "AMD", "INTC"]
    
    # Dictionary to store all results - initialize properly
    all_results = {}
    
    # Make sure we have a valid API key
    if not NEWSAPI_KEY or NEWSAPI_KEY == "your_newsapi_key_here":
        print("\n✗ ERROR: NewsAPI key not configured!")
        print("  Please set NEWSAPI_KEY in your .env file")
        return {}
    
    # Loop through each ticker
    for ticker in test_tickers:
        print(f"\n{'#'*80}")
        print(f"# Testing: {ticker}")
        print(f"{'#'*80}")
        
        try:
            # Fetch news for this ticker
            articles = fetch_news_by_ticker(ticker)
            
            # Store results - make sure articles is a list
            if articles is None:
                articles = []
            all_results[ticker] = articles
            
        except Exception as e:
            print(f"✗ Error processing {ticker}: {e}")
            all_results[ticker] = []
            continue
        
        # If we got articles, show the first 3
        if articles:
            print(f"\nShowing first 3 articles for {ticker}:")
            
            for i, article in enumerate(articles[:3]):
                cleaned = extract_article_info(article)
                print_article_summary(cleaned, i)
        else:
            print(f"\nNo financial articles found for {ticker}")
        
        # Wait 1 second between requests to be nice to the API
        if ticker != test_tickers[-1]:  # Don't wait after last one
            print("\nWaiting 1 second before next request...")
            time.sleep(1)
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for ticker, articles in all_results.items():
        print(f"{ticker}: {len(articles)} financial articles found")
    print("="*80)
    
    # Save all results to JSON file
    save_to_json(all_results)
    
    return all_results


# This runs when you execute the file directly
if __name__ == "__main__":
    # Run the test
    results = test_newsapi()
    
    print("\n✓ Test complete!")
    print(f"Total financial articles across all tickers: {sum(len(articles) for articles in results.values())}")