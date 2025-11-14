# preprocess_pipeline.py
"""
Complete preprocessing pipeline for financial news articles.
Integrates all preprocessing steps: cleaning, tokenization, lemmatization, feature extraction.
"""

import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocessor.text_cleaner import TextCleaner
from preprocessor.duplicate_detector import DuplicateDetector
from preprocessor.tokenizer import Tokenizer
from preprocessor.stop_words import StopWordsRemover
from preprocessor.lemmatizer import Lemmatizer
from preprocessor.feature_extractor import FeatureExtractor


class PreprocessingPipeline:
    """Complete preprocessing pipeline for news articles."""
    
    def __init__(self):
        """Initialize all preprocessing components."""
        
        print("\n" + "="*80)
        print("INITIALIZING PREPROCESSING PIPELINE")
        print("="*80)
        
        print("\n🔧 Loading components...")
        
        self.text_cleaner = TextCleaner()
        print("   ✓ Text cleaner loaded")
        
        self.duplicate_detector = DuplicateDetector(similarity_threshold=0.85)
        print("   ✓ Duplicate detector loaded")
        
        self.tokenizer = Tokenizer()
        print("   ✓ Tokenizer loaded")
        
        self.stopwords_remover = StopWordsRemover()
        print("   ✓ Stop words remover loaded")
        
        self.lemmatizer = Lemmatizer()
        print("   ✓ Lemmatizer loaded")
        
        self.feature_extractor = FeatureExtractor()
        print("   ✓ Feature extractor loaded")
        
        print("\n✅ All components initialized!")
    
    def preprocess_article(self, article):
        """
        Apply complete preprocessing to a single article.
        
        Args:
            article (dict): Article with 'title' and 'body'
            
        Returns:
            dict: Preprocessed article with all features
        """
        # Original text
        original_title = article.get('title', '')
        original_body = article.get('body', '')
        full_text = f"{original_title}. {original_body}"
        
        # Step 1: Clean text
        cleaned_title = self.text_cleaner.clean(original_title)
        cleaned_body = self.text_cleaner.clean(original_body)
        cleaned_text = f"{cleaned_title}. {cleaned_body}"
        
        # Step 2: Tokenize
        title_tokens = self.tokenizer.tokenize_words(cleaned_title)
        body_tokens = self.tokenizer.tokenize_words(cleaned_body)
        all_tokens = title_tokens + body_tokens
        
        # Step 3: Remove stop words
        filtered_tokens = self.stopwords_remover.remove(all_tokens)
        
        # Step 4: Lemmatize
        lemmatized_tokens = self.lemmatizer.lemmatize_tokens(filtered_tokens)
        
        # Step 5: Extract features
        features = self.feature_extractor.extract_all_features(full_text, lemmatized_tokens)
        
        # Step 6: Get text statistics
        text_stats = self.tokenizer.count_tokens(cleaned_text)
        
        # Compile preprocessed article
        preprocessed = {
            # Original data
            'original_title': original_title,
            'original_body': original_body,
            
            # Cleaned data
            'cleaned_title': cleaned_title,
            'cleaned_body': cleaned_body,
            'cleaned_text': cleaned_text,
            
            # Tokens
            'tokens': {
                'original': all_tokens,
                'filtered': filtered_tokens,
                'lemmatized': lemmatized_tokens
            },
            
            # Features
            'features': features,
            
            # Statistics
            'stats': text_stats,
            
            # Metadata
            'processed_at': datetime.now().isoformat(),
            'preprocessing_version': '1.0'
        }
        
        # Preserve other fields from original article
        for key, value in article.items():
            if key not in preprocessed:
                preprocessed[key] = value
        
        return preprocessed
    
    def preprocess_articles(self, articles, remove_duplicates=True):
        """
        Preprocess multiple articles.
        
        Args:
            articles (list): List of articles
            remove_duplicates (bool): Whether to remove duplicates
            
        Returns:
            list: Preprocessed articles
        """
        print(f"\n{'='*80}")
        print(f"PREPROCESSING {len(articles)} ARTICLES")
        print(f"{'='*80}")
        
        # Step 1: Remove duplicates if requested
        if remove_duplicates:
            print("\n1️⃣ Removing duplicates...")
            articles = self.duplicate_detector.remove_duplicates(articles)
        
        # Step 2: Preprocess each article
        print(f"\n2️⃣ Preprocessing {len(articles)} articles...")
        
        preprocessed_articles = []
        for i, article in enumerate(articles):
            if (i + 1) % 50 == 0:
                print(f"   Processed {i + 1}/{len(articles)} articles...")
            
            try:
                preprocessed = self.preprocess_article(article)
                preprocessed_articles.append(preprocessed)
            except Exception as e:
                print(f"   ⚠️  Error processing article {i+1}: {e}")
                continue
        
        print(f"   ✓ Preprocessing complete!")
        
        return preprocessed_articles
    
    def process_and_save(self, input_file, output_file, remove_duplicates=True):
        """
        Load articles, preprocess, and save to file.
        
        Args:
            input_file (str): Path to input JSON file
            output_file (str): Path to output JSON file
            remove_duplicates (bool): Whether to remove duplicates
        """
        print(f"\n{'='*80}")
        print(f"PROCESSING ARTICLES FROM FILE")
        print(f"{'='*80}")
        
        # Load articles
        print(f"\n📂 Loading articles from: {input_file}")
        
        if not os.path.exists(input_file):
            print(f"❌ Error: File not found: {input_file}")
            return
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different data formats
        if isinstance(data, dict):
            # Format: {ticker: [articles]}
            all_articles = []
            for ticker, articles in data.items():
                for article in articles:
                    article['ticker'] = ticker
                    all_articles.append(article)
            articles = all_articles
        elif isinstance(data, list):
            # Format: [articles]
            articles = data
        else:
            print(f"❌ Error: Unexpected data format")
            return
        
        print(f"✓ Loaded {len(articles)} articles")
        
        # Preprocess
        preprocessed = self.preprocess_articles(articles, remove_duplicates=remove_duplicates)
        
        # Save
        print(f"\n💾 Saving preprocessed articles to: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(preprocessed, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(preprocessed)} preprocessed articles")
        
        # Print summary
        print(f"\n{'='*80}")
        print("PREPROCESSING SUMMARY")
        print(f"{'='*80}")
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        print(f"Articles processed: {len(preprocessed)}")
        print(f"Duplicates removed: {len(articles) - len(preprocessed)}")
        print(f"{'='*80}")


