from genoequity.gwas import load_prs_variants

variants = load_prs_variants("GCST90018999")

print("Number of variants:", len(variants))
print("First 5 variants:")

for v in variants[:5]:
    print(v)
