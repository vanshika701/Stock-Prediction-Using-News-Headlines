# api/output_api.py
"""
Output API for providing data to Person 2 (Sentiment Analysis/IR).
Provides cleaned articles with ticker information in JSON format.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from database.cache_manager import CacheManager

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize database and cache
db = DatabaseManager()
if not db.conn:
    db.connect()

cache = CacheManager()
if cache.redis_client:
    cache.connect()


@app.route('/')
def home():
    """API home endpoint."""
    return jsonify({
        'message': 'News Scraper Output API',
        'version': '1.0',
        'endpoints': {
            '/api/articles': 'Get all articles',
            '/api/articles/ticker/<ticker>': 'Get articles by ticker',
            '/api/articles/recent': 'Get recent articles',
            '/api/articles/date-range': 'Get articles by date range',
            '/api/stream/latest': 'Get real-time data stream',
            '/api/health': 'API health check'
        }
    })


@app.route('/api/health')
def health_check():
    """Check API health and database connection."""
    try:
        # Test database
        db.cursor.execute("SELECT 1")
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    try:
        # Test cache
        cache.redis_client.ping()
        cache_status = "connected"
    except:
        cache_status = "disconnected"
    
    return jsonify({
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'database': db_status,
        'cache': cache_status,
        'published_at': datetime.now().isoformat()
    })


@app.route('/api/articles', methods=['GET'])
def get_all_articles():
    """
    Get all articles with optional filters.
    
    Query params:
        limit (int): Max articles to return (default: 100)
        offset (int): Pagination offset (default: 0)
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get articles from database
        query = """
            SELECT article_id, title, body, source, published_at, 
                   url, ticker, sentiment_score
            FROM articles
            ORDER BY published_at DESC
            LIMIT %s OFFSET %s
        """
        
        db.cursor.execute(query, (limit, offset))
        articles = db.cursor.fetchall()
        
        # Convert to list of dicts
        result = []
        for article in articles:
            result.append({
                'article_id': article['article_id'],
                'title': article['title'],
                'body': article['body'],
                'source': article['source'],
                'published_at': article['published_at'],
                'url': article['url'],
                'tickers': article['ticker'].split(',') if article['ticker'] else [],
                'sentiment_score': article['sentiment_score']
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'articles': result
        })
    
    # In api/output_api.py, inside the get_all_articles function
    
    except Exception as e:
        # 1. Add Rollback to clear the transaction state
        if db.conn:
            db.conn.rollback() # <--- THIS IS THE CRITICAL LINE
            
        # 2. Return the error response
        # Changed error message for clarity
        return jsonify({
            'success': False,
            'error': "Database Error: " + str(e)
        }), 500

