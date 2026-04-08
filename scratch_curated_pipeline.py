from genoequity.curated import load_prs_csv
from genoequity.gnomad import batch_fetch_frequencies
from genoequity.scoring import compute_variant_scores, compute_gap_index

variants = load_prs_csv("data/examples/curated_prs_example.csv")
rsids = [v.rsid for v in variants if v.rsid]

print("total curated variants:", len(variants))
print("total rsIDs sent to gnomAD:", len(rsids))

freqs = batch_fetch_frequencies(rsids)
non_empty = sum(1 for v in freqs.values() if v)
empty = sum(1 for v in freqs.values() if not v)

print("rsIDs with non-empty frequency data:", non_empty)
print("rsIDs with empty frequency data:", empty)

flagged, coverage, reliability = compute_variant_scores(freqs, variants)
gap = compute_gap_index(reliability)

order = ["AFR", "AMR", "ASJ", "EAS", "FIN", "NFE", "SAS"]
print("Population  Coverage  Reliability  Gap")
for pop in order:
    cov = round(coverage.get(pop, 0.0), 3)
    rel = round(reliability.get(pop, 0.0), 3)
    g = round(gap.get(pop, 0.0), 3)
    print(f"{pop:>9}  {cov:>8.3f}  {rel:>11.3f}  {g:>5.3f}")

gaps_no_nfe = {k: v for k, v in gap.items() if k != "NFE" and k in order}
if gaps_no_nfe:
    highest_gap_pop = max(gaps_no_nfe, key=gaps_no_nfe.get)
    lowest_gap_pop = min(gaps_no_nfe, key=gaps_no_nfe.get)
    print(
        f"Highest gap: {highest_gap_pop} ({gap.get(highest_gap_pop, 0.0):.3f}); "
        f"Lowest gap (excluding NFE): {lowest_gap_pop} ({gap.get(lowest_gap_pop, 0.0):.3f})"
    )
else:
    print("Highest gap: N/A; Lowest gap (excluding NFE): N/A")
