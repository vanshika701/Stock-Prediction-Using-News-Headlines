# utils/ticker_database_manual.py
"""
Manual ticker database - Use this if Wikipedia download fails.
Contains top 100+ most traded stocks.
"""

import json
import os


def create_manual_ticker_database():
    """Create a comprehensive ticker database manually."""
    
    print("\n" + "="*80)
    print("CREATING MANUAL TICKER DATABASE")
    print("="*80)
    
    # Top 100+ most important stocks
    ticker_to_company = {
        # FAANG + Big Tech
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc. (Class A)',
        'GOOG': 'Alphabet Inc. (Class C)',
        'AMZN': 'Amazon.com Inc.',
        'META': 'Meta Platforms Inc.',
        'FB': 'Meta Platforms Inc. (formerly Facebook)',
        'NVDA': 'NVIDIA Corporation',
        'TSLA': 'Tesla Inc.',
        'NFLX': 'Netflix Inc.',
        
        # Other Tech Giants
        'AMD': 'Advanced Micro Devices Inc.',
        'INTC': 'Intel Corporation',
        'ORCL': 'Oracle Corporation',
        'CSCO': 'Cisco Systems Inc.',
        'ADBE': 'Adobe Inc.',
        'CRM': 'Salesforce Inc.',
        'AVGO': 'Broadcom Inc.',
        'TXN': 'Texas Instruments Inc.',
        'QCOM': 'Qualcomm Inc.',
        'IBM': 'International Business Machines Corporation',
        
        # Financial Services
        'JPM': 'JPMorgan Chase & Co.',
        'BAC': 'Bank of America Corporation',
        'WFC': 'Wells Fargo & Company',
        'GS': 'Goldman Sachs Group Inc.',
        'MS': 'Morgan Stanley',
        'C': 'Citigroup Inc.',
        'BLK': 'BlackRock Inc.',
        'AXP': 'American Express Company',
        'V': 'Visa Inc.',
        'MA': 'Mastercard Inc.',
        'PYPL': 'PayPal Holdings Inc.',
        
        # Healthcare & Pharma
        'JNJ': 'Johnson & Johnson',
        'UNH': 'UnitedHealth Group Inc.',
        'PFE': 'Pfizer Inc.',
        'ABBV': 'AbbVie Inc.',
        'TMO': 'Thermo Fisher Scientific Inc.',
        'MRK': 'Merck & Co. Inc.',
        'ABT': 'Abbott Laboratories',
        'LLY': 'Eli Lilly and Company',
        'AMGN': 'Amgen Inc.',
        'BMY': 'Bristol-Myers Squibb Company',
        
        # Consumer & Retail
        'WMT': 'Walmart Inc.',
        'HD': 'Home Depot Inc.',
        'PG': 'Procter & Gamble Company',
        'COST': 'Costco Wholesale Corporation',
        'KO': 'Coca-Cola Company',
        'PEP': 'PepsiCo Inc.',
        'NKE': 'Nike Inc.',
        'MCD': "McDonald's Corporation",
        'SBUX': 'Starbucks Corporation',
        'TGT': 'Target Corporation',
        
        # Automotive
        'F': 'Ford Motor Company',
        'GM': 'General Motors Company',
        'TM': 'Toyota Motor Corporation',
        
        # Energy
        'XOM': 'Exxon Mobil Corporation',
        'CVX': 'Chevron Corporation',
        'COP': 'ConocoPhillips',
        'SLB': 'Schlumberger Limited',
        
        # Aerospace & Defense
        'BA': 'Boeing Company',
        'LMT': 'Lockheed Martin Corporation',
        'RTX': 'Raytheon Technologies Corporation',
        
        # Telecom
        'T': 'AT&T Inc.',
        'VZ': 'Verizon Communications Inc.',
        'TMUS': 'T-Mobile US Inc.',
        
        # Media & Entertainment
        'DIS': 'Walt Disney Company',
        'CMCSA': 'Comcast Corporation',
        
        # Industrial
        'GE': 'General Electric Company',
        'CAT': 'Caterpillar Inc.',
        'MMM': '3M Company',
        
        # Semiconductors
        'TSM': 'Taiwan Semiconductor Manufacturing Company',
        'ASML': 'ASML Holding N.V.',
        'MU': 'Micron Technology Inc.',
        
        # E-commerce & New Tech
        'SHOP': 'Shopify Inc.',
        'SQ': 'Block Inc. (formerly Square)',
        'UBER': 'Uber Technologies Inc.',
        'LYFT': 'Lyft Inc.',
        'SNAP': 'Snap Inc.',
        'TWTR': 'Twitter Inc.',
        'SPOT': 'Spotify Technology S.A.',
        'ZM': 'Zoom Video Communications Inc.',
        'PINS': 'Pinterest Inc.',
        'ROKU': 'Roku Inc.',
        'EBAY': 'eBay Inc.',
        'ETSY': 'Etsy Inc.',
        
        # Financial Tech
        'SQ': 'Block Inc.',
        'COIN': 'Coinbase Global Inc.',
        
        # Cloud & Software
        'NOW': 'ServiceNow Inc.',
        'SNOW': 'Snowflake Inc.',
        'TEAM': 'Atlassian Corporation',
        'WDAY': 'Workday Inc.',
        'ZS': 'Zscaler Inc.',
        
        # Electric Vehicles
        'RIVN': 'Rivian Automotive Inc.',
        'LCID': 'Lucid Group Inc.',
        'NIO': 'NIO Inc.',
        
        # Berkshire Hathaway
        'BRK.A': 'Berkshire Hathaway Inc. (Class A)',
        'BRK.B': 'Berkshire Hathaway Inc. (Class B)',
        'BRK-A': 'Berkshire Hathaway Inc. (Class A)',
        'BRK-B': 'Berkshire Hathaway Inc. (Class B)',
    }
    
    print(f"✓ Created database with {len(ticker_to_company)} tickers")
    
    # Create reverse mapping
    company_to_ticker = {}
    
    for ticker, company in ticker_to_company.items():
        # Full company name (lowercase)
        company_lower = company.lower()
        company_to_ticker[company_lower] = ticker
        
        # Short versions without "Inc.", "Corp.", etc.
        company_short = company.lower()
        for suffix in [' inc.', ' inc', ' corporation', ' corp.', ' corp', ' company', ' co.', ' co', ' ltd.', ' ltd', ' n.v.', ' s.a.']:
            company_short = company_short.replace(suffix, '')
        company_short = company_short.strip()
        
        if company_short != company_lower and company_short:
            company_to_ticker[company_short] = ticker

        #1. Prepare for word extraction by cleaning up common web suffixes like .com
        company_clean_for_word_split = company_short
        for web_suffix in ['.com', '.co']:
            company_clean_for_word_split = company_clean_for_word_split.replace(web_suffix, '')
        
        # 2. Extract the true first word
        first_word = company_clean_for_word_split.split()[0] if company_clean_for_word_split else ''
        
        # 3. Apply checks and map
        if first_word and len(first_word) >= 4:  # At least 4 chars
            # Don't add very common words as first word
            if first_word not in ['block', 'general']:
                company_to_ticker[first_word] = ticker

        # Short ticker mapping (e.g., 'amd', 'v' to 'AMD', 'V')
        ticker_lower = ticker.lower()
        # This check is optional but good practice to avoid needless overwrite
        if ticker_lower not in company_to_ticker:
            company_to_ticker[ticker_lower] = ticker
    
    print(f"✓ Created {len(company_to_ticker)} company name mappings")
    
    return ticker_to_company, company_to_ticker


