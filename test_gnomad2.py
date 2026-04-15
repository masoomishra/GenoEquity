import httpx

ENDPOINT = "https://gnomad.broadinstitute.org/api"

VARIANT_QUERY = """
query VariantFrequencies($dataset: DatasetId!, $variantId: String!) {
  variant(variantId: $variantId, dataset: $dataset) {
    genome {
      populations {
        id
        ac
        an
      }
    }
    exome {
      populations {
        id
        ac
        an
      }
    }
  }
}
"""

# These are the resolved IDs from the previous test
test_variants = [
    ("rs2981582", "10-121592803-A-G"),
    ("rs6983267", "8-127401060-G-T"),
    ("rs10795668", "10-8659256-G-A"),
]

with httpx.Client() as client:
    for rsid, variant_id in test_variants:
        r = client.post(
            ENDPOINT,
            json={
                "query": VARIANT_QUERY,
                "variables": {"dataset": "gnomad_r4", "variantId": variant_id},
            },
            timeout=30,
        )
        data = r.json()
        variant = (data.get("data") or {}).get("variant") or {}
        genome_pops = (variant.get("genome") or {}).get("populations") or []
        exome_pops = (variant.get("exome") or {}).get("populations") or []
        print(f"{rsid} ({variant_id})")
        print(f"  genome populations: {len(genome_pops)}")
        print(f"  exome populations:  {len(exome_pops)}")
        if genome_pops:
            print(f"  first genome pop:   {genome_pops[0]}")
        if exome_pops:
            print(f"  first exome pop:    {exome_pops[0]}")
        if not genome_pops and not exome_pops:
            print(f"  RAW RESPONSE: {data}")
        print()
