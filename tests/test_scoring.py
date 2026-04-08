import pytest

from genoequity.models import PRSVariant
from genoequity.scoring import compute_gap_index, compute_variant_scores


def test_compute_variant_scores_weighted():
    variants = [
        PRSVariant(variant_id="1-100-A-G", effect_size=2.0),
        PRSVariant(variant_id="1-200-C-T", effect_size=1.0),
    ]
    freqs = {
        "1-100-A-G": {
            "NFE": {"an": 10000},
            "AFR": {"an": 500},
        },
        "1-200-C-T": {
            "NFE": {"an": 500},
            "AFR": {"an": 20000},
        },
    }

    flagged, coverage, reliability = compute_variant_scores(freqs, variants)

    assert flagged == ["1-100-A-G"]
    assert coverage["NFE"] == pytest.approx(2.0 / 3.0)
    assert coverage["AFR"] == pytest.approx(1.0 / 3.0)
    assert reliability["NFE"] == pytest.approx(2.05 / 3.0)
    assert reliability["AFR"] == pytest.approx(1.1 / 3.0)


def test_compute_variant_scores_handles_missing_an():
    variants = [PRSVariant(variant_id="1-300-G-A", effect_size=3.0)]
    freqs = {"1-300-G-A": {"NFE": {"an": None}}}
    flagged, coverage, reliability = compute_variant_scores(freqs, variants)
    assert flagged == ["1-300-G-A"]
    assert coverage["NFE"] == 0.0
    assert reliability["NFE"] == 0.0


def test_compute_variant_scores_missing_variant_counts_against():
    variants = [
        PRSVariant(variant_id="1-100-A-G", effect_size=2.0),
        PRSVariant(variant_id="1-999-T-C", effect_size=2.0),
    ]
    freqs = {
        "1-100-A-G": {
            "NFE": {"an": 10000},
            "AFR": {"an": 10000},
        }
    }

    flagged, coverage, reliability = compute_variant_scores(freqs, variants)

    assert flagged == ["1-999-T-C"]
    assert coverage["NFE"] == pytest.approx(0.5)
    assert coverage["AFR"] == pytest.approx(0.5)
    assert reliability["NFE"] == pytest.approx(0.5)
    assert reliability["AFR"] == pytest.approx(0.5)


def test_compute_gap_index():
    scores = {"NFE": 0.8, "AFR": 0.4, "EAS": 0.8}
    gap = compute_gap_index(scores)
    assert gap["NFE"] == 0.0
    assert gap["AFR"] == pytest.approx(0.5)
    assert gap["EAS"] == pytest.approx(0.0)


def test_compute_gap_index_no_baseline():
    scores = {"AFR": 0.2}
    gap = compute_gap_index(scores, baseline="NFE")
    assert gap["AFR"] == 0.0
