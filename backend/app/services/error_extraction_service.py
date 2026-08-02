"""
Service for extracting structured information (error type and affected
component) from review texts.

This is a deterministic, rule-based extractor that recognizes common
app-store review patterns in both Spanish and English. It produces a
JSON-friendly structure such as:

    {"error_type": "crash", "component": "profile_picture_upload"}
"""

import logging
import re

logger = logging.getLogger(__name__)


class ErrorExtractionService:
    """
    Rule-based extractor that classifies a review into an error type and
    the affected component.
    """

    # Maps a canonical error_type to the keywords that trigger it.
    ERROR_TYPE_RULES = [
        ("crash", [
            "crash", "crashes", "crashed", "crashing",
            "se bloquea", "bloquea", "bloqueo", "bloqueada", "bloqueado",
            "se cierra", "cierra sola", "se sale",
            "se congela", "congela", "se cuelga", "cuelga", "colgada",
            "se traba", "traba", "se detiene", "se cae", "se cerró",
            "pantalla azul", "reinicia", "se reinicia",
        ]),
        ("login_authentication", [
            "login", "log in", "iniciar sesion", "sesion", "iniciar sesión",
            "autentica", "authentication", "acceso", "no puedo entrar",
            "no entra", "cerrar sesion", "cuenta bloqueada",
        ]),
        ("payment_billing", [
            "pago", "pagar", "payment", "pay", "cobro", "cobra",
            "factura", "charge", "charged", "tarjeta", "card",
            "suscripcion", "subscription", "devolucion", "refund",
            "doble cobro", "double charge",
        ]),
        ("connection_network", [
            "conexion", "connection", "offline", "wifi", "internet",
            "network", "red", "servidor", "server", "timeout",
            "sin señal", "no hay conexion", "se desconecta",
        ]),
        ("installation_update", [
            "instalar", "installation", "install", "actualizar", "update",
            "actualizacion", "no se instala", "no instala", "no se actualiza",
            "descargar", "download", "failed to install",
        ]),
        ("performance", [
            "lento", "slow", "lag", "tarda mucho", "se tarda",
            "congelada", "poca memoria", "memory", "se queda cargando",
            "no responde", "unresponsive", "se traba",
        ]),
        ("general_error", [
            "error", "problem", "problema", "problemas", "bug",
            "fallo", "falla", "falla", "no funciona", "does not work",
            "no sirve", "is useless", "fail", "failed", "exception",
        ]),
    ]

    # Maps a canonical component to the keywords that trigger it.
    COMPONENT_RULES = [
        ("profile_picture_upload", [
            "foto de perfil", "profile picture", "profile photo",
            "avatar", "foto del perfil", "imagen de perfil",
        ]),
        ("photo_upload", [
            "subir foto", "upload photo", "subir imagen", "upload image",
            "galeria", "gallery", "camara", "camera", "adjuntar",
            "foto", "photo", "imagen", "image",
        ]),
        ("login", [
            "login", "log in", "iniciar sesion", "sesion", "iniciar sesión",
            "autentica", "password", "contraseña", "contrasena", "acceso",
            "cuenta", "account",
        ]),
        ("payment_checkout", [
            "pago", "pagar", "payment", "pay", "cobro", "factura",
            "tarjeta", "card", "checkout", "compra", "purchase",
        ]),
        ("notifications", [
            "notificacion", "notification", "notificaciones", "notifications",
            "alerta", "alert", "push",
        ]),
        ("file_upload", [
            "subir archivo", "upload file", "adjuntar archivo",
            "archivo", "file", "documento", "document",
        ]),
        ("video_player", [
            "video", "video player", "reproductor", "se corta el video",
        ]),
        ("general_ui", [
            "boton", "button", "menu", "pantalla", "screen",
            "interfaz", "interface", "ui", "claro", "oscuro",
        ]),
    ]

    @staticmethod
    def extract(text) -> dict:
        """
        Extract error_type and component from a review text.

        Args:
            text: Review text (Spanish or English)

        Returns:
            dict: {"error_type": str, "component": str}
        """
        normalized = ErrorExtractionService._normalize(text)

        error_type = ErrorExtractionService._match(
            normalized, ErrorExtractionService.ERROR_TYPE_RULES, "general_error"
        )
        component = ErrorExtractionService._match(
            normalized, ErrorExtractionService.COMPONENT_RULES, "general"
        )

        return {
            "error_type": error_type,
            "component": component,
        }

    @staticmethod
    def _normalize(text) -> str:
        """Lowercase and normalize whitespace for matching."""
        if not text:
            return ""
        text = str(text).lower()
        text = re.sub(r"á", "a", text)
        text = re.sub(r"é", "e", text)
        text = re.sub(r"í", "i", text)
        text = re.sub(r"ó", "o", text)
        text = re.sub(r"ú", "u", text)
        text = re.sub(r"ñ", "n", text)
        text = re.sub(r"[^\w\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _match(normalized_text, rules, default) -> str:
        """
        Return the first rule whose keyword appears in the normalized text.

        Args:
            normalized_text (str): Normalized review text
            rules (list): List of (category, keywords) tuples
            default (str): Fallback category when nothing matches

        Returns:
            str: Matched category or the default
        """
        for category, keywords in rules:
            for keyword in keywords:
                if keyword in normalized_text:
                    return category
        return default
