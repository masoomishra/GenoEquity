from genoequity.models import PRSVariant
from genoequity.scoring import compute_variant_scores, compute_gap_index

variants = [
    PRSVariant(variant_id="v1", effect_size=2.0),
    PRSVariant(variant_id="v2", effect_size=1.0),
]

variant_frequencies = {
    "v1": {
        "NFE": {"an": 12000},
        "AFR": {"an": 500},
    },
    "v2": {
        "NFE": {"an": 8000},
        "AFR": {"an": 11000},
    },
}

flagged, coverage_scores, reliability_scores = compute_variant_scores(
    variant_frequencies, variants
)

gap_index = compute_gap_index(reliability_scores)

print("Flagged:", flagged)
print("Coverage:", coverage_scores)
print("Reliability:", reliability_scores)
print("Gap:", gap_index)
