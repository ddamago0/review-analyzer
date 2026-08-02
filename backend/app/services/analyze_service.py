"""
Service that orchestrates the token optimization pipeline.

For each review it:
1. Counts tokens of the original (Spanish) text using o200k_base
2. Translates the text into English
3. Counts tokens of the translated (English) text
4. Computes the token difference
5. Projects monthly savings based on the cost model
6. Extracts structured error information (error_type / component)
"""

import logging
from collections import Counter

from app.services.token_service import TokenService
from app.services.translation_service import TranslationService
from app.services.cost_service import CostService
from app.services.error_extraction_service import ErrorExtractionService
from app.config.settings import TRANSLATION_SAMPLE_SIZE

logger = logging.getLogger(__name__)


class AnalyzeService:
    """
    Service responsible for running the token optimization analysis on
    single reviews or batches of reviews.
    """

    @staticmethod
    def analyze_review(review: str) -> dict:
        """
        Run the full token optimization pipeline on a single review.

        Args:
            review (str): Review text (Spanish)

        Returns:
            dict: Complete analysis for the review
        """
        review = str(review).strip()

        original_tokens = TokenService.count_tokens(review)
        translated = TranslationService.translate_spanish_to_english(review)
        translated_tokens = TokenService.count_tokens(translated)
        token_difference = original_tokens - translated_tokens

        token_difference_percent = 0.0
        if original_tokens > 0:
            token_difference_percent = round(
                (token_difference / original_tokens) * 100, 2
            )

        projection = CostService.build_projection(
            original_tokens=original_tokens,
            translated_tokens=translated_tokens,
            reviews_analyzed=1,
        )

        extraction = ErrorExtractionService.extract(review)

        return {
            "original_text": review,
            "translated_text": translated,
            "original_tokens": original_tokens,
            "translated_tokens": translated_tokens,
            "token_difference": token_difference,
            "token_difference_percent": token_difference_percent,
            "projection": projection,
            "extraction": extraction,
        }

    @staticmethod
    def analyze_batch(reviews, sample_size: int = TRANSLATION_SAMPLE_SIZE) -> dict:
        """
        Run the token optimization pipeline over a batch of reviews.

        Tokens of every review are counted locally (fast). Translation is
        performed on a representative sample and the token reduction ratio
        is extrapolated to the whole batch to estimate monthly savings.

        Args:
            reviews (list): List of review texts
            sample_size (int): Number of reviews to translate

        Returns:
            dict: Aggregate token analysis for the batch
        """
        if not reviews:
            return AnalyzeService._empty_batch_result()

        reviews = [str(r) for r in reviews]
        total_original_tokens = TokenService.count_tokens_batch(reviews)

        # Sample for translation (deterministic: evenly spread through the batch)
        step = max(1, len(reviews) // sample_size)
        sample_indices = sorted(set(range(0, len(reviews), step)))[:sample_size]
        sample_reviews = [reviews[i] for i in sample_indices]

        sample_original_tokens = TokenService.count_tokens_batch(sample_reviews)
        sample_translated_tokens = 0
        samples = []

        for review in sample_reviews:
            analyzed = AnalyzeService.analyze_review(review)
            sample_translated_tokens += analyzed["translated_tokens"]
            samples.append(analyzed)

        # Estimate total translated tokens using the measured reduction ratio
        if sample_original_tokens > 0:
            ratio = sample_translated_tokens / sample_original_tokens
            estimated_translated_tokens = int(total_original_tokens * ratio)
        else:
            estimated_translated_tokens = total_original_tokens

        token_difference = total_original_tokens - estimated_translated_tokens
        token_difference_percent = 0.0
        if total_original_tokens > 0:
            token_difference_percent = round(
                (token_difference / total_original_tokens) * 100, 2
            )

        projection = CostService.build_projection(
            original_tokens=total_original_tokens,
            translated_tokens=estimated_translated_tokens,
            reviews_analyzed=len(reviews),
        )

        # Aggregate structured extractions across the whole batch (fast, local)
        error_types = Counter()
        components = Counter()
        for review in reviews:
            extraction = ErrorExtractionService.extract(review)
            error_types[extraction["error_type"]] += 1
            components[extraction["component"]] += 1

        return {
            "enabled": True,
            "reviews_analyzed": len(reviews),
            "translation_sample_size": len(sample_reviews),
            "total_original_tokens": total_original_tokens,
            "total_translated_tokens": estimated_translated_tokens,
            "token_difference": token_difference,
            "token_difference_percent": token_difference_percent,
            "projection": projection,
            "samples": samples[:5],
            "error_types": error_types.most_common(10),
            "components": components.most_common(10),
        }

    @staticmethod
    def _empty_batch_result() -> dict:
        """Return a neutral result when there are no reviews to analyze."""
        return {
            "enabled": True,
            "reviews_analyzed": 0,
            "translation_sample_size": 0,
            "total_original_tokens": 0,
            "total_translated_tokens": 0,
            "token_difference": 0,
            "token_difference_percent": 0,
            "projection": CostService.build_projection(0, 0, 0),
            "samples": [],
            "error_types": [],
            "components": [],
        }
