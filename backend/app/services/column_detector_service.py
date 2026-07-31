from typing import Optional, List
import re
import pandas as pd
import logging

from app.config.settings import POSSIBLE_COLUMNS

logger = logging.getLogger(__name__)

class ColumnDetectorService:
    """
    Service responsible for automatically detecting the column containing reviews.
    """

    @staticmethod
    def detect(df: pd.DataFrame) -> Optional[str]:
        """
        Detect the most likely review column in the DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame to analyze
            
        Returns:
            Optional[str]: Name of the detected column, or None if not found
        """
        logger.debug("Detecting column containing reviews...")
        
        best_column = None
        best_score = -1
        
        for column in df.columns:
            score = ColumnDetectorService.score_column(df, column)
            
            if score > best_score:
                best_score = score
                best_column = column
                
        logger.debug(f"Best column detected: {best_column} with score {best_score}")
        return best_column

    @staticmethod
    def score_column(df: pd.DataFrame, column: str) -> int:
        """
        Score a column based on how likely it contains reviews.
        
        Args:
            df (pd.DataFrame): DataFrame containing the column
            column (str): Name of the column to score
            
        Returns:
            int: Score representing likelihood of being a review column
        """
        score = 0
        name = str(column).strip().lower()
        
        # Score based on column name
        if name in POSSIBLE_COLUMNS:
            score += 100
        elif any(possible in name for possible in POSSIBLE_COLUMNS):
            score += 40
            
        # Analyze content
        values = (
            df[column]
            .dropna()
            .astype(str)
            .str.strip()
        )
        
        if values.empty:
            return score
            
        # Score based on average text length
        avg_length = values.str.len().mean()
        if avg_length > 20:
            score += 40
        elif avg_length > 10:
            score += 20
            
        # Score based on text content ratio
        text_cells = 0
        for value in values:
            if re.search(r"[a-zA-ZáéíóúñÁÉÍÓÚ]", value):
                text_cells += 1
                
        text_ratio = text_cells / len(values)
        score += int(text_ratio * 40)
        
        # Penalize numeric columns
        numeric = pd.to_numeric(
            values,
            errors="coerce"
        ).notna().sum()
        
        numeric_ratio = numeric / len(values)
        score -= int(numeric_ratio * 40)
        
        return score