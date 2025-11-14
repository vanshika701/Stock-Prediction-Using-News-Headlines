# scheduler/priority_scheduler.py
"""
Priority-based scheduler that fetches high-volume stocks more frequently.
"""

import schedule
import time
import sys
import os
from datetime import datetime
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.master_scraper import fetch_all_news_for_multiple_tickers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class PriorityScheduler:
    """Scheduler with priority tiers for different stocks."""
    
    def __init__(self):
        """Initialize with priority tiers."""
        
        # High priority: Fetch every 10 minutes
        self.high_priority = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN']
        
        # Medium priority: Fetch every 20 minutes
        self.medium_priority = ['NVDA', 'META', 'NFLX', 'AMD', 'INTC']
        
        # Low priority: Fetch every 30 minutes
        self.low_priority = ['BA', 'DIS', 'JPM', 'V', 'WMT']
        
        logger.info("✓ Priority scheduler initialized")
    
    def fetch_high_priority(self):
        """Fetch high-priority stocks."""
        logger.info(f"📈 Fetching HIGH priority stocks: {self.high_priority}")
        
        try:
            articles = fetch_all_news_for_multiple_tickers(self.high_priority)
            total = sum(len(a) for a in articles.values())
            logger.info(f"✓ Fetched {total} articles from high priority stocks")
        except Exception as e:
            logger.error(f"Error fetching high priority: {e}")
    
    def fetch_medium_priority(self):
        """Fetch medium-priority stocks."""
        logger.info(f"📊 Fetching MEDIUM priority stocks: {self.medium_priority}")
        
        try:
            articles = fetch_all_news(self.medium_priority)
            total = sum(len(a) for a in articles.values())
            logger.info(f"✓ Fetched {total} articles from medium priority stocks")
        except Exception as e:
            logger.error(f"Error fetching medium priority: {e}")
    
    def fetch_low_priority(self):
        """Fetch low-priority stocks."""
        logger.info(f"📉 Fetching LOW priority stocks: {self.low_priority}")
        
        try:
            articles = fetch_all_news(self.low_priority)
            total = sum(len(a) for a in articles.values())
            logger.info(f"✓ Fetched {total} articles from low priority stocks")
        except Exception as e:
            logger.error(f"Error fetching low priority: {e}")
    
    def run(self):
        """Run priority-based scheduler."""
        
        logger.info("\n🚀 Starting priority-based scheduler...")
        logger.info("   High priority: Every 10 minutes")
        logger.info("   Medium priority: Every 20 minutes")
        logger.info("   Low priority: Every 30 minutes")
        logger.info("   Press Ctrl+C to stop\n")
        
        # Schedule jobs
        schedule.every(10).minutes.do(self.fetch_high_priority)
        schedule.every(20).minutes.do(self.fetch_medium_priority)
        schedule.every(30).minutes.do(self.fetch_low_priority)
        
        # Run once immediately
        self.fetch_high_priority()
        
        # Run continuously
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Priority scheduler stopped")


if __name__ == "__main__":
    scheduler = PriorityScheduler()
    scheduler.run()
