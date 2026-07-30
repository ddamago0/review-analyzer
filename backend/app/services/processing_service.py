from app.models.review import ReviewDataset
from app.services.excel_service import ExcelService

from app.analyzers.statistics_analyzer import StatisticsAnalyzer
from app.analyzers.word_frequency_analyzer import WordFrequencyAnalyzer


class ProcessingService:
    """
    Procesa uno o varios archivos Excel y unifica
    todas las reseñas eliminando duplicados globales.
    """

    @staticmethod
    def process_files(
        file_paths: list[str],
        limit: int | None = None
    ) -> dict:

        all_reviews = []

        total_original = 0
        total_duplicates = 0
        total_empty = 0

        detected_column = ""

        for file_path in file_paths:

            dataset = ExcelService.read_excel(file_path)

            detected_column = dataset.column_name

            total_original += dataset.total_original
            total_duplicates += dataset.duplicates_removed
            total_empty += dataset.empty_removed

            all_reviews.extend(dataset.reviews)

        unique_reviews = []
        seen = set()

        duplicates_between_files = 0

        for review in all_reviews:

            key = review.lower()

            if key in seen:
                duplicates_between_files += 1
                continue

            seen.add(key)
            unique_reviews.append(review)

        total_duplicates += duplicates_between_files

        # Aplicar límite
        if limit is not None:
            unique_reviews = unique_reviews[:limit]

        # Estadísticas
        statistics = StatisticsAnalyzer.analyze(
            unique_reviews
        )

        # Frecuencia de palabras
        word_frequency = WordFrequencyAnalyzer.analyze(
            unique_reviews,
            top=20
        )

        # Dataset final
        dataset = ReviewDataset(
            column_name=detected_column,
            total_original=total_original,
            duplicates_removed=total_duplicates,
            empty_removed=total_empty,
            total_clean=len(unique_reviews),
            reviews=unique_reviews
        )

        response = {
            "dataset": dataset,
            "statistics": statistics,
            "word_frequency": word_frequency
        }

        print("=" * 60)
        print("PROCESSING SERVICE")
        print("Response keys:", response.keys())
        print("Word Frequency items:", len(word_frequency))
        print("=" * 60)

        return response