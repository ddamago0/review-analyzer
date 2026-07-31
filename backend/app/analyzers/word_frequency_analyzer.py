from typing import List, Dict, Any
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)

class WordFrequencyAnalyzer:
    """
    Service responsible for analyzing word frequency in reviews.
    """

    @staticmethod
    def analyze(
        reviews: List[str],
        top: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Analyze word frequency in reviews.
        
        Args:
            reviews (List[str]): List of review texts
            top (int): Number of top words to return
            
        Returns:
            List[Dict[str, Any]]: List of word-frequency pairs
        """
        logger.debug(f"Analyzing word frequency for {len(reviews)} reviews")
        
        counter = Counter()
        
        for review in reviews:
            words = re.findall(r"\b[\wáéíóúüñ]+\b", review.lower())
            counter.update(words)
            
        result = []
        for word, count in counter.most_common(top):
            result.append({
                "word": word,
                "count": count
            })
            
        logger.debug(f"Word frequency analysis complete. Top {len(result)} words found.")
        return result