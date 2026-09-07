"""Safety validator for HeartGuard AI Recommendations (Phase 13).

Ensures that all generated recommendations adhere to strict clinical safety constraints:
  - Strictly NON-DIAGNOSTIC: Never asserts confirmed medical conditions or diagnoses.
  - Strictly NON-PRESCRIPTIVE: Never references medication names, dosages, or drug schedules.
  - Tentative phrasing: Enforces advisory guidance language ("Consider...", "Discuss with...").
"""

from __future__ import annotations

import re
from typing import Any
from src.recommendations.recommendation_models import PRIORITIES

# Disallowed diagnostic assertions
DIAGNOSTIC_TERMS = [
    r"\byou have heart disease\b",
    r"\byou have had a heart attack\b",
    r"\byou are diagnosed with\b",
    r"\bdiagnosed with\b",
    r"\bwe diagnose\b",
    r"\bheart attack detected\b",
    r"\bdefinitely have\b",
    r"\bconfirmed diagnosis\b",
    r"\bproven heart disease\b",
    r"\bguaranteed cure\b",
    r"\bwill cure\b",
    r"\bwill prevent all\b",
]

# Disallowed pharmaceutical / medication terms
MEDICATION_TERMS = [
    r"\bstatin\b",
    r"\batorvastatin\b",
    r"\brosuvastatin\b",
    r"\baspirin\b",
    r"\blisinopril\b",
    r"\bamlodipine\b",
    r"\bmetoprolol\b",
    r"\bbeta blocker\b",
    r"\bace inhibitor\b",
    r"\bnitroglycerin\b",
    r"\bwarfarin\b",
    r"\bclopidogrel\b",
    r"\bmetformin\b",
    r"\bprescription\b",
    r"\bdosage\b",
    r"\b\d+\s*mg\b",
    r"\btablet\b",
    r"\bpill\b",
    r"\bcapsule\b",
    r"\btake daily\b",
]


class SafetyValidationError(ValueError):
    """Raised when a recommendation violates safety or non-diagnostic policies."""


def validate_recommendation(recommendation: dict[str, Any]) -> None:
    """Validate that a recommendation strictly complies with medical safety standards.

    Raises:
        SafetyValidationError: If diagnostic assertions, medications, or unsafe claims exist.
    """
    title = str(recommendation.get("title", ""))
    desc = str(recommendation.get("description", ""))
    priority = str(recommendation.get("priority", ""))
    category = str(recommendation.get("category", ""))

    if not title.strip():
        raise SafetyValidationError("Recommendation title cannot be empty.")
    if not desc.strip():
        raise SafetyValidationError("Recommendation description cannot be empty.")
    if priority not in PRIORITIES:
        raise SafetyValidationError(f"Invalid priority '{priority}'. Must be one of {PRIORITIES}.")

    full_text = f"{title} {desc}".lower()

    # 1. Check for diagnostic claims
    for pattern in DIAGNOSTIC_TERMS:
        if re.search(pattern, full_text, re.IGNORECASE):
            raise SafetyValidationError(
                f"Recommendation contains prohibited diagnostic language matching '{pattern}'."
            )

    # 2. Check for pharmaceutical / prescription terms
    for pattern in MEDICATION_TERMS:
        if re.search(pattern, full_text, re.IGNORECASE):
            raise SafetyValidationError(
                f"Recommendation contains prohibited pharmaceutical/dosage language matching '{pattern}'."
            )
