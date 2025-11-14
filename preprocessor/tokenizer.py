# preprocessor/tokenizer.py
"""
Tokenization module for splitting text into sentences and words.
Uses NLTK for robust tokenization.
"""

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import re


class Tokenizer:
    """Tokenize text into sentences and words."""
    
    def __init__(self):
        """Initialize tokenizer and ensure NLTK data is downloaded."""
        
        # Make sure NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt')
        
        # Financial terms that should stay together
        self.financial_terms = [
            'bull market', 'bear market', 'market cap', 'price target',
            'earnings per share', 'stock split', 'initial public offering',
            'hedge fund', 'mutual fund', 'trading volume', 'stock price',
            'market share', 'revenue growth', 'profit margin'
        ]
        
        # Compile regex for financial term preservation
        self.financial_term_patterns = [
            (term, re.compile(r'\b' + term.replace(' ', r'\s+') + r'\b', re.IGNORECASE))
            for term in self.financial_terms
        ]
    
    def tokenize_sentences(self, text):
        """
        Split text into sentences.
        
        Args:
            text (str): Text to tokenize
            
        Returns:
            list: List of sentences
        """
        if not text:
            return []
        
        # Use NLTK's sentence tokenizer
        sentences = sent_tokenize(text)
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def tokenize_words(self, text, lowercase=True, preserve_financial_symbols=True):
        """
        Split text into words/tokens.
        
        Args:
            text (str): Text to tokenize
            lowercase (bool): Convert to lowercase
            preserve_financial_symbols (bool): Keep $, %, etc.
            
        Returns:
            list: List of word tokens
        """
        if not text:
            return []
        
        # Lowercase if requested
        if lowercase:
            text = text.lower()
        
        # Preserve financial terms before tokenization
        preserved_terms = {}
        for i, (term, pattern) in enumerate(self.financial_term_patterns):
            placeholder = f"FINANCIALTERM{i}"
            if pattern.search(text):
                text = pattern.sub(placeholder, text)
                preserved_terms[placeholder] = term
        
        # Tokenize with NLTK
        tokens = word_tokenize(text)
        
        # Restore preserved financial terms
        restored_tokens = []
        for token in tokens:
            if token in preserved_terms:
                # Split the term back into words if needed
                term = preserved_terms[token]
                restored_tokens.extend(term.split())
            else:
                restored_tokens.append(token)
        
        # Filter out empty tokens
        tokens = [t for t in restored_tokens if t.strip()]
        
        # Optionally remove financial symbols
        if not preserve_financial_symbols:
            tokens = [t for t in tokens if not re.match(r'^[$%€£¥]+$', t)]
        
        return tokens
    
    def tokenize_sentences_and_words(self, text, lowercase=True):
        """
        Tokenize text into sentences, then each sentence into words.
        
        Args:
            text (str): Text to tokenize
            lowercase (bool): Convert to lowercase
            
        Returns:
            list: List of sentences, each containing list of words
        """
        if not text:
            return []
        
        # Split into sentences
        sentences = self.tokenize_sentences(text)
        
        # Tokenize each sentence
        tokenized_sentences = []
        for sentence in sentences:
            words = self.tokenize_words(sentence, lowercase=lowercase)
            if words:  # Only include non-empty sentences
                tokenized_sentences.append(words)
        
        return tokenized_sentences
    
    def count_tokens(self, text):
        """
        Count various token statistics.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Token statistics
        """
        if not text:
            return {
                'num_sentences': 0,
                'num_words': 0,
                'avg_words_per_sentence': 0,
                'num_unique_words': 0
            }
        
        sentences = self.tokenize_sentences(text)
        words = self.tokenize_words(text)
        unique_words = set(words)
        
        avg_words = len(words) / len(sentences) if sentences else 0
        
        return {
            'num_sentences': len(sentences),
            'num_words': len(words),
            'avg_words_per_sentence': round(avg_words, 2),
            'num_unique_words': len(unique_words)
        }


def test_tokenizer():
    """Test the tokenizer with sample texts."""
    
    print("\n" + "="*80)
    print("TESTING TOKENIZER")
    print("="*80)
    
    tokenizer = Tokenizer()
    
    # Test texts
    test_texts = [
        {
            "name": "Simple sentence",
            "text": "Apple stock rises 5% today."
        },
        {
            "name": "Multiple sentences",
            "text": "Tesla reported strong earnings. The stock surged 10%. Investors are optimistic."
        },
        {
            "name": "Financial terms",
            "text": "The bull market continues as the stock price reaches new highs. Market cap exceeded $2 trillion."
        },
        {
            "name": "Complex article",
            "text": "Apple Inc. announced record Q1 earnings today. The company's revenue grew 15% year-over-year. CEO Tim Cook stated, 'This is our best quarter ever.' The stock price jumped $10, reaching an all-time high of $180 per share."
        }
    ]
    
    for i, test in enumerate(test_texts, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*80}")
        
        text = test['text']
        print(f"\nOriginal text:\n{text}")
        
        # Tokenize sentences
        sentences = tokenizer.tokenize_sentences(text)
        print(f"\n📝 Sentences ({len(sentences)}):")
        for j, sent in enumerate(sentences, 1):
            print(f"   {j}. {sent}")
        
        # Tokenize words
        words = tokenizer.tokenize_words(text)
        print(f"\n🔤 Words ({len(words)}):")
        print(f"   {', '.join(words[:20])}" + ("..." if len(words) > 20 else ""))
        
        # Get statistics
        stats = tokenizer.count_tokens(text)
        print(f"\n📊 Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    # Test sentence + word tokenization
    print(f"\n{'='*80}")
    print("Test: Sentences with Words")
    print(f"{'='*80}")
    
    text = "Apple reports earnings. Revenue up 15%. Stock surges."
    tokenized = tokenizer.tokenize_sentences_and_words(text)
    
    print(f"\nOriginal: {text}")
    print(f"\nTokenized structure:")
    for i, sent_tokens in enumerate(tokenized, 1):
        print(f"   Sentence {i}: {sent_tokens}")
    
    print("\n✅ Tokenizer tests complete!")


if __name__ == "__main__":
    test_tokenizer()