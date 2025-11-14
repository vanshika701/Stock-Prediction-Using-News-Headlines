# utils/context_extractor.py
"""
Extract context (surrounding words) around ticker mentions.
This helps sentiment analysis understand WHY a ticker was mentioned.
"""

import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load ticker database with fallback
try:
    from utils.ticker_database import load_ticker_database
except ImportError:
    # Fallback: load directly from JSON
    def load_ticker_database():
        import json
        filepath = os.path.join(os.path.dirname(__file__), 'ticker_database.json')
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data.get('ticker_to_company', {}), data.get('company_to_ticker', {})
        except:
            return {}, {}


class ContextExtractor:
    """Extract context around ticker mentions in text."""
    
    def __init__(self, context_window=10):
        """
        Initialize context extractor.
        
        Args:
            context_window (int): Number of words to extract on each side of ticker
        """
        self.context_window = context_window
        self.ticker_to_company, self.company_to_ticker = load_ticker_database()
        
        print(f"🔧 Context Extractor initialized (window: {context_window} words)")
    
    def extract_context_for_ticker(self, text, ticker):
        """
        Extract all contexts where a ticker is mentioned.
        
        Args:
            text (str): Full article text
            ticker (str): Ticker to find
        
        Returns:
            list: List of context strings
        """
        contexts = []
        
        # Method 1: Find $TICKER format
        dollar_contexts = self._find_dollar_ticker_contexts(text, ticker)
        contexts.extend(dollar_contexts)
        
        # Method 2: Find company name
        company_name = self.ticker_to_company.get(ticker)
        if company_name:
            company_contexts = self._find_company_name_contexts(text, company_name)
            contexts.extend(company_contexts)
        
        # Remove duplicates while preserving order
        unique_contexts = []
        seen = set()
        for ctx in contexts:
            ctx_normalized = ctx.lower().strip()
            if ctx_normalized not in seen:
                unique_contexts.append(ctx)
                seen.add(ctx_normalized)
        
        return unique_contexts
    
    def _find_dollar_ticker_contexts(self, text, ticker):
        """Find contexts around $TICKER mentions."""
        contexts = []
        
        # Pattern to find $TICKER
        pattern = rf'\${ticker}\b'
        
        # Find all matches
        for match in re.finditer(pattern, text, re.IGNORECASE):
            context = self._extract_window_around_position(text, match.start(), match.end())
            contexts.append(context)
        
        return contexts
    
    def _find_company_name_contexts(self, text, company_name):
        """Find contexts around company name mentions."""
        contexts = []
        
        # Search case-insensitive
        text_lower = text.lower()
        company_lower = company_name.lower()
        
        # Find all occurrences
        pos = 0
        while True:
            pos = text_lower.find(company_lower, pos)
            if pos == -1:
                break
            
            # Extract context
            end_pos = pos + len(company_lower)
            context = self._extract_window_around_position(text, pos, end_pos)
            contexts.append(context)
            
            # Move to next occurrence
            pos = end_pos
        
        return contexts
    
    def _extract_window_around_position(self, text, start_pos, end_pos):
        """
        Extract N words before and after a position.
        
        Args:
            text (str): Full text
            start_pos (int): Start position of ticker mention
            end_pos (int): End position of ticker mention
        
        Returns:
            str: Context window
        """
        # Split text into words
        words = text.split()
        
        # Find word positions
        word_positions = []
        current_pos = 0
        for word in words:
            word_start = text.find(word, current_pos)
            word_end = word_start + len(word)
            word_positions.append((word_start, word_end, word))
            current_pos = word_end
        
        # Find which word contains our ticker
        ticker_word_index = None
        for i, (w_start, w_end, word) in enumerate(word_positions):
            if w_start <= start_pos < w_end or w_start < end_pos <= w_end:
                ticker_word_index = i
                break
        
        if ticker_word_index is None:
            return ""
        
        # Extract window
        start_index = max(0, ticker_word_index - self.context_window)
        end_index = min(len(words), ticker_word_index + self.context_window + 1)
        
        context_words = words[start_index:end_index]
        
        # Highlight the ticker in context
        result = []
        for i, word in enumerate(context_words):
            if start_index + i == ticker_word_index:
                result.append(f"**{word}**")  # Mark ticker with **
            else:
                result.append(word)
        
        return ' '.join(result)
    
    def extract_all_contexts(self, text, tickers):
        """
        Extract contexts for all tickers in a list.
        
        Args:
            text (str): Article text
            tickers (list): List of tickers to find
        
        Returns:
            dict: {ticker: [contexts]} mapping
        """
        all_contexts = {}
        
        for ticker in tickers:
            contexts = self.extract_context_for_ticker(text, ticker)
            if contexts:
                all_contexts[ticker] = contexts
        
        return all_contexts
    
    def get_sentiment_relevant_context(self, text, ticker):
        """
        Extract only the most sentiment-relevant context.
        Prioritizes contexts with sentiment words.
        
        Args:
            text (str): Article text
            ticker (str): Ticker symbol
        
        Returns:
            str: Most relevant context
        """
        # Sentiment keywords to prioritize
        sentiment_keywords = {
            'positive': ['surge', 'gain', 'up', 'rise', 'beat', 'exceed', 'strong', 
                        'growth', 'profit', 'success', 'bullish', 'rally'],
            'negative': ['fall', 'drop', 'down', 'loss', 'miss', 'weak', 'decline',
                        'bearish', 'crash', 'plunge', 'slump', 'concern']
        }
        
        all_contexts = self.extract_context_for_ticker(text, ticker)
        
        if not all_contexts:
            return ""
        
        # Score each context by sentiment word presence
        scored_contexts = []
        for context in all_contexts:
            context_lower = context.lower()
            score = 0
            
            for sentiment_list in sentiment_keywords.values():
                for word in sentiment_list:
                    if word in context_lower:
                        score += 1
            
            scored_contexts.append((score, context))
        
        # Return highest scoring context
        scored_contexts.sort(reverse=True, key=lambda x: x[0])
        return scored_contexts[0][1] if scored_contexts else all_contexts[0]


