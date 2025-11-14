# utils/ticker_extractor.py
"""
Smart ticker extraction from news articles.
Detects both $TICKER format and company names in text.
"""

import re
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.ticker_database import load_ticker_database, create_ambiguous_words_list
except ImportError:
    # Fallback if ticker_database doesn't exist
    print("⚠️  Warning: Using fallback ticker database loading")
    def load_ticker_database():
        import json
        filepath = os.path.join(os.path.dirname(__file__), 'ticker_database.json')
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data.get('ticker_to_company', {}), data.get('company_to_ticker', {})
        except:
            return {}, {}
    
    def create_ambiguous_words_list():
        return {'target', 'general', 'apple', 'amazon', 'meta', 'oracle', 'gap', 'best'}


class TickerExtractor:
    """Extract stock tickers from news article text."""
    
    def __init__(self):
        """Initialize the ticker extractor with database."""
        print("🔧 Initializing Ticker Extractor...")
        
        # Load ticker database
        self.ticker_to_company, self.company_to_ticker = load_ticker_database()
        
        # Load ambiguous words
        self.ambiguous_words = create_ambiguous_words_list()
        
        # Add "target" and "amazon" to ambiguous words that need context
        self.ambiguous_words.update(['target', 'amazon', 'apple'])
        
        # Common financial context words (help identify if it's really a stock mention)
        self.financial_context = {
            'stock', 'shares', 'trading', 'market', 'price', 'nasdaq', 
            'nyse', 'dow', 's&p', 'earnings', 'revenue', 'investor',
            'wall street', 'analyst', 'buy', 'sell', 'ticker', 'symbol'
        }
        
        print(f"✓ Loaded {len(self.ticker_to_company)} tickers")
        print(f"✓ Loaded {len(self.company_to_ticker)} company name mappings")
    
    def extract_dollar_tickers(self, text):
        """
        Extract tickers in $TICKER format (e.g., $AAPL, $TSLA).
        
        Args:
            text (str): Article text
        
        Returns:
            list: List of tickers found
        """
        # Pattern: $ followed by 1-5 uppercase letters
        pattern = r'\$([A-Z]{1,5})\b'
        
        matches = re.findall(pattern, text)
        
        # Filter to only valid tickers in our database
        valid_tickers = [t for t in matches if t in self.ticker_to_company]
        
        return valid_tickers
    
    def extract_company_names(self, text, require_context=True):
        """
        Extract company names from text and map to tickers.
        
        Args:
            text (str): Article text
            require_context (bool): Require financial context words nearby
        
        Returns:
            list: List of tickers found
        """
        text_lower = text.lower()
        found_tickers = []
        
        # Search for each company name in our database
        for company_name, ticker in self.company_to_ticker.items():
            # Skip very short names (too many false positives)
            if len(company_name) < 4:
                continue
            
            # Check if company name appears in text
            if company_name in text_lower:
                # Handle ambiguous words
                simple_name = company_name.split()[0]  # First word of company
                
                # IMPROVED: Check word boundaries to avoid partial matches
                # "target" should match as a word, not in "targets"
                import re
                pattern = r'\b' + re.escape(company_name) + r'\b'
                if not re.search(pattern, text_lower):
                    continue  # Not a complete word match, skip it
                
                if simple_name in self.ambiguous_words and require_context:
                    # For ambiguous words, require financial context nearby
                    if self._has_financial_context(text_lower, company_name):
                        found_tickers.append(ticker)
                else:
                    # Not ambiguous, add it
                    found_tickers.append(ticker)
        
        return found_tickers
    
    def _has_financial_context(self, text, company_name):
        """
        Check if company mention has financial context nearby.
        
        Args:
            text (str): Full text (lowercase)
            company_name (str): Company name to check around
        
        Returns:
            bool: True if financial context found nearby
        """
        # Find position of company name
        pos = text.find(company_name)
        if pos == -1:
            return False
        
        # Extract 100 characters before and after
        start = max(0, pos - 100)
        end = min(len(text), pos + len(company_name) + 100)
        context = text[start:end]
        
        # Check if any financial words appear in context
        return any(word in context for word in self.financial_context)
    
    def extract_all_tickers(self, text):
        """
        Extract all tickers from text using all methods.
        
        Args:
            text (str): Article text
        
        Returns:
            list: Unique list of tickers found
        """
        # Method 1: Dollar sign tickers ($AAPL)
        dollar_tickers = self.extract_dollar_tickers(text)
        
        # Method 2: Company names
        company_tickers = self.extract_company_names(text, require_context=True)
        
        # Combine and remove duplicates
        all_tickers = list(set(dollar_tickers + company_tickers))
        
        return all_tickers
    
    def extract_with_confidence(self, text):
        """
        Extract tickers with confidence scores.
        
        Args:
            text (str): Article text
        
        Returns:
            dict: {ticker: confidence_score} where score is 0-100
        """
        ticker_confidence = {}
        
        # Dollar sign format = 100% confidence
        dollar_tickers = self.extract_dollar_tickers(text)
        for ticker in dollar_tickers:
            ticker_confidence[ticker] = 100
        
        # Company name = 80% confidence (could be false positive)
        company_tickers = self.extract_company_names(text, require_context=True)
        for ticker in company_tickers:
            if ticker not in ticker_confidence:
                ticker_confidence[ticker] = 80
        
        # Company name without context = 50% confidence
        company_tickers_no_context = self.extract_company_names(text, require_context=False)
        for ticker in company_tickers_no_context:
            if ticker not in ticker_confidence:
                ticker_confidence[ticker] = 50
        
        return ticker_confidence
    
    def get_ticker_info(self, ticker):
        """
        Get company information for a ticker.
        
        Args:
            ticker (str): Stock ticker
        
        Returns:
            dict: Information about the ticker
        """
        company = self.ticker_to_company.get(ticker, 'Unknown')
        
        return {
            'ticker': ticker,
            'company_name': company,
            'is_valid': ticker in self.ticker_to_company
        }


