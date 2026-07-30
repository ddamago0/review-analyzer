import re
import unicodedata


class NormalizationService:
    """
    Servicio encargado de normalizar texto para comparar reseñas.
    No modifica el texto mostrado al usuario; únicamente genera una
    versión estandarizada para detectar duplicados.
    """

    @staticmethod
    def normalize(text: str) -> str:

        if text is None:
            return ""

        text = str(text)

        # minúsculas
        text = text.lower()

        # eliminar tildes
        text = "".join(
            c
            for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )

        # eliminar emojis y caracteres no ASCII
        text = text.encode(
            "ascii",
            "ignore"
        ).decode()

        # eliminar signos de puntuación
        text = re.sub(
            r"[^\w\s]",
            " ",
            text
        )

        # reducir espacios múltiples
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        # eliminar caracteres repetidos exagerados
        text = re.sub(
            r"(.)\1{2,}",
            r"\1",
            text
        )

        return text.strip()