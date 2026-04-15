"""Population explorer for gnomAD allele frequencies."""

import plotly.graph_objects as go
import streamlit as st

from genoequity.gnomad import batch_fetch_frequencies

ANCESTRY_ORDER = ["AFR", "AMR", "ASJ", "EAS", "FIN", "NFE", "SAS"]

st.header("Population Explorer")

rsid_input = st.text_area(
    "Paste rsIDs (comma-separated)",
    placeholder="rs12123821, rs2736155, rs10156602",
)

if st.button("Fetch frequencies"):
    rsids = [r.strip() for r in rsid_input.split(",") if r.strip()]
    if not rsids:
        st.error("Please provide at least one rsID.")
    else:
        with st.spinner("Querying gnomAD..."):
            freqs = batch_fetch_frequencies(rsids)

        for rsid, pops in freqs.items():
            if not pops:
                st.warning(f"No frequency data found for {rsid}.")
                continue
            values = [pops.get(pop, {}).get("af", 0.0) for pop in ANCESTRY_ORDER]
            fig = go.Figure(
                data=[go.Bar(x=ANCESTRY_ORDER, y=values, marker_color="#2E7D8C")]
            )
            fig.update_layout(
                title=f"Allele Frequency by Ancestry: {rsid}",
                xaxis_title="Population",
                yaxis_title="Allele Frequency",
                yaxis=dict(range=[0, 1]),
            )
            st.plotly_chart(fig, use_container_width=True)
