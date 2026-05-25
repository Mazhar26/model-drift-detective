"""
test_timeline.py — Unit tests for drift timeline simulation module.
"""

from src.timeline import simulate_drift_over_time


def test_timeline_simulation_runs():
    """Timeline simulation should return expected list of timeline entries."""
    steps = 3
    result = simulate_drift_over_time(steps=steps)
    assert isinstance(result, list)
    assert len(result) == steps

    for entry in result:
        assert isinstance(entry, dict)
        assert "step" in entry
        assert "feature" in entry
        assert "drift_score" in entry
        assert isinstance(entry["step"], int)
        assert isinstance(entry["feature"], str)
        assert isinstance(entry["drift_score"], float)
