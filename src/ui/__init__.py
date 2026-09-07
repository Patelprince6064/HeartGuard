"""HeartGuard UI Design System & Component Library (Phase 12).

Exports reusable badges, cards, charts, tables, and dashboard components.
"""

from src.ui.badges import (
    get_alert_status_badge,
    get_review_status_badge,
    get_risk_category_badge,
    render_badge,
)
from src.ui.cards import (
    format_risk_percentage,
    render_assessment_summary_card,
    render_emergency_disclaimer,
    render_medical_disclaimer,
    render_metric_card,
    render_risk_components_cards,
    render_trend_disclaimer,
)
from src.ui.charts import (
    prepare_alert_distribution_chart,
    prepare_category_distribution_chart,
    prepare_review_distribution_chart,
    prepare_risk_components_chart,
    prepare_risk_trend_chart,
    prepare_shap_chart,
    render_chart,
)
from src.ui.dashboard_components import (
    render_dashboard_header,
    render_empty_dashboard_state,
    render_lifestyle_insights,
    render_quick_actions,
    safe_render_section,
)
from src.ui.tables import (
    render_recent_assessments_table,
    render_reviewer_queue_table,
)

__all__ = [
    "format_risk_percentage",
    "get_alert_status_badge",
    "get_review_status_badge",
    "get_risk_category_badge",
    "prepare_alert_distribution_chart",
    "prepare_category_distribution_chart",
    "prepare_review_distribution_chart",
    "prepare_risk_components_chart",
    "prepare_risk_trend_chart",
    "prepare_shap_chart",
    "render_assessment_summary_card",
    "render_badge",
    "render_chart",
    "render_dashboard_header",
    "render_emergency_disclaimer",
    "render_empty_dashboard_state",
    "render_lifestyle_insights",
    "render_medical_disclaimer",
    "render_metric_card",
    "render_recent_assessments_table",
    "render_reviewer_queue_table",
    "render_quick_actions",
    "render_risk_components_cards",
    "render_trend_disclaimer",
    "safe_render_section",
]
