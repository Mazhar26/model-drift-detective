"""
test_importance.py — Unit tests for feature importance analysis module.
"""

import pytest
import pandas as pd
from src.data_setup import load_data
from src.importance import get_feature_importance, feature_importance_analysis


@pytest.fixture(scope="module")
def data():
    """Load train and live datasets once."""
    return load_data()


def test_importance_analysis_runs(data):
    """Importance analysis should execute and return expected dictionary mapping."""
    train, live = data
    result = get_feature_importance(train, live)
    assert isinstance(result, dict)
    assert len(result) > 0

    # Verify keys
    assert "MonthlyCharges" in result
    feature_result = result["MonthlyCharges"]
    assert "train_importance" in feature_result
    assert "live_importance" in feature_result
    assert "change" in feature_result


def test_importance_analysis_alias(data):
    """The public alias should point to the correct function and run."""
    train, live = data
    result = feature_importance_analysis(train, live)
    assert isinstance(result, dict)
    assert len(result) > 0


def test_importance_analysis_empty():
    """Importance analysis should handle empty dataframes gracefully."""
    train = pd.DataFrame()
    live = pd.DataFrame()
    result = get_feature_importance(train, live)
    assert result == {}


def test_importance_analysis_missing_churn(data):
    """Importance analysis should handle missing target column Churn gracefully."""
    train, live = data
    train_no_churn = train.drop(columns=["Churn"])
    result = get_feature_importance(train_no_churn, live)
    assert result == {}
