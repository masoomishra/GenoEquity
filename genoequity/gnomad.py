"""gnomAD GraphQL API client.

Two-step flow for rsIDs:
1) Resolve rsID -> gnomAD variant_id via variant_search.
2) Fetch populations for that variant_id via variant.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

import httpx

GNOMAD_ENDPOINT = "https://gnomad.broadinstitute.org/api"
GNOMAD_DATASET = "gnomad_r4"

POPULATION_MAP = {
    "afr": "AFR",
    "amr": "AMR",
    "asj": "ASJ",
    "eas": "EAS",
    "fin": "FIN",
    "nfe": "NFE",
    "oth": "OTH",
    "sas": "SAS",
}

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

SEARCH_QUERY = """
query SearchVariants($query: String!, $dataset: DatasetId!) {
  variant_search(query: $query, dataset: $dataset) {
    variant_id
  }
}
"""


def _search_variant_ids(client: httpx.Client, rsid: str) -> List[str]:
    """Resolve an rsID to one or more gnomAD variant_id strings."""
    payload = {"query": SEARCH_QUERY, "variables": {"dataset": GNOMAD_DATASET, "query": rsid}}
    response = client.post(GNOMAD_ENDPOINT, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json().get("data", {}) or {}
    results = data.get("variant_search") or []
    return [item.get("variant_id") for item in results if item.get("variant_id")]


def _is_snv(variant_id: str) -> bool:
    parts = variant_id.split("-")
    if len(parts) != 4:
        return False
    ref = parts[2]
    alt = parts[3]
    return len(ref) == 1 and len(alt) == 1


def _fetch_variant_frequencies(client: httpx.Client, variant_id: str) -> Dict[str, Any]:
    """Fetch raw frequency payload for one gnomAD variant_id."""
    payload = {"query": VARIANT_QUERY, "variables": {"dataset": GNOMAD_DATASET, "variantId": variant_id}}
    response = client.post(GNOMAD_ENDPOINT, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("data", {})


def resolve_variant_id(client: httpx.Client, rsid: str) -> tuple[str | None, Dict[str, Any] | None]:
    """Resolve rsID to the best gnomAD variant_id and return its payload.

    Prefers SNVs and candidates with any genome/exome population data.
    """
    candidate_ids = _search_variant_ids(client, rsid)
    if not candidate_ids:
        return None, None

    sorted_ids = sorted(candidate_ids, key=lambda vid: _is_snv(vid), reverse=True)
    fallback_payload: Dict[str, Any] | None = None
    for variant_id in sorted_ids:
        payload = _fetch_variant_frequencies(client, variant_id)
        if not payload or payload.get("variant") is None:
            if fallback_payload is None:
                fallback_payload = payload
            continue
        variant = payload.get("variant") or {}
        genome_pops = (variant.get("genome") or {}).get("populations") or []
        exome_pops = (variant.get("exome") or {}).get("populations") or []
        if genome_pops or exome_pops:
            return variant_id, payload
        if fallback_payload is None:
            fallback_payload = payload
    return sorted_ids[0], fallback_payload


def parse_population_frequencies(payload: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Parse population frequencies from a GraphQL response payload."""
    result: Dict[str, Dict[str, float]] = {}
    variant = payload.get("variant") or {}
    genome = variant.get("genome") or {}
    exome = variant.get("exome") or {}
    populations = genome.get("populations") or exome.get("populations") or []
    for pop in populations:
        pop_id = pop.get("id")
        label = POPULATION_MAP.get(pop_id, pop_id.upper() if pop_id else "UNK")
        # Keep only high-level ancestry groups; drop subpops and sex splits.
        if (
            not label
            or label not in {"AFR", "AMR", "EAS", "NFE", "SAS", "FIN", "ASJ"}
            or "_" in label
            or label.startswith("HGDP:")
            or label.startswith("1KG:")
        ):
            continue
        ac = pop.get("ac")
        an = pop.get("an")
        af = pop.get("af")
        if af is None and ac is not None and an:
            try:
                af = float(ac) / float(an)
            except (TypeError, ValueError, ZeroDivisionError):
                af = None
        result[label] = {
            "af": af,
            "an": an,
            "ac": ac,
        }
    return result


def batch_fetch_frequencies(rsids: Iterable[str]) -> Dict[str, Dict[str, Dict[str, float]]]:
    """Fetch population frequencies for a batch of rsIDs.

    Returns: {rsid: {POP: {ac, an, af}}}
    """
    results: Dict[str, Dict[str, Dict[str, float]]] = {}
    resolved = 0
    total = 0
    with httpx.Client() as client:
        for rsid in rsids:
            total += 1
            try:
                variant_id, payload = resolve_variant_id(client, rsid)
                if not variant_id:
                    results[rsid] = {}
                    continue
                resolved += 1
                if not payload or payload.get("variant") is None:
                    results[rsid] = {}
                    continue
                results[rsid] = parse_population_frequencies(payload)
            except (httpx.HTTPError, ValueError):
                results[rsid] = {}
    print(f"Resolved rsIDs: {resolved}/{total}")
    return results