def test_pipeline():
    """Test the complete preprocessing pipeline."""
    
    print("\n" + "="*80)
    print("TESTING PREPROCESSING PIPELINE")
    print("="*80)
    
    # Initialize pipeline
    pipeline = PreprocessingPipeline()
    
    # Test article
    test_article = {
        "article_id": "test_1",
        "title": "Apple Inc. Reports Record Q1 Earnings",
        "body": "Apple announced record earnings today. The stock surged 10% after beating analyst expectations. "
               "CEO Tim Cook stated that iPhone sales were up 25% year-over-year. Revenue reached $120 billion, "
               "exceeding Wall Street estimates. The company also announced a new stock buyback program.",
        "url": "https://example.com/article",
        "source": "TechNews",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    print("\n📰 Original Article:")
    print(f"   Title: {test_article['title']}")
    print(f"   Body: {test_article['body'][:100]}...")
    
    # Preprocess
    print("\n🔄 Preprocessing...")
    preprocessed = pipeline.preprocess_article(test_article)
    
    # Display results
    print("\n✅ Preprocessing Complete!")
    
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    
    print(f"\n1️⃣ Cleaned Text:")
    print(f"   {preprocessed['cleaned_text'][:150]}...")
    
    print(f"\n2️⃣ Tokens (first 15):")
    print(f"   Original: {', '.join(preprocessed['tokens']['original'][:15])}")
    print(f"   Filtered: {', '.join(preprocessed['tokens']['filtered'][:15])}")
    print(f"   Lemmatized: {', '.join(preprocessed['tokens']['lemmatized'][:15])}")
    
    print(f"\n3️⃣ Named Entities:")
    for entity_type, entities in preprocessed['features']['entities'].items():
        if entities:
            print(f"   {entity_type}: {', '.join(entities)}")
    
    print(f"\n4️⃣ Financial Keywords:")
    for sentiment, keywords in preprocessed['features']['financial_keywords'].items():
        if keywords:
            print(f"   {sentiment.capitalize()}: {', '.join(keywords)}")
    
    print(f"\n5️⃣ Numbers & Percentages:")
    print(f"   Numbers: {', '.join(preprocessed['features']['numbers'])}")
    print(f"   Percentages: {', '.join(preprocessed['features']['percentages'])}")
    
    print(f"\n6️⃣ Statistics:")
    for key, value in preprocessed['stats'].items():
        print(f"   {key}: {value}")
    
    print(f"\n{'='*80}")
    print("✅ Pipeline test complete!")
    print(f"{'='*80}")


if __name__ == "__main__":
    # Test the pipeline
    test_pipeline()
    
    # Process actual articles if they exist
    input_file = "news_with_tickers.json"
    output_file = "preprocessed_articles.json"
    
    if os.path.exists(input_file):
        print(f"\n{'='*80}")
        print("PROCESSING ACTUAL ARTICLES")
        print(f"{'='*80}")
        
        pipeline = PreprocessingPipeline()
        pipeline.process_and_save(input_file, output_file, remove_duplicates=True)
    else:
        print(f"\n⚠️  Note: {input_file} not found. Run the scrapers first.")
        print("   To process articles: python preprocess_pipeline.py")