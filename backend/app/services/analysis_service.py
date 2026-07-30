from app.services.excel_service import ExcelService
from app.services.file_service import FileService
from app.services.sampling_service import SamplingService
from app.services.statistics_service import StatisticsService


class AnalysisService:
    """
    Servicio principal encargado de coordinar
    todo el procesamiento de reseñas.
    """

    @staticmethod
    def process_excel(
        file_path: str,
        sample_size: int | None = None
    ) -> dict:

        dataset = ExcelService.read_excel(file_path)

        sampled_reviews = SamplingService.sample_reviews(
            reviews=dataset.reviews,
            sample_size=sample_size
        )

        statistics = StatisticsService.calculate(
            reviews=sampled_reviews,
            total_original=dataset.total_original,
            duplicates_removed=dataset.duplicates_removed
        )

        return {
            "processed_files": 1,
            "column_name": dataset.column_name,
            "statistics": statistics,
            "reviews": sampled_reviews
        }

    @staticmethod
    def process_multiple_files(
        files: list[str],
        sample_size: int | None = None
    ) -> dict:

        unique_reviews = set()

        total_original = 0
        duplicates_removed = 0

        column_name = None

        processed_files = 0

        for file in files:

            dataset = ExcelService.read_excel(file)

            processed_files += 1

            if column_name is None:
                column_name = dataset.column_name

            total_original += dataset.total_original
            duplicates_removed += dataset.duplicates_removed

            before = len(unique_reviews)

            unique_reviews.update(dataset.reviews)

            duplicates_removed += (
                len(dataset.reviews)
                - (len(unique_reviews) - before)
            )

        reviews = list(unique_reviews)

        sampled_reviews = SamplingService.sample_reviews(
            reviews=reviews,
            sample_size=sample_size
        )

        statistics = StatisticsService.calculate(
            reviews=sampled_reviews,
            total_original=total_original,
            duplicates_removed=duplicates_removed
        )

        return {
            "processed_files": processed_files,
            "column_name": column_name,
            "statistics": statistics,
            "reviews": sampled_reviews
        }

    @staticmethod
    def process_folder(
        folder: str,
        sample_size: int | None = None,
        recursive: bool = False
    ) -> dict:

        if recursive:
            files = FileService.get_excel_files_recursive(folder)
        else:
            files = FileService.get_excel_files(folder)

        if not files:
            raise ValueError(
                "No se encontraron archivos Excel."
            )

        return AnalysisService.process_multiple_files(
            files=[str(file) for file in files],
            sample_size=sample_size
        )