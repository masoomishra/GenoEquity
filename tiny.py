from genoequity.gwas import fetch_study_metadata

metadata = fetch_study_metadata("GCST90029052")
print(type(metadata))
print(metadata.keys() if isinstance(metadata, dict) else metadata)
print(metadata)
