# load_preprocessed_to_database.py
"""
Load preprocessed articles from JSON into PostgreSQL database.
"""

import json
import sys
import os
from datetime import datetime

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager


def load_preprocessed_articles():
    """Load preprocessed articles into database."""
    
    print("\n" + "="*80)
    print("LOADING PREPROCESSED ARTICLES TO DATABASE")
    print("="*80)
    
    # Initialize database manager
    print("\n🔧 Connecting to database...")
    db = DatabaseManager()
    
    # Manually connect if not connected
    if not db.conn:
        print("   Establishing connection...")
        db.connect()
    
    if not db.conn:
        print("❌ Error: Could not connect to database!")
        return
    
    print("✓ Database connected")
    
    # Load preprocessed articles
    input_file = "preprocessed_articles.json"
    
    print(f"\n📂 Loading articles from: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"❌ Error: File not found: {input_file}")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"✓ Loaded {len(articles)} preprocessed articles")
    
    # Convert to database format
    print("\n🔄 Converting to database format...")
    
    db_articles = []
    for article in articles:
        # Extract data
        article_id = article.get('article_id', f"article_{hash(article.get('url', ''))}")
        title = article.get('cleaned_title', article.get('original_title', ''))
        body = article.get('cleaned_body', article.get('original_body', ''))
        source = article.get('source', article.get('source_api', 'Unknown'))
        url = article.get('url', '')
        
        # Get timestamp
        timestamp = article.get('timestamp', article.get('published_at', ''))
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        # Get tickers
        tickers = article.get('tickers_mentioned', [])
        ticker_str = ','.join(tickers) if tickers else None
        
        # Get sentiment data from features
        features = article.get('features', {})
        keywords = features.get('financial_keywords', {})
        
        positive_keywords = len(keywords.get('positive', []))
        negative_keywords = len(keywords.get('negative', []))
        
        # Simple sentiment calculation
        if positive_keywords > negative_keywords:
            sentiment = 'positive'
        elif negative_keywords > positive_keywords:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Create database record
        db_article = {
            'article_id': article_id,
            'title': title,
            'body': body,
            'source': source,
            'published_at': timestamp,
            'url': url,
            'raw_text': article.get('cleaned_text', ''),
            'ticker': ticker_str,
            'sentiment_score': sentiment,
            'processed_tokens': json.dumps(article.get('tokens', {})),
            'features': json.dumps(features)
        }
        
        db_articles.append(db_article)
    
    print(f"✓ Converted {len(db_articles)} articles")
    
    # Insert using batch method
    print("\n💾 Inserting into database (batch mode)...")
    
    try:
        # Try batch insert first
        result = db.insert_articles_batch(db_articles)
        print(f"✓ Batch insertion complete!")
        print(f"   Result: {result}")
    except Exception as e:
        # --- CRITICAL FIX 1: Log the full traceback for the batch failure ---
        import traceback
        print("\n" + "-"*50)
        print("⚠️  CRITICAL BATCH INSERT FAILED! TRACEBACK BELOW:")
        traceback.print_exc()
        print("-"*50)
        
        print("\n💾 Trying individual inserts (to isolate the failing article)...")
        
        # Fall back to individual inserts
        inserted = 0
        errors = 0
        
        for i, article in enumerate(db_articles):
            if (i + 1) % 100 == 0:
                print(f"   Processed {i + 1}/{len(db_articles)} articles...")
            
            try:
                db.insert_article(article)
                inserted += 1
            except Exception as e:
                # --- CRITICAL FIX 2: Log details on the first few errors ---
                errors += 1
                if errors <= 5:
                    print(f"   ⚠️  Error inserting article {i+1} (ID: {article['article_id']}):")
                    print(f"      Full Error: {e}") # Print full error, not just the start
                # IMPORTANT: If the error persists, the issue is likely a data type mismatch
                # in the article structure itself, not a unique constraint.
                continue
        
        print(f"\n✓ Individual insertion complete!")
        print(f"   Inserted: {inserted}")
        print(f"   Errors: {errors}")
    
    # Show statistics
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)
    
    # Sample articles
    print("\n📊 Sample articles:")
    for i, article in enumerate(db_articles[:5], 1):
        tickers = article.get('ticker', 'None')
        sentiment = article.get('sentiment_score', 'Unknown')
        print(f"   {i}. {article['title'][:50]}...")
        print(f"      Tickers: {tickers}, Sentiment: {sentiment}")
    
    print("\n" + "="*80)
    print("✅ LOADING COMPLETE!")
    print("="*80)
    
    db.close()


