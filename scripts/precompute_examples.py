"""Generate placeholder example audits for the UI scaffold."""

from __future__ import annotations

import json
from pathlib import Path

from genoequity.models import AuditResult, AuditSummary

EXAMPLES = {
    "GCST90016564": "Colorectal Cancer",
    "GCST90029052": "Breast Cancer",
    "GCST90018999": "Prostate Cancer",
}

OUTPUT_DIR = Path("data/examples")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for accession, name in EXAMPLES.items():
        summary = AuditSummary(
            accession=accession,
            model_name=name,
            total_variants=150,
            coverage_scores={"AFR": 0.62, "AMR": 0.70, "EAS": 0.75, "NFE": 0.95},
            reliability_scores={"AFR": 0.58, "AMR": 0.66, "EAS": 0.72, "NFE": 0.96},
            gap_index={"AFR": 0.40, "AMR": 0.31, "EAS": 0.25, "NFE": 0.0},
            flagged_variants=["1-55505021-A-G", "3-18597547-C-T"],
        )
        audit = AuditResult(summary=summary, variants=[], frequencies=[], coverage=[])
        (OUTPUT_DIR / f"{accession}.json").write_text(json.dumps(audit.model_dump(), indent=2))


if __name__ == "__main__":
    main()
