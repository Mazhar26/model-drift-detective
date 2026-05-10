import numpy as np
from src.data_setup import load_data
from src.drift import detect_drift
from logger import get_logger

logger = get_logger(__name__)


def simulate_drift_over_time(steps=10):
    """
    Simulate increasing drift over time by progressively adding noise.

    Args:
        steps: Number of simulation steps.

    Returns:
        List of dicts with step, feature, and drift_score.
    """
    logger.info("Starting drift timeline simulation with %d steps", steps)
    timeline = []

    # Load data ONCE, not per step
    train, base_live = load_data()

    for step in range(steps):
        live = base_live.copy()

        # Increase drift over time
        live['MonthlyCharges'] = live['MonthlyCharges'] + np.random.normal(step * 5, 10, len(live))

        drift = detect_drift(train, live)

        if not drift:
            logger.warning("No drift results for step %d", step)
            continue

        # Get top drift score
        top_feature = max(drift.items(), key=lambda x: x[1]["drift_score"])

        timeline.append({
            "step": step,
            "feature": top_feature[0],
            "drift_score": top_feature[1]["drift_score"]
        })

        logger.debug(
            "Step %d: top=%s, score=%.4f",
            step, top_feature[0], top_feature[1]["drift_score"]
        )

    logger.info("Timeline simulation completed — %d data points", len(timeline))
    return timeline