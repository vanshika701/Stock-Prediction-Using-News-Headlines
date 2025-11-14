# preprocessor/duplicate_detector.py
"""
Detect duplicate or near-duplicate news articles.
Uses multiple similarity metrics for robust detection.
"""

import re
import hashlib
from difflib import SequenceMatcher


class DuplicateDetector:
    """Detect duplicate articles using multiple similarity metrics."""
    
    def __init__(self, similarity_threshold=0.85):
        """
        Initialize duplicate detector.
        
        Args:
            similarity_threshold (float): Minimum similarity (0-1) to consider duplicate
        """
        self.similarity_threshold = similarity_threshold
        self.seen_articles = {}  # hash -> article_id mapping
    
    def compute_text_hash(self, text):
        """
        Compute MD5 hash of text (for exact duplicates).
        
        Args:
            text (str): Text to hash
            
        Returns:
            str: MD5 hash
        """
        if not text:
            return None
        
        # Normalize text before hashing
        normalized = text.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def compute_url_hash(self, url):
        """
        Compute hash of URL (for same article from different sources).
        
        Args:
            url (str): Article URL
            
        Returns:
            str: MD5 hash of URL
        """
        if not url:
            return None
        
        # Remove protocol and www
        url = re.sub(r'https?://(www\.)?', '', url)
        url = url.lower().strip()
        
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def jaccard_similarity(self, text1, text2):
        """
        Calculate Jaccard similarity between two texts.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # Convert to sets of words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    
    def sequence_similarity(self, text1, text2):
        """
        Calculate sequence similarity using SequenceMatcher.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def title_similarity(self, title1, title2):
        """
        Calculate title similarity (more strict than body).
        
        Args:
            title1 (str): First title
            title2 (str): Second title
            
        Returns:
            float: Similarity score (0-1)
        """
        if not title1 or not title2:
            return 0.0
        
        # Titles should be very similar to be duplicates
        return self.sequence_similarity(title1, title2)
    
    def is_duplicate(self, article1, article2):
        """
        Check if two articles are duplicates using multiple metrics.
        
        Args:
            article1 (dict): First article with 'title', 'body', 'url'
            article2 (dict): Second article
            
        Returns:
            tuple: (is_duplicate (bool), similarity_score (float), reason (str))
        """
        # Check exact text match
        text1 = f"{article1.get('title', '')} {article1.get('body', '')}"
        text2 = f"{article2.get('title', '')} {article2.get('body', '')}"
        
        hash1 = self.compute_text_hash(text1)
        hash2 = self.compute_text_hash(text2)
        
        if hash1 and hash2 and hash1 == hash2:
            return True, 1.0, "Exact text match"
        
        # Check URL similarity
        url1 = article1.get('url', '')
        url2 = article2.get('url', '')
        
        if url1 and url2:
            url_hash1 = self.compute_url_hash(url1)
            url_hash2 = self.compute_url_hash(url2)
            
            if url_hash1 == url_hash2:
                return True, 1.0, "Same URL"
        
        # Check title similarity
        title1 = article1.get('title', '')
        title2 = article2.get('title', '')
        
        if title1 and title2:
            title_sim = self.title_similarity(title1, title2)
            
            # If titles are >90% similar, likely duplicate
            if title_sim > 0.90:
                return True, title_sim, "Very similar titles"
        
        # Check body similarity using Jaccard
        body1 = article1.get('body', '')
        body2 = article2.get('body', '')
        
        if body1 and body2:
            jaccard_sim = self.jaccard_similarity(body1, body2)
            
            if jaccard_sim >= self.similarity_threshold:
                return True, jaccard_sim, f"Similar content (Jaccard: {jaccard_sim:.2f})"
            
            # Also check sequence similarity
            seq_sim = self.sequence_similarity(body1, body2)
            
            if seq_sim >= self.similarity_threshold:
                return True, seq_sim, f"Similar content (Sequence: {seq_sim:.2f})"
        
        # Not a duplicate
        return False, 0.0, "Different articles"
    
    def mark_duplicates(self, articles):
        """
        Mark duplicate articles in a list.
        
        Args:
            articles (list): List of article dictionaries
            
        Returns:
            list: Articles with 'is_duplicate' flag and 'duplicate_of' field
        """
        print(f"\n🔍 Checking {len(articles)} articles for duplicates...")
        
        marked_articles = []
        duplicate_count = 0
        
        for i, article in enumerate(articles):
            # Add fields for duplicate tracking
            article['is_duplicate'] = False
            article['duplicate_of'] = None
            article['similarity_score'] = 0.0
            
            # Compare with all previous articles
            for j, prev_article in enumerate(marked_articles):
                # Skip if previous article is already a duplicate
                if prev_article.get('is_duplicate'):
                    continue
                
                # Check similarity
                is_dup, sim_score, reason = self.is_duplicate(article, prev_article)
                
                if is_dup:
                    article['is_duplicate'] = True
                    article['duplicate_of'] = prev_article.get('article_id', j)
                    article['similarity_score'] = sim_score
                    article['duplicate_reason'] = reason
                    duplicate_count += 1
                    
                    print(f"   Duplicate found: Article {i+1} is duplicate of Article {j+1}")
                    print(f"      Reason: {reason}")
                    break
            
            marked_articles.append(article)
        
        print(f"✓ Found {duplicate_count} duplicates out of {len(articles)} articles")
        print(f"✓ Duplicate rate: {duplicate_count/len(articles)*100:.1f}%")
        
        return marked_articles
    
    def remove_duplicates(self, articles):
        """
        Remove duplicate articles from list.
        
        Args:
            articles (list): List of articles
            
        Returns:
            list: Unique articles only
        """
        marked = self.mark_duplicates(articles)
        unique = [a for a in marked if not a.get('is_duplicate', False)]
        
        print(f"✓ Kept {len(unique)} unique articles (removed {len(articles) - len(unique)})")
        
        return unique


