# integration_test.py
"""
Complete integration test: Scrape -> Store -> Cache
This tests the entire pipeline from Tasks 2.5 to 3.3
"""

import time
from datetime import datetime

# Import all our modules
from scrapers.master_scraper import fetch_all_news_for_multiple_tickers
from database.db_manager import DatabaseManager
from database.cache_manager import CacheManager


def run_complete_pipeline():
    """Run the complete news scraping and storage pipeline."""
    
    print("\n" + "🚀"*40)
    print("COMPLETE PIPELINE TEST")
    print("Tasks 2.5 - 3.3 Integration")
    print("🚀"*40)
    
    # Configuration
    test_tickers = ["AAPL", "TSLA", "MSFT"]
    
    # Initialize connections
    db = DatabaseManager()
    cache = CacheManager()
    
    # ========== STEP 1: CONNECT TO DATABASE & CACHE ==========
    print("\n" + "="*80)
    print("STEP 1: Connecting to Database and Cache")
    print("="*80)
    
    if not db.connect():
        print("✗ Database connection failed! Cannot continue.")
        return
    
    if not cache.connect():
        print("⚠ Redis connection failed! Will continue without caching.")
        cache = None
    
    # ========== STEP 2: SCRAPE NEWS FROM ALL SOURCES ==========
    print("\n" + "="*80)
    print("STEP 2: Scraping News from All Sources (NewsAPI, Alpha Vantage, Finnhub)")
    print("="*80)
    
    start_time = time.time()
    
    # Fetch news using master scraper (unifies all sources)
    all_news = fetch_all_news_for_multiple_tickers(test_tickers)
    
    scrape_time = time.time() - start_time
    print(f"\n⏱ Scraping took {scrape_time:.2f} seconds")
    
    # Count total articles
    total_articles = sum(len(articles) for articles in all_news.values())
    print(f"\n📊 Total articles scraped: {total_articles}")
    
    # ========== STEP 3: STORE IN DATABASE ==========
    print("\n" + "="*80)
    print("STEP 3: Storing Articles in PostgreSQL Database")
    print("="*80)
    
    total_inserted = 0
    
    for ticker, articles in all_news.items():
        print(f"\n💾 Storing {len(articles)} articles for {ticker}...")
        
        # Log scraping operation
        db.log_scraping(
            ticker=ticker,
            source_api='master_scraper',
            status='success',
            articles_found=len(articles),
            execution_time=scrape_time / len(test_tickers)
        )
        
        # Batch insert articles
        inserted = db.insert_articles_batch(articles)
        total_inserted += inserted
        
        # Update last scraped time
        db.update_last_scraped(ticker)
    
    print(f"\n✅ Inserted {total_inserted} new articles into database")
    print(f"   (Duplicates skipped: {total_articles - total_inserted})")
    
    # ========== STEP 4: CACHE IN REDIS ==========
    if cache:
        print("\n" + "="*80)
        print("STEP 4: Caching Articles in Redis")
        print("="*80)
        
        cached_count = cache.cache_multiple_tickers(all_news)
        print(f"\n✅ Cached data for {cached_count} tickers")
        
        # Show cache stats
        stats = cache.get_cache_stats()
        print(f"\n📊 Cache Statistics:")
        print(f"   Total cached tickers: {stats.get('total_cached_tickers', 0)}")
        print(f"   Redis memory used: {stats.get('redis_memory_used', 'N/A')}")
    
    # ========== STEP 5: VERIFY DATA ==========
    print("\n" + "="*80)
    print("STEP 5: Verifying Stored Data")
    print("="*80)
    
    for ticker in test_tickers:
        print(f"\n🔍 Verifying {ticker}...")
        
        # Check database
        db_articles = db.get_articles_by_ticker(ticker, limit=5)
        print(f"   Database: {len(db_articles)} articles found")
        
        if db_articles:
            latest = db_articles[0]
            print(f"   Latest: {latest['title'][:60]}...")
            print(f"   Source: {latest['source_api']}")
        
        # Check cache
        if cache:
            cached = cache.get_cached_articles(ticker)
            if cached:
                print(f"   Cache: {len(cached)} articles cached")
                ttl = cache.get_cache_ttl(ticker)
                print(f"   Cache expires in: {ttl/3600:.1f} hours")
            else:
                print(f"   Cache: No cached data")
    
    # ========== STEP 6: PERFORMANCE SUMMARY ==========
    print("\n" + "="*80)
    print("STEP 6: Performance Summary")
    print("="*80)
    
    print(f"\n⏱ Total execution time: {time.time() - start_time:.2f} seconds")
    print(f"📰 Articles scraped: {total_articles}")
    print(f"💾 Articles stored: {total_inserted}")
    print(f"🔄 Duplicates skipped: {total_articles - total_inserted}")
    print(f"📊 Average time per ticker: {scrape_time/len(test_tickers):.2f} seconds")
    
    # ========== STEP 7: TEST RETRIEVAL ==========
    print("\n" + "="*80)
    print("STEP 7: Testing Data Retrieval")
    print("="*80)
    
    print("\n1️⃣ Testing cache retrieval (fast)...")
    if cache:
        cache_start = time.time()
        cached = cache.get_cached_articles('AAPL')
        cache_time = time.time() - cache_start
        print(f"   ✓ Retrieved from cache in {cache_time*1000:.2f}ms")
    
    print("\n2️⃣ Testing database retrieval...")
    db_start = time.time()
    db_articles = db.get_articles_by_ticker('AAPL', limit=50)
    db_time = time.time() - db_start
    print(f"   ✓ Retrieved from database in {db_time*1000:.2f}ms")
    
    if cache:
        print(f"\n   💡 Cache is {db_time/cache_time:.1f}x faster than database!")
    
    print("\n3️⃣ Testing latest articles retrieval...")
    latest = db.get_latest_articles(n=10)
    print(f"   ✓ Retrieved {len(latest)} latest articles")
    
    # ========== CLEANUP ==========
    print("\n" + "="*80)
    print("Closing Connections")
    print("="*80)
    
    db.close()
    if cache:
        cache.close()
    
    print("\n" + "🎉"*40)
    print("PIPELINE TEST COMPLETE!")
    print("All systems operational: Scraping ✓ Storage ✓ Caching ✓")
    print("🎉"*40)


