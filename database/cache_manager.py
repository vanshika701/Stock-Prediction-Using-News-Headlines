# database/cache_manager.py

import redis
import json
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import REDIS_URL


class CacheManager:
    """Manages Redis caching for news articles."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = None
        self.cache_expiry = 86400  # 24 hours in seconds
    
    def connect(self):
        """Establish connection to Redis."""
        try:
            self.redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True  # Auto-decode bytes to strings
            )
            # Test connection
            self.redis_client.ping()
            print("✓ Redis connected successfully!")
            return True
        except Exception as e:
            print(f"✗ Redis connection error: {e}")
            print("  Make sure Redis server is running!")
            return False
    
    def close(self):
        """Close Redis connection."""
        if self.redis_client:
            self.redis_client.close()
            print("✓ Redis connection closed")
    
    # ========== KEY GENERATION ==========
    
    def generate_key(self, ticker, date=None):
        """
        Generate cache key for ticker and date.
        
        Format: ticker:YYYY-MM-DD or ticker:latest
        
        Args:
            ticker (str): Stock ticker symbol
            date (str): Date in YYYY-MM-DD format, or None for 'latest'
        
        Returns:
            str: Redis key
        """
        if date:
            return f"{ticker}:{date}"
        else:
            return f"{ticker}:latest"
    
    def generate_list_key(self, prefix="articles"):
        """
        Generate key for list of all cached tickers.
        
        Args:
            prefix (str): Prefix for the key
        
        Returns:
            str: Redis key
        """
        return f"{prefix}:cached_tickers"
    
    # ========== CACHE OPERATIONS ==========
    
    def cache_articles(self, ticker, articles, expiry=None):
        """
        Cache articles for a ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            articles (list): List of article dictionaries
            expiry (int): Expiry time in seconds (default: 24 hours)
        
        Returns:
            bool: True if successful
        """
        if not self.redis_client:
            print("✗ Redis not connected!")
            return False
        
        try:
            # Generate key
            key = self.generate_key(ticker)
            
            # Convert articles to JSON
            data = json.dumps(articles)
            
            # Set in Redis with expiry
            expiry_time = expiry or self.cache_expiry
            self.redis_client.setex(key, expiry_time, data)
            
            # Add ticker to list of cached tickers
            self.redis_client.sadd(self.generate_list_key(), ticker)
            
            print(f"✓ Cached {len(articles)} articles for {ticker}")
            return True
        
        except Exception as e:
            print(f"✗ Cache error for {ticker}: {e}")
            return False
    
    def get_cached_articles(self, ticker):
        """
        Retrieve cached articles for a ticker.
        
        Args:
            ticker (str): Stock ticker symbol
        
        Returns:
            list: List of articles, or None if not found/expired
        """
        if not self.redis_client:
            print("✗ Redis not connected!")
            return None
        
        try:
            key = self.generate_key(ticker)
            
            # Get from Redis
            data = self.redis_client.get(key)
            
            if data:
                articles = json.loads(data)
                print(f"✓ Cache HIT: Retrieved {len(articles)} articles for {ticker}")
                return articles
            else:
                print(f"✗ Cache MISS: No cached articles for {ticker}")
                return None
        
        except Exception as e:
            print(f"✗ Cache retrieval error for {ticker}: {e}")
            return None
    
    def cache_exists(self, ticker):
        """
        Check if cache exists for a ticker.
        
        Args:
            ticker (str): Stock ticker symbol
        
        Returns:
            bool: True if cache exists and not expired
        """
        if not self.redis_client:
            return False
        
        try:
            key = self.generate_key(ticker)
            return self.redis_client.exists(key) > 0
        except:
            return False
    
    def delete_cache(self, ticker):
        """
        Delete cached articles for a ticker.
        
        Args:
            ticker (str): Stock ticker symbol
        
        Returns:
            bool: True if successful
        """
        if not self.redis_client:
            return False
        
        try:
            key = self.generate_key(ticker)
            self.redis_client.delete(key)
            
            # Remove from cached tickers list
            self.redis_client.srem(self.generate_list_key(), ticker)
            
            print(f"✓ Deleted cache for {ticker}")
            return True
        except Exception as e:
            print(f"✗ Cache deletion error for {ticker}: {e}")
            return False
    
    def clear_all_cache(self):
        """
        Clear all cached articles.
        
        Returns:
            bool: True if successful
        """
        if not self.redis_client:
            return False
        
        try:
            # Get all cached tickers
            list_key = self.generate_list_key()
            tickers = self.redis_client.smembers(list_key)
            
            # Delete each ticker's cache
            for ticker in tickers:
                key = self.generate_key(ticker)
                self.redis_client.delete(key)
            
            # Clear the list
            self.redis_client.delete(list_key)
            
            print(f"✓ Cleared cache for {len(tickers)} tickers")
            return True
        except Exception as e:
            print(f"✗ Cache clear error: {e}")
            return False
    
    def get_cached_tickers(self):
        """
        Get list of all tickers that have cached data.
        
        Returns:
            set: Set of ticker symbols
        """
        if not self.redis_client:
            return set()
        
        try:
            list_key = self.generate_list_key()
            return self.redis_client.smembers(list_key)
        except:
            return set()
    
    def get_cache_ttl(self, ticker):
        """
        Get time-to-live (TTL) for cached ticker in seconds.
        
        Args:
            ticker (str): Stock ticker symbol
        
        Returns:
            int: Seconds until expiry, or -1 if expired/not found
        """
        if not self.redis_client:
            return -1
        
        try:
            key = self.generate_key(ticker)
            ttl = self.redis_client.ttl(key)
            return ttl
        except:
            return -1
    
    # ========== BATCH OPERATIONS ==========
    
    def cache_multiple_tickers(self, data_dict):
        """
        Cache articles for multiple tickers at once.
        
        Args:
            data_dict (dict): Dictionary with ticker -> articles mapping
        
        Returns:
            int: Number of successfully cached tickers
        """
        success_count = 0
        
        for ticker, articles in data_dict.items():
            if self.cache_articles(ticker, articles):
                success_count += 1
        
        print(f"✓ Cached {success_count}/{len(data_dict)} tickers")
        return success_count
    
    # ========== STATISTICS ==========
    
    def get_cache_stats(self):
        """
        Get statistics about the cache.
        
        Returns:
            dict: Cache statistics
        """
        if not self.redis_client:
            return {}
        
        try:
            cached_tickers = self.get_cached_tickers()
            
            stats = {
                'total_cached_tickers': len(cached_tickers),
                'cached_tickers': list(cached_tickers),
                'redis_memory_used': self.redis_client.info('memory').get('used_memory_human', 'N/A')
            }
            
            return stats
        except Exception as e:
            print(f"✗ Error getting cache stats: {e}")
            return {}


def test_cache():
    """Test Redis cache manager."""
    
    print("\n" + "="*80)
    print("TESTING REDIS CACHE MANAGER")
    print("="*80)
    
    cache = CacheManager()
    
    # Test 1: Connect
    print("\n1️⃣ Testing connection...")
    if not cache.connect():
        print("✗ Cannot continue without Redis connection")
        print("  Make sure Redis is running: redis-server")
        return
    
    # Test 2: Cache some sample articles
    print("\n2️⃣ Caching sample articles...")
    sample_articles = [
        {
            'article_id': 'test1',
            'title': 'Test Article 1',
            'ticker': 'AAPL',
            'source': 'Test Source'
        },
        {
            'article_id': 'test2',
            'title': 'Test Article 2',
            'ticker': 'AAPL',
            'source': 'Test Source'
        }
    ]
    
    cache.cache_articles('AAPL', sample_articles)
    
    # Test 3: Check if cache exists
    print("\n3️⃣ Checking if cache exists...")
    exists = cache.cache_exists('AAPL')
    print(f"✓ Cache exists for AAPL: {exists}")
    
    # Test 4: Retrieve from cache
    print("\n4️⃣ Retrieving from cache...")
    cached_data = cache.get_cached_articles('AAPL')
    if cached_data:
        print(f"✓ Retrieved {len(cached_data)} articles")
    
    # Test 5: Check TTL
    print("\n5️⃣ Checking cache TTL...")
    ttl = cache.get_cache_ttl('AAPL')
    print(f"✓ Cache expires in {ttl} seconds ({ttl/3600:.1f} hours)")
    
    # Test 6: Get cache stats
    print("\n6️⃣ Getting cache statistics...")
    stats = cache.get_cache_stats()
    print(f"✓ Total cached tickers: {stats.get('total_cached_tickers', 0)}")
    print(f"✓ Redis memory used: {stats.get('redis_memory_used', 'N/A')}")
    
    # Test 7: Cache miss scenario
    print("\n7️⃣ Testing cache miss...")
    cached_data = cache.get_cached_articles('NONEXISTENT')
    
    # Clean up
    print("\n8️⃣ Cleaning up test data...")
    cache.delete_cache('AAPL')
    
    cache.close()
    print("\n✅ All cache tests passed!")


if __name__ == "__main__":
    test_cache()