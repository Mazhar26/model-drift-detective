"""
test_alerts.py — Unit tests for email alert system.

Tests alert logic without actually sending emails.
All tests work with ALERTS_ENABLED=false (default).
"""

import pytest

from src.alerts import send_drift_alert, check_and_alert


# ── Tests ─────────────────────────────────────────────

def test_alerts_disabled_by_default():
    """send_drift_alert should return False when alerts are disabled."""
    result = send_drift_alert("test_feature", 0.5, "high")
    assert result is False, "Alert should not send when ALERTS_ENABLED=false"


def test_below_threshold_skipped():
    """Drift scores below ALERT_THRESHOLD should be skipped."""
    result = send_drift_alert("test_feature", 0.01, "low")
    assert result is False, "Low drift should not trigger alert"


def test_check_and_alert_returns_dict():
    """check_and_alert should return a status dict."""
    drift_results = {
        "feature_a": {
            "drift_detected": True,
            "drift_score": 0.5,
            "severity": "high",
        },
    }
    result = check_and_alert(drift_results)

    assert isinstance(result, dict)
    assert "alerts_enabled" in result
    assert "alerts_sent" in result
    assert "alerts_skipped" in result
    assert isinstance(result["alerts_sent"], list)


def test_check_and_alert_with_no_drift():
    """No alerts should be sent when no features have drift_detected=True."""
    drift_results = {
        "feature_a": {
            "drift_detected": False,
            "drift_score": 0.01,
            "severity": "low",
        },
    }
    result = check_and_alert(drift_results)

    assert len(result["alerts_sent"]) == 0
    assert result["alerts_skipped"] == 0