def verify_database():
    """Verify data is in database."""
    
    print("\n" + "="*80)
    print("VERIFYING DATABASE")
    print("="*80)
    
    db = DatabaseManager()
    
    # Manually connect if needed
    if not db.conn:
        db.connect()
    
    if not db.conn:
        print("❌ Error: Could not connect to database")
        return
    
    try:
        # Count total articles
        query = "SELECT COUNT(*) as count FROM articles"
        db.cursor.execute(query)
        result = db.cursor.fetchone()
        total = result[0] if result else 0
        
        print(f"\n📊 Total articles in database: {total}")
        
        # Get recent articles using existing method
        try:
            articles = db.get_latest_articles(limit=5)
            
            if articles:
                print("\n📰 Recent articles:")
                for article in articles:
                    print(f"\n   ID: {article.get('article_id', 'N/A')}")
                    print(f"   Title: {article.get('title', 'N/A')[:70]}...")
                    print(f"   Source: {article.get('source', 'N/A')}")
                    print(f"   Tickers: {article.get('ticker', 'None')}")
                    print(f"   Sentiment: {article.get('sentiment_score', 'Unknown')}")
            else:
                print("\n⚠️  No articles found")
        except Exception as e:
            print(f"\n⚠️  Could not fetch articles: {e}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    db.close()
    print("\n✅ Verification complete!")


if __name__ == "__main__":
    # Load articles
    load_preprocessed_articles()
    
    # Verify
    print("\n" + "="*80)
    verify_database()

# load_preprocessed_to_database.py
"""
Load preprocessed articles from JSON into PostgreSQL database.
"""

import json
import sys
import os
from datetime import datetime

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager


def load_preprocessed_articles():
    """Load preprocessed articles into database."""
    
    print("\n" + "="*80)
    print("LOADING PREPROCESSED ARTICLES TO DATABASE")
    print("="*80)
    
    # Initialize database manager
    print("\n🔧 Connecting to database...")
    db = DatabaseManager()
    
    # Manually connect if not connected
    if not db.conn:
        print("   Establishing connection...")
        db.connect()
    
    if not db.conn:
        print("❌ Error: Could not connect to database!")
        return
    
    print("✓ Database connected")
    
    # Load preprocessed articles
    input_file = "preprocessed_articles.json"
    
    print(f"\n📂 Loading articles from: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"❌ Error: File not found: {input_file}")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"✓ Loaded {len(articles)} preprocessed articles")
    
    # Convert to database format
    print("\n🔄 Converting to database format...")
    
    db_articles = []
    for article in articles:
        # Extract data
        article_id = article.get('article_id', f"article_{hash(article.get('url', ''))}")
        title = article.get('cleaned_title', article.get('original_title', ''))
        body = article.get('cleaned_body', article.get('original_body', ''))
        source = article.get('source', article.get('source_api', 'Unknown'))
        url = article.get('url', '')
        
        # Get timestamp
        timestamp = article.get('timestamp', article.get('published_at', ''))
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        # Get tickers
        tickers = article.get('ticker', [])
        ticker_str = ','.join(tickers) if tickers else None
        
        # Get sentiment data from features
        features = article.get('features', {})
        keywords = features.get('financial_keywords', {})
        
        positive_keywords = len(keywords.get('positive', []))
        negative_keywords = len(keywords.get('negative', []))
        
        # Simple sentiment calculation
        if positive_keywords > negative_keywords:
            sentiment = 'positive'
        elif negative_keywords > positive_keywords:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Create database record
        db_article = {
            'article_id': article_id,
            'title': title,
            'body': body,
            'source': source,
            'published_at': timestamp,
            'url': url,
            'raw_text': article.get('cleaned_text', ''),
            'ticker': ticker_str,
            'sentiment_score': sentiment,
            'processed_tokens': json.dumps(article.get('tokens', {})),
            'features': json.dumps(features)
        }
        
        db_articles.append(db_article)
    
    print(f"✓ Converted {len(db_articles)} articles")
    
    # Insert using batch method
    print("\n💾 Inserting into database (batch mode)...")
    
    try:
        # Try batch insert first
        result = db.insert_articles_batch(db_articles)
        print(f"✓ Batch insertion complete!")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"⚠️  Batch insert failed: {e}")
        print("\n💾 Trying individual inserts...")
        
        # Fall back to individual inserts
        inserted = 0
        errors = 0
        
        for i, article in enumerate(db_articles):
            if (i + 1) % 100 == 0:
                print(f"   Processed {i + 1}/{len(db_articles)} articles...")
            
            try:
                db.insert_article(article)
                inserted += 1
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"   ⚠️  Error inserting article {i+1}: {str(e)[:100]}")
                continue
        
        print(f"\n✓ Individual insertion complete!")
        print(f"   Inserted: {inserted}")
        print(f"   Errors: {errors}")
    
    # Show statistics
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)
    
    # Sample articles
    print("\n📊 Sample articles:")
    for i, article in enumerate(db_articles[:5], 1):
        tickers = article.get('ticker', 'None')
        sentiment = article.get('sentiment', 'Unknown')
        print(f"   {i}. {article['title'][:50]}...")
        print(f"      Tickers: {tickers}, Sentiment: {sentiment}")
    
    print("\n" + "="*80)
    print("✅ LOADING COMPLETE!")
    print("="*80)
    
    db.close()


def verify_database():
    """Verify data is in database."""
    
    print("\n" + "="*80)
    print("VERIFYING DATABASE")
    print("="*80)
    
    db = DatabaseManager()
    
    # Manually connect if needed
    if not db.conn:
        db.connect()
    
    if not db.conn:
        print("❌ Error: Could not connect to database")
        return
    
    try:
        # Count total articles
        query = "SELECT COUNT(*) as count FROM articles"
        db.cursor.execute(query)
        result = db.cursor.fetchone()
        total = result[0] if result else 0
        
        print(f"\n📊 Total articles in database: {total}")
        
        # Get recent articles using existing method
        try:
            articles = db.get_latest_articles(limit=5)
            
            if articles:
                print("\n📰 Recent articles:")
                for article in articles:
                    print(f"\n   ID: {article.get('article_id', 'N/A')}")
                    print(f"   Title: {article.get('title', 'N/A')[:70]}...")
                    print(f"   Source: {article.get('source', 'N/A')}")
                    print(f"   Tickers: {article.get('ticker', 'None')}")
                    print(f"   Sentiment: {article.get('sentiment_score', 'Unknown')}")
            else:
                print("\n⚠️  No articles found")
        except Exception as e:
            print(f"\n⚠️  Could not fetch articles: {e}")
            
    except Exception as e:
        print(f"\n Error: {e}")
    
    db.close()
    print("\n✅ Verification complete!")


if __name__ == "__main__":
    # Load articles
    load_preprocessed_articles()
    
    # Verify
    print("\n" + "="*80)
    verify_database()
