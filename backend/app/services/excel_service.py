from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import logging

from app.models.review import ReviewDataset
from app.services.cleaning_service import CleaningService
from app.config.settings import POSSIBLE_COLUMNS
from app.exceptions import ColumnDetectionError, InvalidFileError

logger = logging.getLogger(__name__)

class ExcelService:
    """
    Service responsible for reading and processing Excel files.
    """

    @staticmethod
    def read_excel(file_path: str) -> ReviewDataset:
        """
        Read an Excel file and extract review data.
        
        Args:
            file_path (str): Path to the Excel file
            
        Returns:
            ReviewDataset: Dataset containing review information
            
        Raises:
            InvalidFileError: If file is invalid or cannot be read
            ColumnDetectionError: If review column cannot be detected
        """
        logger.debug(f"Reading Excel file: {file_path}")
        
        path = Path(file_path)
        
        if not path.exists():
            raise InvalidFileError("El archivo no existe.")
            
        try:
            df = pd.read_excel(path)
        except Exception as e:
            raise InvalidFileError(f"Error reading Excel file: {str(e)}")
            
        if df.empty:
            raise InvalidFileError("El archivo está vacío.")
            
        review_column = ExcelService.detect_review_column(df)
        
        if review_column is None:
            raise ColumnDetectionError(
                "No se encontró una columna de reseñas."
            )
            
        logger.debug(f"Detected review column: {review_column}")
        
        reviews = df[review_column].tolist()
        
        cleaned_reviews, duplicates_removed, empty_removed = CleaningService.clean_reviews(reviews)
        
        dataset = ReviewDataset(
            column_name=review_column,
            total_original=len(reviews),
            duplicates_removed=duplicates_removed,
            empty_removed=empty_removed,
            total_clean=len(cleaned_reviews),
            reviews=cleaned_reviews
        )
        
        logger.debug(f"Processed dataset: {dataset}")
        return dataset

    @staticmethod
    def detect_review_column(df: pd.DataFrame) -> Optional[str]:
        """
        Detect the column that likely contains reviews.
        
        Args:
            df (pd.DataFrame): DataFrame to analyze
            
        Returns:
            Optional[str]: Name of the review column, or None if not found
        """
        logger.debug("Detecting review column...")
        
        # First check for exact matches
        for column in df.columns:
            if str(column).strip().lower() in POSSIBLE_COLUMNS:
                return column
                
        # Then check for partial matches
        for column in df.columns:
            name = str(column).strip().lower()
            for possible in POSSIBLE_COLUMNS:
                if possible in name:
                    return column
                    
        return None