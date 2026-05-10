def recommend_actions(drift_results, impact):
    recommendations = {}

    # ✅ Safe access
    accuracy_drop = impact.get("accuracy_drop", 0)

    for feature, result in drift_results.items():

        if not result.get("drift_detected", False):
            continue

        drift_score = result.get("drift_score", 0)
        severity = result.get("severity", "low")

        # 🔥 Smarter decision logic
        if accuracy_drop > 0.1 and severity == "high":
            action = "🚨 Immediate retraining required"

        elif severity == "high":
            action = "⚠️ High drift — retrain soon"

        elif severity == "medium":
            action = "👀 Monitor closely"

        else:
            action = "Low priority drift"

        recommendations[feature] = action

    return recommendations