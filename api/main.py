from fastapi import FastAPI, HTTPException, Query, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, RootModel
from typing import Any, Dict, List, Optional
from src.data_setup import load_data
from src.drift import detect_drift
from src.explain import explain_drift
from src.recommend import recommend_actions
from src.impact import analyze_impact
from src.timeline import simulate_drift_over_time
from src.importance import feature_importance_analysis
from src.history import save_drift_result, get_drift_history, get_drift_trend
from src.alerts import check_and_alert

from logger import get_logger

logger = get_logger(__name__)


# ══════════════════════════════════════════════════
# Pydantic Response Models
# ══════════════════════════════════════════════════

class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Error description")
    code: int = Field(..., description="HTTP status code")


class DriftFeatureResult(BaseModel):
    """Drift detection result for a single feature."""
    p_value: float = Field(..., description="KS-test p-value")
    drift_detected: bool = Field(..., description="Whether drift was detected")
    drift_score: float = Field(..., description="KS-test statistic (drift magnitude)")
    severity: str = Field(..., description="Drift severity: high, medium, or low")


class DriftResponse(RootModel[Dict[str, DriftFeatureResult]]):
    """Response model for drift detection endpoint."""


class ExplainFeatureResult(BaseModel):
    """Explanation result for a single feature."""
    severity: str = Field(..., description="Drift severity classification")
    p_value: float = Field(..., description="KS-test p-value")
    mean_shift: float = Field(..., description="Difference in means between train and live")
    segment_shift: Any = Field(..., description="Segment-level distribution shift")


class ExplainResponse(RootModel[Dict[str, ExplainFeatureResult]]):
    """Response model for drift explanation endpoint."""


class ImpactResponse(BaseModel):
    """Response model for accuracy impact analysis."""
    train_accuracy: float = Field(..., description="Model accuracy on training data")
    live_accuracy: float = Field(..., description="Model accuracy on live/drifted data")
    accuracy_drop: float = Field(..., description="Accuracy degradation (train - live)")


class RecommendResponse(RootModel[Dict[str, str]]):
    """Response model for action recommendations."""


class ImportanceFeatureResult(BaseModel):
    """Feature importance result for a single feature."""
    train_importance: float = Field(..., description="Feature importance on training data")
    live_importance: float = Field(..., description="Feature importance on live data")
    change: float = Field(..., description="Change in importance (live - train)")


class ImportanceResponse(RootModel[Dict[str, ImportanceFeatureResult]]):
    """Response model for feature importance comparison."""


class TimelineEntry(BaseModel):
    """Single entry in drift timeline."""
    step: int = Field(..., description="Simulation step number")
    feature: str = Field(..., description="Top drifted feature at this step")
    drift_score: float = Field(..., description="Maximum drift score at this step")


class TimelineResponse(RootModel[List[TimelineEntry]]):
    """Response model for drift timeline simulation."""


class SummaryResponse(BaseModel):
    """Response model for system summary."""
    total_features: int = Field(..., description="Total number of analyzed features")
    drifted_features_count: int = Field(..., description="Number of features with detected drift")
    top_drift_feature: Optional[str] = Field(None, description="Feature with highest drift score")
    accuracy_drop: float = Field(..., description="Model accuracy degradation")
    status: str = Field(..., description="Overall system status")


class HistoryEntry(BaseModel):
    """Single drift history record."""
    id: int = Field(..., description="Record ID")
    timestamp: str = Field(..., description="ISO timestamp of drift check")
    features_drifted: int = Field(..., description="Number of drifted features")
    avg_drift_score: float = Field(..., description="Average drift score across all features")
    accuracy_drop: float = Field(..., description="Model accuracy degradation")
    severity: str = Field(..., description="Overall severity: high, medium, or low")


class DriftTrendEntry(BaseModel):
    """Daily drift trend record."""
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    avg_drift_score: float = Field(..., description="Average drift score for the day")
    avg_accuracy_drop: float = Field(..., description="Average accuracy drop for the day")
    check_count: int = Field(..., description="Number of drift checks on this day")


class HealthResponse(BaseModel):
    """Response model for health check."""
    message: str = Field(..., description="API status message")


# ══════════════════════════════════════════════════
# Application Setup
# ══════════════════════════════════════════════════

