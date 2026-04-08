"""Audit page for GenoEquity."""

from pathlib import Path

import json
import streamlit as st

from genoequity.models import AuditResult, AuditSummary
from genoequity.report import generate_report

EXAMPLES_DIR = Path("data/examples")
EXAMPLE_IDS = {
    "Colorectal Cancer": "GCST90016564",
    "Breast Cancer": "GCST90029052",
    "Prostate Cancer": "GCST90018999",
}

st.header("PRS Bias Audit")

with st.sidebar:
    st.subheader("Examples")
    example_label = st.selectbox("Choose a precomputed example", list(EXAMPLE_IDS.keys()))
    use_example = st.button("Load example")

accession = st.text_input("GWAS Catalog accession", value=EXAMPLE_IDS[example_label])

if use_example:
    example_path = EXAMPLES_DIR / f"{EXAMPLE_IDS[example_label]}.json"
    if example_path.exists():
        payload = json.loads(example_path.read_text())
        audit = AuditResult.model_validate(payload)
        st.success("Loaded example audit.")
    else:
        st.error("Example data not found. Run scripts/precompute_examples.py.")
        audit = None
else:
    audit = None

if st.button("Run audit"):
    st.warning("Pipeline not wired yet. This scaffold expects cached examples.")

if audit:
    summary = audit.summary
    st.subheader("Summary")
    st.metric("Total Variants", summary.total_variants)
    st.dataframe(summary.coverage_scores, use_container_width=True)
    st.dataframe(summary.reliability_scores, use_container_width=True)

    report_path = Path("data/reports") / f"genoequity_audit_{summary.accession}.pdf"
    generate_report(audit, report_path)
    st.download_button(
        "Download Audit Report",
        data=report_path.read_bytes(),
        file_name=report_path.name,
        mime="application/pdf",
    )
