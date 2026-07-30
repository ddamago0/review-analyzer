from statistics import mean


class StatisticsService:
    """
    Calcula estadísticas generales de un conjunto de reseñas.
    """

    @staticmethod
    def calculate(
        reviews: list[str],
        total_original: int,
        duplicates_removed: int
    ) -> dict:

        if not reviews:
            return {
                "total_original": total_original,
                "total_clean": 0,
                "duplicates_removed": duplicates_removed,
                "duplicate_percentage": 0,
                "average_characters": 0,
                "average_words": 0,
                "longest_review": "",
                "shortest_review": ""
            }

        characters = [
            len(review)
            for review in reviews
        ]

        words = [
            len(review.split())
            for review in reviews
        ]

        duplicate_percentage = round(
            (duplicates_removed / total_original) * 100,
            2
        ) if total_original else 0

        return {
            "total_original": total_original,
            "total_clean": len(reviews),
            "duplicates_removed": duplicates_removed,
            "duplicate_percentage": duplicate_percentage,
            "average_characters": round(mean(characters), 2),
            "average_words": round(mean(words), 2),
            "longest_review": max(
                reviews,
                key=len
            ),
            "shortest_review": min(
                reviews,
                key=len
            )
        }