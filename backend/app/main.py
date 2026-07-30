from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router


app = FastAPI(
    title="Review Analyzer API",
    version="1.0.0",
    description="Sistema para analizar reseñas de manera local y sin IA."
)

# Permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Más adelante lo limitaremos al dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(upload_router, prefix="/api")

# Ruta de prueba
@app.get("/")
def root():
    return {
        "message": "Review Analyzer API funcionando correctamente."
    }