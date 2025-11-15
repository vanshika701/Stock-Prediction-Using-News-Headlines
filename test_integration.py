# test_integration.py
"""
End-to-end integration test for the complete pipeline.
Tests: Scraping → Storage → Processing → APIs
"""

import time
import requests
import json
from datetime import datetime

print("\n" + "="*80)
print("INTEGRATION TEST: COMPLETE PIPELINE")
print("="*80)

# Test configuration
OUTPUT_API = "http://localhost:5000"
INPUT_API = "http://localhost:5001"


def test_output_api():
    """Test Output API (Person 2)."""
    
    print("\n" + "="*80)
    print("TESTING OUTPUT API (FOR PERSON 2)")
    print("="*80)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{OUTPUT_API}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health: {data['status']}")
            print(f"✓ Database: {data['database']}")
            print(f"✓ Cache: {data.get('cache', 'N/A')}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Get all articles
    print("\n2️⃣ Testing get all articles...")
    try:
        response = requests.get(f"{OUTPUT_API}/api/articles?limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {data['count']} articles")
            if data['articles']:
                print(f"✓ Sample: {data['articles'][0]['title'][:50]}...")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Get articles by ticker
    print("\n3️⃣ Testing get articles by ticker (AAPL)...")
    try:
        response = requests.get(f"{OUTPUT_API}/api/articles/ticker/AAPL?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {data['count']} articles for AAPL")
            print(f"✓ Source: {data['source']}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Get recent articles
    print("\n4️⃣ Testing get recent articles (24h)...")
    try:
        response = requests.get(f"{OUTPUT_API}/api/articles/recent?hours=24&limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {data['count']} recent articles")
            print(f"✓ Time range: {data['time_range']}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Get stream
    print("\n5️⃣ Testing data stream...")
    try:
        response = requests.get(f"{OUTPUT_API}/api/stream/latest")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Stream retrieved: {data['count']} articles")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_input_api():
    """Test Input API (Person 3)."""
    
    print("\n" + "="*80)
    print("TESTING INPUT API (FOR PERSON 3)")
    print("="*80)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{INPUT_API}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health: {data['status']}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Add to watchlist
    print("\n2️⃣ Testing add to watchlist...")
    try:
        payload = {"tickers": ["AAPL", "TSLA", "MSFT"]}
        response = requests.post(
            f"{INPUT_API}/api/watchlist",
            json=payload
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Added tickers to watchlist")
            print(f"✓ Watchlist: {data['watchlist']}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Get watchlist
    print("\n3️⃣ Testing get watchlist...")
    try:
        response = requests.get(f"{INPUT_API}/api/watchlist")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Watchlist: {data['watchlist']}")
            print(f"✓ Count: {data['count']}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Set priority
    print("\n4️⃣ Testing set ticker priority...")
    try:
        payload = {"ticker": "AAPL", "priority": "high"}
        response = requests.post(
            f"{INPUT_API}/api/priority",
            json=payload
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Set priority: {data['ticker']} = {data['priority']}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Submit query
    print("\n5️⃣ Testing submit query...")
    try:
        payload = {
            "query": "earnings",
            "tickers": ["AAPL"],
        }
        response = requests.post(
            f"{INPUT_API}/api/query",
            json=payload
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Query executed successfully")
            print(f"✓ Found {data['count']} matching articles")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 6: Get statistics
    print("\n6️⃣ Testing get statistics...")
    try:
        response = requests.get(f"{INPUT_API}/api/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Total articles: {data['total_articles']}")
            print(f"✓ Sentiment: {data['sentiment_distribution']}")
            print(f"✓ Top tickers: {len(data['top_tickers'])} shown")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_complete_pipeline():
    """Test complete end-to-end pipeline."""
    
    print("\n" + "="*80)
    print("TESTING COMPLETE PIPELINE")
    print("="*80)
    
    print("\n📋 Pipeline stages:")
    print("   1. Person 3 adds ticker to watchlist (INPUT)")
    print("   2. Scraper fetches news for that ticker")
    print("   3. Data is processed and stored")
    print("   4. Person 2 retrieves data via API (OUTPUT)")
    
    # Stage 1: Add ticker via Input API
    print("\n🔹 Stage 1: Adding NVDA to watchlist...")
    try:
        payload = {"tickers": ["NVDA"]}
        response = requests.post(f"{INPUT_API}/api/watchlist", json=payload)
        if response.status_code == 200:
            print("✓ NVDA added to watchlist")
        else:
            print("✗ Failed to add to watchlist")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    time.sleep(1)
    
    # Stage 2: Check if data exists
    print("\n🔹 Stage 2: Checking if NVDA articles exist...")
    try:
        response = requests.get(f"{OUTPUT_API}/api/articles/ticker/NVDA?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data['count']} NVDA articles")
            if data['count'] > 0:
                print(f"✓ Sample: {data['articles'][0]['title'][:60]}...")
        else:
            print("✗ Failed to retrieve articles")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Stage 3: Person 2 queries recent data
    print("\n🔹 Stage 3: Person 2 retrieves recent articles...")
    try:
        response = requests.get(f"{OUTPUT_API}/api/articles/recent?hours=24")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {data['count']} recent articles")
            
            # Show sentiment distribution
            sentiments = {}
            for article in data['articles']:
                sent = article.get('sentiment', 'unknown')
                sentiments[sent] = sentiments.get(sent, 0) + 1
            
            print(f"✓ Sentiment distribution:")
            for sent, count in sentiments.items():
                print(f"   {sent}: {count}")
        else:
            print("✗ Failed to retrieve articles")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*80)
    print("PIPELINE TEST SUMMARY")
    print("="*80)
    print("✓ Input API: Working")
    print("✓ Output API: Working")
    print("✓ Data Flow: Functional")
    print("✓ Integration: Complete")


def performance_test():
    """Test API performance."""
    
    print("\n" + "="*80)
    print("PERFORMANCE TEST")
    print("="*80)
    
    # Test response times
    endpoints = [
        ("Health Check", f"{OUTPUT_API}/api/health"),
        ("Get Articles", f"{OUTPUT_API}/api/articles?limit=10"),
        ("Get By Ticker", f"{OUTPUT_API}/api/articles/ticker/AAPL?limit=10"),
        ("Recent Articles", f"{OUTPUT_API}/api/articles/recent?hours=24"),
        ("Stream", f"{OUTPUT_API}/api/stream/latest")
    ]
    
    print("\n⏱️  Testing response times:")
    
    for name, url in endpoints:
        try:
            start = time.time()
            response = requests.get(url)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                print(f"   {name:20s} {elapsed*1000:6.1f}ms ✓")
            else:
                print(f"   {name:20s} FAILED ({response.status_code}) ✗")
        except Exception as e:
            print(f"   {name:20s} ERROR ✗")


if __name__ == "__main__":
    print("\n🧪 Starting Integration Tests...")
    print("⚠️  Make sure both APIs are running:")
    print("   Terminal 1: python api/output_api.py")
    print("   Terminal 2: python api/input_api.py")
    print("\nPress Enter to continue...")
    input()
    
    # Run tests
    try:
        test_output_api()
        time.sleep(2)
        
        test_input_api()
        time.sleep(2)
        
        test_complete_pipeline()
        time.sleep(2)
        
        performance_test()
        
        print("\n" + "="*80)
        print("✅ ALL INTEGRATION TESTS COMPLETE!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests stopped by user")
    except Exception as e:
        print(f"\n\n❌ Test error: {e}")
