# GenoEquity

GenoEquity is an ancestry-aware cancer PRS bias auditor. This repo currently contains a scaffold of the core modules, Streamlit pages, and report generator described in the project spec.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/precompute_examples.py
streamlit run app/main.py
```

## Structure

- `genoequity/`: core data models and scoring utilities
- `app/main.py`: Streamlit entrypoint
- `pages/`: Streamlit pages
- `scripts/precompute_examples.py`: placeholder examples
- `data/examples/`: cached example JSONs

## Notes

The pipeline wiring for live GWAS and gnomAD requests is intentionally stubbed for now. Replace the placeholders in `genoequity/gwas.py`, `genoequity/gnomad.py`, and `genoequity/scoring.py` when implementing the full data flow.
