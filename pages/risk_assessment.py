"""Risk Assessment page for HeartGuard."""

import streamlit as st

st.title("Risk Assessment")

st.markdown(
    "**Disclaimer:** HeartGuard is an academic/research prototype and is not a "
    "medical diagnostic system. Model predictions are experimental estimates based "
    "on the provided data and should not replace evaluation or advice from a "
    "qualified healthcare professional."
)

st.divider()

st.info(
    "Clinical risk prediction will be available after the ML pipeline is implemented."
)

st.markdown("### Planned Features")

st.markdown(
    "- Clinical data input form\n"
    "- Machine learning risk prediction\n"
    "- Risk level classification\n"
    "- Probability scoring"
)

st.divider()

st.info("Module under development. Coming in Phase 6.")
