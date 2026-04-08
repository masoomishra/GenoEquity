"""Coverage and reliability scoring logic."""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from .models import PRSVariant

AN_THRESHOLD = 1000 #if allele number is at least 1000, you count that variant as covered 
AN_TARGET = 10000 #if allele number reaches 10000, you treate the variant as fully reliable 
FLAG_WEIGHT_THRESHOLD = 2.0 #if variant has a big enough effect size and bad coverage, flag it as important 


#Helper Function 
#How much should this variant matter in the scoring? 
#if the variant has no effect size, it gets weight 1.0 
#if it does have an effect size, use the absolute value. why? because strength is what matters and not direction 
def _variant_weight(variant: PRSVariant) -> float:
    if variant.effect_size is None:
        return 1.0
    return abs(variant.effect_size)


#This takes variant frequencies (ancestry data for each variant), variants(the PRS variants themselves) and returns flagged variants, coverage scores by ancestry, reliability scores by ancestry 
def compute_variant_scores(
    variant_frequencies: Dict[str, Dict[str, Dict[str, float]]],
    variants: Iterable[PRSVariant],
) -> Tuple[List[str], Dict[str, float], Dict[str, float]]:
    #This creates a quick lookup table like: this helps answer how important is this variant quickly 
    variants_list = list(variants)
    weight_map = {v.variant_id: _variant_weight(v) for v in variants_list}
    #These start empty, they store total weighted coverage per ancestry, weighted reliability per ancestry, total weight per ancestry, flagged variants 
    coverage_totals: Dict[str, float] = {}
    reliability_totals: Dict[str, float] = {}
    weight_totals: Dict[str, float] = {}
    flagged: set[str] = set()

    all_ancestries: set[str] = set()
    for pops in variant_frequencies.values():
        all_ancestries.update(pops.keys())

    #Loop through each variant 
    #For each variant, pops contains ancestry info like NFE, AFR, AMR, etc 
    for variant in variants_list:
        variant_id = variant.variant_id
        lookup_id = variant.rsid or variant_id
        #Find how important the variant is. If it is somehow missing from the weight map, default to 1.0
        weight = weight_map.get(variant_id, 1.0)
        pops = variant_frequencies.get(lookup_id)
        if not pops:
            for ancestry in all_ancestries:
                weight_totals[ancestry] = weight_totals.get(ancestry, 0.0) + weight
            if weight >= FLAG_WEIGHT_THRESHOLD:
                flagged.add(variant_id)
            continue

        #Loop through each ancestry for that variant
        for ancestry, metrics in pops.items():
            #Read the allele number, how much data do we have for this ancestry at this variant?
            an_raw = metrics.get("an")
            an = max(float(an_raw), 0.0) if an_raw is not None else 0.0
            #If an>=1000, coverage is 1. Otherwise, coverage is 0. 
            #So the coverage here is binary: enough data, not enough data 
            coverage = 1.0 if an >= AN_THRESHOLD else 0.0
            #This is more gradual. It says if an=0, reliability is 0, if an=5000, reliability is 0.5, and if an=10000 or more, reliability is 1.0 
            reliability = min(an / AN_TARGET, 1.0) if an else 0.0

            coverage_totals[ancestry] = coverage_totals.get(ancestry, 0.0) + coverage * weight
            reliability_totals[ancestry] = reliability_totals.get(ancestry, 0.0) + reliability * weight
            weight_totals[ancestry] = weight_totals.get(ancestry, 0.0) + weight

            if coverage == 0.0 and weight >= FLAG_WEIGHT_THRESHOLD:
                flagged.add(variant_id)

    #Final coverage scores, weighted average coverage for each ancestry 
    coverage_scores = {
        ancestry: coverage_totals[ancestry] / weight_totals[ancestry]
        for ancestry in coverage_totals
        if weight_totals.get(ancestry)
    }
    #Final reliability score 
    reliability_scores = {
        ancestry: reliability_totals[ancestry] / weight_totals[ancestry]
        for ancestry in reliability_totals
        if weight_totals.get(ancestry)
    }

    return sorted(flagged), coverage_scores, reliability_scores
    #The function gives back: list of flagged variants, coverage score by ancestry, reliability score by ancestry 

#Gap index function 
#this compares every ancestry to the baseline 
def compute_gap_index(reliability_scores: Dict[str, float], baseline: str = "NFE") -> Dict[str, float]:
    #this gets NFE's reliability score
    baseline_score = reliability_scores.get(baseline, 0.0) or 0.0
    #If baseline is zero, just return zero gaps everywhere. this avoids crashing
    if baseline_score == 0:
        return {ancestry: 0.0 for ancestry in reliability_scores}
    return {
        ancestry: max(0.0, (baseline_score - score) / baseline_score)
        for ancestry, score in reliability_scores.items()
    }

#What this code is saying biologically 
#For each ancestry, I look at whether the PRS variants are represented well enough in population reference data, 
#Weight those variants by their importance, and then summarize how much support the model loses outside the NFE baseline. 
