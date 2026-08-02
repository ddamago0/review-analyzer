"""
Configuration module for the Review Analyzer application.
Handles all application settings and constants.
"""

from pathlib import Path

# Application settings
APP_NAME = "Review Analyzer"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Sistema para analizar reseñas de manera local y sin IA."

# File settings
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Processing settings
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_REVIEW_LENGTH = 10000  # Characters
MAX_REVIEW_COUNT = 100000  # Reviews

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = "app.log"

# Excel settings
POSSIBLE_COLUMNS = [
    "review",
    "reviews",
    "reseña",
    "reseñas",
    "comentario",
    "comentarios",
    "comment",
    "comments",
    "feedback",
    "opinion",
    "opiniones",
    "texto",
    "text",
    "content",
    "mensaje",
    "observacion",
    "observaciones"
]

# Token encoding (OpenAI o200k_base)
TOKEN_ENCODING = "o200k_base"

# Translation settings
TRANSLATION_SOURCE_LANG = "es"
TRANSLATION_TARGET_LANG = "en"

# Number of reviews used to estimate token reduction during batch processing.
# Translating every single review through an external service is impractical
# at scale, so a representative sample is used and extrapolated.
TRANSLATION_SAMPLE_SIZE = 50

# Cost model (USD)
# https://openai.com/api/pricing/
PRICE_PER_MILLION_INPUT_TOKENS = 2.50
REVIEWS_PER_DAY = 10000
DAYS_PER_MONTH = 30
