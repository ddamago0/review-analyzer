from pathlib import Path


class FileService:
    """
    Servicio encargado de localizar archivos Excel.
    """

    VALID_EXTENSIONS = {
        ".xlsx",
        ".xls"
    }

    @staticmethod
    def is_excel_file(path: Path) -> bool:
        """
        Verifica si un archivo es un Excel válido.
        """

        return (
            path.is_file()
            and path.suffix.lower() in FileService.VALID_EXTENSIONS
        )

    @staticmethod
    def get_excel_files(folder: str) -> list[Path]:
        """
        Devuelve todos los archivos Excel de una carpeta.
        No busca en subcarpetas.
        """

        directory = Path(folder)

        if not directory.exists():
            raise FileNotFoundError(
                "La carpeta no existe."
            )

        if not directory.is_dir():
            raise ValueError(
                "La ruta indicada no es una carpeta."
            )

        excel_files = []

        for file in directory.iterdir():

            if FileService.is_excel_file(file):
                excel_files.append(file)

        excel_files.sort()

        return excel_files

    @staticmethod
    def get_excel_files_recursive(folder: str) -> list[Path]:
        """
        Busca archivos Excel incluyendo subcarpetas.
        """

        directory = Path(folder)

        if not directory.exists():
            raise FileNotFoundError(
                "La carpeta no existe."
            )

        if not directory.is_dir():
            raise ValueError(
                "La ruta indicada no es una carpeta."
            )

        excel_files = []

        for file in directory.rglob("*"):

            if FileService.is_excel_file(file):
                excel_files.append(file)

        excel_files.sort()

        return excel_files