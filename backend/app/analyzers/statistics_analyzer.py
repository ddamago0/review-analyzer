from typing import List, Dict, Any
from statistics import mean
import logging

logger = logging.getLogger(__name__)

class StatisticsAnalyzer:
    """
    Service responsible for calculating general statistics about reviews.
    """

    @staticmethod
    def analyze(reviews: List[str]) -> Dict[str, Any]:
        """
        Calculate statistics for a list of reviews.
        
        Args:
            reviews (List[str]): List of review texts
            
        Returns:
            Dict[str, Any]: Dictionary containing statistics
        """
        logger.debug(f"Calculating statistics for {len(reviews)} reviews")
        
        if not reviews:
            return {
                "total_reviews": 0,
                "average_length": 0,
                "shortest_review": 0,
                "longest_review": 0,
                "average_words": 0
            }

        lengths = [len(review) for review in reviews]
        words = [len(review.split()) for review in reviews]

        result = {
            "total_reviews": len(reviews),
            "average_length": round(mean(lengths), 2),
            "shortest_review": min(lengths),
            "longest_review": max(lengths),
            "average_words": round(mean(words), 2)
        }
        
        logger.debug(f"Statistics calculated: {result}")
        return result