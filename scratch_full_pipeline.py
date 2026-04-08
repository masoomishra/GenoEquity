from genoequity.gnomad import batch_fetch_frequencies
from genoequity.gwas import load_prs_variants
from genoequity.scoring import compute_gap_index, compute_variant_scores

# step 1: get variants
variants = load_prs_variants("GCST90018999")
print("total GWAS variants:", len(variants))

# step 2: extract rsids
rsids = [v.rsid for v in variants if v.rsid]
print("total rsIDs sent to gnomAD:", len(rsids))

# step 3: get frequencies for all rsids
freqs = batch_fetch_frequencies(rsids)
non_empty = sum(1 for v in freqs.values() if v)
empty = sum(1 for v in freqs.values() if not v)
print("rsIDs with non-empty frequency data:", non_empty)
print("rsIDs with empty frequency data:", empty)
resolution_rate = non_empty / len(rsids) if rsids else 0.0
print("resolution rate:", resolution_rate)
if resolution_rate < 0.5:
    print("WARNING: Low rsID resolution rate (< 0.5).")
    print("Interpretation: scoring is based on a limited resolved subset and may not fully represent the study.")

# step 4: scoring
flagged, coverage, reliability = compute_variant_scores(freqs, variants)
gap = compute_gap_index(reliability)

print("Coverage:", coverage)
print("Reliability:", reliability)
print("Gap:", gap)
print("Flagged:", flagged)
