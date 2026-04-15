"""Audit page for GenoEquity."""

from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st

from genoequity.gnomad import batch_fetch_frequencies
from genoequity.gwas import load_prs_variants
from genoequity.models import AuditResult, AuditSummary
from genoequity.report import generate_report
from genoequity.scoring import compute_gap_index, compute_variant_scores

EXAMPLES_DIR = Path("data/examples")
EXAMPLE_IDS = {
    "Colorectal Cancer": "GCST90016564",
    "Breast Cancer": "GCST90029052",
    "Prostate Cancer": "GCST90018999",
}
ANCESTRY_ORDER = ["AFR", "AMR", "ASJ", "EAS", "FIN", "NFE", "SAS"]


@st.cache_data(show_spinner=False)
def _cached_variants(accession: str):
    return load_prs_variants(accession)


@st.cache_data(show_spinner=False)
def _cached_frequencies(rsids: tuple[str, ...]):
    return batch_fetch_frequencies(list(rsids))


def _build_audit(accession: str) -> AuditResult:
    with st.spinner("Fetching variants from GWAS Catalog..."):
        variants = _cached_variants(accession)

    rsids = [v.rsid or v.variant_id for v in variants if v.rsid or v.variant_id]
    with st.spinner(f"Querying gnomAD for {len(rsids)} variants..."):
        freqs = _cached_frequencies(tuple(rsids))

    with st.spinner("Computing scores..."):
        flagged, coverage, reliability = compute_variant_scores(freqs, variants)
        gap = compute_gap_index(reliability)

    summary = AuditSummary(
        accession=accession,
        model_name=None,
        total_variants=len(variants),
        coverage_scores=coverage,
        reliability_scores=reliability,
        gap_index=gap,
        flagged_variants=flagged,
    )
    return AuditResult(summary=summary, variants=variants, frequencies=[], coverage=[])


st.header("PRS Bias Audit")

with st.sidebar:
    st.subheader("Examples")
    example_label = st.selectbox("Choose a precomputed example", list(EXAMPLE_IDS.keys()))
    use_example = st.button("Load example")

accession = st.text_input("GWAS Catalog accession", value=EXAMPLE_IDS[example_label])

audit = None
if use_example:
    example_path = EXAMPLES_DIR / f"{EXAMPLE_IDS[example_label]}.json"
    if example_path.exists():
        payload = json.loads(example_path.read_text())
        audit = AuditResult.model_validate(payload)
        st.success("Loaded example audit.")
    else:
        st.error("Example data not found. Run scripts/precompute_examples.py.")

if st.button("Run audit"):
    audit = _build_audit(accession)

if audit:
    summary = audit.summary
    st.subheader("Summary")
    st.metric("Total Variants", summary.total_variants)

    heatmap_df = pd.DataFrame(
        {
            "Coverage": [summary.coverage_scores.get(a, 0.0) for a in ANCESTRY_ORDER],
            "Reliability": [summary.reliability_scores.get(a, 0.0) for a in ANCESTRY_ORDER],
            "Gap": [summary.gap_index.get(a, 0.0) for a in ANCESTRY_ORDER],
        },
        index=ANCESTRY_ORDER,
    )
    fig = px.imshow(
        heatmap_df,
        text_auto=".2f",
        color_continuous_scale="Viridis",
        aspect="auto",
    )
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

    flagged_rows = []
    effect_map = {v.rsid or v.variant_id: v.effect_size for v in audit.variants}
    for variant_id in summary.flagged_variants:
        flagged_rows.append(
            {"Variant": variant_id, "Effect Size": effect_map.get(variant_id)}
        )
    if flagged_rows:
        st.dataframe(flagged_rows, use_container_width=True)
    else:
        st.info("No flagged high-impact variants.")

    report_bytes = generate_report(audit)
    report_name = f"genoequity_audit_{summary.accession}.pdf"
    st.download_button(
        "Download Audit Report",
        data=report_bytes,
        file_name=report_name,
        mime="application/pdf",
    )
