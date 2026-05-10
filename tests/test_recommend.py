"""
test_recommend.py — Unit tests for recommendation engine.

All tests are independent and do not require a running server.
They test the recommendation logic directly with synthetic inputs.
"""

import pytest

from src.recommend import recommend_actions


# ── Fixtures ──────────────────────────────────────────

@pytest.fixture
def high_drift_results():
    """Drift results with high severity features."""
    return {
        "MonthlyCharges": {
            "p_value": 0.001,
            "drift_detected": True,
            "drift_score": 0.85,
            "severity": "high",
        },
        "tenure": {
            "p_value": 0.01,
            "drift_detected": True,
            "drift_score": 0.45,
            "severity": "high",
        },
    }


@pytest.fixture
def low_drift_results():
    """Drift results with low severity features."""
    return {
        "feature_a": {
            "p_value": 0.04,
            "drift_detected": True,
            "drift_score": 0.08,
            "severity": "low",
        },
    }


@pytest.fixture
def high_impact():
    """Impact results with significant accuracy drop."""
    return {
        "train_accuracy": 0.95,
        "live_accuracy": 0.75,
        "accuracy_drop": 0.20,
    }


@pytest.fixture
def low_impact():
    """Impact results with minimal accuracy drop."""
    return {
        "train_accuracy": 0.95,
        "live_accuracy": 0.93,
        "accuracy_drop": 0.02,
    }


# ── Tests ─────────────────────────────────────────────

def test_high_drift_returns_retrain(high_drift_results, high_impact):
    """High drift + high impact should recommend immediate retraining."""
    recs = recommend_actions(high_drift_results, high_impact)

    assert len(recs) > 0
    # At least one feature should have "retraining" in recommendation
    retrain_recs = [v for v in recs.values() if "retrain" in v.lower()]
    assert len(retrain_recs) > 0, (
        f"Expected retraining recommendation, got: {recs}"
    )


def test_low_drift_returns_monitor(low_drift_results, low_impact):
    """Low drift + low impact should not recommend retraining."""
    recs = recommend_actions(low_drift_results, low_impact)

    for feature, action in recs.items():
        assert "Immediate retraining" not in action, (
            f"Low drift should not trigger immediate retraining: {action}"
        )


def test_recommendations_not_empty(high_drift_results, high_impact):
    """Recommendations should not be empty when drift is detected."""
    recs = recommend_actions(high_drift_results, high_impact)

    assert isinstance(recs, dict)
    assert len(recs) > 0, "Recommendations should not be empty for drifted features"


def test_recommendation_has_required_keys(high_drift_results, high_impact):
    """Each recommendation should be a feature→action string mapping."""
    recs = recommend_actions(high_drift_results, high_impact)

    for feature, action in recs.items():
        assert isinstance(feature, str), f"Feature key should be string, got {type(feature)}"
        assert isinstance(action, str), f"Action should be string, got {type(action)}"
        assert len(action) > 0, f"Action for {feature} should not be empty"
