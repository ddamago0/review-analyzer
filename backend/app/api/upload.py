from dataclasses import asdict
from pathlib import Path
import shutil
import uuid
from typing import List, Dict, Any

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile
)
import logging

from app.services.processing_service import ProcessingService
from app.config.settings import UPLOAD_FOLDER
from app.exceptions import ValidationError, InvalidFileError
from app.utils.validation import validate_file_path

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_excel(
    files: List[UploadFile] = File(...),
    limit: str = Form("")
):
    """
    Upload and process Excel files containing reviews.
    
    Args:
        files: List of uploaded Excel files
        limit: Optional limit on number of reviews to process
        
    Returns:
        Dictionary with processing results
        
    Raises:
        HTTPException: If validation fails or processing errors occur
    """
    
    logger.info(f"Received {len(files)} files for processing")
    
    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="No se recibieron archivos."
        )

    review_limit = None

    if limit.strip() != "":
        try:
            review_limit = int(limit)
            if review_limit <= 0:
                raise ValueError()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="La cantidad de reseñas debe ser un número mayor que cero."
            )

    saved_files = []

    try:
        for file in files:
            if not file.filename:
                continue

            if not file.filename.lower().endswith((".xlsx", ".xls")):
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} no es un archivo Excel."
                )

            unique_name = f"{uuid.uuid4()}_{file.filename}"
            file_path = UPLOAD_FOLDER / unique_name

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_files.append(str(file_path))

        logger.info(f"Files saved to {len(saved_files)} locations")
        
        result = ProcessingService.process_files(
            saved_files,
            review_limit
        )

        return {
            "success": True,
            "message": "Archivos procesados correctamente.",
            "files_processed": len(saved_files),
            "data": asdict(result["dataset"]),
            "statistics": result["statistics"],
            "word_frequency": result["word_frequency"]
        }

    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    finally:
        # Clean up uploaded files
        for file_path in saved_files:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.debug(f"Cleaned up temporary file: {file_path}")