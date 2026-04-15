import httpx

ENDPOINT = "https://gnomad.broadinstitute.org/api"
QUERY = """
query SearchVariants($query: String!, $dataset: DatasetId!) {
  variant_search(query: $query, dataset: $dataset) {
    variant_id
  }
}
"""

with httpx.Client() as client:
    for rsid in ["rs2981582", "rs6983267", "rs10795668"]:
        r = client.post(
            ENDPOINT,
            json={"query": QUERY, "variables": {"dataset": "gnomad_r4", "query": rsid}},
            timeout=30,
        )
        print(rsid, "->", r.json())
