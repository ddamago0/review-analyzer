from pathlib import Path

import pandas as pd

from app.models.review import ReviewDataset
from app.services.cleaning_service import CleaningService


POSSIBLE_COLUMNS = [
    "review",
    "reviews",
    "reseña",
    "reseñas",
    "comentario",
    "comentarios",
    "comment",
    "comments",
    "opinion",
    "opiniones",
    "texto",
    "text",
    "content"
]


class ExcelService:
    """
    Servicio encargado únicamente de leer archivos Excel.
    """

    @staticmethod
    def read_excel(file_path: str) -> ReviewDataset:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("El archivo no existe.")

        df = pd.read_excel(path)

        if df.empty:
            raise ValueError("El archivo está vacío.")

        review_column = ExcelService.detect_review_column(df)

        if review_column is None:
            raise ValueError(
                "No se encontró una columna de reseñas."
            )

        reviews = df[review_column].tolist()

        (
            cleaned_reviews,
            duplicates_removed,
            empty_removed
        ) = CleaningService.clean_reviews(reviews)

        return ReviewDataset(
            column_name=review_column,
            total_original=len(reviews),
            duplicates_removed=duplicates_removed,
            empty_removed=empty_removed,
            total_clean=len(cleaned_reviews),
            reviews=cleaned_reviews
        )

    @staticmethod
    def detect_review_column(df: pd.DataFrame):

        for column in df.columns:

            if str(column).strip().lower() in POSSIBLE_COLUMNS:
                return column

        for column in df.columns:

            name = str(column).strip().lower()

            for possible in POSSIBLE_COLUMNS:

                if possible in name:
                    return column

        return None