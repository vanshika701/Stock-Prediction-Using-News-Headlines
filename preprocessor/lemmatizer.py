# preprocessor/lemmatizer.py
"""
Lemmatization module for converting words to their base forms.
Uses NLTK's WordNet Lemmatizer with POS tagging for accuracy.
"""

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import pos_tag


class Lemmatizer:
    """Lemmatize words to their base forms."""
    
    def __init__(self):
        """Initialize lemmatizer and download required NLTK data."""
        
        # Download required NLTK data
        required_data = ['wordnet', 'averaged_perceptron_tagger', 'omw-1.4']
        for data in required_data:
            try:
                nltk.data.find(f'corpora/{data}' if 'wordnet' in data or 'omw' in data else f'taggers/{data}')
            except LookupError:
                print(f"Downloading NLTK {data}...")
                nltk.download(data)
        
        # Initialize WordNet lemmatizer
        self.lemmatizer = WordNetLemmatizer()
        
        # Financial terms that should NOT be lemmatized
        self.preserve_terms = {
            'earnings', 'sales', 'shares', 'proceeds',
            'futures', 'options', 'securities', 'commodities',
            'holdings', 'savings', 'returns'
        }
        
        print("✓ Lemmatizer initialized")
    
    def get_wordnet_pos(self, treebank_tag):
        """
        Convert Penn Treebank POS tag to WordNet POS tag.
        
        Args:
            treebank_tag (str): Penn Treebank POS tag
            
        Returns:
            str: WordNet POS tag
        """
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN  # Default to noun
    
    def lemmatize_word(self, word, pos=None):
        """
        Lemmatize a single word.
        
        Args:
            word (str): Word to lemmatize
            pos (str): Part-of-speech tag (optional)
            
        Returns:
            str: Lemmatized word
        """
        if not word:
            return ""
        
        # Check if word should be preserved
        if word.lower() in self.preserve_terms:
            return word
        
        # Lemmatize with POS tag if provided
        if pos:
            return self.lemmatizer.lemmatize(word.lower(), pos=pos)
        else:
            # Try all POS tags and return shortest result
            results = []
            for pos_tag in [wordnet.NOUN, wordnet.VERB, wordnet.ADJ, wordnet.ADV]:
                results.append(self.lemmatizer.lemmatize(word.lower(), pos=pos_tag))
            
            # Return shortest lemma (usually most accurate)
            return min(results, key=len)
    
    def lemmatize_tokens(self, tokens, use_pos_tags=True):
        """
        Lemmatize a list of tokens.
        
        Args:
            tokens (list): List of word tokens
            use_pos_tags (bool): Use POS tagging for better accuracy
            
        Returns:
            list: Lemmatized tokens
        """
        if not tokens:
            return []
        
        if use_pos_tags:
            # Get POS tags for all tokens
            pos_tags = pos_tag(tokens)
            
            # Lemmatize with POS information
            lemmatized = []
            for word, tag in pos_tags:
                # Check if should be preserved
                if word.lower() in self.preserve_terms:
                    lemmatized.append(word)
                else:
                    # Convert tag and lemmatize
                    wn_tag = self.get_wordnet_pos(tag)
                    lemma = self.lemmatizer.lemmatize(word.lower(), pos=wn_tag)
                    lemmatized.append(lemma)
            
            return lemmatized
        else:
            # Lemmatize without POS tagging (faster but less accurate)
            return [self.lemmatize_word(word) for word in tokens]
    
    def lemmatize_text(self, text, use_pos_tags=True):
        """
        Lemmatize text after tokenizing.
        
        Args:
            text (str): Text to lemmatize
            use_pos_tags (bool): Use POS tagging
            
        Returns:
            str: Lemmatized text
        """
        if not text:
            return ""
        
        # Simple tokenization
        tokens = text.split()
        
        # Lemmatize
        lemmatized = self.lemmatize_tokens(tokens, use_pos_tags=use_pos_tags)
        
        # Rejoin
        return ' '.join(lemmatized)
    
    def compare_lemmatization(self, tokens):
        """
        Compare lemmatization with and without POS tagging.
        
        Args:
            tokens (list): Tokens to compare
            
        Returns:
            dict: Comparison results
        """
        with_pos = self.lemmatize_tokens(tokens, use_pos_tags=True)
        without_pos = self.lemmatize_tokens(tokens, use_pos_tags=False)
        
        # Find differences
        differences = []
        for orig, with_p, without_p in zip(tokens, with_pos, without_pos):
            if with_p != without_p:
                differences.append({
                    'original': orig,
                    'with_pos': with_p,
                    'without_pos': without_p
                })
        
        return {
            'original': tokens,
            'with_pos': with_pos,
            'without_pos': without_pos,
            'differences': differences,
            'num_differences': len(differences)
        }


