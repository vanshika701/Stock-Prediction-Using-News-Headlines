# export_tool.py
"""
Complete export tool for Person 2.
Allows exporting by ticker, date range, and custom filters.
"""

import json
import sys
import os
from datetime import datetime, timedelta
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager


class DataExporter:
    """Export tool for sentiment analysis team."""
    
    def __init__(self):
        """Initialize exporter."""
        self.db = DatabaseManager()
        if not self.db.conn:
            self.db.connect()
    
    def export_by_ticker(self, ticker, limit=100, output_file=None):
        """Export articles for specific ticker."""
        
        if not output_file:
            output_file = f"{ticker.lower()}_export.json"
        
        print(f"\n📤 Exporting {ticker} articles (limit: {limit})...")
        
        articles = self.db.get_articles_by_ticker(ticker, limit=limit)
        
        export_data = {
            'export_type': 'by_ticker',
            'ticker': ticker,
            'count': len(articles),
            'exported_at': datetime.now().isoformat(),
            'articles': self.format_articles(articles)
        }
        
        self.save_json(export_data, output_file)
        print(f"✓ Saved to {output_file}")
        
        return output_file
    
    def export_by_date_range(self, start_date, end_date, output_file=None):
        """Export articles within date range."""
        
        if not output_file:
            output_file = f"articles_{start_date}_to_{end_date}.json"
        
        print(f"\n📅 Exporting articles from {start_date} to {end_date}...")
        
        articles = self.db.get_articles_by_date_range(start_date, end_date)
        
        export_data = {
            'export_type': 'by_date_range',
            'start_date': start_date,
            'end_date': end_date,
            'count': len(articles),
            'exported_at': datetime.now().isoformat(),
            'articles': self.format_articles(articles)
        }
        
        self.save_json(export_data, output_file)
        print(f"✓ Saved to {output_file}")
        
        return output_file
    
    def export_all_recent(self, days=7, output_file='recent_articles.json'):
        """Export all recent articles from last N days."""
        
        print(f"\n📊 Exporting articles from last {days} days...")
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        return self.export_by_date_range(start_date, end_date, output_file)
    
    def export_multiple_tickers(self, tickers, limit=100):
        """Export multiple tickers."""
        
        print(f"\n📦 Exporting {len(tickers)} tickers...")
        
        files = []
        for ticker in tickers:
            try:
                file = self.export_by_ticker(ticker, limit)
                files.append(file)
            except Exception as e:
                print(f"✗ Error exporting {ticker}: {e}")
        
        return files
    
    def format_articles(self, articles):
        """Format articles for sentiment analysis."""
        
        formatted = []
        
        for article in articles:
            formatted.append({
                'id': article.get('article_id'),
                'title': article.get('title'),
                'body': article.get('body'),
                'text': article.get('raw_text'),
                'ticker': article.get('tickers_mentioned'),
                'sentiment': article.get('sentiment'),
                'date': str(article.get('timestamp')),
                'source': article.get('source'),
                'url': article.get('url'),
                'features': article.get('features')
            })
        
        return formatted
    
    def save_json(self, data, filename):
        """Save data to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def cleanup(self):
        """Close database connection."""
        self.db.close()


def main():
    """Command-line interface for export tool."""
    
    parser = argparse.ArgumentParser(description='Export articles for sentiment analysis')
    parser.add_argument('--ticker', type=str, help='Stock ticker (e.g., AAPL)')
    parser.add_argument('--tickers', type=str, help='Comma-separated tickers (e.g., AAPL,TSLA,MSFT)')
    parser.add_argument('--days', type=int, default=7, help='Export last N days (default: 7)')
    parser.add_argument('--limit', type=int, default=100, help='Max articles per ticker (default: 100)')
    parser.add_argument('--output', type=str, help='Output filename')
    
    args = parser.parse_args()
    
    exporter = DataExporter()
    
    try:
        if args.ticker:
            # Single ticker
            exporter.export_by_ticker(args.ticker, args.limit, args.output)
        
        elif args.tickers:
            # Multiple tickers
            tickers = [t.strip().upper() for t in args.tickers.split(',')]
            exporter.export_multiple_tickers(tickers, args.limit)
        
        else:
            # All recent articles
            exporter.export_all_recent(args.days, args.output or 'recent_articles.json')
        
        print("\n✅ Export complete!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        exporter.cleanup()


if __name__ == "__main__":
    # If no arguments, show examples
    if len(sys.argv) == 1:
        print("\n" + "="*80)
        print("DATA EXPORT TOOL FOR PERSON 2 (SENTIMENT ANALYSIS)")
        print("="*80)
        
        print("\n📚 Usage Examples:")
        print("\n  # Export single ticker:")
        print("  python export_tool.py --ticker AAPL --limit 100")
        
        print("\n  # Export multiple tickers:")
        print("  python export_tool.py --tickers AAPL,TSLA,MSFT --limit 50")
        
        print("\n  # Export last 7 days:")
        print("  python export_tool.py --days 7")
        
        print("\n  # Export with custom filename:")
        print("  python export_tool.py --ticker AAPL --output my_data.json")
        
        print("\n" + "="*80 + "\n")
        
        # Run default export
        print("Running default export (last 7 days)...\n")
        exporter = DataExporter()
        exporter.export_all_recent(days=7)
        exporter.cleanup()
    else:
        main()
