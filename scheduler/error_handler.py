# scheduler/error_handler.py
"""
Error handling and retry logic for scrapers.
Implements exponential backoff and fallback sources.
"""

import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries=3, base_delay=2):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        base_delay (int): Base delay in seconds (doubles each retry)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    
                    if retries > max_retries:
                        logger.error(f"Max retries reached for {func.__name__}: {e}")
                        raise
                    
                    delay = base_delay * (2 ** (retries - 1))
                    logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} after {delay}s: {e}")
                    time.sleep(delay)
            
        return wrapper
    return decorator


class ErrorHandler:
    """Handle errors and implement fallback strategies."""
    
    def __init__(self):
        """Initialize error handler."""
        self.error_count = {}
        self.last_errors = {}
    
    def log_error(self, source, error):
        """
        Log an error for a specific source.
        
        Args:
            source (str): Source name (e.g., 'newsapi', 'alphavantage')
            error (Exception): The error that occurred
        """
        if source not in self.error_count:
            self.error_count[source] = 0
        
        self.error_count[source] += 1
        self.last_errors[source] = {
            'error': str(error),
            'timestamp': time.time()
        }
        
        logger.error(f"Error in {source}: {error}")
        logger.info(f"Total errors for {source}: {self.error_count[source]}")
    
    def should_use_source(self, source, threshold=5):
        """
        Check if a source should be used based on error history.
        
        Args:
            source (str): Source name
            threshold (int): Max errors before disabling source
            
        Returns:
            bool: True if source should be used
        """
        error_count = self.error_count.get(source, 0)
        
        if error_count >= threshold:
            logger.warning(f"Source {source} disabled (too many errors: {error_count})")
            return False
        
        return True
    
    def get_fallback_source(self, failed_source):
        """
        Get fallback source when primary fails.
        
        Args:
            failed_source (str): Source that failed
            
        Returns:
            str: Fallback source name
        """
        fallbacks = {
            'newsapi': 'alphavantage',
            'alphavantage': 'finnhub',
            'finnhub': 'rss'
        }
        
        fallback = fallbacks.get(failed_source, 'rss')
        logger.info(f"Using fallback source: {fallback} (primary {failed_source} failed)")
        
        return fallback
    
    def reset_errors(self, source=None):
        """Reset error count for a source or all sources."""
        if source:
            self.error_count[source] = 0
            logger.info(f"Reset error count for {source}")
        else:
            self.error_count = {}
            logger.info("Reset all error counts")


# Example usage decorator
@retry_with_backoff(max_retries=3, base_delay=2)
def fetch_with_retry(url):
    """Example function that retries on failure."""
    import requests
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def test_error_handler():
    """Test error handling functionality."""
    
    print("\n" + "="*80)
    print("TESTING ERROR HANDLER")
    print("="*80)
    
    handler = ErrorHandler()
    
    # Simulate errors
    print("\n1️⃣ Simulating errors...")
    for i in range(3):
        handler.log_error('newsapi', Exception(f"Test error {i+1}"))
    
    # Check if should use source
    print("\n2️⃣ Checking source status...")
    print(f"Should use newsapi: {handler.should_use_source('newsapi')}")
    print(f"Should use alphavantage: {handler.should_use_source('alphavantage')}")
    
    # Test fallback
    print("\n3️⃣ Testing fallback...")
    fallback = handler.get_fallback_source('newsapi')
    print(f"Fallback for newsapi: {fallback}")
    
    # Reset errors
    print("\n4️⃣ Resetting errors...")
    handler.reset_errors('newsapi')
    print(f"Should use newsapi after reset: {handler.should_use_source('newsapi')}")
    
    print("\n✅ Error handler test complete!")


if __name__ == "__main__":
    test_error_handler()