def test_lemmatizer():
    """Test the lemmatizer with sample texts."""
    
    print("\n" + "="*80)
    print("TESTING LEMMATIZER")
    print("="*80)
    
    lemmatizer = Lemmatizer()
    
    # Test individual words
    print(f"\n{'='*80}")
    print("Test 1: Individual Words")
    print(f"{'='*80}")
    
    test_words = [
        ('running', 'run'),
        ('better', 'good'),
        ('earnings', 'earnings'),  # Should be preserved
        ('companies', 'company'),
        ('rising', 'rise'),
        ('highest', 'high')
    ]
    
    print("\nWord lemmatization:")
    for word, expected in test_words:
        lemma = lemmatizer.lemmatize_word(word)
        status = "✅" if lemma == expected else "⚠️"
        print(f"   {status} {word} -> {lemma} (expected: {expected})")
    
    # Test token lists
    print(f"\n{'='*80}")
    print("Test 2: Token Lists")
    print(f"{'='*80}")
    
    test_cases = [
        {
            "name": "Verbs",
            "tokens": ["running", "jumped", "flies", "swimming"]
        },
        {
            "name": "Nouns",
            "tokens": ["companies", "stocks", "earnings", "analyses"]
        },
        {
            "name": "Adjectives",
            "tokens": ["better", "best", "higher", "strongest"]
        },
        {
            "name": "Mixed sentence",
            "tokens": ["the", "companies", "are", "reporting", "better", "earnings", "today"]
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        tokens = test['tokens']
        lemmatized = lemmatizer.lemmatize_tokens(tokens)
        
        print(f"   Original:   {' '.join(tokens)}")
        print(f"   Lemmatized: {' '.join(lemmatized)}")
    
    # Test POS tagging comparison
    print(f"\n{'='*80}")
    print("Test 3: POS Tagging Impact")
    print(f"{'='*80}")
    
    tokens = ["the", "company", "saw", "better", "earnings", "rising", "significantly"]
    comparison = lemmatizer.compare_lemmatization(tokens)
    
    print(f"\nOriginal tokens:")
    print(f"   {' '.join(comparison['original'])}")
    
    print(f"\nWith POS tagging:")
    print(f"   {' '.join(comparison['with_pos'])}")
    
    print(f"\nWithout POS tagging:")
    print(f"   {' '.join(comparison['without_pos'])}")
    
    if comparison['differences']:
        print(f"\nDifferences found ({comparison['num_differences']}):")
        for diff in comparison['differences']:
            print(f"   '{diff['original']}':")
            print(f"      With POS: {diff['with_pos']}")
            print(f"      Without POS: {diff['without_pos']}")
    else:
        print("\nNo differences (POS tagging didn't affect results)")
    
    # Test full text
    print(f"\n{'='*80}")
    print("Test 4: Full Text")
    print(f"{'='*80}")
    
    text = "The companies reported better earnings. Stocks were rising significantly."
    lemmatized = lemmatizer.lemmatize_text(text)
    
    print(f"\nOriginal text:")
    print(f"   {text}")
    print(f"\nLemmatized text:")
    print(f"   {lemmatized}")
    
    # Show preserved terms
    print(f"\n{'='*80}")
    print("Preserved Financial Terms")
    print(f"{'='*80}")
    print(f"These terms are NOT lemmatized to preserve financial meaning:")
    print(f"   {', '.join(sorted(lemmatizer.preserve_terms))}")
    
    print("\n✅ Lemmatizer tests complete!")


if __name__ == "__main__":
    test_lemmatizer()