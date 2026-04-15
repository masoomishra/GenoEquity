"""Generate example audits using curated PRS CSV inputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from genoequity.curated import load_prs_csv
from genoequity.gnomad import batch_fetch_frequencies
from genoequity.models import AuditResult, AuditSummary
from genoequity.scoring import compute_gap_index, compute_variant_scores

EXAMPLES = {
    "GCST90016564": ("Colorectal Cancer", "data/examples/colorectal_prs.csv"),
    "GCST90029052": ("Breast Cancer", "data/examples/breast_prs.csv"),
    "GCST90018999": ("Prostate Cancer", "data/examples/prostate_prs.csv"),
}

OUTPUT_DIR = Path("data/examples")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for accession, (name, csv_path) in EXAMPLES.items():
        print(f"Processing {accession} ({name})...")
        variants = load_prs_csv(csv_path)
        rsids = [v.rsid or v.variant_id for v in variants if v.rsid or v.variant_id]
        print(f"  variants: {len(variants)} | rsIDs: {len(rsids)}")

        freqs = batch_fetch_frequencies(rsids)
        flagged, coverage, reliability = compute_variant_scores(freqs, variants)
        gap = compute_gap_index(reliability)

        summary = AuditSummary(
            accession=accession,
            model_name=name,
            total_variants=len(variants),
            coverage_scores=coverage,
            reliability_scores=reliability,
            gap_index=gap,
            flagged_variants=flagged,
        )
        audit = AuditResult(summary=summary, variants=variants, frequencies=[], coverage=[])
        output_path = OUTPUT_DIR / f"{accession}.json"
        output_path.write_text(json.dumps(audit.model_dump(), indent=2))
        print(f"  saved -> {output_path}")


if __name__ == "__main__":
    main()
