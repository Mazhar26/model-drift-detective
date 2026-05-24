import numpy as np
from src.data_setup import load_data
from src.drift import detect_drift
from logger import get_logger

logger = get_logger(__name__)


def simulate_drift_over_time(steps=10):
    """
    Simulate increasing drift over time.

    This function progressively modifies live data
    to imitate real-world production drift.

    Args:
        steps (int):
            Number of simulation steps.

    Returns:
        list:
            Timeline containing top drifted feature
            and drift score per step.
    """

    logger.info(
        "Starting drift timeline simulation with %d steps",
        steps
    )

    timeline = []

    # Load dataset once
    train, base_live = load_data()

    for step in range(steps):

        # Create fresh copy for this step
        live = base_live.copy()

        # -----------------------------------
        # Simulate MonthlyCharges drift
        # -----------------------------------
        live['MonthlyCharges'] = (
            live['MonthlyCharges']
            + np.random.normal(
                loc=step * 5,
                scale=10,
                size=len(live)
            )
        )

        # -----------------------------------
        # Simulate tenure drift
        # -----------------------------------
        live['tenure'] = (
            live['tenure']
            - np.random.normal(
                loc=step * 2,
                scale=3,
                size=len(live)
            )
        )

        # Prevent invalid negative tenure
        live['tenure'] = live['tenure'].clip(lower=0)

        # -----------------------------------
        # Run drift detection
        # -----------------------------------
        drift = detect_drift(train, live)

        if not drift:
            logger.warning(
                "No drift results generated for step %d",
                step
            )
            continue

        # -----------------------------------
        # Get highest drift feature
        # -----------------------------------
        top_feature = max(
            drift.items(),
            key=lambda x: x[1]["drift_score"]
        )

        timeline.append({
            "step": step,
            "feature": top_feature[0],
            "drift_score": top_feature[1]["drift_score"]
        })

        logger.info(
            "Step %d completed — top feature=%s score=%.4f",
            step,
            top_feature[0],
            top_feature[1]["drift_score"]
        )

    logger.info(
        "Timeline simulation completed — %d points generated",
        len(timeline)
    )

    return timeline
