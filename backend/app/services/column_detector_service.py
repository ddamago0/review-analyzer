import re

import pandas as pd


POSSIBLE_COLUMNS = [
    "review",
    "reviews",
    "reseña",
    "reseñas",
    "comentario",
    "comentarios",
    "comment",
    "comments",
    "feedback",
    "opinion",
    "opiniones",
    "texto",
    "text",
    "content",
    "mensaje",
    "observacion",
    "observaciones"
]


class ColumnDetectorService:
    """
    Detecta automáticamente la columna que
    probablemente contiene las reseñas.
    """

    @staticmethod
    def detect(df: pd.DataFrame):

        best_column = None
        best_score = -1

        for column in df.columns:

            score = ColumnDetectorService.score_column(
                df,
                column
            )

            if score > best_score:
                best_score = score
                best_column = column

        return best_column

    @staticmethod
    def score_column(df: pd.DataFrame, column):

        score = 0

        name = str(column).strip().lower()

        # --------------------------
        # Nombre de la columna
        # --------------------------

        if name in POSSIBLE_COLUMNS:
            score += 100

        for possible in POSSIBLE_COLUMNS:

            if possible in name:
                score += 40

        # --------------------------
        # Analizar contenido
        # --------------------------

        values = (
            df[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        if values.empty:
            return score

        avg_length = values.str.len().mean()

        if avg_length > 20:
            score += 40

        elif avg_length > 10:
            score += 20

        # porcentaje de texto

        text_cells = 0

        for value in values:

            if re.search(r"[a-zA-ZáéíóúñÁÉÍÓÚ]", value):
                text_cells += 1

        text_ratio = text_cells / len(values)

        score += int(text_ratio * 40)

        # penalizar columnas numéricas

        numeric = pd.to_numeric(
            values,
            errors="coerce"
        ).notna().sum()

        numeric_ratio = numeric / len(values)

        score -= int(numeric_ratio * 40)

        return score