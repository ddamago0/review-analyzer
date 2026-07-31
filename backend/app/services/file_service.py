from pathlib import Path
from typing import List
import logging

from app.exceptions import InvalidFileError

logger = logging.getLogger(__name__)

class FileService:
    """
    Service responsible for file system operations.
    """

    VALID_EXTENSIONS = {".xlsx", ".xls"}

    @staticmethod
    def is_excel_file(path: Path) -> bool:
        """
        Check if a file is a valid Excel file.
        
        Args:
            path (Path): Path to the file
            
        Returns:
            bool: True if file is a valid Excel file
        """
        return (
            path.is_file()
            and path.suffix.lower() in FileService.VALID_EXTENSIONS
        )

    @staticmethod
    def get_excel_files(folder: str) -> List[Path]:
        """
        Get all Excel files from a folder (non-recursive).
        
        Args:
            folder (str): Path to the folder
            
        Returns:
            List[Path]: List of Excel file paths
            
        Raises:
            InvalidFileError: If folder is invalid
        """
        directory = Path(folder)
        
        if not directory.exists():
            raise InvalidFileError("La carpeta no existe.")
            
        if not directory.is_dir():
            raise InvalidFileError("La ruta indicada no es una carpeta.")
            
        excel_files = []
        for file in directory.iterdir():
            if FileService.is_excel_file(file):
                excel_files.append(file)
                
        excel_files.sort()
        logger.debug(f"Found {len(excel_files)} Excel files in {folder}")
        return excel_files

    @staticmethod
    def get_excel_files_recursive(folder: str) -> List[Path]:
        """
        Get all Excel files from a folder and subfolders.
        
        Args:
            folder (str): Path to the folder
            
        Returns:
            List[Path]: List of Excel file paths
            
        Raises:
            InvalidFileError: If folder is invalid
        """
        directory = Path(folder)
        
        if not directory.exists():
            raise InvalidFileError("La carpeta no existe.")
            
        if not directory.is_dir():
            raise InvalidFileError("La ruta indicada no es una carpeta.")
            
        excel_files = []
        for file in directory.rglob("*"):
            if FileService.is_excel_file(file):
                excel_files.append(file)
                
        excel_files.sort()
        logger.debug(f"Found {len(excel_files)} Excel files recursively in {folder}")
        return excel_files