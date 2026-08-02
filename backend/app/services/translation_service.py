"""
Service for translating Spanish reviews into English.

The primary provider uses the deep-translator library (online, Google
Translate) for accurate translations. When the online service is not
available, a deterministic offline translator is used as a fallback so
the pipeline keeps working without connectivity.
"""

import logging
import re

from app.config.settings import TRANSLATION_SOURCE_LANG, TRANSLATION_TARGET_LANG

logger = logging.getLogger(__name__)


class OfflineTranslator:
    """
    Deterministic fallback translator based on a curated Spanish->English
    vocabulary of common app-review terms. Used only when the online
    translation provider is unavailable.
    """

    PHRASES = {
        "cada vez que": "every time",
        "foto de perfil": "profile picture",
        "no me funciona": "does not work for me",
        "no funciona": "does not work",
        "no me deja": "will not let me",
        "no puedo entrar": "i cannot log in",
        "no puedo iniciar sesion": "i cannot log in",
        "no puedo": "i can not",
        "iniciar sesion": "log in",
        "contraseña incorrecta": "wrong password",
        "contrasena incorrecta": "wrong password",
        "se bloquea": "crashes",
        "se cierra": "closes itself",
        "se detiene": "stops",
        "se actualiza": "updates",
        "no carga": "does not load",
        "no se actualiza": "does not update",
        "la aplicacion": "the application",
        "mi telefono": "my phone",
        "todos los dias": "every day",
        "me gustaria": "i would like",
        "por favor": "please",
        "muy buena": "very good",
        "muy bueno": "very good",
        "muy mala": "very bad",
        "muy malo": "very bad",
        "de nuevo": "again",
        "no me gusta": "i do not like",
        "no sirve": "is useless",
        "desde mi": "from my",
        "desde el": "from the",
        "desde la": "from the",
        "una vez": "once",
        "me dice": "says to me",
        "me ha cobrado": "charged me",
        "no me cobres": "do not charge me",
    }

    WORDS = {
        # Articles and pronouns
        "el": "the", "la": "the", "los": "the", "las": "the",
        "un": "a", "una": "a", "unos": "some", "unas": "some",
        "mi": "my", "mis": "my", "tu": "your", "tus": "your",
        "su": "their", "sus": "their", "me": "me", "te": "you",
        "lo": "it", "del": "of the", "al": "to the",
        # Prepositions and conjunctions
        "y": "and", "de": "of", "a": "to", "en": "in", "con": "with",
        "para": "to", "por": "for", "que": "that", "desde": "from",
        "hasta": "until", "entre": "between", "sobre": "about",
        "sin": "without", "despues": "after", "antes": "before",
        "porque": "because", "cuando": "when", "donde": "where",
        "como": "how", "tambien": "also", "pero": "but", "o": "or",
        "si": "if", "ya": "already", "se": "itself",
        # Verbs
        "es": "is", "son": "are", "fue": "was", "era": "was",
        "está": "is", "esta": "is", "estan": "are",
        "funciona": "works", "funcionar": "work", "trabaja": "works",
        "carga": "loads", "cargar": "load", "subir": "upload",
        "subo": "upload", "sube": "uploads", "ver": "see", "usar": "use",
        "tener": "have", "tengo": "have", "poder": "can", "puedo": "can",
        "creo": "think", "enviar": "send", "recibir": "receive",
        "actualizar": "update", "instalar": "install", "instala": "installs",
        "descargar": "download", "borrar": "delete", "eliminar": "delete",
        "tarda": "takes", "pagar": "pay", "pago": "payment",
        "cobra": "charges", "comprar": "buy", "compra": "purchase",
        "recomiendo": "recommend", "mejorar": "improve",
        "entrar": "enter", "abrir": "open", "cerrar": "close",
        "intento": "try", "intenta": "tries", "intente": "try",
        "dice": "says", "dijo": "said", "dijera": "said",
        "incorrecta": "wrong", "incorrecto": "wrong",
        # Nouns
        "aplicacion": "application", "app": "app",
        "usuario": "user", "usuarios": "users",
        "telefono": "phone", "celular": "phone",
        "galeria": "gallery", "foto": "photo",
        "fotografia": "photo", "imagen": "image",
        "imagenes": "images", "perfil": "profile",
        "actualizacion": "update", "version": "version",
        "pantalla": "screen", "bateria": "battery",
        "notificacion": "notification", "notificaciones": "notifications",
        "publicidad": "ads", "anuncios": "ads",
        "privacidad": "privacy", "datos": "data",
        "conexion": "connection", "internet": "internet",
        "wifi": "wifi", "servidor": "server", "sesion": "session",
        "contraseña": "password", "contrasena": "password",
        "cuenta": "account", "correo": "email",
        "mensaje": "message", "mensajes": "messages",
        "video": "video", "juego": "game", "graficos": "graphics",
        "sonido": "sound", "ayuda": "help", "soporte": "support",
        "error": "error", "problema": "problem", "problemas": "problems",
        "bug": "bug", "fallo": "bug", "falla": "failure",
        "opinion": "opinion", "calificacion": "rating",
        "estrellas": "stars", "nota": "note", "respuesta": "response",
        "clave": "key", "codigo": "code", "configuracion": "settings",
        "opcion": "option", "menu": "menu", "boton": "button",
        "archivo": "file", "archivos": "files", "documento": "document",
        # Adjectives
        "muy": "very", "mas": "more", "menos": "less",
        "siempre": "always", "nunca": "never", "todavia": "still",
        "bueno": "good", "buena": "good", "buenos": "good", "buenas": "good",
        "excelente": "excellent", "perfecto": "perfect", "perfecta": "perfect",
        "genial": "great", "increible": "incredible", "fantastico": "fantastic",
        "fantastica": "fantastic", "horrible": "horrible",
        "pesimo": "terrible", "pesima": "terrible",
        "malo": "bad", "mala": "bad", "malos": "bad", "malas": "bad",
        "rapido": "fast", "rapida": "fast", "lento": "slow", "lenta": "slow",
        "facil": "easy", "dificil": "hard", "nuevo": "new", "nueva": "new",
        "nuevos": "new", "nuevas": "new", "actual": "latest",
        "ultimo": "latest", "ultima": "latest", "amable": "friendly",
        "gratis": "free", "pago": "paid",
        # Adverbs / misc
        "ahora": "now", "ayer": "yesterday", "hoy": "today",
        "gracias": "thanks", "mucho": "much", "mucha": "much",
        "muchos": "many", "muchas": "many", "otra": "another",
        "otro": "another", "otros": "others", "todas": "all",
        "todo": "all", "toda": "all", "cada": "each",
        "solo": "only", "solo": "only", "igual": "same",
    }

    @classmethod
    def translate(cls, text: str) -> str:
        """
        Translate a Spanish sentence into English using the offline dictionary.

        Args:
            text (str): Spanish text

        Returns:
            str: English translation (lowercase)
        """
        normalized = cls._normalize(text)
        words = normalized.split()
        output = []
        i = 0
        n = len(words)

        # Sort phrases by word count descending for longest-match-first
        phrase_keys = sorted(cls.PHRASES, key=lambda p: len(p.split()), reverse=True)

        while i < n:
            matched = False
            for phrase in phrase_keys:
                phrase_words = phrase.split()
                length = len(phrase_words)
                if i + length <= n and " ".join(words[i:i + length]) == phrase:
                    output.append(cls.PHRASES[phrase])
                    i += length
                    matched = True
                    break
            if matched:
                continue

            word = words[i]
            output.append(cls.WORDS.get(word, word))
            i += 1

        translation = " ".join(output)
        return cls._restore_case(translation)

    @staticmethod
    def _normalize(text: str) -> str:
        """Lowercase and strip accents where needed for dictionary matching."""
        text = text.lower()
        text = re.sub(r"á", "a", text)
        text = re.sub(r"é", "e", text)
        text = re.sub(r"í", "i", text)
        text = re.sub(r"ó", "o", text)
        text = re.sub(r"ú", "u", text)
        text = re.sub(r"ü", "u", text)
        text = re.sub(r"[^\w\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _restore_case(text: str) -> str:
        """Capitalize the first letter of the sentence."""
        if not text:
            return text
        return text[0].upper() + text[1:]


class TranslationService:
    """
    Service responsible for translating Spanish reviews into English.
    """

    @staticmethod
    def translate_spanish_to_english(text: str) -> str:
        """
        Translate a Spanish text into English.

        Uses the online provider (deep-translator) when available and falls
        back to the offline deterministic translator otherwise.

        Args:
            text (str): Spanish text

        Returns:
            str: English translation
        """
        text = str(text).strip()
        if not text:
            return text

        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(
                source=TRANSLATION_SOURCE_LANG,
                target=TRANSLATION_TARGET_LANG
            )
            translated = translator.translate(text)
            if translated:
                return translated.strip()
            raise ValueError("Empty translation returned")
        except Exception as e:
            logger.warning(
                f"Online translation unavailable ({str(e)[:120]}), "
                "using offline fallback translator."
            )
            return OfflineTranslator.translate(text)