def extract_tickers_from_article(article):
    """
    Extract tickers from a standardized article dictionary.
    
    Args:
        article (dict): Article with 'title', 'description', 'body' fields
    
    Returns:
        dict: Article with added 'tickers_mentioned' field
    """
    extractor = TickerExtractor()
    
    # Combine all text fields
    text_parts = [
        article.get('title', ''),
        article.get('description', ''),
        article.get('body', '')
    ]
    full_text = ' '.join(text_parts)
    
    # Extract tickers with confidence
    tickers_with_confidence = extractor.extract_with_confidence(full_text)
    
    # Add to article
    article['tickers_mentioned'] = list(tickers_with_confidence.keys())
    article['ticker_confidence'] = tickers_with_confidence
    
    return article


def test_ticker_extraction():
    """Test ticker extraction with sample headlines."""
    
    print("\n" + "="*80)
    print("TESTING TICKER EXTRACTION")
    print("="*80)
    
    extractor = TickerExtractor()
    
    # Test cases with expected results
    test_cases = [
        {
            'text': '$AAPL stock surges after iPhone sales beat expectations',
            'expected': ['AAPL']
        },
        {
            'text': 'Tesla and Amazon see gains as tech stocks rally',
            'expected': ['TSLA', 'AMZN']
        },
        {
            'text': '$GOOGL, $MSFT lead market higher with strong earnings',
            'expected': ['GOOGL', 'MSFT']
        },
        {
            'text': 'Apple Inc. announces new product line, shares up 5%',
            'expected': ['AAPL']
        },
        {
            'text': 'I went to Target to buy an apple today',  # Should NOT detect (no financial context)
            'expected': []
        },
        {
            'text': 'Microsoft Corporation earnings exceed analyst forecasts',
            'expected': ['MSFT']
        },
        {
            'text': 'NVIDIA and AMD battle for GPU market share',
            'expected': ['NVDA', 'AMD']
        },
        {
            'text': 'The general consensus is positive',  # Should NOT detect "General"
            'expected': []
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test['text'][:60]}...")
        
        # Extract tickers
        found = extractor.extract_all_tickers(test['text'])
        expected = test['expected']
        
        # Check if correct
        found_set = set(found)
        expected_set = set(expected)
        
        if found_set == expected_set:
            print(f"   ✅ PASS - Found: {found}")
            passed += 1
        else:
            print(f"   ❌ FAIL")
            print(f"      Expected: {expected}")
            print(f"      Found: {found}")
            failed += 1
    
    # Summary
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("="*80)
    
    # Calculate accuracy
    accuracy = (passed / len(test_cases)) * 100
    print(f"\n📊 Accuracy: {accuracy:.1f}%")
    
    return accuracy


def test_with_confidence():
    """Test confidence scoring."""
    
    print("\n" + "="*80)
    print("TESTING CONFIDENCE SCORING")
    print("="*80)
    
    extractor = TickerExtractor()
    
    test_texts = [
        "$AAPL rises 5%",  # Dollar sign = 100%
        "Apple Inc. stock gains",  # Company name with context = 80%
        "I like Apple products",  # Company name, no financial context = 50%
    ]
    
    for text in test_texts:
        print(f"\n📝 Text: {text}")
        confidence = extractor.extract_with_confidence(text)
        
        for ticker, score in confidence.items():
            company = extractor.get_ticker_info(ticker)['company_name']
            print(f"   {ticker} ({company}): {score}% confidence")


if __name__ == "__main__":
    # Run tests
    accuracy = test_ticker_extraction()
    
    print("\n")
    test_with_confidence()
    
    print("\n✅ Ticker extraction tests complete!")