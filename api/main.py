from fastapi import FastAPI
from src.data_setup import load_data
from src.drift import detect_drift
from src.explain import explain_drift
from src.recommend import recommend_actions
from src.impact import analyze_impact
from src.timeline import simulate_drift_over_time
from src.importance import feature_importance_analysis
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Load data once
train, live = load_data()

# ✅ Pre-compute expensive results at startup (data is static)
_drift_cache = None
_impact_cache = None
_importance_cache = None


def get_drift():
    global _drift_cache
    if _drift_cache is None:
        _drift_cache = detect_drift(train, live)
    return _drift_cache


def get_impact():
    global _impact_cache
    if _impact_cache is None:
        _impact_cache = analyze_impact(train, live)
    return _impact_cache


def get_importance():
    global _importance_cache
    if _importance_cache is None:
        _importance_cache = feature_importance_analysis(train, live)
    return _importance_cache


@app.get("/")
def home():
    return {"message": "Model Drift Detective API is running"}


# ✅ SAFE DETECT
@app.get("/detect")
def detect(threshold: float = 0.3):
    try:
        results = get_drift()

        if not results:
            return {}

        filtered = {
            feature: res
            for feature, res in results.items()
            if res.get("drift_score", 0) > threshold
        }

        return filtered

    except Exception as e:
        logger.error(f"❌ /detect failed: {e}")
        return {}


# ✅ FIXED EXPLAIN
@app.get("/explain")
def explain():
    try:
        results = get_drift()
        explanations = explain_drift(train, live)

        final_output = {}

        for feature, result in results.items():
            if result["drift_detected"]:
                final_output[feature] = {
                    "severity": "high" if result["drift_score"] > 0.8 else "medium",
                    "p_value": result["p_value"],
                    "mean_shift": explanations.get(feature, {}).get("difference", 0),
                    "segment_shift": explanations.get(feature, {}).get("segment_shift", {})
                }

        return final_output

    except Exception as e:
        logger.error(f"❌ /explain failed: {e}")
        return {}


# ✅ SAFE RECOMMEND
@app.get("/recommend")
def recommend():
    try:
        drift = get_drift()
        impact = get_impact()
        return recommend_actions(drift, impact)

    except Exception as e:
        logger.error(f"❌ /recommend failed: {e}")
        return {}


# ✅ SAFE IMPACT
@app.get("/impact")
def impact():
    try:
        return get_impact()

    except Exception as e:
        logger.error(f"❌ /impact failed: {e}")
        return {}


# ✅ SAFE TIMELINE
@app.get("/timeline")
def timeline():
    try:
        return simulate_drift_over_time()

    except Exception as e:
        logger.error(f"❌ /timeline failed: {e}")
        return {}


# ✅ SAFE IMPORTANCE
@app.get("/importance")
def importance():
    try:
        return get_importance()

    except Exception as e:
        logger.error(f"❌ /importance failed: {e}")
        return {}


# ✅ SAFE SUMMARY
@app.get("/summary")
def summary():
    try:
        drift = get_drift()
        impact = get_impact()

        if not drift:
            return {
                "total_features": 0,
                "drifted_features_count": 0,
                "top_drift_feature": None,
                "accuracy_drop": 0,
                "status": "No Data"
            }

        drifted_features = [
            k for k, v in drift.items() if v["drift_detected"]
        ]

        top_feature = max(
            drift.items(),
            key=lambda x: x[1]["drift_score"]
        )[0] if drift else None

        # Status logic
        if impact.get("accuracy_drop", 0) > 0.1:
            status = "High Impact Drift"
        elif drifted_features:
            status = "Moderate Drift"
        else:
            status = "No Significant Drift"

        return {
            "total_features": len(drift),
            "drifted_features_count": len(drifted_features),
            "top_drift_feature": top_feature,
            "accuracy_drop": impact.get("accuracy_drop", 0),
            "status": status
        }

    except Exception as e:
        logger.error(f"❌ /summary failed: {e}")
        return {"error": str(e)}