import requests
import json

def export_articles_for_sentiment_analysis():
    """Export articles as JSON for Person 2 (Sentiment Analysis)."""
    
    print("\n" + "="*80)
    print("EXPORTING DATA FOR PERSON 2 (SENTIMENT ANALYSIS)")
    print("="*80)
    
    base_url = "http://localhost:5000"
    
    # Tickers to export
    tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN']
    
    for ticker in tickers:
        print(f"\n📤 Exporting {ticker} articles...")
        
        try:
            # Get articles from API
            response = requests.get(
                f"{base_url}/export/json",
                params={'ticker': ticker, 'limit': 100}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Save to file
                filename = f"{ticker.lower()}_articles.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✓ Exported {data['count']} articles to {filename}")
            else:
                print(f"✗ Error: {response.status_code}")
        
        except Exception as e:
            print(f"✗ Error exporting {ticker}: {e}")
    
    # Also export all recent articles
    print(f"\n📤 Exporting all recent articles...")
    
    try:
        response = requests.get(
            f"{base_url}/export/json",
            params={'limit': 500}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            with open('all_recent_articles.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Exported {data['count']} articles to all_recent_articles.json")
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*80)
    print("✅ EXPORT COMPLETE!")
    print("="*80)
    
    print("\n📁 Files created:")
    print("   - aapl_articles.json")
    print("   - tsla_articles.json")
    print("   - msft_articles.json")
    print("   - googl_articles.json")
    print("   - amzn_articles.json")
    print("   - all_recent_articles.json")
    
    print("\n💡 Share these files with Person 2 for sentiment analysis!")

if __name__ == "__main__":
    export_articles_for_sentiment_analysis()
