import re


class CleaningService:
    """
    Servicio encargado de limpiar y normalizar las reseñas.
    """

    @staticmethod
    def clean_reviews(reviews):

        cleaned_reviews = []

        seen = set()

        duplicates_removed = 0
        empty_removed = 0

        for review in reviews:

            # Valor nulo
            if review is None:
                empty_removed += 1
                continue

            review = str(review)

            # Eliminar espacios
            review = review.strip()

            # Cadena vacía
            if review == "":
                empty_removed += 1
                continue

            # NaN convertido en texto
            if review.lower() == "nan":
                empty_removed += 1
                continue

            # Reducir espacios múltiples
            review = re.sub(r"\s+", " ", review)

            # Detectar duplicados ignorando mayúsculas
            normalized = review.lower()

            if normalized in seen:
                duplicates_removed += 1
                continue

            seen.add(normalized)

            cleaned_reviews.append(review)

        return (
            cleaned_reviews,
            duplicates_removed,
            empty_removed
        )