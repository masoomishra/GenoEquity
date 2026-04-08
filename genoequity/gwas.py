"""GWAS Catalog API client."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from .models import PRSVariant

GWAS_BASE_URL = "https://www.ebi.ac.uk/gwas/rest/api"
ASSOCIATION_PROJECTION = "associationByStudy"


def _first_not_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def fetch_study_metadata(accession: str) -> Dict[str, Any]:
    url = f"{GWAS_BASE_URL}/studies/{accession}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_study_associations(accession: str, size: int = 1000) -> Dict[str, Any]:
    url = f"{GWAS_BASE_URL}/studies/{accession}/associations"
    params = {"projection": ASSOCIATION_PROJECTION, "size": size}
    associations: List[Dict[str, Any]] = []

    while url:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        embedded = payload.get("_embedded", {})
        associations.extend(embedded.get("associations", []))

        next_link = (payload.get("_links") or {}).get("next")
        next_href = (next_link or {}).get("href")
        url = next_href
        params = None

    return {"_embedded": {"associations": associations}}


def parse_variants(association_payload: Dict[str, Any]) -> List[PRSVariant]:
    variants: List[PRSVariant] = []
    embedded = association_payload.get("_embedded", {})
    for assoc in embedded.get("associations", []):
        variant = assoc.get("variant") or {}
        variant_id = variant.get("variantId") or variant.get("variant_id")
        effect_allele = _first_not_none(assoc.get("effectAllele"), assoc.get("effect_allele"))
        other_allele = _first_not_none(assoc.get("otherAllele"), assoc.get("other_allele"))
        effect_size = _first_not_none(
            assoc.get("betaNum"),
            assoc.get("orPerCopyNum"),
            assoc.get("beta"),
            assoc.get("oddsRatio"),
            assoc.get("effectSize"),
        )
        p_value = _first_not_none(assoc.get("pvalue"), assoc.get("pValue"))

        loci = assoc.get("loci") or []
        risk_name = None
        if loci:
            strongest = (loci[0] or {}).get("strongestRiskAlleles") or []
            if strongest:
                risk_name = (strongest[0] or {}).get("riskAlleleName")
                if isinstance(risk_name, str) and "-" in risk_name:
                    rsid_part, allele_part = risk_name.split("-", 1)
                    if not effect_allele:
                        effect_allele = allele_part
                    variant_rsid = rsid_part
                else:
                    variant_rsid = risk_name if isinstance(risk_name, str) else None
            else:
                variant_rsid = None
        else:
            variant_rsid = None

        if not variant_id:
            variant_id = risk_name if isinstance(risk_name, str) else None
        if not variant_id:
            continue
        variants.append(
            PRSVariant(
                variant_id=variant_id,
                rsid=_first_not_none(variant.get("rsId"), variant.get("rsid"), variant_rsid),
                effect_allele=effect_allele,
                other_allele=other_allele,
                effect_size=effect_size,
                p_value=p_value,
            )
        )
    return variants


def load_prs_variants(accession: str) -> List[PRSVariant]:
    payload = fetch_study_associations(accession)
    return parse_variants(payload)


def get_study_title(metadata: Dict[str, Any]) -> Optional[str]:
    publication = metadata.get("publicationInfo") or {}
    return publication.get("title") or metadata.get("title") or metadata.get("studyTitle")
