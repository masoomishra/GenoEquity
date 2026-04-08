# GenoEquity

GenoEquity is an ancestry-aware polygenic risk score (PRS) bias auditor. It evaluates how well a published PRS model is represented across ancestry groups and summarizes coverage gaps that can drive inequitable clinical performance.

**What problem is GenoEquity solving?**

PRS models aggregate many genetic variants to estimate disease risk. Most published PRS models are built from GWAS cohorts dominated by European ancestry. When these models are applied to people with African, Latino, East Asian, South Asian, or mixed ancestry, accuracy can degrade because variant discovery, effect sizes, and allele frequencies are not evenly represented. GenoEquity provides an automated audit that shows where a PRS is well supported and where it is likely to underperform.

**Why PRS fairness matters**

PRS are increasingly used in screening and clinical decision support. If a PRS is trained on one ancestry and deployed universally, it can systematically underestimate or overestimate risk for underrepresented groups. That is both a scientific and equity risk: miscalibrated scores can mislead clinicians, introduce bias into care, and widen existing health disparities. A fairness audit makes these gaps visible so researchers and practitioners can quantify risk and communicate limitations clearly.

## How the pipeline works

The pipeline is designed to be simple and reproducible:

1. **Input PRS variants**
   - Preferred path: a curated CSV of PRS variants (rsid, effect_allele, effect_size, p_value).
   - Optional path: GWAS Catalog associations (useful for exploration, less reliable for demo).
2. **Resolve ancestry frequencies**
   - Use gnomAD to obtain allele frequency statistics by ancestry.
   - Normalize and filter to high-level populations: AFR, AMR, ASJ, EAS, FIN, NFE, SAS.
3. **Compute scores**
   - Coverage: whether a variant is represented above a minimum allele count.
   - Reliability: how much allele number supports a variant (scaled to a target).
   - Gap index: relative loss vs. a European baseline (NFE).
   - Flagged variants: high-effect variants with poor coverage.
4. **Report**
   - The output is a per-ancestry summary that highlights where a PRS may be less reliable.

## What the results show

GenoEquity outputs three core metrics per population:

- **Coverage**: the fraction of weighted variants that have enough population data.
- **Reliability**: the weighted strength of population data supporting the PRS.
- **Gap**: how much reliability drops relative to the NFE baseline.

In practice, a model with strong NFE support and weak non‑European coverage will show high gap scores for non‑European populations. That does not prove clinical failure, but it is a strong indicator of risk that requires interpretation, caution, and potentially population‑specific calibration.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/precompute_examples.py
streamlit run app/main.py
```

## Curated Demo Path (recommended)

Use a small curated CSV to produce a clean, reproducible audit.

```bash
python3 scratch_curated_pipeline.py
python3 scratch_curated_plot.py
```

The example CSV lives at `data/examples/curated_prs_example.csv`. You can replace it with your own curated PRS table as long as it matches the columns:

```
rsid,effect_allele,effect_size,p_value
```

## GWAS Catalog Path (exploratory)

The GWAS path is useful to explore studies but is more fragile because rsID resolution can be incomplete.

```bash
python3 scratch_full_pipeline.py
```

If the rsID resolution rate is low, GenoEquity will warn that the scores are based on a limited subset.

## Repository Structure

- `genoequity/`: core models, API clients, scoring logic, curated loader
- `app/main.py`: Streamlit entrypoint
- `pages/`: Streamlit pages
- `data/examples/`: curated CSV and example data files
- `scripts/`: helper scripts for precomputing demo data
- `scratch_*.py`: runnable pipeline experiments

## Limitations (important)

GenoEquity audits coverage and data support, not clinical performance:

- Effect sizes are derived from published studies and may not transfer across ancestries.
- gnomAD represents population reference data, not case/control cohorts.
- LD structure differences and cohort-specific calibration are not modeled.

These limitations are why the tool reports gaps rather than making clinical claims.
