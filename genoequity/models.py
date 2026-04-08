"""Pydantic models for GenoEquity domain objects."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PRSVariant(BaseModel):
    model_config = ConfigDict(extra="ignore")
    variant_id: str
    rsid: Optional[str] = None
    effect_allele: Optional[str] = None
    other_allele: Optional[str] = None
    effect_size: Optional[float] = None
    p_value: Optional[float] = None


class AncestryFrequency(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ancestry: str
    allele_frequency: Optional[float] = None
    allele_number: Optional[int] = None


class VariantFrequencies(BaseModel):
    model_config = ConfigDict(extra="ignore")
    variant_id: str
    frequencies: List[AncestryFrequency]


class VariantCoverage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    variant_id: str
    coverage_by_ancestry: Dict[str, float] = Field(default_factory=dict)
    reliability_by_ancestry: Dict[str, float] = Field(default_factory=dict)


class AuditSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")
    accession: str
    model_name: Optional[str] = None
    total_variants: int
    coverage_scores: Dict[str, float]
    reliability_scores: Dict[str, float]
    gap_index: Dict[str, float]
    flagged_variants: List[str] = Field(default_factory=list)


class AuditResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    summary: AuditSummary
    variants: List[PRSVariant]
    frequencies: List[VariantFrequencies]
    coverage: List[VariantCoverage]
