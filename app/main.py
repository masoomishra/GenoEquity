"""GenoEquity CLI entrypoint (Streamlit-free version)."""

import argparse

from genoequity.gwas import load_prs_variants
from genoequity.gnomad import batch_fetch_frequencies
from genoequity.scoring import compute_variant_scores, compute_gap_index
from genoequity.report_builder import build_html_report


def main():
    # ----------------------------
    # CLI ARGUMENT PARSING
    # ----------------------------
    parser = argparse.ArgumentParser(
        description="GenoEquity PRS Bias Audit Tool"
    )

    parser.add_argument(
        "--gwas",
        required=True,
        help="GWAS accession ID (e.g., GCST004746)"
    )

    args = parser.parse_args()

    # ----------------------------
    # HEADER
    # ----------------------------
    print("\nGenoEquity PRS Audit\n")
    print(f"Input GWAS: {args.gwas}\n")

    # ----------------------------
    # STEP 1: GWAS VARIANTS
    # ----------------------------
    print("Fetching GWAS variants...")
    variants = load_prs_variants(args.gwas)

    rsids = [v.rsid for v in variants if v.rsid]

    print(f"Total variants loaded: {len(variants)}")

    # ----------------------------
    # STEP 2: GNOMAD FREQUENCIES
    # ----------------------------
    print(f"Fetching frequencies for {len(rsids)} variants from gnomAD...")
    variant_frequencies = batch_fetch_frequencies(rsids)

    # ----------------------------
    # STEP 3: SCORING
    # ----------------------------
    print("Computing scores...")

    flagged, coverage, reliability = compute_variant_scores(
        variant_frequencies,
        variants
    )

    gap = compute_gap_index(reliability)

    # ----------------------------
    # RESULTS
    # ----------------------------
    print("\nRESULTS:\n")

    print("Flagged Variants:", flagged[:10], "...\n")
    print("Coverage:", coverage)
    print("Reliability:", reliability)
    print("Gap index:", gap)

    # ----------------------------
    # HTML REPORT GENERATION
    # ----------------------------
    print("\nGenerating HTML report...")

    html = build_html_report(
        args.gwas,
        len(variants),
        len(rsids),
        flagged,
        coverage,
        reliability,
        gap
    )

    with open("report.html", "w") as f:
        f.write(html)

    print("Report saved as report.html")


if __name__ == "__main__":
    main()