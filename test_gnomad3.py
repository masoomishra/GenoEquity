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
  }
}
"""

with httpx.Client() as client:
    r = client.post(
        ENDPOINT,
        json={
            "query": VARIANT_QUERY,
            "variables": {"dataset": "gnomad_r4", "variantId": "10-121592803-A-G"},
        },
        timeout=30,
    )
    data = r.json()
    pops = data["data"]["variant"]["genome"]["populations"]
    print(f"Total populations returned: {len(pops)}")
    print("\nAll population IDs and their AN values:")
    for p in sorted(pops, key=lambda x: x["id"]):
        print(f"  id={p['id']:<30} an={p['an']}")
