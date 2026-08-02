# Review Analyzer

Plataforma para el procesamiento y análisis masivo de reseñas almacenadas en
archivos Excel. Incluye detección automática de la columna de reseñas,
limpieza de datos, análisis estadístico, frecuencia de palabras y un pipeline
de **optimización de tokens** basado en `o200k_base`.

## Features

- Carga de uno o varios archivos Excel (`.xlsx`, `.xls`)
- Carga de carpetas completas
- Detección automática de la columna de reseñas
- Limpieza automática de duplicados y reseñas vacías
- Estadísticas: total, promedio de caracteres/palabras, longitudes mínima y máxima
- Top 20 palabras más frecuentes
- Vista previa de reseñas
- Pipeline opcional `optimize_tokens`:
  - Tokenización con `o200k_base` (tiktoken)
  - Traducción español → inglés
  - Comparación de tokens originales vs traducidos
  - Proyección mensual (10,000 reseñas/día × 30 días)
  - Ahorro estimado a `$2.50 USD` por millón de tokens de entrada
  - Extracción estructurada `error_type` / `component`
- Análisis de una reseña individual a través de `/api/analyze`
- Exportación de resultados en JSON, CSV y Excel

## Endpoints

| Método | Ruta             | Descripción                                             |
|--------|------------------|---------------------------------------------------------|
| GET    | `/`              | Estado de la API                                        |
| POST   | `/api/upload`    | Subir archivos/carpetas Excel y procesarlos             |
| POST   | `/api/analyze`   | Análisis de tokens de una sola reseña                   |
| POST   | `/api/export/xlsx` | Exportar los resultados a un libro Excel              |

### Ejemplo `/api/analyze`

```json
POST /api/analyze
{
    "review": "La aplicación se bloquea cada vez que intento subir una foto de perfil desde mi galería del teléfono.",
    "optimize_tokens": true
}
```

Respuesta parcial:

```json
{
    "error_type": "crash",
    "component": "profile_picture_upload",
    "original_tokens": 21,
    "translated_tokens": 17,
    "token_difference": 4,
    "monthly_savings_usd": 3.0
}
```

## Instalación (local)

1. Crear y activar un entorno virtual:
```bash
cd backend
python -m venv venv
source venv/bin/activate
```

2. Instalar dependencias:
```bash
pip install -r backend/requirements.txt
```

3. Iniciar el backend:
```bash
cd backend
uvicorn app.main:app --reload
```

4. Abrir `frontend/index.html` en un navegador.

> La traducción online (Google Translate) requiere conexión a internet.
> Si no hay conexión, el sistema usa un traductor offline determinista.

## Instalación (Docker)

```bash
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost`

## Uso

1. Selecciona archivos Excel o una carpeta que los contenga.
2. Opcionalmente activa **"Reducir costos por tokens"** para ejecutar el
   pipeline de optimización de tokens.
3. Haz clic en **"Iniciar análisis"**.
4. Revisa el resumen, las visualizaciones y exporta los resultados.

También puedes pegar una reseña en el panel **"Análisis de tokens"** para
obtener la comparación de tokens, la proyección de ahorro y la extracción
estructurada `error_type` / `component`.

## Estructura del proyecto

```
.
├── backend/                  # Backend FastAPI
│   ├── app/
│   │   ├── api/              # Endpoints (upload, analyze, export)
│   │   ├── analyzers/        # Estadísticas y frecuencia de palabras
│   │   ├── config/           # Configuración y constantes
│   │   ├── core/             # Logging
│   │   ├── exceptions/       # Excepciones de dominio
│   │   ├── models/           # Modelos de datos
│   │   ├── services/         # Lógica de negocio
│   │   └── utils/            # Utilidades
│   └── requirements.txt
├── frontend/                 # Frontend HTML/CSS/JavaScript (vanilla)
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```

## Licencia

MIT
