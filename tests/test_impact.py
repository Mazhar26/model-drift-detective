"""
test_impact.py — Unit tests for impact analysis module.

All tests are independent and do not require a running server.
They test the impact analysis logic using the real Telco dataset.
"""

import pytest

from src.data_setup import load_data
from src.impact import analyze_impact


# ── Fixtures ──────────────────────────────────────────

@pytest.fixture(scope="module")
def impact_results():
    """Run impact analysis once and reuse across tests."""
    train, live = load_data()
    return analyze_impact(train, live)


# ── Tests ─────────────────────────────────────────────

def test_train_accuracy_above_zero(impact_results):
    """Training accuracy should be above zero."""
    assert impact_results["train_accuracy"] > 0, (
        f"Train accuracy should be > 0, got {impact_results['train_accuracy']}"
    )


def test_live_accuracy_above_zero(impact_results):
    """Live accuracy should be above zero."""
    assert impact_results["live_accuracy"] > 0, (
        f"Live accuracy should be > 0, got {impact_results['live_accuracy']}"
    )


def test_accuracy_drop_is_calculated(impact_results):
    """Accuracy drop should equal train_accuracy - live_accuracy."""
    expected_drop = impact_results["train_accuracy"] - impact_results["live_accuracy"]
    actual_drop = impact_results["accuracy_drop"]

    assert abs(actual_drop - expected_drop) < 1e-6, (
        f"Accuracy drop mismatch: expected {expected_drop}, got {actual_drop}"
    )


def test_accuracy_values_between_0_and_1(impact_results):
    """All accuracy values should be between 0 and 1."""
    assert 0.0 <= impact_results["train_accuracy"] <= 1.0, (
        f"Train accuracy out of range: {impact_results['train_accuracy']}"
    )
    assert 0.0 <= impact_results["live_accuracy"] <= 1.0, (
        f"Live accuracy out of range: {impact_results['live_accuracy']}"
    )
    assert -1.0 <= impact_results["accuracy_drop"] <= 1.0, (
        f"Accuracy drop out of range: {impact_results['accuracy_drop']}"
    )
