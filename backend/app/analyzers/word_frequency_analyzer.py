from collections import Counter
import re


class WordFrequencyAnalyzer:
    """
    Analiza la frecuencia de palabras
    presentes en las reseñas.
    """

    @staticmethod
    def analyze(
        reviews: list[str],
        top: int = 20
    ) -> list[dict]:

        counter = Counter()

        for review in reviews:

            words = re.findall(
                r"\b[\wáéíóúüñ]+\b",
                review.lower()
            )

            counter.update(words)

        result = []

        for word, count in counter.most_common(top):

            result.append(
                {
                    "word": word,
                    "count": count
                }
            )

        return result