from logger import get_logger

logger = get_logger(__name__)


def recommend_actions(drift_results, impact):
    """
    Generate smart recommendations based on:
    - drift severity
    - drift score
    - model accuracy degradation

    Args:
        drift_results:
            Drift detection output.

        impact:
            Impact analysis output.

    Returns:
        Dictionary of recommendations.
    """

    logger.info("Starting recommendation analysis")

    recommendations = {}

    try:

        if not drift_results:
            logger.warning("No drift results provided")
            return {}

        accuracy_drop = impact.get("accuracy_drop", 0)

        for feature, result in drift_results.items():

            if not result.get("drift_detected", False):
                continue

            severity = result.get("severity", "low")

            # ============================================
            # Recommendation Logic
            # ============================================

            if severity == "high":

                if accuracy_drop > 0.10:

                    action = (
                        "🚨 Critical drift detected. " "Immediate model retraining recommended."
                    )

                else:

                    action = (
                        "⚠️ High feature drift detected. " "Monitor closely and prepare retraining."
                    )

            elif severity == "medium":

                action = "👀 Moderate drift detected. " "Increase monitoring frequency."

            else:

                action = "✅ Minor drift detected. " "No immediate action required."

            recommendations[feature] = action

            logger.info("Recommendation generated for %s", feature)

        logger.info("Recommendation analysis completed — %d recommendations", len(recommendations))

        return recommendations

    except Exception as e:

        logger.error("Recommendation engine failed: %s", e)

        return {}
