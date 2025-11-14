# scheduler/scheduler.py
"""
Scheduler for automatic news scraping and processing.
Runs scrapers at specified intervals and updates database.
"""

import schedule
import time
import sys
import os
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.master_scraper import fetch_all_news_for_multiple_tickers
from utils.ticker_extractor import TickerExtractor
from utils.context_extractor import ContextExtractor
from preprocessor.text_cleaner import TextCleaner
from preprocessor.tokenizer import Tokenizer
from preprocessor.stop_words import StopWordsRemover
from preprocessor.lemmatizer import Lemmatizer
from preprocessor.feature_extractor import FeatureExtractor
from database.db_manager import DatabaseManager
from database.cache_manager import CacheManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class NewsScheduler:
    """Automated news scraping and processing scheduler."""
    
    def __init__(self):
        """Initialize scheduler with all components."""
        
        logger.info("="*80)
        logger.info("INITIALIZING NEWS SCHEDULER")
        logger.info("="*80)
        
        # Initialize components
        self.ticker_extractor = TickerExtractor()
        self.context_extractor = ContextExtractor()
        self.text_cleaner = TextCleaner()
        self.tokenizer = Tokenizer()
        self.stopwords_remover = StopWordsRemover()
        self.lemmatizer = Lemmatizer()
        self.feature_extractor = FeatureExtractor()
        
        # Initialize database and cache
        self.db = DatabaseManager()
        if not self.db.conn:
            self.db.connect()
        
        self.cache = CacheManager()
        self.cache.connect()
        logger.info("✓ All components initialized")
        
        # Track last run
        self.last_run = None
        self.run_count = 0
    
    def process_article(self, article):
        """
        Process a single article through complete pipeline.
        
        Args:
            article (dict): Raw article
            
        Returns:
            dict: Processed article or None if error
        """
        try:
            # Extract tickers
            title = article.get('title', '')
            body = article.get('body', '')
            full_text = f"{title}. {body}"
            
            tickers = self.ticker_extractor.extract_all_tickers(full_text)
            
            # Extract contexts
            contexts = {}
            for ticker in tickers:
                ticker_contexts = self.context_extractor.extract_context_for_ticker(
                    full_text, ticker
                )
                contexts[ticker] = ticker_contexts
            
            # Clean text
            cleaned_title = self.text_cleaner.clean(title)
            cleaned_body = self.text_cleaner.clean(body)
            cleaned_text = f"{cleaned_title}. {cleaned_body}"
            
            # Tokenize
            tokens = self.tokenizer.tokenize_words(cleaned_text)
            filtered = self.stopwords_remover.remove(tokens)
            lemmatized = self.lemmatizer.lemmatize_tokens(filtered)
            
            # Extract features
            features = self.feature_extractor.extract_all_features(
                full_text, lemmatized
            )
            
            # Calculate sentiment
            keywords = features.get('financial_keywords', {})
            pos = len(keywords.get('positive', []))
            neg = len(keywords.get('negative', []))
            
            if pos > neg:
                sentiment = 'positive'
            elif neg > pos:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Create processed article
            processed = {
                'article_id': article.get('article_id', ''),
                'title': cleaned_title,
                'body': cleaned_body,
                'source': article.get('source', 'Unknown'),
                'timestamp': article.get('timestamp', datetime.now().isoformat()),
                'url': article.get('url', ''),
                'raw_text': cleaned_text,
                'tickers_mentioned': ','.join(tickers) if tickers else None,
                'sentiment': sentiment,
                'ticker_contexts': contexts,
                'features': features,
                'tokens': {
                    'original': tokens,
                    'filtered': filtered,
                    'lemmatized': lemmatized
                }
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            return None
    
    def scrape_and_process(self):
        """
        Main function: Scrape news, process, and store in database.
        """
        
        self.run_count += 1
        
        logger.info("="*80)
        logger.info(f"SCHEDULED RUN #{self.run_count}")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        try:
            # Step 1: Scrape news
            logger.info("\n1️⃣ Scraping news from all sources...")
            
            tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN']
            raw_articles = fetch_all_news_for_multiple_tickers(tickers)
            
            total_raw = sum(len(articles) for articles in raw_articles.values())
            logger.info(f"✓ Scraped {total_raw} articles")
            
            # Step 2: Process articles
            logger.info("\n2️⃣ Processing articles...")
            
            processed_articles = []
            for ticker, articles in raw_articles.items():
                for article in articles:
                    processed = self.process_article(article)
                    if processed:
                        processed_articles.append(processed)
            
            logger.info(f"✓ Processed {len(processed_articles)} articles")
            
            # Step 3: Store in database
            logger.info("\n3️⃣ Storing in database...")
            
            stored = 0
            skipped = 0
            
            for article in processed_articles:
                try:
                    # Check if already exists
                    if not self.db.article_exists(article['article_id']):
                        self.db.insert_article(article)
                        stored += 1
                    else:
                        skipped += 1
                except Exception as e:
                    logger.error(f"Error storing article: {e}")
            
            logger.info(f"✓ Stored {stored} new articles")
            logger.info(f"✓ Skipped {skipped} duplicates")
            
            # Step 4: Update cache
            logger.info("\n4️⃣ Updating cache...")

            # Prepare data structure for cache_multiple_tickers (which takes a dict: {ticker: [articles]})
            articles_by_ticker = {}

            for article in processed_articles[:50]:
                # Retrieve the tickers_mentioned value; ensure it defaults to a string if None/missing
                tickers_str = article.get('tickers_mentioned')
    
                # 🛑 ROBUST FIX: Ensure tickers_str is a non-empty string before splitting
                if isinstance(tickers_str, str) and tickers_str.strip():
                    ticker = tickers_str.split(',')[0].strip()
                else:
                    # Fallback for None or empty string
                    ticker = 'GENERAL'
                
                if ticker not in articles_by_ticker:
                    articles_by_ticker[ticker] = []
        
                # We only need the key fields for cache, not the whole processed dict
                cacheable_data = {
                    'article_id': article.get('article_id', ''),
                    'title': article.get('title', ''),
                    'source': article.get('source', 'Unknown'),
                    'timestamp': article.get('timestamp', datetime.now().isoformat()),
                    'url': article.get('url', ''),
                    'sentiment': article.get('sentiment', 'neutral'),
                    'tickers_mentioned': article.get('tickers_mentioned', '')
                }
                
                articles_by_ticker[ticker].append(cacheable_data)

            # Call the correct batch method from CacheManager
            if articles_by_ticker:
                try:
                    self.cache.cache_multiple_tickers(articles_by_ticker) 
                    logger.info(f"✓ Cache updated for {len(articles_by_ticker)} ticker groups")
                except Exception as e:
                    # Note the general error for the batch operation
                    logger.error(f"Error caching articles: {e}") 
            else:
                logger.info("✓ No articles to cache.")
            
            # Summary
            logger.info("\n" + "="*80)
            logger.info("RUN SUMMARY")
            logger.info("="*80)
            logger.info(f"Scraped: {total_raw} articles")
            logger.info(f"Processed: {len(processed_articles)} articles")
            logger.info(f"Stored: {stored} new articles")
            logger.info(f"Skipped: {skipped} duplicates")
            logger.info(f"Next run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80)
            
            self.last_run = datetime.now()
            
        except Exception as e:
            logger.error(f"Error in scheduled run: {e}")
    
    def run_continuously(self, interval_minutes=15):
        """
        Run scraper continuously at specified interval.
        
        Args:
            interval_minutes (int): Minutes between runs
        """
        
        logger.info(f"\n🚀 Starting continuous scraper...")
        logger.info(f"   Interval: Every {interval_minutes} minutes")
        logger.info(f"   Press Ctrl+C to stop\n")
        
        # Schedule the job
        schedule.every(interval_minutes).minutes.do(self.scrape_and_process)
        
        # Run once immediately
        logger.info("Running initial scrape...")
        self.scrape_and_process()
        
        # Run continuously
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\n\n⏹️  Scheduler stopped by user")
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up...")
        self.db.close()
        logger.info("✅ Cleanup complete")


def test_scheduler():
    """Test the scheduler with a single run."""
    
    print("\n" + "="*80)
    print("TESTING SCHEDULER")
    print("="*80)
    
    scheduler = NewsScheduler()
    
    print("\n🧪 Running test scrape...")
    scheduler.scrape_and_process()
    
    print("\n✅ Test complete!")
    
    scheduler.cleanup()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Test mode: run once
        test_scheduler()
    else:
        # Production mode: run continuously
        scheduler = NewsScheduler()
        scheduler.run_continuously(interval_minutes=15)
