"""
Service for counting tokens using OpenAI's o200k_base encoding.
The encoding is loaded lazily and cached for performance.
"""

import logging
import threading

from app.config.settings import TOKEN_ENCODING

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_encoding = None


def _get_encoding():
    """
    Lazily load and cache the tiktoken encoding.

    Returns:
        tiktoken.Encoding: The requested encoding instance
    """
    global _encoding
    if _encoding is None:
        with _lock:
            if _encoding is None:
                import tiktoken
                _encoding = tiktoken.get_encoding(TOKEN_ENCODING)
                logger.info(f"Loaded token encoding: {TOKEN_ENCODING}")
    return _encoding


class TokenService:
    """
    Service responsible for counting tokens in text using the o200k_base encoding.
    """

    @staticmethod
    def count_tokens(text) -> int:
        """
        Count the number of tokens in a text using the o200k_base encoding.

        Args:
            text: Text to count tokens for (string or None)

        Returns:
            int: Number of tokens
        """
        if text is None or not str(text).strip():
            return 0

        try:
            encoding = _get_encoding()
            return len(encoding.encode(str(text)))
        except Exception as e:
            logger.warning(f"Token counting failed, falling back to estimate: {str(e)}")
            return TokenService._estimate_tokens(str(text))

    @staticmethod
    def count_tokens_batch(reviews) -> int:
        """
        Count total tokens for a list of reviews.

        Args:
            reviews (list): List of review texts

        Returns:
            int: Total number of tokens
        """
        return sum(TokenService.count_tokens(review) for review in reviews)

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Fallback token estimator used when tiktoken is unavailable.
        Approximates tokens as ~4 characters per token (o200k heuristic).

        Args:
            text (str): Text to estimate

        Returns:
            int: Estimated number of tokens
        """
        return max(1, len(text) // 4)
