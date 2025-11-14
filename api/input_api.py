# api/input_api.py
"""
Input API for receiving requests from Person 3 (UI Team).
Allows UI to request specific tickers, set priorities, and get queries.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager

app = Flask(__name__)
CORS(app)

# Initialize database
db = DatabaseManager()
if not db.conn:
    db.connect()

# Store watchlist and priorities in memory (in production, use database)
WATCHLIST = []
TICKER_PRIORITIES = {}


@app.route('/')
def home():
    """API home endpoint."""
    return jsonify({
        'message': 'News Scraper Input API',
        'version': '1.0',
        'endpoints': {
            '/api/watchlist': 'Get/Set user watchlist',
            '/api/priority': 'Set ticker priority',
            '/api/query': 'Submit search query',
            '/api/request/scrape': 'Request immediate scrape',
            '/api/health': 'API health check'
        }
    })


@app.route('/api/health')
def health_check():
    """Check API health."""
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if db.conn else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/watchlist', methods=['GET', 'POST'])
def manage_watchlist():
    """
    Get or set user watchlist.
    
    GET: Returns current watchlist
    POST: Adds tickers to watchlist
        Body: {"tickers": ["AAPL", "TSLA", "MSFT"]}
    """
    global WATCHLIST
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'watchlist': WATCHLIST,
            'count': len(WATCHLIST)
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            tickers = data.get('tickers', [])
            
            # Add to watchlist (remove duplicates)
            for ticker in tickers:
                ticker = ticker.upper()
                if ticker not in WATCHLIST:
                    WATCHLIST.append(ticker)
            
            return jsonify({
                'success': True,
                'message': f'Added {len(tickers)} tickers to watchlist',
                'watchlist': WATCHLIST,
                'count': len(WATCHLIST)
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400


@app.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    """
    Remove tickers from watchlist.
    
    Body: {"tickers": ["AAPL", "TSLA"]}
    """
    global WATCHLIST
    
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        
        for ticker in tickers:
            ticker = ticker.upper()
            if ticker in WATCHLIST:
                WATCHLIST.remove(ticker)
        
        return jsonify({
            'success': True,
            'message': f'Removed {len(tickers)} tickers',
            'watchlist': WATCHLIST,
            'count': len(WATCHLIST)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/watchlist/clear', methods=['POST'])
def clear_watchlist():
    """Clear entire watchlist."""
    global WATCHLIST
    WATCHLIST = []
    
    return jsonify({
        'success': True,
        'message': 'Watchlist cleared',
        'watchlist': []
    })


@app.route('/api/priority', methods=['GET', 'POST'])
def manage_priority():
    """
    Get or set ticker priorities.
    
    GET: Returns all priorities
    POST: Set priority for ticker
        Body: {"ticker": "AAPL", "priority": "high"}
    """
    global TICKER_PRIORITIES
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'priorities': TICKER_PRIORITIES
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            ticker = data.get('ticker', '').upper()
            priority = data.get('priority', 'medium')  # high, medium, low
            
            if not ticker:
                return jsonify({
                    'success': False,
                    'error': 'Ticker is required'
                }), 400
            
            if priority not in ['high', 'medium', 'low']:
                return jsonify({
                    'success': False,
                    'error': 'Priority must be high, medium, or low'
                }), 400
            
            TICKER_PRIORITIES[ticker] = priority
            
            return jsonify({
                'success': True,
                'message': f'Set {ticker} priority to {priority}',
                'ticker': ticker,
                'priority': priority
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400


@app.route('/api/query', methods=['POST'])
def submit_query():
    """
    Submit a search query from UI.
    
    Body: {
        "query": "Apple earnings report",
        "tickers": ["AAPL"],
        "date_from": "2024-01-01",
        "date_to": "2024-01-31"
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        tickers = data.get('tickers', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        # Build SQL query
        conditions = []
        params = []
        
        if query:
            conditions.append("(title ILIKE %s OR body ILIKE %s)")
            params.extend([f'%{query}%', f'%{query}%'])
        
        if tickers:
            ticker_conditions = []
            for ticker in tickers:
                ticker_conditions.append("tickers_mentioned LIKE %s")
                params.append(f'%{ticker.upper()}%')
            conditions.append(f"({' OR '.join(ticker_conditions)})")
        
        if date_from:
            conditions.append("timestamp >= %s")
            params.append(date_from)
        
        if date_to:
            conditions.append("timestamp <= %s")
            params.append(date_to)
        
        # Execute query
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        sql = f"""
            SELECT article_id, title, body, source, timestamp, 
                   url, tickers_mentioned, sentiment
            FROM articles
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT 100
        """
        
        db.cursor.execute(sql, tuple(params))
        articles = db.cursor.fetchall()
        
        # Convert to list of dicts
        result = []
        for article in articles:
            result.append({
                'article_id': article['article_id'],
                'title': article['title'],
                'body': article['body'],
                'source': article['source'],
                'timestamp': article['timestamp'],
                'url': article['url'],
                'tickers': article['tickers_mentioned'].split(',') if article['tickers_mentioned'] else [],
                'sentiment': article['sentiment']
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'tickers': tickers,
            'count': len(result),
            'articles': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/request/scrape', methods=['POST'])
def request_scrape():
    """
    Request immediate scrape for specific tickers.
    
    Body: {"tickers": ["AAPL", "TSLA"]}
    """
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        
        if not tickers:
            return jsonify({
                'success': False,
                'error': 'Tickers are required'
            }), 400
        
        # In production, this would trigger the scraper
        # For now, just acknowledge the request
        
        return jsonify({
            'success': True,
            'message': f'Scrape requested for {len(tickers)} tickers',
            'tickers': tickers,
            'status': 'queued',
            'note': 'Scrape will be performed in background'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics."""
    try:
        # Count total articles
        db.cursor.execute("SELECT COUNT(*) FROM articles")
        total_articles = db.cursor.fetchone()[0]
        
        # Count by sentiment
        db.cursor.execute("""
            SELECT sentiment, COUNT(*) as count
            FROM articles
            GROUP BY sentiment
        """)
        sentiment_counts = {row['sentiment']: row['count'] for row in db.cursor.fetchall()}
        
        # Get most mentioned tickers
        db.cursor.execute("""
            SELECT tickers_mentioned, COUNT(*) as count
            FROM articles
            WHERE tickers_mentioned IS NOT NULL
            GROUP BY tickers_mentioned
            ORDER BY count DESC
            LIMIT 10
        """)
        top_tickers = [
            {'ticker': row['tickers_mentioned'], 'count': row['count']}
            for row in db.cursor.fetchall()
        ]
        
        return jsonify({
            'success': True,
            'total_articles': total_articles,
            'sentiment_distribution': sentiment_counts,
            'top_tickers': top_tickers,
            'watchlist_size': len(WATCHLIST),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*80)
    print("STARTING INPUT API FOR PERSON 3 (UI TEAM)")
    print("="*80)
    print("\n📡 API Endpoints:")
    print("   http://localhost:5001/")
    print("   http://localhost:5001/api/health")
    print("   http://localhost:5001/api/watchlist")
    print("   http://localhost:5001/api/priority")
    print("   http://localhost:5001/api/query")
    print("   http://localhost:5001/api/stats")
    print("\n🚀 Starting server...")
    print("   Press Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
