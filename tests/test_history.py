"""
test_history.py — Unit tests for SQLite drift history module.

Tests database creation, saving, retrieval, and trend aggregation.
"""

import os
import pytest

from src.history import _get_connection, save_drift_result, get_drift_history, get_drift_trend


# ── Fixtures ──────────────────────────────────────────

@pytest.fixture
def sample_drift_result():
    """Realistic drift result payload."""
    return {
        "drift_results": {
            "MonthlyCharges": {
                "p_value": 0.001,
                "drift_detected": True,
                "drift_score": 0.45,
                "severity": "high",
            },
            "tenure": {
                "p_value": 0.02,
                "drift_detected": True,
                "drift_score": 0.15,
                "severity": "medium",
            },
            "Churn": {
                "p_value": 0.5,
                "drift_detected": False,
                "drift_score": 0.01,
                "severity": "low",
            },
        },
        "accuracy_drop": 0.18,
    }


# ── Tests ─────────────────────────────────────────────

def test_database_table_creation():
    """Database and table should be created without errors."""
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='drift_history'"
    )
    tables = cursor.fetchall()
    conn.close()

    assert len(tables) == 1, "drift_history table should exist"


def test_save_and_retrieve(sample_drift_result):
    """Saved drift result should be retrievable from history."""
    # Save
    save_drift_result(sample_drift_result)

    # Retrieve
    history = get_drift_history(limit=1)

    assert len(history) >= 1, "Should have at least 1 history record"

    record = history[0]
    assert "timestamp" in record
    assert "features_drifted" in record
    assert "avg_drift_score" in record
    assert "accuracy_drop" in record
    assert "severity" in record


def test_features_drifted_count(sample_drift_result):
    """features_drifted should count only drift_detected=True features."""
    save_drift_result(sample_drift_result)
    history = get_drift_history(limit=1)

    # Our sample has 2 drifted features (MonthlyCharges + tenure)
    record = history[0]
    assert record["features_drifted"] == 2, (
        f"Expected 2 drifted features, got {record['features_drifted']}"
    )


def test_avg_drift_score_calculation(sample_drift_result):
    """avg_drift_score should be the mean of all feature drift scores."""
    save_drift_result(sample_drift_result)
    history = get_drift_history(limit=1)

    record = history[0]
    # Mean of 0.45, 0.15, 0.01 = 0.2033...
    expected_avg = (0.45 + 0.15 + 0.01) / 3
    assert abs(record["avg_drift_score"] - expected_avg) < 0.01, (
        f"Expected avg ~{expected_avg:.4f}, got {record['avg_drift_score']}"
    )


def test_trend_returns_list():
    """get_drift_trend should return a list (possibly empty)."""
    trend = get_drift_trend()
    assert isinstance(trend, list), f"Trend should be list, got {type(trend)}"
