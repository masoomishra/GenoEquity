"""gnomAD GraphQL API client.

Two-step flow for rsIDs:
1) Resolve rsID -> gnomAD variant_id via variant_search.
2) Fetch populations for that variant_id via variant.
"""

from __future__ import annotations

import random
import time
from typing import Any, Dict, Iterable, List

import httpx

from .cache import Cache

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


def _search_variant_ids(client: httpx.Client, rsid: str) -> List[str] | None:
    """Resolve an rsID to one or more gnomAD variant_id strings."""
    payload = {"query": SEARCH_QUERY, "variables": {"dataset": GNOMAD_DATASET, "query": rsid}}
    for attempt in range(3):
        time.sleep(0.2)
        try:
            response = client.post(GNOMAD_ENDPOINT, json=payload, timeout=10)
        except httpx.HTTPError as e:
            print(f"[SEARCH ERROR] rsid={rsid} error={repr(e)}")
            raise
        if response.status_code == 429:
            wait = (2**attempt) + random.uniform(0, 0.5)
            time.sleep(wait)
            continue
        response.raise_for_status()
        break
    else:
        return None
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
    candidate_ids = _search_variant_ids(client, rsid)
    if candidate_ids is None:
        return None, None
    if not candidate_ids:
        return None, None
    # Prefer SNVs
    sorted_ids = sorted(candidate_ids, key=lambda vid: _is_snv(vid), reverse=True)
    for variant_id in sorted_ids:
        try:
            payload = _fetch_variant_frequencies(client, variant_id)
        except Exception:
            continue
        if not payload:
            continue
        variant = payload.get("variant")
        if not variant:
            continue
        genome_pops = (variant.get("genome") or {}).get("populations") or []
        exome_pops = (variant.get("exome") or {}).get("populations") or []
        if genome_pops or exome_pops:
            return variant_id, payload
    return sorted_ids[0] if sorted_ids else None, None


def parse_population_frequencies(payload: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    result: Dict[str, Dict[str, float]] = {}
    # Handle both raw API response and pre-parsed response
    if "data" in payload:
        variant = (payload.get("data") or {}).get("variant") or {}
    else:
        variant = payload.get("variant") or {}
    genome = variant.get("genome") or {}
    exome = variant.get("exome") or {}
    populations = genome.get("populations") or exome.get("populations") or []
    ALLOWED = {"AFR", "AMR", "EAS", "NFE", "SAS", "FIN", "ASJ"}
    for pop in populations:
        pop_id = pop.get("id") or ""
        # Skip subpopulations, sex splits, and reference panel entries
        if "_" in pop_id or pop_id.startswith("hgdp:") or pop_id.startswith("1kg:"):
            continue
        label = POPULATION_MAP.get(pop_id)
        if not label or label not in ALLOWED:
            continue
        ac = pop.get("ac")
        an = pop.get("an")
        af = pop.get("af")
        if af is None and ac is not None and an:
            try:
                af = float(ac) / float(an)
            except (TypeError, ValueError, ZeroDivisionError):
                af = None
        result[label] = {"af": af, "an": an, "ac": ac}
    return result


def batch_fetch_frequencies(rsids: Iterable[str]) -> Dict[str, Dict[str, Dict[str, float]] | None]:
    results: Dict[str, Dict[str, Dict[str, float]] | None] = {}
    resolved = 0
    total = 0
    cache = Cache()
    with httpx.Client() as client:
        for rsid in rsids:
            total += 1
            results[rsid] = {}
            try:
                found, cached = cache.get_with_presence(f"gnomad:{rsid}", ttl_seconds=60 * 60 * 24 * 30)
                if found:
                    results[rsid] = cached
                    if cached:
                        resolved += 1
                    continue
                variant_id, payload = resolve_variant_id(client, rsid)
                time.sleep(1)
                if variant_id is None and payload is None:
                    results[rsid] = None
                    cache.set(f"gnomad:{rsid}", None, ttl_seconds=60 * 10)
                    continue
                if not variant_id or not payload:
                    results[rsid] = {}
                    cache.set(f"gnomad:{rsid}", {})
                    continue
                parsed = parse_population_frequencies(payload)
                results[rsid] = parsed
                cache.set(f"gnomad:{rsid}", parsed)
                if parsed:
                    resolved += 1
            except (httpx.HTTPError, ValueError):
                results[rsid] = {}
            time.sleep(1)
    print(f"Resolved rsIDs: {resolved}/{total}")
    return results
