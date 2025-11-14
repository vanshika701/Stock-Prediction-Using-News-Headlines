# scheduler/rate_limiter.py
"""
Rate limiting for API calls to prevent exceeding limits.
Tracks API usage and enforces delays.
"""

import time
from collections import deque
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API calls."""
    
    def __init__(self, calls_per_minute=5, calls_per_day=100):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute (int): Max calls per minute
            calls_per_day (int): Max calls per day
        """
        self.calls_per_minute = calls_per_minute
        self.calls_per_day = calls_per_day
        
        # Track recent calls
        self.minute_calls = deque(maxlen=calls_per_minute)
        self.day_calls = deque(maxlen=calls_per_day)
        
        logger.info(f"✓ Rate limiter initialized ({calls_per_minute}/min, {calls_per_day}/day)")
    
    def can_make_call(self):
        """
        Check if a call can be made without exceeding limits.
        
        Returns:
            bool: True if call is allowed
        """
        now = time.time()
        
        # Clean old minute calls (older than 60 seconds)
        while self.minute_calls and (now - self.minute_calls[0]) > 60:
            self.minute_calls.popleft()
        
        # Clean old day calls (older than 24 hours)
        while self.day_calls and (now - self.day_calls[0]) > 86400:
            self.day_calls.popleft()
        
        # Check limits
        minute_ok = len(self.minute_calls) < self.calls_per_minute
        day_ok = len(self.day_calls) < self.calls_per_day
        
        return minute_ok and day_ok
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        
        while not self.can_make_call():
            # Calculate wait time
            if len(self.minute_calls) >= self.calls_per_minute:
                wait_time = 60 - (time.time() - self.minute_calls[0])
                logger.warning(f"Rate limit reached (minute). Waiting {wait_time:.1f}s...")
            else:
                wait_time = 60
                logger.warning(f"Rate limit reached (day). Waiting...")
            
            time.sleep(max(1, wait_time))
    
    def record_call(self):
        """Record that a call was made."""
        now = time.time()
        self.minute_calls.append(now)
        self.day_calls.append(now)
    
    def make_call(self, func, *args, **kwargs):
        """
        Make an API call with rate limiting.
        
        Args:
            func: Function to call
            *args, **kwargs: Arguments for function
            
        Returns:
            Result of function call
        """
        # Wait if needed
        self.wait_if_needed()
        
        # Make call
        try:
            result = func(*args, **kwargs)
            self.record_call()
            return result
        except Exception as e:
            logger.error(f"Error in rate-limited call: {e}")
            raise
    
    def get_stats(self):
        """Get current rate limit statistics."""
        now = time.time()
        
        # Count recent calls
        minute_calls = sum(1 for t in self.minute_calls if (now - t) <= 60)
        day_calls = sum(1 for t in self.day_calls if (now - t) <= 86400)
        
        return {
            'calls_last_minute': minute_calls,
            'calls_last_day': day_calls,
            'minute_limit': self.calls_per_minute,
            'day_limit': self.calls_per_day,
            'minute_remaining': self.calls_per_minute - minute_calls,
            'day_remaining': self.calls_per_day - day_calls
        }


class APIRateLimiters:
    """Manage rate limiters for multiple APIs."""
    
    def __init__(self):
        """Initialize rate limiters for each API."""
        
        # Different limits for each API
        self.limiters = {
            'newsapi': RateLimiter(calls_per_minute=10, calls_per_day=100),
            'alphavantage': RateLimiter(calls_per_minute=5, calls_per_day=500),
            'finnhub': RateLimiter(calls_per_minute=60, calls_per_day=1000),
            'rss': RateLimiter(calls_per_minute=30, calls_per_day=10000)
        }
        
        logger.info("✓ API rate limiters initialized")
    
    def make_call(self, api_name, func, *args, **kwargs):
        """
        Make rate-limited call to specific API.
        
        Args:
            api_name (str): API name ('newsapi', 'alphavantage', etc.)
            func: Function to call
            
        Returns:
            Result of function call
        """
        limiter = self.limiters.get(api_name)
        
        if not limiter:
            logger.warning(f"No rate limiter for {api_name}, calling directly")
            return func(*args, **kwargs)
        
        return limiter.make_call(func, *args, **kwargs)
    
    def get_all_stats(self):
        """Get statistics for all APIs."""
        return {
            api: limiter.get_stats()
            for api, limiter in self.limiters.items()
        }


def test_rate_limiter():
    """Test rate limiting functionality."""
    
    print("\n" + "="*80)
    print("TESTING RATE LIMITER")
    print("="*80)
    
    # Create rate limiter (5 calls per minute for testing)
    limiter = RateLimiter(calls_per_minute=3, calls_per_day=10)
    
    print("\n1️⃣ Making 3 rapid calls (should work)...")
    for i in range(3):
        limiter.wait_if_needed()
        limiter.record_call()
        print(f"   Call {i+1} - Success")
        time.sleep(0.1)
    
    stats = limiter.get_stats()
    print(f"\n📊 Stats: {stats}")
    
    print("\n2️⃣ Attempting 4th call (should wait)...")
    print("   This will wait ~60 seconds...")
    limiter.wait_if_needed()
    limiter.record_call()
    print("   Call 4 - Success after wait")
    
    print("\n✅ Rate limiter test complete!")


if __name__ == "__main__":
    test_rate_limiter()
