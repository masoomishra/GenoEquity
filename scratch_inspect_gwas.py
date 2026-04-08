from genoequity.gwas import fetch_study_associations

payload = fetch_study_associations("GCST90029052")

print(type(payload))
print(payload.keys() if isinstance(payload, dict) else payload)

embedded = payload.get("_embedded", {})
print("Embedded keys:", embedded.keys())
print("Association count:", len(embedded.get("associations", [])))

assocs = embedded.get("associations", [])
if assocs:
    print("First association:")
    print(assocs[0])
