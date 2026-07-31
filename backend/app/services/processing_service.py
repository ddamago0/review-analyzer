from typing import List, Dict, Any, Optional
import logging

from app.models.review import ReviewDataset
from app.services.excel_service import ExcelService
from app.utils.validation import remove_duplicates

from app.analyzers.statistics_analyzer import StatisticsAnalyzer
from app.analyzers.word_frequency_analyzer import WordFrequencyAnalyzer

logger = logging.getLogger(__name__)

class ProcessingService:
    """
    Service responsible for processing multiple Excel files and combining review data.
    """

    @staticmethod
    def process_files(
        file_paths: List[str],
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process multiple Excel files and unify all reviews.
        
        Args:
            file_paths (List[str]): List of file paths to process
            limit (Optional[int]): Optional limit on number of reviews to return
            
        Returns:
            Dict[str, Any]: Processing results including dataset, statistics, and word frequency
        """
        logger.info(f"Processing {len(file_paths)} files")
        
        all_reviews = []
        total_original = 0
        total_duplicates = 0
        total_empty = 0
        detected_column = ""
        
        # Process each file
        for file_path in file_paths:
            try:
                dataset = ExcelService.read_excel(file_path)
                detected_column = dataset.column_name
                
                total_original += dataset.total_original
                total_duplicates += dataset.duplicates_removed
                total_empty += dataset.empty_removed
                
                all_reviews.extend(dataset.reviews)
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
                raise
                
        # Remove cross-file duplicates
        unique_reviews, duplicates_between_files = remove_duplicates(all_reviews)
        total_duplicates += duplicates_between_files
        
        logger.debug(f"Removed {duplicates_between_files} cross-file duplicates")
        
        # Apply limit if specified
        if limit is not None:
            unique_reviews = unique_reviews[:limit]
            logger.debug(f"Applied limit of {limit} reviews")
            
        # Perform analysis
        statistics = StatisticsAnalyzer.analyze(unique_reviews)
        word_frequency = WordFrequencyAnalyzer.analyze(unique_reviews, top=20)
        
        # Create final dataset
        dataset = ReviewDataset(
            column_name=detected_column,
            total_original=total_original,
            duplicates_removed=total_duplicates,
            empty_removed=total_empty,
            total_clean=len(unique_reviews),
            reviews=unique_reviews
        )
        
        response = {
            "dataset": dataset,
            "statistics": statistics,
            "word_frequency": word_frequency
        }
        
        logger.info(f"Processing complete. Total reviews: {len(unique_reviews)}")
        return response