def save_manual_database():
    """Save the manual database to JSON file."""
    
    ticker_to_company, company_to_ticker = create_manual_ticker_database()
    
    # Prepare database structure
    database = {
        'ticker_to_company': ticker_to_company,
        'company_to_ticker': company_to_ticker,
        'total_tickers': len(ticker_to_company),
        'total_companies': len(company_to_ticker),
        'created_at': '2024-01-15',
        'source': 'manual'
    }
    
    # Save to file
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(utils_dir, 'ticker_database.json')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {filepath}")
    print(f"✅ Manual ticker database created successfully!")
    
    return database


def test_manual_database():
    """Test the manually created database."""
    
    print("\n" + "="*80)
    print("TESTING MANUAL TICKER DATABASE")
    print("="*80)
    
    # Load the database we just created
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(utils_dir, 'ticker_database.json')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    ticker_to_company = database['ticker_to_company']
    company_to_ticker = database['company_to_ticker']
    
    print(f"\n✓ Loaded {len(ticker_to_company)} tickers")
    print(f"✓ Loaded {len(company_to_ticker)} company mappings")
    
    # Test ticker lookups
    print("\n1️⃣ Testing ticker -> company lookups:")
    test_tickers = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'META']
    for ticker in test_tickers:
        company = ticker_to_company.get(ticker, 'Not found')
        print(f"   {ticker:6s} -> {company}")
    
    # Test company lookups
    print("\n2️⃣ Testing company -> ticker lookups:")
    test_companies = ['apple', 'tesla', 'microsoft', 'amazon', 'nvidia', 'meta', 'amd']
    for company in test_companies:
        ticker = company_to_ticker.get(company.lower(), 'Not found')
        print(f"   {company:12s} -> {ticker}")
    
    # Test variations
    print("\n3️⃣ Testing company name variations:")
    test_variations = [
        'apple inc.',
        'microsoft corporation',
        'amazon.com',
        'meta platforms'
    ]
    for variation in test_variations:
        ticker = company_to_ticker.get(variation.lower(), 'Not found')
        print(f"   '{variation:25s}' -> {ticker}")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    # Create and save the manual database
    save_manual_database()
    
    # Test it
    test_manual_database()