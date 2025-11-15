"""
Detect duplicate or near-duplicate news articles.
Uses multiple similarity metrics for robust detection.
"""

import re
import hashlib
from difflib import SequenceMatcher
import json # Added for potential logging/testing needs
import logging

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Detect duplicate articles using multiple similarity metrics."""
    
    def __init__(self, similarity_threshold=0.85, title_similarity_threshold=0.90):
        """
        Initialize duplicate detector.
        
        Args:
            similarity_threshold (float): Minimum similarity (0-1) for body/sequence.
            title_similarity_threshold (float): Minimum similarity (0-1) for titles.
        """
        self.similarity_threshold = similarity_threshold
        self.title_similarity_threshold = title_similarity_threshold 
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
        
        # Remove punctuation for better Jaccard similarity
        clean_text1 = re.sub(r'[^\w\s]', '', text1.lower())
        clean_text2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        # Convert to sets of words
        words1 = set(clean_text1.split())
        words2 = set(clean_text2.split())
        
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
            article1 (dict): First article
            article2 (dict): Second article
            
        Returns:
            tuple: (bool is_duplicate, float score, str reason)
        """
        # Prioritize cleaned_title/body if the source data has been cleaned already
        title1 = article1.get('cleaned_title', article1.get('title', ''))
        body1 = article1.get('cleaned_body', article1.get('body', ''))
        title2 = article2.get('cleaned_title', article2.get('title', ''))
        body2 = article2.get('cleaned_body', article2.get('body', ''))
        
        text1 = f"{title1} {body1}"
        text2 = f"{title2} {body2}"
        
        # Check exact text match (using the combined cleaned text)
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
        if title1 and title2:
            title_sim = self.title_similarity(title1, title2)
            
            # Use the instance variable threshold
            if title_sim > self.title_similarity_threshold:
                return True, title_sim, "Very similar titles"
        
        # Check body similarity using Jaccard
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
    
    # -----------------------------------------------------
    # 🛑 MISSING METHODS ADDED HERE (Fixes AttributeError) 🛑
    # -----------------------------------------------------

    def mark_duplicates(self, articles):
        """
        Identify duplicates within a list of articles and mark them.
        The first article found is kept (is_duplicate=False), subsequent matches
        are marked as duplicates of the first.

        Args:
            articles (list): List of article dictionaries.

        Returns:
            list: The list of articles, now marked with 'is_duplicate' and 'duplicate_of' fields.
        """
        # Maps unique article ID/hash to the *first* article object seen
        seen_articles_map = {} 
        
        for article in articles:
            # Initialize duplication flags
            article['is_duplicate'] = False
            article['duplicate_of'] = None
            article['similarity_score'] = 0.0

            # 1. Compute article's text hash
            title = article.get('cleaned_title', article.get('title', ''))
            body = article.get('cleaned_body', article.get('body', ''))
            text_to_hash = f"{title} {body}"
            current_hash = self.compute_text_hash(text_to_hash)
            
            # Use the article's existing ID or a generated hash as its unique ID
            unique_id = article.get('article_id') or current_hash

            # 2. Check against previously seen articles for fuzzy match
            is_dup = False
            best_match_id = None
            best_score = 0.0
            best_reason = None
            
            # Note: The fuzzy check is O(N^2) relative to the number of articles
            for seen_id, seen_article in seen_articles_map.items():
                is_dup, score, reason = self.is_duplicate(article, seen_article)
                
                if is_dup:
                    # Update if this is a better match or simply accept
                    if score > best_score:
                        best_score = score
                        best_match_id = seen_id
                        best_reason = reason
                    
                    if score == 1.0: # Break immediately for perfect matches
                        break
            
            # 3. Apply markings
            if best_match_id:
                article['is_duplicate'] = True
                article['duplicate_of'] = best_match_id
                article['similarity_score'] = best_score
                # logger.debug(f"Marked duplicate: {article.get('title', 'No Title')} (of {best_match_id})")
            
            # If it's a new unique article, add it to the map
            if not article['is_duplicate']:
                # The first time we see an article, its unique ID is stored
                seen_articles_map[unique_id] = article
                # logger.debug(f"Marked unique: {article.get('title', 'No Title')}")
        
        return articles


    def remove_duplicates(self, articles):
        """
        Marks duplicates and returns only the unique articles.
        
        Args:
            articles (list): List of article dictionaries.
            
        Returns:
            list: List containing only unique articles.
        """
        logger.info(f"Starting duplicate detection on {len(articles)} articles...")
        marked_articles = self.mark_duplicates(articles)
        unique_articles = [a for a in marked_articles if a['is_duplicate'] is False]
        
        num_duplicates = len(articles) - len(unique_articles)
        logger.info(f"✓ Found and removed {num_duplicates} duplicates. {len(unique_articles)} unique articles remaining.")

        return unique_articles


# Optional test function for local debugging
def test_duplicate_detector():
    detector = DuplicateDetector()
    
    article_a = {'article_id': 'A', 'title': 'Apple just bought Shazam for $400M', 'body': 'The deal closed today. Apple is expanding.', 'url': 'apple.com/shazam'}
    article_b = {'article_id': 'B', 'title': 'Apple just bought Shazam for $400M', 'body': 'The deal closed today. Apple is expanding.', 'url': 'apple.com/shazam'} # Exact match
    article_c = {'article_id': 'C', 'title': 'Apple buys Shazam for 400M', 'body': 'The deal closed today. Apple is expanding. They announced it.', 'url': 'apple.com/shazam?v=2'} # Fuzzy body/title
    article_d = {'article_id': 'D', 'title': 'Google is launching a new self-driving car', 'body': 'This is totally different news.', 'url': 'google.com/car'} # Different
    
    articles = [article_a, article_b, article_c, article_d]
    
    unique_articles = detector.remove_duplicates(articles)
    
    print("\n--- Test Results ---")
    print(f"Original Count: {len(articles)}")
    print(f"Unique Count: {len(unique_articles)}")
    print("--------------------")
    
    for article in articles:
        print(f"ID: {article['article_id']}, Is Dup: {article.get('is_duplicate')}, Dup Of: {article.get('duplicate_of')}, Score: {article.get('similarity_score')}")

if __name__ == "__main__":
    test_duplicate_detector()