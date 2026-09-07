"""Tests for lifestyle analyzer module."""

import pytest


def test_lifestyle_module_importable():
    """Test that lifestyle analyzer module can be imported."""
    from src.nlp import lifestyle_analyzer

    assert hasattr(lifestyle_analyzer, "analyze_lifestyle_text")
    assert hasattr(lifestyle_analyzer, "detect_risk_factors")
    assert hasattr(lifestyle_analyzer, "calculate_lifestyle_score")


def test_analyze_lifestyle_text_not_implemented():
    """Test that analyze_lifestyle_text raises NotImplementedError."""
    from src.nlp.lifestyle_analyzer import analyze_lifestyle_text

    with pytest.raises(NotImplementedError):
        analyze_lifestyle_text("test")


def test_detect_risk_factors_not_implemented():
    """Test that detect_risk_factors raises NotImplementedError."""
    from src.nlp.lifestyle_analyzer import detect_risk_factors

    with pytest.raises(NotImplementedError):
        detect_risk_factors("test")