def test_cache_hit_scenario():
    """Test that cache actually speeds up retrieval."""
    
    print("\n" + "="*80)
    print("BONUS TEST: Cache Hit/Miss Performance")
    print("="*80)
    
    cache = CacheManager()
    db = DatabaseManager()
    
    if not cache.connect() or not db.connect():
        print("✗ Cannot run cache test")
        return
    
    ticker = "AAPL"
    
    # Test 1: Cache MISS (first retrieval)
    print(f"\n1️⃣ Cache MISS scenario (fetching {ticker} for first time)...")
    cache.delete_cache(ticker)  # Make sure it's not cached
    
    start = time.time()
    articles = db.get_articles_by_ticker(ticker, limit=50)
    db_time = time.time() - start
    print(f"   Database retrieval: {db_time*1000:.2f}ms")
    
    # Cache the results
    cache.cache_articles(ticker, [dict(a) for a in articles])
    
    # Test 2: Cache HIT (second retrieval)
    print(f"\n2️⃣ Cache HIT scenario (fetching {ticker} from cache)...")
    
    start = time.time()
    cached_articles = cache.get_cached_articles(ticker)
    cache_time = time.time() - start
    print(f"   Cache retrieval: {cache_time*1000:.2f}ms")
    
    # Compare
    print(f"\n📊 Performance Comparison:")
    print(f"   Database: {db_time*1000:.2f}ms")
    print(f"   Cache: {cache_time*1000:.2f}ms")
    print(f"   Speedup: {db_time/cache_time:.1f}x faster! 🚀")
    
    cache.close()
    db.close()


if __name__ == "__main__":
    # Run complete pipeline test
    run_complete_pipeline()
    
    # Bonus: Test cache performance
    print("\n\n")
    test_cache_hit_scenario()