def test_duplicate_detector():
    """Test the duplicate detector with sample articles."""
    
    print("\n" + "="*80)
    print("TESTING DUPLICATE DETECTOR")
    print("="*80)
    
    detector = DuplicateDetector(similarity_threshold=0.85)
    
    # Test articles
    articles = [
        {
            "article_id": "1",
            "title": "Apple stock surges 5% on strong iPhone sales",
            "body": "Apple Inc. reported record iPhone sales today, sending the stock up 5%.",
            "url": "https://example.com/article1"
        },
        {
            "article_id": "2",
            "title": "Apple stock surges 5% on strong iPhone sales",
            "body": "Apple Inc. reported record iPhone sales today, sending the stock up 5%.",
            "url": "https://example.com/article1"
        },
        {
            "article_id": "3",
            "title": "AAPL stock rises on iPhone sales",
            "body": "Apple reported strong iPhone demand, boosting shares by 5 percent.",
            "url": "https://different.com/article3"
        },
        {
            "article_id": "4",
            "title": "Tesla announces new model",
            "body": "Tesla Inc. unveiled a new electric vehicle model today.",
            "url": "https://example.com/tesla"
        }
    ]
    
    print("\n📰 Test Articles:")
    for article in articles:
        print(f"   {article['article_id']}: {article['title']}")
    
    # Mark duplicates
    marked = detector.mark_duplicates(articles)
    
    print("\n📊 Results:")
    for article in marked:
        status = "DUPLICATE" if article['is_duplicate'] else "UNIQUE"
        print(f"\n   Article {article['article_id']}: {status}")
        print(f"      Title: {article['title']}")
        
        if article['is_duplicate']:
            print(f"      Duplicate of: {article['duplicate_of']}")
            print(f"      Similarity: {article['similarity_score']:.2%}")
            print(f"      Reason: {article['duplicate_reason']}")
    
    # Remove duplicates
    unique = detector.remove_duplicates(articles)
    
    print("\n✅ Final unique articles:")
    for article in unique:
        print(f"   {article['article_id']}: {article['title']}")


if __name__ == "__main__":
    test_duplicate_detector()
    print("\n✅ Duplicate detector tests complete!")