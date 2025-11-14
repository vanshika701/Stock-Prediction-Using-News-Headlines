# scrapers/rss_scraper.py

import feedparser
from datetime import datetime, timedelta
import time

# List of financial RSS feeds
RSS_FEEDS = {
    'Yahoo Finance': 'https://finance.yahoo.com/news/rssindex',
    'Reuters Business': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
    'MarketWatch': 'http://feeds.marketwatch.com/marketwatch/topstories/',
    'Seeking Alpha': 'https://seekingalpha.com/feed.xml',
    'Benzinga': 'https://www.benzinga.com/feed'
}

# Financial keywords to filter articles
FINANCIAL_KEYWORDS = [
    "stock", "shares", "market", "trading", "investor", "investment",
    "earnings", "revenue", "profit", "quarter", "financial", "price",
    "wall street", "nasdaq", "dow jones", "s&p 500", "analyst",
    "forecast", "valuation", "dividend", "shareholder", "ipo"
]


def is_recent(published_date, days=7):
    """
    Check if article is from the last N days.
    
    Args:
        published_date: Article publish date (struct_time)
        days (int): Number of days to look back
    
    Returns:
        bool: True if article is recent
    """
    if not published_date:
        return False
    
    try:
        # Convert struct_time to datetime
        article_date = datetime(*published_date[:6])
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return article_date >= cutoff_date
    except:
        return False


def is_financial_content(title, summary):
    """
    Check if article content is finance-related.
    
    Args:
        title (str): Article title
        summary (str): Article summary
    
    Returns:
        bool: True if content contains financial keywords
    """
    text = f"{title} {summary}".lower()
    return any(keyword in text for keyword in FINANCIAL_KEYWORDS)


def fetch_rss_feed(feed_name, feed_url):
    """
    Parse a single RSS feed.
    
    Args:
        feed_name (str): Name of the feed
        feed_url (str): URL of the RSS feed
    
    Returns:
        list: List of articles from this feed
    """
    
    print(f"\n🔍 RSS: Parsing {feed_name}")
    
    try:
        # Parse the RSS feed
        feed = feedparser.parse(feed_url)
        
        # Check if feed was parsed successfully
        if feed.bozo:  # bozo = parsing error
            print(f"✗ Warning: Feed may have errors")
        
        articles = []
        
        # Loop through entries in the feed
        for entry in feed.entries:
            # Extract information
            title = entry.get('title', 'No title')
            summary = entry.get('summary', entry.get('description', ''))
            link = entry.get('link', '')
            published = entry.get('published_parsed', None)
            
            # Filter: only recent financial articles
            if is_recent(published, days=7) and is_financial_content(title, summary):
                article = {
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'published': published,
                    'source': feed_name
                }
                articles.append(article)
        
        print(f"✓ Found {len(articles)} relevant articles from {feed_name}")
        return articles
    
    except Exception as e:
        print(f"✗ Error parsing {feed_name}: {e}")
        return []


def extract_article_info(article):
    """
    Convert RSS article to standardized format.
    
    Args:
        article (dict): Raw RSS article
    
    Returns:
        dict: Standardized article format
    """
    
    # Convert published time to ISO format
    published_at = ''
    if article.get('published'):
        try:
            dt = datetime(*article['published'][:6])
            published_at = dt.isoformat()
        except:
            published_at = ''
    
    return {
        'title': article.get('title', 'No title'),
        'description': article.get('summary', ''),
        'source': article.get('source', 'Unknown'),
        'author': 'Unknown',
        'url': article.get('link', ''),
        'published_at': published_at,
        'content': article.get('summary', '')
    }


def fetch_all_rss_feeds():
    """
    Fetch articles from all RSS feeds.
    
    Returns:
        list: Combined list of all articles
    """
    
    print("\n" + "="*80)
    print("FETCHING RSS FEEDS")
    print("="*80)
    
    all_articles = []
    
    for feed_name, feed_url in RSS_FEEDS.items():
        articles = fetch_rss_feed(feed_name, feed_url)
        all_articles.extend(articles)
        
        # Be polite - wait between requests
        time.sleep(1)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total articles from all RSS feeds: {len(all_articles)}")
    
    return all_articles


def test_rss():
    """Test RSS feed parser."""
    
    articles = fetch_all_rss_feeds()
    
    if articles:
        print("\n📰 Sample articles:")
        for i, article in enumerate(articles[:5]):
            cleaned = extract_article_info(article)
            print(f"\n{i+1}. {cleaned['title'][:80]}...")
            print(f"   Source: {cleaned['source']}")
            print(f"   URL: {cleaned['url']}")
    
    return articles


if __name__ == "__main__":
    results = test_rss()
    print(f"\n✓ Test complete! Found {len(results)} financial articles")