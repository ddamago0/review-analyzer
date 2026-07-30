from dataclasses import dataclass


@dataclass
class ReviewDataset:
    """
    Contiene toda la información obtenida después
    del procesamiento de las reseñas.
    """

    column_name: str

    total_original: int

    duplicates_removed: int

    empty_removed: int

    total_clean: int

    reviews: list[str]