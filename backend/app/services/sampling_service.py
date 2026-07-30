import random


class SamplingService:
    """
    Servicio encargado de seleccionar una muestra de reseñas.
    """

    @staticmethod
    def sample_reviews(
        reviews: list[str],
        sample_size: int | None = None,
        random_seed: int = 42
    ) -> list[str]:
        """
        Devuelve una muestra aleatoria de las reseñas.

        sample_size = None -> devuelve todas.
        """

        total_reviews = len(reviews)

        if sample_size is None:
            return reviews

        if sample_size <= 0:
            raise ValueError(
                "La cantidad de reseñas debe ser mayor que cero."
            )

        if sample_size >= total_reviews:
            return reviews

        random.seed(random_seed)

        return random.sample(
            reviews,
            sample_size
        )