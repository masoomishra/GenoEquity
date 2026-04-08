"""Streamlit entrypoint for GenoEquity."""

import streamlit as st

st.set_page_config(page_title="GenoEquity", page_icon="DNA", layout="wide")

st.title("GenoEquity")
st.caption("Ancestry-Aware Cancer PRS Bias Auditor")

st.markdown(
    """
    Use the pages on the left to run a PRS audit, explore population coverage,
    or learn about the methodology.
    """
)

st.info("Start with the Audit page to analyze a GWAS Catalog accession.")
