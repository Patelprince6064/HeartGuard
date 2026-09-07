"""Doctor Review Portal for HeartGuard (Phase 11).

Allows REVIEWER-role users to:
  1. Browse all patient assessments with their current review status
  2. Open any assessment and view the AI-generated results (read-only)
  3. Create or update a professional review entry (notes, status, flags)
  4. Review their own submitted reviews

CRITICAL DISCLAIMER:
  - This portal is NOT a diagnostic, prescriptive, or treatment system.
  - AI-generated risk scores, SHAP values, and recommendations are
    displayed READ-ONLY and can NEVER be modified via this portal.
  - A professional review is an observation record, not a clinical diagnosis.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.auth.authorization import require_reviewer
from src.auth.session_manager import clear_session, get_current_user
from src.review import (
    PROFESSIONAL_NOTES_MAX_LENGTH,
    REVIEW_STATUSES,
    REVIEW_STATUS_LABELS,
    URGENCY_LABELS,
    ReviewService,
)
from src.security.audit_logger import log_event
from src.utils.logger import get_logger

from src.ui import (
    get_alert_status_badge,
    get_review_status_badge,
    get_risk_category_badge,
    prepare_review_distribution_chart,
    prepare_risk_components_chart,
    prepare_shap_chart,
    render_chart,
    render_risk_components_cards,
)

logger = get_logger(__name__)

st.set_page_config(
    page_title="HeartGuard — Doctor Review Portal",
    page_icon="🩺",
    layout="wide",
)

# ── Authorization guard ───────────────────────────────────────────────────────
require_reviewer()
current_user = get_current_user()
reviewer_id: int = current_user["id"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**{current_user['name']}**")
    st.caption(f"Role: `{current_user['role']}`")
    st.divider()
    st.page_link("pages/dashboard.py", label="📊 Patient Dashboard")
    st.page_link("pages/review.py", label="🩺 Doctor Review Portal")
    st.page_link("pages/history.py", label="📜 Assessments & Reports")
    st.page_link("pages/security.py", label="🔐 Security & Profile")
    st.divider()
    if st.button("🚪 Log Out", use_container_width=True, key="review_logout"):
        log_event("logout", "SUCCESS", user_id=reviewer_id, role=current_user["role"])
        clear_session()
        st.switch_page("pages/login.py")

# ── Page header ───────────────────────────────────────────────────────────────
st.title("🩺 Doctor Review Portal")
st.caption("Authorized professional review interface — Phase 12")

# ── Safety disclaimer ─────────────────────────────────────────────────────────
st.error(
    "⚠️ **Clinical Safety Notice**\n\n"
    "This portal provides access to AI-generated cardiovascular risk assessment results "
    "for authorized professional review purposes **only**.\n\n"
    "- HeartGuard is a **research prototype**, NOT a certified medical device.\n"
    "- AI risk scores and recommendations are **experimental estimates** — they are NOT diagnoses.\n"
    "- Professional review notes recorded here are **observations**, NOT clinical diagnoses, "
    "prescriptions, or treatment plans.\n"
    "- **Do NOT enter diagnostic conclusions, medication recommendations, or treatment "
    "decisions** into the notes field.\n"
    "- Any clinical decision must be made by a qualified healthcare professional acting "
    "under their own professional judgment and applicable regulations."
)

st.divider()

# ── Review Queue KPI Metrics ──────────────────────────────────────────────────
try:
    rev_stats = ReviewService.get_review_statistics(reviewer_id=reviewer_id)
    pending_total = rev_stats.get("pending", 0) + rev_stats.get("unassigned_pending", 0)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Pending Reviews", pending_total)
    k2.metric("In Review", rev_stats.get("in_review", 0))
    k3.metric("Reviewed", rev_stats.get("reviewed", 0))
    k4.metric("Follow-Up Recommended", rev_stats.get("follow_up_recommended", 0))
    k5.metric("Total Assigned", rev_stats.get("total_assigned", 0))

    if rev_stats.get("total_assigned", 0) > 0:
        with st.expander("📊 Review Status Distribution", expanded=False):
            dist_map = {
                "PENDING": rev_stats.get("pending", 0),
                "IN_REVIEW": rev_stats.get("in_review", 0),
                "ACCEPTED": rev_stats.get("accepted", 0),
                "MODIFIED": rev_stats.get("modified", 0),
                "REJECTED": rev_stats.get("rejected", 0),
            }
            chart = prepare_review_distribution_chart(dist_map)
            if chart is not None:
                render_chart(chart)
except Exception as exc:
    logger.warning("Could not render review statistics: %s", exc)

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_all, tab_pending, tab_my_reviews = st.tabs(
    ["📋 All Assessments", "⏳ Pending Review", "✅ My Reviews"]
)



# =============================================================================
# Shared helper — Assessment + Review detail panel
# =============================================================================


def _render_review_detail(assessment_id: str) -> None:
    """Render the read-only AI assessment panel and the editable review panel."""
    data = ReviewService.get_assessment_with_review(assessment_id)
    assessment = data["assessment"]
    review = data["review"]

    if assessment is None:
        st.error(f"Assessment '{assessment_id}' not found.")
        return

    # ── AI Assessment Panel (READ-ONLY) ───────────────────────────────────────
    st.markdown(
        "---\n"
        "### 🤖 AI-Generated Assessment  \n"
        "*Read-only — these values represent the AI model output and cannot be edited.*"
    )
    st.warning(
        "The results below are produced by a machine-learning model and are "
        "**NOT a medical diagnosis**. They are provided for professional review context only."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall Risk", f"{assessment.overall_risk:.1f}%")
    col2.metric("Clinical Risk", f"{assessment.clinical_risk:.1f}%")
    col3.metric("Lifestyle Risk", f"{assessment.lifestyle_risk:.1f}%")
    col4.metric("Risk Category", assessment.risk_category.replace("_", " ").title())

    with st.container(border=True):
        st.markdown(f"**Assessment ID:** `{assessment.assessment_id}`")
        st.markdown(f"**Recorded at:** {assessment.created_at[:19].replace('T', ' ')} UTC")
        st.markdown(f"**Model version:** `{assessment.model_version}`")
        st.markdown(f"**Alert status:** `{assessment.alert_status}`")

    if assessment.narrative_summary:
        with st.expander("📝 AI Narrative Summary", expanded=False):
            st.markdown(assessment.narrative_summary)

    top_factors = assessment.get_top_clinical_factors()
    if top_factors:
        with st.expander("📊 Top Clinical SHAP Factors", expanded=False):
            shap_chart = prepare_shap_chart(top_factors, top_n=8)
            if shap_chart is not None:
                render_chart(shap_chart)
            factors_data = [
                {
                    "Feature": f.get("feature", "—"),
                    "SHAP Value": f"{f.get('shap_value', 0):.4f}",
                    "Direction": "↑ Increases Risk" if f.get("shap_value", 0) > 0 else "↓ Decreases Risk",
                }
                for f in top_factors
            ]
            st.dataframe(pd.DataFrame(factors_data), use_container_width=True, hide_index=True)

    lifestyle_factors = assessment.get_lifestyle_factors()
    if lifestyle_factors:
        with st.expander("🏃 Detected Lifestyle Risk Factors", expanded=False):
            lf_data = [
                {
                    "Factor": f.get("display_name", "—"),
                    "Severity": f.get("severity", "—"),
                    "Risk Points": f.get("risk_points", "—"),
                }
                for f in lifestyle_factors
            ]
            st.dataframe(pd.DataFrame(lf_data), use_container_width=True, hide_index=True)

    # ── Professional Review Panel (EDITABLE) ──────────────────────────────────
    st.markdown(
        "---\n"
        "### 📋 Professional Review  \n"
        "*Record your professional observations below. This is NOT a diagnostic form.*"
    )

    is_new = review is None
    owns_review = (not is_new) and (review.reviewer_id == reviewer_id)

    if not is_new and not owns_review:
        st.info(
            f"This assessment has already been reviewed by another reviewer "
            f"(review status: **{REVIEW_STATUS_LABELS.get(review.review_status, review.review_status)}**).\n\n"
            "Review records are owned by the reviewer who created them."
        )
        # Show read-only view of existing review
        with st.container(border=True):
            st.markdown(f"**Status:** {REVIEW_STATUS_LABELS.get(review.review_status, review.review_status)}")
            st.markdown(f"**Follow-up required:** {'Yes' if review.follow_up_required else 'No'}")
            st.markdown(f"**Urgency flag:** {URGENCY_LABELS.get(review.urgency_flag, '—')}")
            if review.professional_notes:
                st.markdown("**Notes:**")
                st.text(review.professional_notes)
        return

    # Determine default values for form fields
    default_status_idx = 0
    default_notes = ""
    default_follow_up = False
    default_urgency = False

    if review is not None:
        default_status_idx = REVIEW_STATUSES.index(review.review_status)
        default_notes = review.professional_notes
        default_follow_up = review.follow_up_required
        default_urgency = review.urgency_flag

    with st.form(key=f"review_form_{assessment_id}"):
        new_status = st.selectbox(
            "Review Status",
            options=REVIEW_STATUSES,
            index=default_status_idx,
            format_func=lambda s: REVIEW_STATUS_LABELS.get(s, s),
            help="Select the current review workflow status for this assessment.",
            key=f"status_{assessment_id}",
        )

        new_follow_up = st.toggle(
            "📅 Follow-up appointment recommended",
            value=default_follow_up,
            key=f"follow_up_{assessment_id}",
        )

        new_urgency = st.toggle(
            "🚨 Flag for urgent attention",
            value=default_urgency,
            key=f"urgency_{assessment_id}",
        )

        new_notes = st.text_area(
            "Professional Notes",
            value=default_notes,
            max_chars=PROFESSIONAL_NOTES_MAX_LENGTH,
            height=200,
            placeholder=(
                "Record your professional observations about this assessment here.\n\n"
                "⚠️ Do NOT enter diagnoses, medication recommendations, treatment plans, "
                "or any other clinical decisions. Notes are observations only."
            ),
            key=f"notes_{assessment_id}",
            help=(
                f"Maximum {PROFESSIONAL_NOTES_MAX_LENGTH} characters. "
                "For professional observations only — not for diagnoses."
            ),
        )

        submit_label = "💾 Save Review" if is_new else "🔄 Update Review"
        submitted = st.form_submit_button(submit_label, use_container_width=True)

    if submitted:
        try:
            if is_new:
                created = ReviewService.create_review(
                    reviewer_id=reviewer_id,
                    assessment_id=assessment_id,
                )
                # Then immediately update with the entered data
                ReviewService.update_review(
                    review_id=created.review_id,
                    reviewer_id=reviewer_id,
                    review_status=new_status,
                    professional_notes=new_notes,
                    follow_up_required=new_follow_up,
                    urgency_flag=new_urgency,
                )
                log_event(
                    "review_created",
                    "SUCCESS",
                    user_id=reviewer_id,
                    role=current_user["role"],
                    details={"assessment_id": assessment_id, "status": new_status},
                )
                st.success("✅ Professional review submitted successfully.")
            else:
                ReviewService.update_review(
                    review_id=review.review_id,
                    reviewer_id=reviewer_id,
                    review_status=new_status,
                    professional_notes=new_notes,
                    follow_up_required=new_follow_up,
                    urgency_flag=new_urgency,
                )
                log_event(
                    "review_updated",
                    "SUCCESS",
                    user_id=reviewer_id,
                    role=current_user["role"],
                    details={"assessment_id": assessment_id, "status": new_status},
                )
                st.success("✅ Review updated successfully.")
            st.rerun()
        except (ValueError, PermissionError) as exc:
            st.error(f"❌ Could not save review: {exc}")
        except Exception:
            logger.exception("Unexpected error saving review for assessment %s", assessment_id)
            st.error("❌ An unexpected error occurred. Please try again.")


# =============================================================================
# Tab 1 — All Assessments
# =============================================================================

with tab_all:
    st.markdown("#### All Patient Assessments")
    st.caption(
        "All recorded assessments across all patients. "
        "Urgency-flagged assessments appear first."
    )

    try:
        all_rows = ReviewService.get_all_assessments_with_review_status()
    except Exception:
        logger.exception("Failed to load all assessments")
        all_rows = []

    if not all_rows:
        st.info("No assessments found in the system.")
    else:
        df_all = pd.DataFrame(all_rows)
        df_all["review_status_label"] = df_all["review_status"].map(
            lambda s: REVIEW_STATUS_LABELS.get(s, s)
        )
        df_all["urgency_flag"] = df_all["urgency_flag"].map(
            lambda v: "🚨 Yes" if v else "—"
        )
        df_all["follow_up_required"] = df_all["follow_up_required"].map(
            lambda v: "📅 Yes" if v else "—"
        )
        df_all["overall_risk"] = df_all["overall_risk"].apply(
            lambda v: f"{v:.1f}%" if v is not None else "—"
        )
        df_all["created_at"] = df_all["created_at"].str[:19].str.replace("T", " ")

        display_df = df_all.rename(columns={
            "assessment_id": "Assessment ID",
            "user_id": "Patient ID",
            "created_at": "Recorded At (UTC)",
            "overall_risk": "Overall Risk",
            "risk_category": "Risk Category",
            "review_status_label": "Review Status",
            "urgency_flag": "Urgent",
            "follow_up_required": "Follow-up",
        })[[
            "Assessment ID", "Patient ID", "Recorded At (UTC)",
            "Overall Risk", "Risk Category", "Review Status", "Urgent", "Follow-up",
        ]]

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.divider()
        selected_id_all = st.selectbox(
            "Select Assessment ID to Review",
            options=[""] + [r["assessment_id"] for r in all_rows],
            format_func=lambda x: "— Select —" if x == "" else x,
            key="select_all_assessment",
        )
        if selected_id_all:
            _render_review_detail(selected_id_all)


# =============================================================================
# Tab 2 — Pending Review
# =============================================================================

with tab_pending:
    st.markdown("#### Assessments Awaiting Professional Review")
    st.caption("Assessments that have not yet been assigned a review record.")

    try:
        pending = ReviewService.get_pending_assessments()
    except Exception:
        logger.exception("Failed to load pending assessments")
        pending = []

    if not pending:
        st.success("✅ All assessments have been reviewed.")
    else:
        st.info(f"**{len(pending)}** assessment(s) awaiting review.")

        df_pending = pd.DataFrame([
            {
                "Assessment ID": a.assessment_id,
                "Patient ID": a.user_id,
                "Recorded At (UTC)": a.created_at[:19].replace("T", " "),
                "Overall Risk": f"{a.overall_risk:.1f}%",
                "Risk Category": a.risk_category.replace("_", " ").title(),
            }
            for a in pending
        ])
        st.dataframe(df_pending, use_container_width=True, hide_index=True)

        st.divider()
        selected_id_pending = st.selectbox(
            "Select Assessment ID to Start Review",
            options=[""] + [a.assessment_id for a in pending],
            format_func=lambda x: "— Select —" if x == "" else x,
            key="select_pending_assessment",
        )
        if selected_id_pending:
            _render_review_detail(selected_id_pending)


# =============================================================================
# Tab 3 — My Reviews
# =============================================================================

with tab_my_reviews:
    st.markdown("#### My Submitted Reviews")
    st.caption("Review records that you have created or last updated.")

    try:
        my_reviews = ReviewService.get_reviews_by_reviewer(reviewer_id)
    except Exception:
        logger.exception("Failed to load reviews for reviewer %s", reviewer_id)
        my_reviews = []

    if not my_reviews:
        st.info("You have not submitted any reviews yet.")
    else:
        df_mine = pd.DataFrame([
            {
                "Review ID": r.review_id,
                "Assessment ID": r.assessment_id,
                "Status": REVIEW_STATUS_LABELS.get(r.review_status, r.review_status),
                "Urgent": "🚨 Yes" if r.urgency_flag else "—",
                "Follow-up": "📅 Yes" if r.follow_up_required else "—",
                "Last Updated (UTC)": r.updated_at[:19].replace("T", " "),
            }
            for r in my_reviews
        ])
        st.dataframe(df_mine, use_container_width=True, hide_index=True)

        st.divider()
        selected_id_mine = st.selectbox(
            "Select Assessment ID to Update Review",
            options=[""] + [r.assessment_id for r in my_reviews],
            format_func=lambda x: "— Select —" if x == "" else x,
            key="select_my_assessment",
        )
        if selected_id_mine:
            _render_review_detail(selected_id_mine)
