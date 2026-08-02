from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

from app.services.analyze_service import AnalyzeService

logger = logging.getLogger(__name__)

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """
    Request body for the token optimization analysis.
    """
    review: str = Field(
        ...,
        min_length=1,
        description="Review text (Spanish) to analyze"
    )
    optimize_tokens: bool = Field(
        True,
        description="Whether to run the translation/token optimization pipeline"
    )


class AnalyzeResponse(BaseModel):
    """
    Response model for a single-review token analysis.
    """
    success: bool
    message: str
    optimize_tokens: bool
    analysis: dict


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_review(request: AnalyzeRequest):
    """
    Analyze a single review using the token optimization pipeline.

    Steps:
    1. Tokenize the original Spanish text with o200k_base
    2. Translate the text into English
    3. Tokenize the translated English text
    4. Compute the token difference
    5. Project monthly savings (10,000 reviews/day, 30 days, $2.50/M tokens)
    6. Extract structured error info (error_type / component)

    Example payload:
    {
        "review": "La aplicación se bloquea cada vez que intento subir una foto de perfil desde mi galería del teléfono.",
        "optimize_tokens": true
    }
    """
    logger.info(f"Analyzing review ({len(request.review)} chars)")

    if not request.optimize_tokens:
        return AnalyzeResponse(
            success=True,
            message="Análisis desactivado: no se realizó optimización de tokens.",
            optimize_tokens=False,
            analysis={},
        )

    try:
        analysis = AnalyzeService.analyze_review(request.review)
    except Exception as e:
        logger.error(f"Error analyzing review: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar la reseña: {str(e)}"
        )

    return AnalyzeResponse(
        success=True,
        message="Análisis de tokens completado correctamente.",
        optimize_tokens=True,
        analysis=analysis,
    )
