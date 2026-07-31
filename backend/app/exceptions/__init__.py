"""
Core exceptions for the Review Analyzer application.
"""

class ReviewAnalyzerError(Exception):
    """Base exception for the Review Analyzer application."""
    pass

class InvalidFileError(ReviewAnalyzerError):
    """Raised when a file is invalid or cannot be processed."""
    pass

class ColumnDetectionError(ReviewAnalyzerError):
    """Raised when review column cannot be detected in Excel file."""
    pass

class ProcessingError(ReviewAnalyzerError):
    """Raised when processing fails."""
    pass

class ValidationError(ReviewAnalyzerError):
    """Raised when validation fails."""
    pass