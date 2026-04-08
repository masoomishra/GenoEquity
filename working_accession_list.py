from genoequity.gwas import load_prs_variants

accessions = [
    "GCST90016564",
    "GCST90029052",
    "GCST90018999",
]

for acc in accessions:
    variants = load_prs_variants(acc)
    print(acc, "->", len(variants))
