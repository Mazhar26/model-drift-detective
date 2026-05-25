"""
test_explain.py — Unit tests for drift explanation module.
"""

import pytest
from src.data_setup import load_data
from src.explain import explain_drift, segment_analysis


@pytest.fixture(scope="module")
def data():
    """Load train and live datasets once."""
    return load_data()


def test_segment_analysis_runs(data):
    """Segment analysis should run and return a list of floats."""
    train, live = data
    result = segment_analysis(train, live, "MonthlyCharges")
    assert isinstance(result, list)
    assert all(isinstance(x, float) for x in result)
    assert len(result) > 0


def test_segment_analysis_empty():
    """Segment analysis should handle empty inputs gracefully."""
    import pandas as pd
    train = pd.DataFrame({"col": []})
    live = pd.DataFrame({"col": []})
    result = segment_analysis(train, live, "col")
    assert result == []


def test_explain_drift_returns_explanations(data):
    """Explain drift should return explanation mapping with correct keys."""
    train, live = data
    explanations = explain_drift(train, live)
    assert isinstance(explanations, dict)
    assert len(explanations) > 0

    # Check a known numerical feature
    assert "MonthlyCharges" in explanations
    charges_exp = explanations["MonthlyCharges"]
    assert "train_mean" in charges_exp
    assert "live_mean" in charges_exp
    assert "difference" in charges_exp
    assert "segment_shift" in charges_exp
    assert isinstance(charges_exp["segment_shift"], list)
