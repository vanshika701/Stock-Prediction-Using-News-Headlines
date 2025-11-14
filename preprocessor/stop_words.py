# preprocessor/stop_words.py
"""
Stop words removal for financial news preprocessing.
Removes common words while preserving financial terminology.
"""

import nltk
from nltk.corpus import stopwords


class StopWordsRemover:
    """Remove stop words while preserving financial terms."""
    
    def __init__(self, custom_stopwords=None):
        """
        Initialize stop words remover.
        
        Args:
            custom_stopwords (set): Additional stop words to remove
        """
        # Download stopwords if not available
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("Downloading NLTK stopwords...")
            nltk.download('stopwords')
        
        # Get English stop words
        self.base_stopwords = set(stopwords.words('english'))
        
        # Financial terms that should NOT be removed (even if they're stop words)
        self.financial_keywords = {
            'up', 'down', 'over', 'under', 'above', 'below',
            'high', 'low', 'more', 'less', 'most', 'least',
            'top', 'bottom', 'best', 'worst',
            'buy', 'sell', 'hold',
            'bull', 'bear',
            'long', 'short',
            'call', 'put',
            'not', 'no'  # Important for sentiment
        }
        
        # Remove financial keywords from stop words
        self.stopwords = self.base_stopwords - self.financial_keywords
        
        # Add custom stop words if provided
        if custom_stopwords:
            self.stopwords.update(custom_stopwords)
        
        print(f"✓ Initialized with {len(self.stopwords)} stop words")
        print(f"✓ Preserving {len(self.financial_keywords)} financial keywords")
    
    def remove(self, tokens, preserve_case=False):
        """
        Remove stop words from token list.
        
        Args:
            tokens (list): List of word tokens
            preserve_case (bool): Keep original casing
            
        Returns:
            list: Filtered tokens
        """
        if not tokens:
            return []
        
        if preserve_case:
            # Check lowercase version but keep original token
            filtered = [
                token for token in tokens
                if token.lower() not in self.stopwords
            ]
        else:
            # Lowercase everything
            filtered = [
                token.lower() for token in tokens
                if token.lower() not in self.stopwords
            ]
        
        return filtered
    
    def remove_from_text(self, text):
        """
        Remove stop words directly from text (simpler but less accurate).
        
        Args:
            text (str): Text to process
            
        Returns:
            str: Text with stop words removed
        """
        if not text:
            return ""
        
        # Split into words
        words = text.split()
        
        # Filter
        filtered = self.remove(words, preserve_case=True)
        
        # Rejoin
        return ' '.join(filtered)
    
    def get_stopwords(self):
        """
        Get the current set of stop words.
        
        Returns:
            set: Stop words
        """
        return self.stopwords.copy()
    
    def add_stopwords(self, words):
        """
        Add custom stop words.
        
        Args:
            words (list or set): Words to add
        """
        if isinstance(words, str):
            words = [words]
        
        self.stopwords.update(words)
        print(f"✓ Added {len(words)} custom stop words")
    
    def remove_stopwords(self, words):
        """
        Remove words from stop word list (preserve them).
        
        Args:
            words (list or set): Words to preserve
        """
        if isinstance(words, str):
            words = [words]
        
        self.stopwords.difference_update(words)
        print(f"✓ Removed {len(words)} words from stop word list")
    
    def calculate_reduction(self, tokens):
        """
        Calculate how much the text is reduced by stop word removal.
        
        Args:
            tokens (list): Original tokens
            
        Returns:
            dict: Statistics about reduction
        """
        if not tokens:
            return {
                'original_count': 0,
                'filtered_count': 0,
                'removed_count': 0,
                'reduction_percent': 0
            }
        
        filtered = self.remove(tokens)
        
        original_count = len(tokens)
        filtered_count = len(filtered)
        removed_count = original_count - filtered_count
        reduction_percent = (removed_count / original_count * 100) if original_count > 0 else 0
        
        return {
            'original_count': original_count,
            'filtered_count': filtered_count,
            'removed_count': removed_count,
            'reduction_percent': round(reduction_percent, 2)
        }


def test_stopwords_remover():
    """Test the stop words remover with sample texts."""
    
    print("\n" + "="*80)
    print("TESTING STOP WORDS REMOVER")
    print("="*80)
    
    remover = StopWordsRemover()
    
    # Test cases
    test_cases = [
        {
            "name": "Simple sentence",
            "tokens": ["the", "stock", "is", "going", "up", "today"]
        },
        {
            "name": "Financial terms preservation",
            "tokens": ["buy", "sell", "hold", "the", "stock", "for", "long", "term"]
        },
        {
            "name": "Sentiment preservation",
            "tokens": ["this", "is", "not", "a", "good", "investment"]
        },
        {
            "name": "Real article snippet",
            "tokens": ["apple", "inc", "reported", "strong", "earnings", "today", 
                      "the", "stock", "surged", "up", "by", "5", "percent", 
                      "exceeding", "analyst", "expectations"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*80}")
        
        tokens = test['tokens']
        filtered = remover.remove(tokens)
        stats = remover.calculate_reduction(tokens)
        
        print(f"\nOriginal tokens ({len(tokens)}):")
        print(f"   {' '.join(tokens)}")
        
        print(f"\nFiltered tokens ({len(filtered)}):")
        print(f"   {' '.join(filtered)}")
        
        print(f"\n📊 Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    # Test with actual text
    print(f"\n{'='*80}")
    print("Test: Full Text Processing")
    print(f"{'='*80}")
    
    text = "The company reported strong earnings today. The stock is up 5%."
    filtered_text = remover.remove_from_text(text)
    
    print(f"\nOriginal text:")
    print(f"   {text}")
    print(f"\nFiltered text:")
    print(f"   {filtered_text}")
    
    # Show which financial keywords are preserved
    print(f"\n{'='*80}")
    print("Preserved Financial Keywords")
    print(f"{'='*80}")
    print(f"These words are NOT removed even though they're in standard stop word lists:")
    print(f"   {', '.join(sorted(remover.financial_keywords))}")
    
    print("\n✅ Stop words remover tests complete!")


if __name__ == "__main__":
    test_stopwords_remover()