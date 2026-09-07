"""Model Performance page for HeartGuard."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from config.settings import MODEL_DIRECTORY, REPORT_DIRECTORY

st.set_page_config(page_title="Model Performance", layout="wide")
st.title("Model Performance")

st.markdown(
    "**Disclaimer:** HeartGuard is an academic/research prototype and is not a "
    "medical diagnostic system. Model predictions are experimental estimates based "
    "on the provided data and should not replace evaluation or advice from a "
    "qualified healthcare professional."
)

st.divider()


# ---------------------------------------------------------------------------
# Helper: load results
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> dict | None:
    """Safely load a JSON file."""
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_csv(path: Path) -> pd.DataFrame | None:
    """Safely load a CSV file."""
    if not path.exists():
        return None
    return pd.read_csv(path, index_col=0)


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------


model_results = _load_json(REPORT_DIRECTORY / "model_results.json")
best_model_info = _load_json(REPORT_DIRECTORY / "best_model.json")
comparison_df = _load_csv(REPORT_DIRECTORY / "model_comparison.csv")

if model_results is None:
    st.info(
        "No training results found. Run model training first:\n\n"
        "```bash\npython scripts/train_models.py\n```"
    )
    st.stop()

# ---- Best model banner ----
if best_model_info:
    st.subheader("Best Model")
    best = best_model_info["model_name"]
    auc = best_model_info.get("cv_roc_auc_mean", "N/A")
    f1 = best_model_info.get("cv_f1_mean", "N/A")
    st.success(f"**{best}** — CV ROC-AUC: {auc:.4f}, CV F1: {f1:.4f}")

st.divider()

# ---- CV Results ----
st.subheader("Cross-Validation Results (5-fold Stratified)")
cv_data = model_results.get("cv_results", {})
if cv_data:
    cv_rows = []
    for name, metrics in cv_data.items():
        cv_rows.append({
            "Model": name,
            "Accuracy (mean±std)": f"{metrics.get('accuracy_mean', 0):.4f} ± {metrics.get('accuracy_std', 0):.4f}",
            "Precision (mean±std)": f"{metrics.get('precision_mean', 0):.4f} ± {metrics.get('precision_std', 0):.4f}",
            "Recall (mean±std)": f"{metrics.get('recall_mean', 0):.4f} ± {metrics.get('recall_std', 0):.4f}",
            "F1 (mean±std)": f"{metrics.get('f1_mean', 0):.4f} ± {metrics.get('f1_std', 0):.4f}",
            "ROC-AUC (mean±std)": f"{metrics.get('roc_auc_mean', 0):.4f} ± {metrics.get('roc_auc_std', 0):.4f}",
        })
    st.dataframe(pd.DataFrame(cv_rows).set_index("Model"), use_container_width=True)

st.divider()

# ---- Test Set Results ----
st.subheader("Test Set Metrics")
test_data = model_results.get("test_results", {})
if test_data:
    test_df = pd.DataFrame(test_data).T
    test_df.index.name = "Model"
    st.dataframe(test_df.round(4), use_container_width=True)

st.divider()

# ---- Visualisations ----
st.subheader("Visualisations")
figures_dir = REPORT_DIRECTORY / "figures"

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### ROC Curve Comparison")
    roc_path = figures_dir / "model_roc_comparison.png"
    if roc_path.exists():
        st.image(str(roc_path), use_container_width=True)
    else:
        st.info("ROC comparison figure not found.")

    st.markdown("#### Neural Network Training Curves")
    nn_path = figures_dir / "neural_network_training_curves.png"
    if nn_path.exists():
        st.image(str(nn_path), use_container_width=True)
    else:
        st.info("Neural network training curves not found.")

with col2:
    st.markdown("#### Metrics Comparison")
    metrics_path = figures_dir / "model_metrics_comparison.png"
    if metrics_path.exists():
        st.image(str(metrics_path), use_container_width=True)
    else:
        st.info("Metrics comparison figure not found.")

    st.markdown("#### Feature Importance")
    feat_path = figures_dir / "feature_importance.png"
    if feat_path.exists():
        st.image(str(feat_path), use_container_width=True)
    else:
        st.info("Feature importance figure not found.")

st.divider()

# ---- Confusion Matrices ----
st.subheader("Confusion Matrices")
model_names = ["logistic_regression", "random_forest", "xgboost", "neural_network"]
cols = st.columns(2)
for i, name in enumerate(model_names):
    with cols[i % 2]:
        st.markdown(f"#### {name.replace('_', ' ').title()}")
        cm_path = figures_dir / f"{name}_confusion_matrix.png"
        if cm_path.exists():
            st.image(str(cm_path), use_container_width=True)
        else:
            st.info(f"Confusion matrix for {name} not found.")

st.divider()

# ---- Model selection note ----
st.caption(
    "Model selection is based on ROC-AUC (primary) and F1 (secondary) on "
    "5-fold stratified cross-validation. No model is hardcoded to be preferred."
)
