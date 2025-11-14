# preprocessor/feature_extractor.py
"""
Extract features from financial news articles.
Includes named entities, financial keywords, numbers, and dates.
"""

import re
from datetime import datetime
from collections import Counter
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree


class FeatureExtractor:
    """Extract meaningful features from financial news text."""
    
    def __init__(self):
        """Initialize feature extractor."""
        
        # Download required NLTK data
        required_data = ['maxent_ne_chunker', 'words']
        for data in required_data:
            try:
                nltk.data.find(f'chunkers/{data}' if 'chunker' in data else f'corpora/{data}')
            except LookupError:
                print(f"Downloading NLTK {data}...")
                nltk.download(data)
        
        # Financial keywords dictionary
        self.financial_keywords = {
            'positive': [
                'surge', 'soar', 'jump', 'rise', 'gain', 'boost', 'rally',
                'strong', 'beat', 'exceed', 'outperform', 'profit', 'growth',
                'record', 'high', 'bullish', 'optimistic', 'upgrade', 'buy'
            ],
            'negative': [
                'plunge', 'crash', 'drop', 'fall', 'decline', 'loss', 'weak',
                'miss', 'disappoint', 'underperform', 'cut', 'lower', 'bearish',
                'pessimistic', 'downgrade', 'sell', 'slump', 'tumble'
            ],
            'neutral': [
                'announce', 'report', 'release', 'state', 'expect', 'forecast',
                'estimate', 'project', 'quarter', 'earnings', 'revenue', 'hold'
            ]
        }
        
        # Compile patterns
        self.number_pattern = re.compile(r'\b\d+(?:\.\d+)?(?:%|M|B|K)?\b')
        self.date_pattern = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b')
        self.percentage_pattern = re.compile(r'\b\d+(?:\.\d+)?%\b')
        
        print("✓ Feature extractor initialized")
    
    def extract_named_entities(self, text):
        """
        Extract named entities (people, organizations, locations).
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Dictionary of entity types and their values
        """
        if not text:
            return {'PERSON': [], 'ORGANIZATION': [], 'GPE': []}
        
        # Tokenize and POS tag
        tokens = word_tokenize(text)
        pos_tagged = pos_tag(tokens)
        
        # Named entity recognition
        chunked = ne_chunk(pos_tagged)
        
        # Extract entities
        entities = {
            'PERSON': [],
            'ORGANIZATION': [],
            'GPE': []  # Geo-Political Entity (locations)
        }
        
        for chunk in chunked:
            if isinstance(chunk, Tree):
                entity_type = chunk.label()
                entity_text = ' '.join([token for token, pos in chunk.leaves()])
                
                if entity_type in entities:
                    entities[entity_type].append(entity_text)
        
        # Remove duplicates while preserving order
        for entity_type in entities:
            entities[entity_type] = list(dict.fromkeys(entities[entity_type]))
        
        return entities
    
    def extract_financial_keywords(self, text):
        """
        Extract financial keywords and categorize by sentiment.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Keywords categorized by sentiment
        """
        if not text:
            return {'positive': [], 'negative': [], 'neutral': []}
        
        text_lower = text.lower()
        words = set(text_lower.split())
        
        found_keywords = {
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        for sentiment, keywords in self.financial_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords[sentiment].append(keyword)
        
        return found_keywords
    
    def extract_numbers(self, text):
        """
        Extract all numbers from text (including percentages, millions, billions).
        
        Args:
            text (str): Text to analyze
            
        Returns:
            list: List of numbers found
        """
        if not text:
            return []
        
        numbers = self.number_pattern.findall(text)
        return numbers
    
    def extract_percentages(self, text):
        """
        Extract percentage values from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            list: List of percentages
        """
        if not text:
            return []
        
        percentages = self.percentage_pattern.findall(text)
        return percentages
    
    def extract_dates(self, text):
        """
        Extract dates from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            list: List of dates found
        """
        if not text:
            return []
        
        dates = self.date_pattern.findall(text)
        return dates
    
    def count_word_frequency(self, tokens, top_n=10):
        """
        Count word frequencies in token list.
        
        Args:
            tokens (list): List of tokens
            top_n (int): Number of top words to return
            
        Returns:
            list: List of (word, count) tuples
        """
        if not tokens:
            return []
        
        # Filter out very short words
        meaningful_tokens = [t for t in tokens if len(t) > 2]
        
        # Count frequencies
        counter = Counter(meaningful_tokens)
        
        # Return top N
        return counter.most_common(top_n)
    
    def extract_all_features(self, text, tokens=None):
        """
        Extract all features from text.
        
        Args:
            text (str): Text to analyze
            tokens (list): Pre-tokenized text (optional)
            
        Returns:
            dict: All extracted features
        """
        features = {}
        
        # Named entities
        features['entities'] = self.extract_named_entities(text)
        
        # Financial keywords
        features['financial_keywords'] = self.extract_financial_keywords(text)
        
        # Numbers and percentages
        features['numbers'] = self.extract_numbers(text)
        features['percentages'] = self.extract_percentages(text)
        features['dates'] = self.extract_dates(text)
        
        # Word frequency
        if tokens:
            features['top_words'] = self.count_word_frequency(tokens)
        
        # Summary statistics
        features['stats'] = {
            'num_entities': sum(len(v) for v in features['entities'].values()),
            'num_positive_keywords': len(features['financial_keywords']['positive']),
            'num_negative_keywords': len(features['financial_keywords']['negative']),
            'num_neutral_keywords': len(features['financial_keywords']['neutral']),
            'num_numbers': len(features['numbers']),
            'num_percentages': len(features['percentages']),
            'num_dates': len(features['dates'])
        }
        
        return features


def test_feature_extractor():
    """Test the feature extractor with sample texts."""
    
    print("\n" + "="*80)
    print("TESTING FEATURE EXTRACTOR")
    print("="*80)
    
    extractor = FeatureExtractor()
    
    # Test articles
    test_articles = [
        {
            "title": "Apple Reports Record Q1 Earnings",
            "text": "Apple Inc. announced record earnings for Q1 2024 on January 15, 2024. "
                   "CEO Tim Cook stated that iPhone sales surged 25% year-over-year, exceeding "
                   "analyst expectations. The stock jumped 10% to $180 per share, reaching an "
                   "all-time high. Revenue grew to $120B, beating Wall Street estimates."
        },
        {
            "title": "Tesla Stock Tumbles on Production Miss",
            "text": "Tesla shares plunged 15% on March 3, 2024, after the company reported "
                   "disappointing Q4 production numbers. CEO Elon Musk acknowledged supply chain "
                   "challenges in China. Deliveries fell 8% short of expectations, causing analysts "
                   "to downgrade the stock from Buy to Hold."
        }
    ]
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n{'='*80}")
        print(f"Article {i}: {article['title']}")
        print(f"{'='*80}")
        
        print(f"\nText:\n{article['text']}")
        
        # Extract features
        features = extractor.extract_all_features(article['text'])
        
        # Display results
        print(f"\n📊 EXTRACTED FEATURES:")
        
        print(f"\n1️⃣ Named Entities:")
        for entity_type, entities in features['entities'].items():
            if entities:
                print(f"   {entity_type}: {', '.join(entities)}")
        
        print(f"\n2️⃣ Financial Keywords:")
        for sentiment, keywords in features['financial_keywords'].items():
            if keywords:
                print(f"   {sentiment.capitalize()}: {', '.join(keywords)}")
        
        print(f"\n3️⃣ Numbers:")
        if features['numbers']:
            print(f"   {', '.join(features['numbers'])}")
        
        print(f"\n4️⃣ Percentages:")
        if features['percentages']:
            print(f"   {', '.join(features['percentages'])}")
        
        print(f"\n5️⃣ Dates:")
        if features['dates']:
            print(f"   {', '.join(features['dates'])}")
        
        print(f"\n📈 Summary Statistics:")
        for key, value in features['stats'].items():
            print(f"   {key}: {value}")
    
    print("\n✅ Feature extractor tests complete!")


if __name__ == "__main__":
    test_feature_extractor()