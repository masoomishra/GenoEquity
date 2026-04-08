from genoequity.gwas import load_prs_variants

variants = load_prs_variants("GCST90018999")

print("Total variants:", len(variants))

rsids = []
for v in variants:
    if v.rsid:
        rsids.append(v.rsid)

print("Variants with rsid:", len(rsids))
print("First 10 rsids:")
for r in rsids[:10]:
    print(r)
