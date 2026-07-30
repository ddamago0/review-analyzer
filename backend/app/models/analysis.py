from dataclasses import dataclass


@dataclass
class AnalysisResult:

    total_reviews: int

    average_length: float

    shortest_review: int

    longest_review: int

    average_words: float