"""
Service for projecting token usage and estimating cost savings.

The cost model is based on:
- Price: 2.50 USD per million input tokens
- Volume: 10,000 reviews per day
- Horizon: 30 days (one month)

By translating Spanish reviews into English before sending them to an
LLM pipeline, the number of input tokens is reduced, producing monthly
savings.
"""

import logging

from app.config.settings import (
    PRICE_PER_MILLION_INPUT_TOKENS,
    REVIEWS_PER_DAY,
    DAYS_PER_MONTH,
)

logger = logging.getLogger(__name__)


class CostService:
    """
    Service responsible for cost projection and savings estimation.
    """

    PRICE_PER_MILLION_INPUT_TOKENS = PRICE_PER_MILLION_INPUT_TOKENS
    REVIEWS_PER_DAY = REVIEWS_PER_DAY
    DAYS_PER_MONTH = DAYS_PER_MONTH

    @staticmethod
    def monthly_tokens(tokens_per_review, reviews_per_day, days) -> float:
        """
        Project the total number of tokens consumed in a month.

        Args:
            tokens_per_review (float): Average tokens per review
            reviews_per_day (int): Reviews processed per day
            days (int): Number of days in the projection period

        Returns:
            float: Total projected tokens
        """
        return tokens_per_review * reviews_per_day * days

    @staticmethod
    def monthly_cost(tokens_per_review, reviews_per_day, days) -> float:
        """
        Project the monthly cost in USD for a given average tokens per review.

        Args:
            tokens_per_review (float): Average tokens per review
            reviews_per_day (int): Reviews processed per day
            days (int): Number of days in the projection period

        Returns:
            float: Monthly cost in USD
        """
        total_tokens = CostService.monthly_tokens(
            tokens_per_review,
            reviews_per_day,
            days
        )
        return round(
            total_tokens / 1_000_000 * CostService.PRICE_PER_MILLION_INPUT_TOKENS,
            2
        )

    @staticmethod
    def build_projection(
        original_tokens,
        translated_tokens,
        reviews_analyzed,
        reviews_per_day=None,
        days=None,
    ) -> dict:
        """
        Build the full monthly projection comparing the original (Spanish)
        pipeline against the translated (English) pipeline.

        Args:
            original_tokens (int): Total original tokens analyzed
            translated_tokens (int): Total translated tokens analyzed
            reviews_analyzed (int): Number of reviews represented by the counts
            reviews_per_day (int, optional): Reviews per day (default from settings)
            days (int, optional): Days per month (default from settings)

        Returns:
            dict: Monthly projection with costs and savings
        """
        reviews_per_day = reviews_per_day or CostService.REVIEWS_PER_DAY
        days = days or CostService.DAYS_PER_MONTH

        if reviews_analyzed <= 0:
            reviews_analyzed = 1

        avg_original = original_tokens / reviews_analyzed
        avg_translated = translated_tokens / reviews_analyzed

        original_monthly = CostService.monthly_cost(avg_original, reviews_per_day, days)
        translated_monthly = CostService.monthly_cost(avg_translated, reviews_per_day, days)
        savings = round(original_monthly - translated_monthly, 2)

        original_monthly_tokens = CostService.monthly_tokens(
            avg_original, reviews_per_day, days
        )
        translated_monthly_tokens = CostService.monthly_tokens(
            avg_translated, reviews_per_day, days
        )

        savings_percent = 0.0
        if original_monthly > 0:
            savings_percent = round((savings / original_monthly) * 100, 2)

        return {
            "reviews_per_day": reviews_per_day,
            "days_per_month": days,
            "original_tokens_per_review": round(avg_original, 2),
            "translated_tokens_per_review": round(avg_translated, 2),
            "original_monthly_tokens": int(original_monthly_tokens),
            "translated_monthly_tokens": int(translated_monthly_tokens),
            "original_monthly_cost_usd": original_monthly,
            "translated_monthly_cost_usd": translated_monthly,
            "monthly_savings_usd": savings,
            "savings_percent": savings_percent,
            "price_per_million_input_tokens_usd": CostService.PRICE_PER_MILLION_INPUT_TOKENS,
        }
