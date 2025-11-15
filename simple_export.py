# simple_export.py
"""
Simple, guaranteed-to-work export script.
"""

import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager


def simple_export():
    """Export articles the simple way."""
    
    print("\n" + "="*80)
    print("SIMPLE DATA EXPORT")
    print("="*80)
    
    # Connect to database
    db = DatabaseManager()
    if not db.conn:
        db.connect()
    
    if not db.conn:
        print("❌ Could not connect to database")
        return
    
    print("✓ Connected to database")
    
    # Export by ticker
    tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN']
    
    for ticker in tickers:
        print(f"\n📊 Exporting {ticker}...")
        
        try:
            # Get articles
            articles = db.get_articles_by_ticker(ticker, limit=100)
            
            if not articles:
                print(f"   No articles found for {ticker}")
                continue
            
            # Format data
            export_data = {
                'ticker': ticker,
                'count': len(articles),
                'exported_at': datetime.now().isoformat(),
                'articles': []
            }
            
            for article in articles:
                export_data['articles'].append({
                    'id': article.get('article_id'),
                    'title': article.get('title'),
                    'body': article.get('body'),
                    'text': article.get('raw_text'),
                    'ticker': article.get('tickers_mentioned'),
                    'sentiment': article.get('sentiment'),
                    'date': str(article.get('timestamp')),
                    'source': article.get('source')
                })
            
            # Save to file
            filename = f"{ticker.lower()}_export.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"   ✓ Saved {len(articles)} articles to {filename}")
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    # Export all recent
    print(f"\n📊 Exporting all recent articles...")
    
    try:
        # Direct SQL query
        query = "SELECT * FROM articles ORDER BY timestamp DESC LIMIT 200"
        db.cursor.execute(query)
        articles = db.cursor.fetchall()
        
        if articles:
            export_data = {
                'ticker': 'ALL',
                'count': len(articles),
                'exported_at': datetime.now().isoformat(),
                'articles': []
            }
            
            for article in articles:
                export_data['articles'].append({
                    'id': article.get('article_id'),
                    'title': article.get('title'),
                    'body': article.get('body'),
                    'text': article.get('raw_text'),
                    'ticker': article.get('tickers_mentioned'),
                    'sentiment': article.get('sentiment'),
                    'date': str(article.get('timestamp')),
                    'source': article.get('source')
                })
            
            filename = 'all_recent_export.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"   ✓ Saved {len(articles)} articles to {filename}")
    
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    db.close()
    
    print("\n" + "="*80)
    print("✅ EXPORT COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    simple_export()
