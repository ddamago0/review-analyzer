from typing import List, Tuple
import logging

from app.utils.validation import validate_review_text

logger = logging.getLogger(__name__)

class CleaningService:
    """
    Service responsible for cleaning and normalizing review texts.
    """

    @staticmethod
    def clean_reviews(reviews: List[str]) -> Tuple[List[str], int, int]:
        """
        Clean and normalize a list of reviews.
        
        Args:
            reviews (List[str]): List of raw review texts
            
        Returns:
            Tuple[List[str], int, int]: (cleaned_reviews, duplicates_removed, empty_removed)
        """
        logger.debug(f"Cleaning {len(reviews)} reviews")
        
        cleaned_reviews = []
        duplicates_removed = 0
        empty_removed = 0
        seen = set()
        
        for review in reviews:
            try:
                # Handle None values
                if review is None:
                    empty_removed += 1
                    continue
                    
                # Validate and clean review text
                cleaned_review = validate_review_text(str(review))
                
                # Check for empty reviews
                if cleaned_review == "":
                    empty_removed += 1
                    continue
                    
                # Check for NaN-like strings
                if cleaned_review.lower() == "nan":
                    empty_removed += 1
                    continue
                    
                # Check for duplicates (case-insensitive)
                normalized = cleaned_review.lower()
                if normalized in seen:
                    duplicates_removed += 1
                    continue
                    
                seen.add(normalized)
                cleaned_reviews.append(cleaned_review)
                
            except ValueError as e:
                logger.warning(f"Skipping invalid review: {str(e)}")
                empty_removed += 1
                continue
                
        logger.debug(f"Cleaning complete: {len(cleaned_reviews)} valid reviews, "
                    f"{duplicates_removed} duplicates removed, {empty_removed} empty removed")
        
        return cleaned_reviews, duplicates_removed, empty_removed