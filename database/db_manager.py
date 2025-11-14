# database/db_manager.py

import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DATABASE_URL


class DatabaseManager:
    """Handles all database operations for the news scraper."""
    
    def __init__(self):
        """Initialize database connection."""
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✓ Database connected successfully!")
            return True
        except Exception as e:
            print(f"✗ Database connection error: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✓ Database connection closed")
    
    def execute_query(self, query, params=None, fetch=False):
        """
        Execute a SQL query.
        
        Args:
            query (str): SQL query
            params (tuple): Query parameters
            fetch (bool): Whether to fetch results
        
        Returns:
            list or None: Query results if fetch=True
        """
        try:
            self.cursor.execute(query, params)
            if fetch:
                return self.cursor.fetchall()
            self.conn.commit()
            return None
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Query error: {e}")
            return None
    
    # ========== ARTICLE OPERATIONS ==========
    
    def article_exists(self, article_id=None, url=None):
        """
        Check if article already exists in database.
        
        Args:
            article_id (str): Unique article ID
            url (str): Article URL
        
        Returns:
            bool: True if article exists
        """
        query = """
            SELECT EXISTS(
                SELECT 1 FROM articles 
                WHERE article_id = %s OR url = %s
            ) AS exists
        """
        result = self.execute_query(query, (article_id, url), fetch=True)
        return result[0]['exists'] if result else False
    
    def insert_article(self, article):
        """
        Insert a new article into the database.
        
        Args:
            article (dict): Standardized article dictionary
        
        Returns:
            bool: True if successful
        """
        # Check if article already exists
        if self.article_exists(article.get('article_id'), article.get('url')):
            print(f"⚠ Article already exists: {article.get('title', '')[:50]}...")
            return False
        
        query = """
            INSERT INTO articles (
                article_id, title, description, body, source, source_api,
                source_priority, url, author, published_at, ticker, raw_text,
                sentiment_score, sentiment_label, image, category, scraped_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        params = (
            article.get('article_id'),
            article.get('title'),
            article.get('description'),
            article.get('body'),
            article.get('source'),
            article.get('source_api'),
            article.get('source_priority', 1),
            article.get('url'),
            article.get('author'),
            article.get('published_at'),
            article.get('ticker'),
            article.get('raw_text'),
            article.get('sentiment_score'),
            article.get('sentiment_label'),
            article.get('image'),
            article.get('category'),
            article.get('scraped_at', datetime.now())
        )
        
        result = self.execute_query(query, params)
        if result is not None or self.cursor.rowcount > 0:
            print(f"✓ Inserted: {article.get('title', '')[:50]}...")
            return True
        return False
    
    def insert_articles_batch(self, articles):
        """
        Insert multiple articles at once (faster).
        
        Args:
            articles (list): List of article dictionaries
        
        Returns:
            int: Number of articles inserted
        """
        if not articles:
            return 0
        
        query = """
            INSERT INTO articles (
                article_id, title, description, body, source, source_api,
                source_priority, url, author, published_at, ticker, raw_text,
                sentiment_score, sentiment_label, image, category, scraped_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (article_id) DO NOTHING
        """
        
        # Prepare batch data
        batch_data = []
        for article in articles:
            params = (
                article.get('article_id'),
                article.get('title'),
                article.get('description'),
                article.get('body'),
                article.get('source'),
                article.get('source_api'),
                article.get('source_priority', 1),
                article.get('url'),
                article.get('author'),
                article.get('published_at'),
                article.get('ticker'),
                article.get('raw_text'),
                article.get('sentiment_score'),
                article.get('sentiment_label'),
                article.get('image'),
                article.get('category'),
                article.get('scraped_at', datetime.now())
            )
            batch_data.append(params)
        
        try:
            execute_batch(self.cursor, query, batch_data, page_size=100)
            self.conn.commit()
            inserted_count = self.cursor.rowcount
            print(f"✓ Batch inserted {inserted_count} articles")
            return inserted_count
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Batch insert error: {e}")
            return 0
    
    def get_articles_by_ticker(self, ticker, limit=100):
        """
        Retrieve articles for a specific ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            limit (int): Maximum number of articles to return
        
        Returns:
            list: List of article dictionaries
        """
        query = """
            SELECT * FROM articles
            WHERE ticker = %s
            ORDER BY published_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (ticker, limit), fetch=True)
    
    def get_articles_by_date_range(self, from_date, to_date, ticker=None):
        """
        Retrieve articles within a date range.
        
        Args:
            from_date (datetime): Start date
            to_date (datetime): End date
            ticker (str): Optional ticker filter
        
        Returns:
            list: List of article dictionaries
        """
        if ticker:
            query = """
                SELECT * FROM articles
                WHERE published_at BETWEEN %s AND %s
                AND ticker = %s
                ORDER BY published_at DESC
            """
            params = (from_date, to_date, ticker)
        else:
            query = """
                SELECT * FROM articles
                WHERE published_at BETWEEN %s AND %s
                ORDER BY published_at DESC
            """
            params = (from_date, to_date)
        
        return self.execute_query(query, params, fetch=True)
    
    def get_latest_articles(self, n=50):
        """
        Get the N most recent articles.
        
        Args:
            n (int): Number of articles to retrieve
        
        Returns:
            list: List of article dictionaries
        """
        query = """
            SELECT * FROM articles
            ORDER BY published_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (n,), fetch=True)
    
    # ========== SCRAPING LOG OPERATIONS ==========
    
    def log_scraping(self, ticker, source_api, status, articles_found=0, 
                    error_message=None, execution_time=None):
        """
        Log a scraping operation.
        
        Args:
            ticker (str): Stock ticker
            source_api (str): Which API was used
            status (str): 'success' or 'error'
            articles_found (int): Number of articles found
            error_message (str): Error message if failed
            execution_time (float): Time taken in seconds
        
        Returns:
            bool: True if successful
        """
        query = """
            INSERT INTO scraping_logs (
                ticker, source_api, status, articles_found,
                error_message, execution_time
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (ticker, source_api, status, articles_found, 
                 error_message, execution_time)
        
        result = self.execute_query(query, params)
        return result is not None or self.cursor.rowcount > 0
    
    def get_recent_logs(self, limit=50):
        """Get recent scraping logs."""
        query = """
            SELECT * FROM scraping_logs
            ORDER BY scraped_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,), fetch=True)
    
    # ========== STOCK TICKER OPERATIONS ==========
    
    def get_active_tickers(self):
        """Get list of all active stock tickers."""
        query = """
            SELECT ticker, company_name, priority
            FROM stock_tickers
            WHERE is_active = TRUE
            ORDER BY priority DESC, ticker ASC
        """
        return self.execute_query(query, fetch=True)
    
    def update_last_scraped(self, ticker):
        """Update the last_scraped timestamp for a ticker."""
        query = """
            UPDATE stock_tickers
            SET last_scraped = %s
            WHERE ticker = %s
        """
        return self.execute_query(query, (datetime.now(), ticker))


def test_database():
    """Test database operations."""
    
    print("\n" + "="*80)
    print("TESTING DATABASE MANAGER")
    print("="*80)
    
    db = DatabaseManager()
    
    # Test 1: Connect
    print("\n1️⃣ Testing connection...")
    if not db.connect():
        print("✗ Cannot continue without database connection")
        return
    
    # Test 2: Get active tickers
    print("\n2️⃣ Getting active tickers...")
    tickers = db.get_active_tickers()
    print(f"✓ Found {len(tickers)} active tickers:")
    for ticker in tickers[:5]:
        print(f"   {ticker['ticker']}: {ticker['company_name']}")
    
    # Test 3: Check if article exists
    print("\n3️⃣ Testing article_exists...")
    exists = db.article_exists(article_id='test123')
    print(f"✓ Article test123 exists: {exists}")
    
    # Test 4: Get recent articles
    print("\n4️⃣ Getting recent articles...")
    articles = db.get_latest_articles(n=5)
    print(f"✓ Found {len(articles)} recent articles")
    
    # Test 5: Get articles by ticker
    print("\n5️⃣ Getting articles for AAPL...")
    aapl_articles = db.get_articles_by_ticker('AAPL', limit=5)
    print(f"✓ Found {len(aapl_articles)} AAPL articles")
    
    # Close connection
    db.close()
    print("\n✅ All database tests passed!")


if __name__ == "__main__":
    test_database()