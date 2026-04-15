import httpx
from genoequity.gnomad import (
    _search_variant_ids,
    _fetch_variant_frequencies,
    parse_population_frequencies,
)

rsid = "rs2981582"

with httpx.Client() as client:
    print("Step 1 - search variant IDs:")
    ids = _search_variant_ids(client, rsid)
    print(f"  result: {ids}")

    if ids:
        variant_id = ids[0]
        print(f"\nStep 2 - fetch frequencies for {variant_id}:")
        payload = _fetch_variant_frequencies(client, variant_id)
        print(f"  payload top-level keys: {list(payload.keys())}")
        if "data" in payload:
            print(f"  payload['data'] keys: {list(payload['data'].keys())}")
        if "variant" in payload:
            print(f"  payload['variant'] keys: {list(payload['variant'].keys())}")

        print(f"\nStep 3 - parse frequencies:")
        parsed = parse_population_frequencies(payload)
        print(f"  result: {parsed}")
