"""Unified Multimodal Risk Assessment Page for HeartGuard (Phase 7 + Phase 9).

Integrates Clinical ML predictions (70%) and Lifestyle NLP risk scoring (30%)
into a single, explainable cardiovascular risk assessment interface.

Phase 9: Authentication required. Lifestyle text is never logged.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

from config.settings import MODEL_DIRECTORY, REPORT_DIRECTORY
from src.auth.authorization import require_authentication
from src.auth.session_manager import clear_session, get_current_user
from src.risk_engine.multimodal_risk import MultimodalRiskEngine
from src.risk_engine.risk_categories import (
    CATEGORY_APPOINTMENT,
    CATEGORY_CRITICAL,
    CATEGORY_MONITORING,
    CLINICAL_WEIGHT,
    LIFESTYLE_WEIGHT,
)
from src.alerts.alert_manager import AlertManager
from src.analytics.history_service import HistoryService
from src.risk_engine.risk_explanation import DISCLAIMER_TEXT
from src.security.audit_logger import log_event
from src.security.input_validator import validate_lifestyle_text_length
from src.utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="HeartGuard Risk Assessment", layout="wide")

# ── Authorization ────────────────────────────────────────────────────────────
require_authentication()
current_user = get_current_user()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**{current_user['name']}**")
    st.caption(f"Role: `{current_user['role']}`")
    st.divider()
    if st.button("🚪 Log Out", use_container_width=True, key="risk_logout"):
        log_event("logout", "SUCCESS", user_id=current_user["id"], role=current_user["role"])
        clear_session()
        st.switch_page("pages/login.py")

st.title("HeartGuard Risk Assessment")
st.markdown(
    "Combine clinical information with lifestyle factors for a multimodal cardiovascular risk assessment."
)

st.markdown(
    "**Disclaimer:** HeartGuard is an academic/research prototype and is not a "
    "medical diagnostic system. Model predictions are experimental estimates based "
    "on the provided data and should not replace evaluation or advice from a "
    "qualified healthcare professional."
)
st.caption(DISCLAIMER_TEXT)

st.divider()

# ---------------------------------------------------------------------------
# Check Prerequisites
# ---------------------------------------------------------------------------
best_model_path = REPORT_DIRECTORY / "best_model.json"
preprocessor_path = MODEL_DIRECTORY / "preprocessor.pkl"

if not best_model_path.exists() or not preprocessor_path.exists():
    st.warning("Clinical models and preprocessor must be trained before performing risk assessment.")
    st.info("Run `python scripts/train_models.py` to generate required model artifacts.")
    st.stop()

# ---------------------------------------------------------------------------
# Section 1: Clinical Patient Features Input
# ---------------------------------------------------------------------------

st.markdown("### 1. Clinical Information")
st.caption("Enter patient physiological measurements and diagnostic test parameters.")

col_c1, col_c2, col_c3 = st.columns(3)

with col_c1:
    st.markdown("**Patient Demographics**")
    age = st.number_input("Age (years)", min_value=1, max_value=120, value=55, step=1, help="Patient age in years.")
    sex = st.selectbox(
        "Sex",
        options=[0, 1],
        format_func=lambda x: "Female" if x == 0 else "Male",
        index=1,
        help="Biological sex.",
    )
    chest_pain_type = st.selectbox(
        "Chest Pain Type",
        options=[0, 1, 2, 3],
        format_func=lambda x: {
            0: "Typical Angina (0)",
            1: "Atypical Angina (1)",
            2: "Non-anginal Pain (2)",
            3: "Asymptomatic (3)",
        }.get(x, str(x)),
        index=0,
        help="Type of chest pain reported by patient.",
    )

with col_c2:
    st.markdown("**Clinical Measurements**")
    resting_bp = st.number_input(
        "Resting Blood Pressure (mm Hg)",
        min_value=50,
        max_value=250,
        value=130,
        step=1,
        help="Resting blood pressure upon hospital admission.",
    )
    cholesterol = st.number_input(
        "Serum Cholesterol (mg/dl)",
        min_value=50,
        max_value=600,
        value=220,
        step=1,
        help="Serum cholesterol level.",
    )
    max_heart_rate = st.number_input(
        "Maximum Heart Rate Achieved",
        min_value=50,
        max_value=250,
        value=150,
        step=1,
        help="Peak heart rate during exercise test.",
    )

with col_c3:
    st.markdown("**Diagnostic Test Findings**")
    st_depression = st.number_input(
        "ST Depression (Oldpeak)",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.1,
        format="%.1f",
        help="ST depression induced by exercise relative to rest.",
    )
    fasting_blood_sugar = st.selectbox(
        "Fasting Blood Sugar > 120 mg/dl",
        options=[0, 1],
        format_func=lambda x: "No (<= 120 mg/dl)" if x == 0 else "Yes (> 120 mg/dl)",
        index=0,
    )
    resting_ecg = st.selectbox(
        "Resting Electrocardiogram (ECG)",
        options=[0, 1, 2],
        format_func=lambda x: {
            0: "Normal (0)",
            1: "ST-T Wave Abnormality (1)",
            2: "Left Ventricular Hypertrophy (2)",
        }.get(x, str(x)),
        index=0,
    )
    exercise_angina = st.selectbox(
        "Exercise-Induced Angina",
        options=[0, 1],
        format_func=lambda x: "No" if x == 0 else "Yes",
        index=0,
    )
    num_major_vessels = st.selectbox(
        "Major Vessels Colored by Fluoroscopy",
        options=[0, 1, 2, 3, 4],
        index=0,
        help="Number of major blood vessels (0-4).",
    )

clinical_data = {
    "age": age,
    "sex": sex,
    "chest_pain_type": chest_pain_type,
    "resting_bp": resting_bp,
    "cholesterol": cholesterol,
    "fasting_blood_sugar": fasting_blood_sugar,
    "resting_ecg": resting_ecg,
    "max_heart_rate": max_heart_rate,
    "exercise_angina": exercise_angina,
    "st_depression": st_depression,
    "num_major_vessels": num_major_vessels,
}

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Lifestyle Narrative Input
# ---------------------------------------------------------------------------

st.markdown("### 2. Lifestyle Narrative")
st.caption("Provide self-reported information on smoking, diet, sleep duration, exercise, and family history.")

sample_lifestyle = (
    "I smoke occasionally, eat fried food, work a desk job, and sleep about 5 hours."
)

lifestyle_text = st.text_area(
    label="Describe your lifestyle",
    value="",
    placeholder=sample_lifestyle,
    height=120,
    help="Include habits like daily diet, workouts, cigarette use, hours of sleep, and family cardiac events.",
)

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Assessment Trigger & Execution
# ---------------------------------------------------------------------------

btn_col, _ = st.columns([2, 5])
with btn_col:
    assess_clicked = st.button("Calculate Overall Risk", type="primary", use_container_width=True)

if assess_clicked:
    if not lifestyle_text or not lifestyle_text.strip():
        st.warning("Lifestyle description is required for multimodal assessment. Please enter lifestyle details above.")
    else:
        # Validate lifestyle text length (security check) — text is NOT logged
        try:
            validate_lifestyle_text_length(lifestyle_text)
        except ValueError as ve:
            st.error(str(ve))
            st.stop()

        with st.spinner("Executing multimodal risk assessment pipeline..."):
            try:
                engine = MultimodalRiskEngine()
                assessment = engine.assess(
                    clinical_data=clinical_data,
                    lifestyle_text=lifestyle_text,
                    include_shap=True,
                )

                # Process emergency alert status (Phase 8)
                alert_manager = AlertManager()
                alert_res = alert_manager.process_risk_result(
                    risk_result=assessment,
                    patient_context=clinical_data,
                )
                alert_status = alert_res.get("notification_status", "NOT_TRIGGERED")
                assessment_id = alert_res.get("assessment_id")

                # Persist assessment record in history database (Phase 10)
                saved_record = HistoryService.save_assessment(
                    user_id=current_user["id"],
                    multimodal_result=assessment,
                    alert_status=alert_status,
                    assessment_id=assessment_id,
                )

                # Store in session state tagged with user_id for isolation
                st.session_state["assessment_result"] = assessment
                st.session_state["assessment_user_id"] = current_user["id"]
                st.session_state["assessment_saved_record"] = saved_record
                st.session_state["alert_result"] = alert_res

            except Exception as exc:
                # NEVER display raw traceback to the user
                logger.error(
                    "Risk assessment failed for user_id=%s: %s",
                    current_user["id"],
                    type(exc).__name__,  # type only — no patient data in log
                )
                st.error("Something went wrong during the risk assessment. Please try again.")

# ---------------------------------------------------------------------------
# Section 4: Assessment Results Display
# ---------------------------------------------------------------------------

if "assessment_result" in st.session_state:
    res = st.session_state["assessment_result"]
    comb = res["combined"]
    clin = res["clinical"]
    life = res["lifestyle"]
    contrib = res["contributions"]

    overall_risk = comb["risk"]
    category = comb["category"]
    action = comb["recommended_action"]

    st.divider()
    res_hdr_col, link_col = st.columns([3, 1])
    with res_hdr_col:
        st.markdown("## Multimodal Assessment Results")
        if "assessment_saved_record" in st.session_state:
            s_rec = st.session_state["assessment_saved_record"]
            st.caption(f"Assessment ID: `{s_rec.assessment_id}` · Saved to History · Alert Status: `{s_rec.alert_status}`")
    with link_col:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.page_link("pages/history.py", label="📜 View History & Reports →")

    # Overall Summary Banner
    if category == CATEGORY_CRITICAL:
        st.error(
            f"### 🔴 CRITICAL RISK — {overall_risk:.1f}%\n\n"
            f"**Recommended Action:** {action}"
        )
    elif category == CATEGORY_APPOINTMENT:
        st.warning(
            f"### 🟡 ELEVATED RISK (APPOINTMENT RECOMMENDED) — {overall_risk:.1f}%\n\n"
            f"**Recommended Action:** {action}"
        )
    else:
        st.success(
            f"### 🟢 LOWER RISK (REGULAR MONITORING) — {overall_risk:.1f}%\n\n"
            f"**Recommended Action:** {action}"
        )

    # Key Metrics Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Overall Risk Score", f"{overall_risk:.1f}%")
        st.progress(overall_risk / 100.0)
    with m2:
        st.metric("Clinical Risk (70%)", f"{clin['risk']:.1f}%")
        st.caption(f"Contribution: +{contrib['clinical']:.1f} pts")
    with m3:
        st.metric("Lifestyle Risk (30%)", f"{life['risk']:.1f}%")
        st.caption(f"Contribution: +{contrib['lifestyle']:.1f} pts")
    with m4:
        st.metric("Active Clinical Model", clin["model"].replace("_", " ").title())
        st.caption(f"Binary prediction: {clin['prediction']} (prob: {clin['probability']:.2f})")

    st.divider()

    # Two column layout: Visual Breakdown + Narrative Explanation
    col_vis, col_narrative = st.columns([1, 1])

    with col_vis:
        st.markdown("### Risk Component Breakdown")

        chart_df = pd.DataFrame(
            {
                "Component": ["Clinical Risk (Raw)", "Lifestyle Risk (Raw)", "Overall Multimodal Risk"],
                "Risk (%)": [clin["risk"], life["risk"], overall_risk],
            }
        ).set_index("Component")
        st.bar_chart(chart_df, y="Risk (%)", color="#3498db")

        st.markdown("#### Weighted Formula Calculation")
        st.code(
            f"Clinical Risk:   {clin['risk']:.1f}%  × 0.70  =  {contrib['clinical']:.2f} pts\n"
            f"Lifestyle Risk:  {life['risk']:.1f}%  × 0.30  =  {contrib['lifestyle']:.2f} pts\n"
            f"----------------------------------------------------\n"
            f"Overall Risk:                     =  {overall_risk:.2f}%",
            language=None,
        )

    with col_narrative:
        st.markdown("### Clinical Interpretation Narrative")
        st.info(res["overall_explanation"])

    st.divider()

    # Detailed Tabs: Clinical Explainability & Lifestyle Factors
    tab_clinical, tab_lifestyle = st.tabs(["🔬 Clinical ML & SHAP Explanation", "🏃 Lifestyle NLP Risk Signals"])

    with tab_clinical:
        st.markdown("#### Why did the clinical model predict this risk level?")
        if res.get("clinical_explanation_available") and res.get("clinical_explanation"):
            c_exp = res["clinical_explanation"]
            st.markdown(f"**Baseline Expected Value:** `{c_exp.get('base_value', 0.0):.4f}`")

            top_factors = c_exp.get("top_risk_factors", [])
            if top_factors:
                st.markdown("**Top Clinical Risk Drivers:**")
                for tf in top_factors:
                    st.markdown(f"- **{tf.get('clinical_label', tf.get('feature'))}** (SHAP: `+{tf.get('shap_value', 0.0):.4f}`)")

            waterfall_file = c_exp.get("waterfall_plot")
            if waterfall_file and Path(waterfall_file).exists():
                st.markdown("**SHAP Waterfall Contribution Plot:**")
                st.image(str(waterfall_file), use_container_width=True)

            st.caption("Visit the Explainable AI page for full interactive SHAP beeswarm and population rankings.")
        else:
            st.info("SHAP clinical explanation is not currently available for this prediction.")

    with tab_lifestyle:
        st.markdown("#### Detected Lifestyle Cardiovascular Risk Signals")
        det_factors = life.get("detected_factors", [])
        if det_factors:
            l_rows = []
            for f in det_factors:
                l_rows.append(
                    {
                        "Risk Factor": f["display_name"],
                        "Points": f"+{f['risk_points']}",
                        "Severity": f["severity"],
                        "Matched Terms": ", ".join(f["matched_terms"]),
                        "Evidence": f["evidence"],
                    }
                )
            st.dataframe(pd.DataFrame(l_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No predefined lifestyle risk factors were detected in the provided text.")

        if life.get("summary"):
            st.markdown("**Lifestyle Summary:**")
            st.code(life["summary"], language=None)
