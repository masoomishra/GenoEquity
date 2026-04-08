"""Curated PRS CSV loader."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from .models import PRSVariant


def load_prs_csv(path: str | Path) -> List[PRSVariant]:
    """Load a curated PRS-style CSV into PRSVariant objects.

    Expected columns: rsid, effect_allele, effect_size, p_value
    """
    csv_path = Path(path)
    variants: List[PRSVariant] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rsid = (row.get("rsid") or "").strip()
            if not rsid:
                continue
            effect_allele = (row.get("effect_allele") or "").strip() or None
            effect_size_raw = (row.get("effect_size") or "").strip()
            p_value_raw = (row.get("p_value") or "").strip()

            effect_size = float(effect_size_raw) if effect_size_raw else None
            p_value = float(p_value_raw) if p_value_raw else None

            variants.append(
                PRSVariant(
                    variant_id=rsid,
                    rsid=rsid,
                    effect_allele=effect_allele,
                    effect_size=effect_size,
                    p_value=p_value,
                )
            )
    return variants
