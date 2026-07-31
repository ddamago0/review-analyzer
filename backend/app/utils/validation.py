"""
Utility functions for the Review Analyzer application.
"""

import logging
from pathlib import Path
from typing import List, Set, Tuple
import re

from app.config.settings import MAX_REVIEW_LENGTH

logger = logging.getLogger(__name__)

def validate_file_path(file_path: str) -> Path:
    """
    Validate and return a Path object for the given file path.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Path: Validated Path object
        
    Raises:
        ValueError: If the path is invalid
    """
    path = Path(file_path)
    
    if not path.exists():
        raise ValueError(f"File does not exist: {file_path}")
        
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
        
    return path

def validate_review_text(review: str) -> str:
    """
    Validate and clean review text.
    
    Args:
        review (str): Raw review text
        
    Returns:
        str: Cleaned review text
        
    Raises:
        ValueError: If review text is invalid
    """
    if not isinstance(review, str):
        raise ValueError("Review must be a string")
        
    # Remove extra whitespace
    review = review.strip()
    
    # Check length
    if len(review) > MAX_REVIEW_LENGTH:
        raise ValueError(f"Review exceeds maximum length of {MAX_REVIEW_LENGTH} characters")
        
    # Check for NaN-like strings
    if review.lower() == "nan":
        raise ValueError("Review contains invalid value 'nan'")
        
    # Normalize whitespace
    review = re.sub(r"\s+", " ", review)
    
    return review

def remove_duplicates(reviews: List[str]) -> Tuple[List[str], int]:
    """
    Remove duplicate reviews (case-insensitive).
    
    Args:
        reviews (List[str]): List of review texts
        
    Returns:
        Tuple[List[str], int]: (unique_reviews, duplicates_removed)
    """
    seen: Set[str] = set()
    unique_reviews = []
    duplicates_removed = 0
    
    for review in reviews:
        normalized = review.lower()
        
        if normalized in seen:
            duplicates_removed += 1
            continue
            
        seen.add(normalized)
        unique_reviews.append(review)
        
    return unique_reviews, duplicates_removed