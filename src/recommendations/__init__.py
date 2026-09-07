"""HeartGuard AI Recommendations & Insights Module (Phase 13).

Provides non-diagnostic, personalized recommendations and AI insights.
"""

from src.recommendations.recommendation_engine import RecommendationEngine
from src.recommendations.recommendation_models import (
    AssessmentInsights,
    PRIORITIES,
    PRIORITY_HIGH,
    PRIORITY_INFO,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    RECOMMENDATION_DISCLAIMER,
    Recommendation,
    init_recommendation_db,
)
from src.recommendations.recommendation_service import RecommendationService
from src.recommendations.recommendation_validator import (
    SafetyValidationError,
    validate_recommendation,
)

__all__ = [
    "AssessmentInsights",
    "PRIORITIES",
    "PRIORITY_HIGH",
    "PRIORITY_INFO",
    "PRIORITY_LOW",
    "PRIORITY_MEDIUM",
    "RECOMMENDATION_DISCLAIMER",
    "Recommendation",
    "RecommendationEngine",
    "RecommendationService",
    "SafetyValidationError",
    "init_recommendation_db",
    "validate_recommendation",
]
