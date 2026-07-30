from statistics import mean


class StatisticsAnalyzer:
    """
    Calcula estadísticas generales
    sobre las reseñas.
    """

    @staticmethod
    def analyze(reviews: list[str]):

        if not reviews:

            return {
                "total_reviews": 0,
                "average_length": 0,
                "shortest_review": 0,
                "longest_review": 0,
                "average_words": 0
            }

        lengths = [
            len(review)
            for review in reviews
        ]

        words = [
            len(review.split())
            for review in reviews
        ]

        return {

            "total_reviews": len(reviews),

            "average_length": round(
                mean(lengths),
                2
            ),

            "shortest_review": min(lengths),

            "longest_review": max(lengths),

            "average_words": round(
                mean(words),
                2
            )

        }