def analyze_article_contexts(article, tickers):
    """
    Analyze an article and extract contexts for all tickers.
    
    Args:
        article (dict): Article dictionary
        tickers (list): List of tickers to analyze
    
    Returns:
        dict: Article with added context information
    """
    extractor = ContextExtractor(context_window=10)
    
    # Combine text
    full_text = f"{article.get('title', '')} {article.get('description', '')} {article.get('body', '')}"
    
    # Extract contexts
    contexts = extractor.extract_all_contexts(full_text, tickers)
    
    # Add to article
    article['ticker_contexts'] = contexts
    
    return article


def test_context_extraction():
    """Test context extraction with sample text."""
    
    print("\n" + "="*80)
    print("TESTING CONTEXT EXTRACTION")
    print("="*80)
    
    extractor = ContextExtractor(context_window=10)
    
    # Sample article text
    test_text = """
    Apple Inc. stock surged 5% today after the company reported record iPhone sales.
    The $AAPL shares reached an all-time high of $180, beating analyst expectations.
    CEO Tim Cook stated that Apple's services division continues to show strong growth.
    Meanwhile, Tesla faces challenges as $TSLA stock dropped 3% on production concerns.
    Investors are worried about Tesla's ability to meet delivery targets this quarter.
    """
    
    # Test 1: Extract context for AAPL
    print("\n1️⃣ Testing context extraction for AAPL:")
    aapl_contexts = extractor.extract_context_for_ticker(test_text, 'AAPL')
    
    for i, context in enumerate(aapl_contexts, 1):
        print(f"\n   Context {i}:")
        print(f"   {context}")
    
    # Test 2: Extract context for TSLA
    print("\n2️⃣ Testing context extraction for TSLA:")
    tsla_contexts = extractor.extract_context_for_ticker(test_text, 'TSLA')
    
    for i, context in enumerate(tsla_contexts, 1):
        print(f"\n   Context {i}:")
        print(f"   {context}")
    
    # Test 3: Extract all contexts
    print("\n3️⃣ Testing batch extraction:")
    all_contexts = extractor.extract_all_contexts(test_text, ['AAPL', 'TSLA'])
    
    for ticker, contexts in all_contexts.items():
        print(f"\n   {ticker}: Found {len(contexts)} contexts")
    
    # Test 4: Get most relevant context (with sentiment words)
    print("\n4️⃣ Testing sentiment-relevant context:")
    
    print("\n   AAPL (should find positive context):")
    aapl_relevant = extractor.get_sentiment_relevant_context(test_text, 'AAPL')
    print(f"   {aapl_relevant}")
    
    print("\n   TSLA (should find negative context):")
    tsla_relevant = extractor.get_sentiment_relevant_context(test_text, 'TSLA')
    print(f"   {tsla_relevant}")
    
    print("\n✅ Context extraction tests complete!")


def test_with_real_headline():
    """Test with realistic financial headlines."""
    
    print("\n" + "="*80)
    print("TESTING WITH REAL HEADLINES")
    print("="*80)
    
    extractor = ContextExtractor(context_window=8)
    
    headlines = [
        {
            'text': '$NVDA soars to new highs as AI chip demand remains robust, analysts raise price targets',
            'ticker': 'NVDA'
        },
        {
            'text': 'Amazon Web Services revenue disappoints as $AMZN shares fall in after-hours trading',
            'ticker': 'AMZN'
        },
        {
            'text': 'Microsoft announces major Azure cloud deal, $MSFT gains 2% on strong enterprise demand',
            'ticker': 'MSFT'
        }
    ]
    
    for i, headline in enumerate(headlines, 1):
        print(f"\n{i}. Headline: {headline['text'][:70]}...")
        
        context = extractor.extract_context_for_ticker(headline['text'], headline['ticker'])
        
        print(f"   Ticker: {headline['ticker']}")
        print(f"   Context: {context[0] if context else 'None found'}")


if __name__ == "__main__":
    # Run tests
    test_context_extraction()
    
    print("\n")
    test_with_real_headline()