app = FastAPI(
    title="Model Drift Detective API",
    description=(
        "REST API for detecting, explaining, and monitoring model drift "
        "in ML systems. Uses KS-test based statistical drift detection "
        "on the Telco Customer Churn dataset."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Versioned API router — all domain endpoints live under /api/v1/
router = APIRouter(prefix="/api/v1", tags=["v1"])

# Load data once at startup
logger.info("Loading datasets at startup")
train, live = load_data()

# Pre-compute expensive results at startup (data is static)
_drift_cache = None
_impact_cache = None
_importance_cache = None


def get_drift():
    """Lazy-load and cache drift detection results."""
    global _drift_cache
    if _drift_cache is None:
        logger.info("Computing drift results (first call)")
        _drift_cache = detect_drift(train, live)
    return _drift_cache


def get_impact():
    """Lazy-load and cache impact analysis results."""
    global _impact_cache
    if _impact_cache is None:
        logger.info("Computing impact analysis (first call)")
        _impact_cache = analyze_impact(train, live)
    return _impact_cache


def get_importance():
    """Lazy-load and cache feature importance results."""
    global _importance_cache
    if _importance_cache is None:
        logger.info("Computing feature importance (first call)")
        _importance_cache = feature_importance_analysis(train, live)
    return _importance_cache


# ══════════════════════════════════════════════════
# Global Exception Handler
# ══════════════════════════════════════════════════

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all handler for unhandled exceptions."""
    logger.error("Unhandled exception on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "code": 500}
    )


# ══════════════════════════════════════════════════
# Health Check — No version prefix
# ══════════════════════════════════════════════════

@app.get(
    "/",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verify that the API is running and responsive.",
    tags=["System"]
)
def home():
    """Health check endpoint — returns API status."""
    return {"message": "Model Drift Detective API is running"}


# ══════════════════════════════════════════════════
# Versioned API Endpoints — /api/v1/*
# ══════════════════════════════════════════════════

@router.get(
    "/detect",
    summary="Detect Drift",
    description=(
        "Run KS-test based drift detection across all numeric features. "
        "Returns only features with drift score above the specified threshold."
    ),
    tags=["Drift Detection"],
    responses={
        200: {"description": "Drift detection results"},
        400: {"model": ErrorResponse, "description": "Invalid threshold value"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def detect(
    threshold: float = Query(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum drift score to include in results (0.0 to 1.0)"
    )
):
    """
    Detect statistical drift between training and live data.

    Uses the Kolmogorov-Smirnov test on each numeric feature.
    Only features with drift_score > threshold are returned.
    """
    try:
        if threshold < 0 or threshold > 1:
            logger.warning("Invalid threshold: %s", threshold)
            raise HTTPException(
                status_code=400,
                detail={"error": "Threshold must be between 0 and 1", "code": 400}
            )

        results = get_drift()

        if not results:
            logger.warning("No drift results available")
            return {}

        filtered = {
            feature: res
            for feature, res in results.items()
            if res.get("drift_score", 0) > threshold
        }

        logger.info("Detect endpoint: %d features above threshold %.2f", len(filtered), threshold)

        # Save to drift history
        try:
            impact_data = get_impact()
            save_drift_result({
                "drift_results": results,
                "accuracy_drop": impact_data.get("accuracy_drop", 0.0)
            })
        except Exception as save_err:
            logger.error("Failed to save drift history: %s", save_err)

        # Trigger email alerts if enabled
        try:
            alert_result = check_and_alert(results)
            if alert_result["alerts_sent"]:
                logger.info("Alerts sent for: %s", alert_result["alerts_sent"])
            else:
                logger.debug("No alerts triggered (enabled=%s)", alert_result["alerts_enabled"])
        except Exception as alert_err:
            logger.error("Alert check failed: %s", alert_err)

        return filtered

    except HTTPException:
        raise
    except Exception as e:
        logger.error("/api/v1/detect failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": f"Drift detection failed: {str(e)}", "code": 500}
        )


@router.get(
    "/explain",
    summary="Explain Drift",
    description=(
        "Provide root cause analysis for detected drift, including "
        "mean shifts and segment-level distribution changes."
    ),
    tags=["Drift Analysis"],
    responses={
        200: {"description": "Drift explanations for all drifted features"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def explain():
    """
    Generate explanations for all features where drift was detected.

    Includes severity classification, p-value, mean shift, and segment analysis.
    """
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

        logger.info("Explain endpoint: %d features explained", len(final_output))
        return final_output

    except Exception as e:
        logger.error("/api/v1/explain failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": f"Drift explanation failed: {str(e)}", "code": 500}
        )


@router.get(
    "/recommend",
    summary="Get Recommendations",
    description=(
        "Generate smart action recommendations based on drift severity "
        "and accuracy impact analysis."
    ),
    tags=["Drift Analysis"],
    responses={
        200: {"description": "Recommended actions per feature"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def recommend():
    """
    Generate action recommendations based on drift severity and model impact.

    Recommendations range from 'monitor closely' to 'immediate retraining required'.
    """
    try:
        drift = get_drift()
        impact_data = get_impact()
        recommendations = recommend_actions(drift, impact_data)
        logger.info("Recommend endpoint: %d recommendations", len(recommendations))
        return recommendations

    except Exception as e:
        logger.error("/api/v1/recommend failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": f"Recommendation generation failed: {str(e)}", "code": 500}
        )


@router.get(
    "/impact",
    response_model=ImpactResponse,
    summary="Analyze Impact",
    description=(
        "Measure the accuracy impact of drift by comparing model performance "
        "on training data versus live/drifted data."
    ),
    tags=["Drift Analysis"],
    responses={
        200: {"description": "Accuracy impact metrics"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def impact():
    """
    Analyze accuracy impact of drift.

    Trains a RandomForest model and compares accuracy on train vs live data.
    """
    try:
        result = get_impact()
        logger.info("Impact endpoint called")
        return result

    except Exception as e:
        logger.error("/api/v1/impact failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": f"Impact analysis failed: {str(e)}", "code": 500}
        )


@router.get(
    "/timeline",
    summary="Drift Timeline",
    description=(
        "Simulate drift progression over time by incrementally adding noise "
        "and measuring drift scores at each step."
    ),
    tags=["Simulation"],
    responses={
        200: {"description": "List of drift timeline entries"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def timeline():
    """
    Simulate drift over time with progressive noise injection.

    Returns a timeline of drift scores showing how drift evolves.
    """
    try:
        result = simulate_drift_over_time()
        logger.info("Timeline endpoint: %d data points", len(result))
        return result

    except Exception as e:
        logger.error("/api/v1/timeline failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": f"Timeline simulation failed: {str(e)}", "code": 500}
        )


@router.get(
    "/importance",
    summary="Feature Importance",
    description=(
        "Compare feature importance between models trained on training data "
        "and live/drifted data to identify importance shifts."
    ),
    tags=["Drift Analysis"],
    responses={
        200: {"description": "Feature importance comparison"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def importance():
    """
    Compare feature importance between train and live models.

    Highlights which features gained or lost importance after drift.
    """
    try:
        result = get_importance()
        logger.info("Importance endpoint called")
        return result

    except Exception as e:
        logger.error("/api/v1/importance failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": f"Feature importance analysis failed: {str(e)}", "code": 500}
        )


@router.get(
    "/summary",
    response_model=SummaryResponse,
    summary="System Summary",
    description=(
        "Get a high-level summary of the drift detection system status, "
        "including drift counts, top drifted feature, and overall health."
    ),
    tags=["System"],
    responses={
        200: {"description": "System summary with drift status"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def summary():
    """
    Get high-level system summary.

    Includes total/drifted feature counts, accuracy drop, and overall status.
    """
    try:
        drift = get_drift()
        impact_data = get_impact()

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
        if impact_data.get("accuracy_drop", 0) > 0.1:
            status = "High Impact Drift"
        elif drifted_features:
            status = "Moderate Drift"
        else:
            status = "No Significant Drift"

        logger.info("Summary endpoint: status=%s, drifted=%d", status, len(drifted_features))

        return {
            "total_features": len(drift),
            "drifted_features_count": len(drifted_features),
            "top_drift_feature": top_feature,
            "accuracy_drop": impact_data.get("accuracy_drop", 0),
            "status": status
        }

    except Exception as e:
        logger.error("/api/v1/summary failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": f"Summary generation failed: {str(e)}", "code": 500}
        )


@router.get(
    "/history",
    response_model=List[HistoryEntry],
    summary="Drift History",
    description=(
        "Retrieve the last 50 drift check results from the persistent "
        "SQLite history database."
    ),
    tags=["History"],
    responses={
        200: {"description": "List of drift history records"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def history():
    """
    Get historical drift check results.

    Returns the last 50 drift detection runs with timestamps,
    drifted feature counts, average scores, and severity.
    """
    try:
        records = get_drift_history(limit=50)
        logger.info("History endpoint: %d records", len(records))
        return records

    except Exception as e:
        logger.error("/api/v1/history failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": f"History retrieval failed: {str(e)}", "code": 500}
        )


@router.get(
    "/history/trend",
    response_model=List[DriftTrendEntry],
    summary="Drift Trend",
    description="Get daily average drift scores for trend analysis.",
    tags=["History"],
    responses={
        200: {"description": "Daily drift trend data"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def history_trend():
    """
    Get daily aggregated drift trends.

    Returns daily averages of drift scores and accuracy drops.
    """
    try:
        trend = get_drift_trend()
        logger.info("History trend endpoint: %d days", len(trend))
        return trend

    except Exception as e:
        logger.error("/api/v1/history/trend failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": f"Trend retrieval failed: {str(e)}", "code": 500}
        )


# ══════════════════════════════════════════════════
# Register the versioned router
# ══════════════════════════════════════════════════
app.include_router(router)
