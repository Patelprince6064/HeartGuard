"""Lifestyle Risk Analyzer Streamlit Page for HeartGuard (Phase 6).

Provides an interactive user interface to analyze free-text lifestyle
descriptions for cardiovascular risk signals using rule-based NLP.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.nlp.explanation import DISCLAIMER_TEXT
from src.nlp.lifestyle_analyzer import MAX_INPUT_CHARACTERS, LifestyleAnalyzer

st.set_page_config(page_title="Lifestyle Risk Analyzer", layout="wide")

st.title("Lifestyle Risk Analyzer")
st.markdown(
    "Describe your lifestyle habits and HeartGuard will identify potential "
    "lifestyle risk signals using predefined cardiovascular risk factors."
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
# Section 1: Patient Input
# ---------------------------------------------------------------------------

st.markdown("### Lifestyle Description")
st.markdown(
    "Enter a detailed or brief description of daily habits, physical activity, "
    "diet, sleep duration, family history, smoking, and alcohol consumption."
)

sample_placeholder = (
    "Example: I smoke about 10 cigarettes a day, eat oily food, work a desk job, "
    "sleep 5 hours, drink occasionally, and do not exercise regularly."
)

user_text = st.text_area(
    label="Describe your lifestyle",
    value="",
    placeholder=sample_placeholder,
    height=150,
    help="Describe daily habits such as diet, exercise, smoking, alcohol, sleep, and family history.",
)

col_actions, col_info = st.columns([1, 3])
with col_actions:
    analyze_clicked = st.button("Analyze Lifestyle", type="primary", use_container_width=True)
with col_info:
    char_count = len(user_text)
    if char_count > 0:
        st.caption(f"{char_count:,} / {MAX_INPUT_CHARACTERS:,} characters")

# ---------------------------------------------------------------------------
# Section 2: Analysis Execution & Results
# ---------------------------------------------------------------------------

if analyze_clicked:
    if not user_text or not user_text.strip():
        st.warning("Please describe your lifestyle before running the analysis.")
    elif len(user_text) > MAX_INPUT_CHARACTERS:
        st.error(
            f"Input exceeds maximum allowed limit of {MAX_INPUT_CHARACTERS:,} characters. "
            f"Currently: {len(user_text):,} characters. Please shorten your description."
        )
    else:
        with st.spinner("Analyzing lifestyle description with HeartGuard NLP..."):
            analyzer = LifestyleAnalyzer()
            result = analyzer.analyze(user_text)

            score = result["lifestyle_score"]
            category = result["risk_category"]
            detected = result["detected_risk_factors"]
            top_factors = result["top_risk_factors"]
            summary = result["summary"]

            st.divider()
            st.markdown("### Analysis Results")

            # Metrics Row
            m_col1, m_col2, m_col3 = st.columns(3)

            with m_col1:
                st.metric("Lifestyle Risk Score", f"{score} / 100")
                st.progress(score / 100.0)

            with m_col2:
                # Color code category
                color_map = {
                    "LOW": "🟢",
                    "MODERATE": "🟡",
                    "HIGH": "🟠",
                    "CRITICAL": "🔴",
                }
                icon = color_map.get(category, "⚪")
                st.metric("Risk Category", f"{icon} {category}")
                st.caption("Thresholds: 0-29 Low, 30-59 Mod, 60-84 High, 85+ Crit")

            with m_col3:
                st.metric("Detected Risk Factors", len(detected))
                st.caption(f"{len(result.get('tokens', []))} tokens processed")

            st.divider()

            # If no risk factors detected
            if not detected:
                st.info(
                    "No predefined lifestyle risk factors were detected in the provided text.\n\n"
                    "Note: The analyzer checks exclusively for predefined lifestyle indicators "
                    "(smoking, inactivity, unhealthy diet, sleep < 6h, family cardiac history, alcohol). "
                    "This does not represent a complete cardiovascular medical evaluation."
                )
            else:
                # Two column layout: Table on left, breakdown chart on right
                layout_col1, layout_col2 = st.columns([3, 2])

                with layout_col1:
                    st.markdown("#### Detected Risk Factors")

                    table_rows = []
                    for f in detected:
                        table_rows.append(
                            {
                                "Risk Factor": f["display_name"],
                                "Points": f"+{f['risk_points']}",
                                "Severity": f["severity"],
                                "Matched Term(s)": ", ".join(f["matched_terms"]),
                                "Evidence Context": f["evidence"],
                            }
                        )
                    table_df = pd.DataFrame(table_rows)
                    st.dataframe(table_df, use_container_width=True, hide_index=True)

                    st.markdown("#### Top Risk Factors")
                    for i, tf in enumerate(top_factors, 1):
                        st.markdown(
                            f"{i}. **{tf['display_name']}** (`+{tf['risk_points']} pts` | "
                            f"Severity: *{tf['severity']}*) — *\"{tf['evidence']}\"*"
                        )

                with layout_col2:
                    st.markdown("#### Risk Contribution Breakdown")

                    chart_data = pd.DataFrame(
                        {
                            "Risk Factor": [f["display_name"] for f in detected],
                            "Risk Points": [f["risk_points"] for f in detected],
                        }
                    ).set_index("Risk Factor")

                    st.bar_chart(chart_data, y="Risk Points", color="#e74c3c")

                    # Score calculation callout
                    pts_sum = sum(f["risk_points"] for f in detected)
                    st.caption(
                        f"Raw Points Sum: **{pts_sum}** | "
                        f"Capped Score: **{score} / 100**"
                    )

                st.divider()

                # Human-Readable Explanation
                st.markdown("#### Clinical Interpretation Narrative")
                st.info(summary)

# ---------------------------------------------------------------------------
# Section 3: Reference Lexicon Accordion
# ---------------------------------------------------------------------------

with st.expander("ℹ️ HeartGuard Predefined Risk Lexicon Reference"):
    st.markdown(
        """
| Category | Configured Points | Severity | Primary Documented Triggers |
|---|---|---|---|
| **Smoking** | +25 | High | smoke, smoking, cigarette, cigarettes, tobacco, nicotine |
| **Physical Inactivity** | +15 | High | no exercise, sedentary, desk job, inactive |
| **Unhealthy Diet** | +18 | Moderate | oily food, junk, fast food, fried |
| **Poor Sleep** | +12 | Moderate | sleep < 6 hours, insomnia, poor sleep, lack of sleep |
| **Family History** | +20 | High | family history, heart attack, cardiac history |
| **Alcohol Use** | +10 | Low | drink alcohol, beer, wine, liquor, spirits |

*Note: The score is capped at 100. Disambiguation rules prevent non-alcoholic beverages (e.g. water) from triggering alcohol risk.*
    """
    )
