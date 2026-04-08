"""About and methodology page."""

import streamlit as st

st.header("About GenoEquity")

st.markdown(
    """
    GenoEquity audits published cancer PRS models for ancestry representation bias.
    It combines GWAS Catalog PRS variants with gnomAD v4.1 allele frequencies to
    compute coverage, reliability, and gap indices across populations.
    """
)

st.subheader("Limitations")
st.markdown(
    """
    - Effect sizes are derived from European GWAS and may not transfer.
    - gnomAD is not a clinical cohort; coverage does not equal clinical validity.
    - LD structure differences are not modeled.
    - Coverage thresholds are design decisions.
    """
)
