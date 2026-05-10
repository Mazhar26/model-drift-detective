"""
test_drift.py — Unit tests for drift detection module.

All tests are independent and do not require a running server.
They test the core drift detection logic directly.
"""

import numpy as np
import pandas as pd
import pytest

from src.drift import detect_drift, get_severity


# ── Fixtures ──────────────────────────────────────────

@pytest.fixture
def identical_data():
    """Create two identical DataFrames (no drift expected)."""
    np.random.seed(42)
    data = {
        "feature_a": np.random.normal(50, 10, 500),
        "feature_b": np.random.normal(100, 20, 500),
        "Churn": np.random.randint(0, 2, 500),
    }
    df = pd.DataFrame(data)
    return df.copy(), df.copy()


@pytest.fixture
def drifted_data():
    """Create train/live DataFrames with significant drift."""
    np.random.seed(42)
    train = pd.DataFrame({
        "feature_a": np.random.normal(50, 10, 500),
        "feature_b": np.random.normal(100, 20, 500),
        "Churn": np.random.randint(0, 2, 500),
    })
    live = pd.DataFrame({
        "feature_a": np.random.normal(200, 10, 500),  # Large shift
        "feature_b": np.random.normal(500, 50, 500),  # Large shift
        "Churn": np.random.randint(0, 2, 500),
    })
    return train, live


@pytest.fixture
def real_data():
    """Load the actual Telco dataset for integration-style tests."""
    from src.data_setup import load_data
    return load_data()


# ── Tests ─────────────────────────────────────────────

def test_ks_test_returns_score(real_data):
    """Drift detection should return drift_score for each feature."""
    train, live = real_data
    results = detect_drift(train, live)

    assert isinstance(results, dict)
    assert len(results) > 0

    for feature, result in results.items():
        assert "drift_score" in result
        assert isinstance(result["drift_score"], float)


def test_drift_score_between_0_and_1(real_data):
    """All drift scores should be between 0 and 1 (KS statistic range)."""
    train, live = real_data
    results = detect_drift(train, live)

    for feature, result in results.items():
        assert 0.0 <= result["drift_score"] <= 1.0, (
            f"{feature}: drift_score={result['drift_score']} out of range"
        )


def test_drift_detected_is_boolean(real_data):
    """drift_detected field must be a boolean."""
    train, live = real_data
    results = detect_drift(train, live)

    for feature, result in results.items():
        assert isinstance(result["drift_detected"], bool), (
            f"{feature}: drift_detected is {type(result['drift_detected'])}, expected bool"
        )


def test_no_drift_on_identical_data(identical_data):
    """Identical datasets should show no significant drift."""
    train, live = identical_data
    results = detect_drift(train, live)

    for feature, result in results.items():
        if feature == "Churn":
            continue
        # Identical data → KS statistic should be 0 (or very close)
        assert result["drift_score"] < 0.05, (
            f"{feature}: unexpected drift on identical data (score={result['drift_score']})"
        )


def test_high_drift_on_different_data(drifted_data):
    """Significantly different distributions should produce high drift scores."""
    train, live = drifted_data
    results = detect_drift(train, live)

    assert len(results) > 0, "No drift results for clearly different data"

    # At least one feature should have high drift
    high_drift_features = [
        f for f, r in results.items()
        if r["drift_score"] > 0.3 and f != "Churn"
    ]
    assert len(high_drift_features) > 0, (
        "No high drift detected on clearly different distributions"
    )


def test_severity_high_above_0_3():
    """Scores above 0.3 should be classified as 'high' severity."""
    assert get_severity(0.5) == "high"
    assert get_severity(0.31) == "high"
    assert get_severity(0.9) == "high"
    assert get_severity(1.0) == "high"


def test_severity_medium_between_0_1_and_0_3():
    """Scores between 0.1 and 0.3 should be classified as 'medium' severity."""
    assert get_severity(0.2) == "medium"
    assert get_severity(0.15) == "medium"
    assert get_severity(0.11) == "medium"
    assert get_severity(0.29) == "medium"


def test_severity_low_below_0_1():
    """Scores at or below 0.1 should be classified as 'low' severity."""
    assert get_severity(0.05) == "low"
    assert get_severity(0.0) == "low"
    assert get_severity(0.1) == "low"
    assert get_severity(0.09) == "low"
