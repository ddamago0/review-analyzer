from fastapi import APIRouter, UploadFile, File
import pandas as pd
from io import BytesIO

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Leer el archivo enviado
    contenido = await file.read()

    # Abrir el Excel con pandas
    df = pd.read_excel(BytesIO(contenido))

    # Lista de posibles nombres para la columna de reseñas
    posibles_columnas = [
        "reseña",
        "review",
        "reviews",
        "comentario",
        "comentarios",
        "feedback"
    ]

    # Buscar automáticamente la columna
    columna_resena = None

    for columna in df.columns:
        if columna.strip().lower() in posibles_columnas:
            columna_resena = columna
            break

    # Si no existe la columna, devolver un error
    if columna_resena is None:
        return {
            "success": False,
            "message": "No se encontró una columna de reseñas.",
            "columns": df.columns.tolist()
        }

    # Contar reseñas válidas
    reseñas_validas = df[columna_resena].dropna()

    return {
        "success": True,
        "filename": file.filename,
        "rows": len(df),
        "columns": df.columns.tolist(),
        "review_column": columna_resena,
        "valid_reviews": len(reseñas_validas),
        "empty_reviews": len(df) - len(reseñas_validas)
    }