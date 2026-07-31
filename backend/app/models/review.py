from dataclasses import dataclass
from typing import List

@dataclass
class ReviewDataset:
    """
    Contains all the information obtained after processing reviews.
    
    Attributes:
        column_name: Name of the column containing reviews
        total_original: Total number of reviews before cleaning
        duplicates_removed: Number of duplicate reviews removed
        empty_removed: Number of empty/invalid reviews removed
        total_clean: Total number of clean reviews after processing
        reviews: List of cleaned review texts
    """
    
    column_name: str
    total_original: int
    duplicates_removed: int
    empty_removed: int
    total_clean: int
    reviews: List[str]