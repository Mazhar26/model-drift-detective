from logger import get_logger

logger = get_logger(__name__)


def recommend_actions(drift_results, impact):
    """
    Generate smart action recommendations based on drift severity and impact.

    Args:
        drift_results: Dict of drift detection results per feature.
        impact: Dict with accuracy impact metrics.

    Returns:
        Dict mapping feature names to recommended actions.
    """
    logger.info("Generating recommendations")
    recommendations = {}

    # Safe access
    accuracy_drop = impact.get("accuracy_drop", 0)

    for feature, result in drift_results.items():

        if not result.get("drift_detected", False):
            continue

        severity = result.get("severity", "low")

        # Smarter decision logic
        if accuracy_drop > 0.1 and severity == "high":
            action = "🚨 Immediate retraining required"
            logger.warning(
                "CRITICAL: %s requires immediate retraining (drop=%.4f)",
                feature, accuracy_drop
            )

        elif severity == "high":
            action = "⚠️ High drift — retrain soon"
            logger.warning("HIGH: %s needs retraining soon", feature)

        elif severity == "medium":
            action = "👀 Monitor closely"
            logger.info("MEDIUM: %s should be monitored", feature)

        else:
            action = "Low priority drift"
            logger.debug("LOW: %s — low priority", feature)

        recommendations[feature] = action

    logger.info("Recommendations generated — %d actions", len(recommendations))
    return recommendations
