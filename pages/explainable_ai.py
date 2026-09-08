"""Explainable AI page for HeartGuard (Phase 9 — Admin Only).

SHAP-based population-level prediction explanations for the clinical ML model.
Patients can view their own SHAP results on the Risk Assessment page.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd
import streamlit as st

from config.settings import MODEL_DIRECTORY, PROCESSED_DATA_DIRECTORY, REPORT_DIRECTORY
from src.auth.authorization import require_role
from src.auth.session_manager import get_current_user
from src.ui import render_sidebar, inject_global_theme

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Explainable AI", layout="wide")

# ── Authorization (Admin only) ───────────────────────────────────────────────
require_role("ADMIN")
current_user = get_current_user()

render_sidebar()
inject_global_theme()

st.title("Explainable AI")

st.markdown(
    "**Disclaimer:** HeartGuard is an academic/research prototype and is not a "
    "medical diagnostic system. Model predictions are experimental estimates based "
    "on the provided data and should not replace evaluation or advice from a "
    "qualified healthcare professional."
)
st.caption(
    "SHAP explanations describe model behavior and should not be "
    "interpreted as clinical causation."
)

st.divider()

# ---------------------------------------------------------------------------
# Check prerequisites
# ---------------------------------------------------------------------------

best_model_path = REPORT_DIRECTORY / "best_model.json"
feature_names_path = MODEL_DIRECTORY / "feature_names.json"
preprocessor_path = MODEL_DIRECTORY / "preprocessor.pkl"

if not best_model_path.exists() or not feature_names_path.exists():
    st.warning("Train the HeartGuard models before using Explainable AI.")
    st.info(
        "Run: `python scripts/train_models.py` to generate model artifacts."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Load model info
# ---------------------------------------------------------------------------

with open(best_model_path, "r", encoding="utf-8") as f:
    best_info = json.load(f)

model_name = best_info["model_name"]

with open(feature_names_path, "r", encoding="utf-8") as f:
    feature_names = json.load(f)

# Determine explainer type
from src.explainability.shap_explainer import _is_tree_model, _is_linear_model

model_path = MODEL_DIRECTORY / f"{model_name}.pkl"
if model_path.exists():
    import joblib
    _temp_model = joblib.load(model_path)
    if _is_tree_model(_temp_model):
        explainer_type = "TreeExplainer"
    elif _is_linear_model(_temp_model):
        explainer_type = "LinearExplainer"
    else:
        explainer_type = "KernelExplainer"
    del _temp_model
else:
    explainer_type = "Unknown"

# ---------------------------------------------------------------------------
# Section 1: Selected Model
# ---------------------------------------------------------------------------

st.markdown("### Selected Model")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Best Model", model_name.replace("_", " ").title())
with col2:
    st.metric("Explainer", explainer_type)
with col3:
    cv_auc = best_info.get("cv_roc_auc_mean", "N/A")
    if isinstance(cv_auc, (int, float)):
        st.metric("CV ROC-AUC", f"{cv_auc:.4f}")
    else:
        st.metric("CV ROC-AUC", cv_auc)

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Patient Input
# ---------------------------------------------------------------------------

st.markdown("### Patient Input")

# Canonical clinical features with sensible defaults
col_a, col_b = st.columns(2)

with col_a:
    age = st.number_input("Age", min_value=1, max_value=120, value=55, step=1)
    sex = st.selectbox("Sex", options=[0, 1], format_func=lambda x: "Female" if x == 0 else "Male", index=1)
    chest_pain_type = st.selectbox("Chest Pain Type", options=[0, 1, 2, 3], index=0)
    resting_bp = st.number_input("Resting Blood Pressure (mm Hg)", min_value=50, max_value=250, value=130, step=1)
    cholesterol = st.number_input("Cholesterol (mg/dl)", min_value=50, max_value=600, value=200, step=1)

with col_b:
    fasting_blood_sugar = st.selectbox("Fasting Blood Sugar > 120 mg/dl", options=[0, 1], format_func=lambda x: "No" if x == 0 else "Yes", index=0)
    resting_ecg = st.selectbox("Resting ECG", options=[0, 1, 2], index=0)
    max_heart_rate = st.number_input("Maximum Heart Rate", min_value=50, max_value=250, value=150, step=1)
    exercise_angina = st.selectbox("Exercise-Induced Angina", options=[0, 1], format_func=lambda x: "No" if x == 0 else "Yes", index=0)
    st_depression = st.number_input("ST Depression", min_value=0.0, max_value=10.0, value=1.0, step=0.1, format="%.1f")
    num_major_vessels = st.selectbox("Number of Major Vessels (0-4)", options=[0, 1, 2, 3, 4], index=0)

patient_data = {
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

# ---------------------------------------------------------------------------
# Section 3: Explain Prediction
# ---------------------------------------------------------------------------

st.divider()
st.markdown("### Model Prediction & Explanation")

if st.button("Explain Prediction", type="primary", use_container_width=True):
    with st.spinner("Loading model and computing SHAP explanation..."):
        try:
            from src.explainability.service import SHAPExplainerService

            service = SHAPExplainerService()
            explanation = service.explain_patient(patient_data, save_artifacts=True)

            # --- Model Prediction ---
            st.markdown("#### Model Prediction")
            pred_col1, pred_col2 = st.columns(2)
            with pred_col1:
                pred_label = "Presence" if explanation["prediction"] == 1 else "Absence"
                st.metric("Prediction", pred_label)
            with pred_col2:
                if explanation["probability"] is not None:
                    st.metric("Probability", f"{explanation['probability']:.1%}")

            st.caption(f"Base value (expected model output): {explanation['base_value']:.4f}")

            st.divider()

            # --- SHAP Waterfall ---
            st.markdown("#### SHAP Waterfall Plot")
            waterfall_path = explanation.get("waterfall_plot")
            if waterfall_path and Path(waterfall_path).exists():
                st.image(str(waterfall_path), use_container_width=True)
            else:
                st.info("Waterfall plot not available.")

            st.divider()

            # --- Top Contributing Features ---
            st.markdown("#### Top Contributing Features")
            features = explanation.get("features", [])
            if features:
                feat_df = pd.DataFrame(features)
                display_df = feat_df[["clinical_label", "value", "shap_value", "direction"]].copy()
                display_df.columns = ["Feature", "Value", "SHAP Value", "Direction"]
                display_df["SHAP Value"] = display_df["SHAP Value"].apply(lambda x: f"{x:+.4f}")
                st.dataframe(display_df.head(10), use_container_width=True, hide_index=True)

            st.divider()

            # --- Risk Factors ---
            risk_cols = st.columns(2)

            with risk_cols[0]:
                st.markdown("#### Factors Increasing Model Risk")
                positive = [f for f in features if f["direction"] == "increases_risk"][:5]
                if positive:
                    for feat in positive:
                        st.markdown(
                            f"- **{feat['clinical_label']}** "
                            f"(value: {feat.get('value', 'N/A')}, "
                            f"SHAP: {feat['shap_value']:+.4f})"
                        )
                else:
                    st.info("No significant risk-increasing factors.")

            with risk_cols[1]:
                st.markdown("#### Factors Decreasing Model Risk")
                negative = [f for f in features if f["direction"] == "decreases_risk"][:5]
                if negative:
                    for feat in negative:
                        st.markdown(
                            f"- **{feat['clinical_label']}** "
                            f"(value: {feat.get('value', 'N/A')}, "
                            f"SHAP: {feat['shap_value']:+.4f})"
                        )
                else:
                    st.info("No significant risk-decreasing factors.")

            st.divider()

            # --- Human-Readable Explanation ---
            st.markdown("#### Human-Readable Explanation")
            st.code(explanation.get("human_readable_summary", ""), language=None)

            # --- Local Importance Plot ---
            local_plot = explanation.get("local_importance_plot")
            if local_plot and Path(local_plot).exists():
                st.markdown("#### Feature Importance Visualization")
                st.image(str(local_plot), use_container_width=True)

        except Exception as exc:
            logger.exception("SHAP explanation failed: %s", exc)
            st.error("Unable to generate explanation. Please try again or contact support.")

# ---------------------------------------------------------------------------
# Section 4: Global Feature Importance
# ---------------------------------------------------------------------------

st.divider()
st.markdown("### Global Model Explanation")

if st.button("Compute Global Feature Importance", use_container_width=True):
    with st.spinner("Computing SHAP values across training data..."):
        try:
            from src.explainability.service import SHAPExplainerService

            service = SHAPExplainerService()
            global_imp = service.global_importance(save_artifacts=True)

            # Display ranked features
            st.markdown("#### Ranked Features by Mean |SHAP Value|")
            display_global = global_imp[["rank", "clinical_label", "mean_absolute_shap"]].copy()
            display_global.columns = ["Rank", "Feature", "Mean |SHAP|"]
            display_global["Mean |SHAP|"] = display_global["Mean |SHAP|"].apply(lambda x: f"{x:.4f}")
            st.dataframe(display_global, use_container_width=True, hide_index=True)

            # Display plots
            global_plot_path = REPORT_DIRECTORY / "figures" / "shap_global_importance.png"
            if global_plot_path.exists():
                st.markdown("#### Global Feature Importance Chart")
                st.image(str(global_plot_path), use_container_width=True)

            summary_plot_path = REPORT_DIRECTORY / "figures" / "shap_summary.png"
            if summary_plot_path.exists():
                st.markdown("#### SHAP Summary (Beeswarm) Plot")
                st.image(str(summary_plot_path), use_container_width=True)

        except Exception as exc:
            logger.exception("Global importance computation failed: %s", exc)
            st.error("Unable to compute global feature importance. Please try again or contact support.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    "SHAP (SHapley Additive exPlanations) explains individual predictions by "
    "computing the contribution of each feature to the prediction. The base value "
    "represents the average model output, and SHAP values show how each feature "
    "pushes the prediction above or below the base value."
)