@app.route('/api/articles/ticker/<ticker>', methods=['GET'])
def get_articles_by_ticker(ticker):
    """
    Get articles for a specific ticker.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., AAPL, TSLA)
        
    Query params:
        limit (int): Max articles to return (default: 50)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        ticker = ticker.upper()
        
        # Try cache first
        cached = None
        if cache.redis_client:
            try:
                cached = cache.get_cached_articles(ticker)
            except:
                pass
        
        if cached:
            return jsonify({
                'success': True,
                'ticker': ticker,
                'source': 'cache',
                'count': len(cached),
                'articles': cached[:limit]
            })
        
        # Get from database
        articles = db.get_articles_by_ticker(ticker, limit=limit)
        
        # Convert to list of dicts
        result = []
        for article in articles:
            result.append({
                'article_id': article['article_id'],
                'title': article['title'],
                'body': article['body'],
                'source': article['source'],
                'published_at': article['published_at'],
                'url': article['url'],
                'tickers': article['ticker'].split(',') if article['ticker'] else [],
                'sentiment_score': article['sentiment_score']
            })
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'source': 'database',
            'count': len(result),
            'articles': result
        })
    
    except Exception as e:
        # 1. Add Rollback to clear the transaction state
        # This is CRITICAL. It tells the database connection to forget the failed transaction.
        if db.conn:
            db.conn.rollback() 
            
        # 2. Return the error response
        # Using a more descriptive error message
        return jsonify({
            'success': False,
            'error': "Database Error while fetching ticker: " + str(e)
        }), 500


@app.route('/api/articles/recent', methods=['GET'])
def get_recent_articles():
    """
    Get most recent articles (last 24 hours).
    
    Query params:
        hours (int): Hours to look back (default: 24)
        limit (int): Max articles (default: 100)
    """
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        # Calculate time range
        to_date = datetime.now()
        from_date = to_date - timedelta(hours=hours)
        
        # Get articles
        articles = db.get_articles_by_date_range(from_date, to_date)
        
        # Convert to list of dicts
        result = []
        for article in articles[:limit]:
            result.append({
                'article_id': article['article_id'],
                'title': article['title'],
                'body': article['body'],
                'source': article['source'],
                'published_at': article['published_at'],
                'url': article['url'],
                'tickers': article['ticker'].split(',') if article['ticker'] else [],
                'sentiment_score': article['sentiment_score']
            })
        
        return jsonify({
            'success': True,
            'time_range': f'Last {hours} hours',
            'from': from_date.isoformat(),
            'to': to_date.isoformat(),
            'count': len(result),
            'articles': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/articles/date-range', methods=['GET'])
def get_articles_by_date_range():
    """
    Get articles within a date range.
    
    Query params:
        from_date (str): Start date (YYYY-MM-DD)
        to_date (str): End date (YYYY-MM-DD)
        ticker (str): Optional ticker filter
    """
    try:
        from_date_str = request.args.get('from_date')
        to_date_str = request.args.get('to_date')
        ticker = request.args.get('ticker')
        
        if not from_date_str or not to_date_str:
            return jsonify({
                'success': False,
                'error': 'from_date and to_date are required'
            }), 400
        
        # Parse dates
        from_date = datetime.fromisoformat(from_date_str)
        to_date = datetime.fromisoformat(to_date_str)
        
        # Get articles
        articles = db.get_articles_by_date_range(from_date, to_date, ticker=ticker)
        
        # Convert to list of dicts
        result = []
        for article in articles:
            result.append({
                'article_id': article['article_id'],
                'title': article['title'],
                'body': article['body'],
                'source': article['source'],
                'published_at': article['published_at'],
                'url': article['url'],
                'tickers': article['ticker'].split(',') if article['ticker'] else [],
                'sentiment_score': article['sentiment_score']
            })
        
        return jsonify({
            'success': True,
            'from': from_date_str,
            'to': to_date_str,
            'ticker': ticker or 'all',
            'count': len(result),
            'articles': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stream/latest', methods=['GET'])
def stream_latest():
    """
    Get real-time stream of latest articles.
    Returns last 50 articles ordered by published_at.
    """
    try:
        articles = db.get_latest_articles(n=50)
        
        # Convert to list of dicts
        result = []
        for article in articles:
            result.append({
                'article_id': article['article_id'],
                'title': article['title'],
                'body': article['body'],
                'source': article['source'],
                'published_at': article['published_at'],
                'url': article['url'],
                'tickers': article['ticker'].split(',') if article['ticker'] else [],
                'sentiment_score': article['sentiment_score']
            })
        
        return jsonify({
            'success': True,
            'stream_time': datetime.now().isoformat(),
            'count': len(result),
            'articles': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/json', methods=['GET'])
def export_json():
    """
    Export all articles as JSON file.
    
    Query params:
        ticker (str): Optional ticker filter
    """
    try:
        ticker = request.args.get('ticker')
        
        if ticker:
            articles = db.get_articles_by_ticker(ticker.upper(), limit=1000)
        else:
            articles = db.get_latest_articles(n=1000)
        
        # Convert to list of dicts
        result = []
        for article in articles:
            result.append({
                'article_id': article['article_id'],
                'title': article['title'],
                'body': article['body'],
                'source': article['source'],
                'published_at': article['published_at'],
                'url': article['url'],
                'tickers': article['ticker'].split(',') if article['ticker'] else [],
                'sentiment_score': article['sentiment_score']
            })
        
        return jsonify({
            'export_time': datetime.now().isoformat(),
            'ticker': ticker or 'all',
            'count': len(result),
            'articles': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*80)
    print("STARTING OUTPUT API FOR PERSON 2 (SENTIMENT ANALYSIS)")
    print("="*80)
    print("\n📡 API Endpoints:")
    print("   http://localhost:5000/")
    print("   http://localhost:5000/api/health")
    print("   http://localhost:5000/api/articles")
    print("   http://localhost:5000/api/articles/ticker/AAPL")
    print("   http://localhost:5000/api/articles/recent")
    print("   http://localhost:5000/api/stream/latest")
    print("\n🚀 Starting server...")
    print("   Press Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
