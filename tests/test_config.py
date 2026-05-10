"""
test_config.py — Unit tests for centralized configuration.

All tests are independent and do not require a running server.
They verify that config values have valid types and defaults.
"""

import pytest

from config import (
    API_PORT,
    DEFAULT_THRESHOLD,
    LOG_LEVEL,
    API_HOST,
    DATA_PATH,
    MODEL_PARAMS,
    SEVERITY_HIGH_THRESHOLD,
    SEVERITY_MEDIUM_THRESHOLD,
    P_VALUE_THRESHOLD,
)


# ── Tests ─────────────────────────────────────────────

def test_default_threshold_is_valid():
    """DEFAULT_THRESHOLD must be a float between 0 and 1."""
    assert isinstance(DEFAULT_THRESHOLD, float), (
        f"DEFAULT_THRESHOLD should be float, got {type(DEFAULT_THRESHOLD)}"
    )
    assert 0.0 <= DEFAULT_THRESHOLD <= 1.0, (
        f"DEFAULT_THRESHOLD out of range: {DEFAULT_THRESHOLD}"
    )


def test_api_port_is_integer():
    """API_PORT must be a valid integer port number."""
    assert isinstance(API_PORT, int), (
        f"API_PORT should be int, got {type(API_PORT)}"
    )
    assert 1 <= API_PORT <= 65535, (
        f"API_PORT out of valid range: {API_PORT}"
    )


def test_log_level_is_valid_string():
    """LOG_LEVEL must be a valid Python logging level name."""
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    assert isinstance(LOG_LEVEL, str), (
        f"LOG_LEVEL should be str, got {type(LOG_LEVEL)}"
    )
    assert LOG_LEVEL in valid_levels, (
        f"LOG_LEVEL '{LOG_LEVEL}' not in valid levels: {valid_levels}"
    )
