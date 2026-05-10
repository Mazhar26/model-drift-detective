"""
Smoke test — quick sanity check for all core modules.
Run: python smoke_test.py
"""

from src.data_setup import load_data
from src.drift import detect_drift
from src.explain import explain_drift
from src.impact import analyze_impact
from src.importance import feature_importance_analysis
from src.timeline import simulate_drift_over_time

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name} — {detail}")
        failed += 1


# --- Data Loading ---
print("\n📦 Data Loading")
train, live = load_data()

check("Train set loaded", train is not None and not train.empty, "train is empty")
check("Live set loaded", live is not None and not live.empty, "live is empty")
check("Churn column exists", "Churn" in train.columns, "missing Churn column")
check("No NaN in train", train.isna().sum().sum() == 0, "NaNs found")
check("Churn is integer", train["Churn"].dtype in ["int64", "int32", "uint8"], f"got {train['Churn'].dtype}")

# --- Drift Detection ---
print("\n🔍 Drift Detection")
drift = detect_drift(train, live)

check("Drift results returned", isinstance(drift, dict) and len(drift) > 0, "empty dict")
check("Results have expected keys", all(
    {"p_value", "drift_detected", "drift_score", "severity"} <= set(v.keys())
    for v in drift.values()
), "missing keys in drift results")

# --- Explanation ---
print("\n📝 Drift Explanation")
explanation = explain_drift(train, live)

check("Explanation returned", isinstance(explanation, dict) and len(explanation) > 0, "empty dict")
check("Contains mean values", all(
    "train_mean" in v and "live_mean" in v
    for v in explanation.values()
), "missing mean fields")

# --- Impact ---
print("\n📉 Impact Analysis")
impact = analyze_impact(train, live)

check("Impact returned", isinstance(impact, dict), "not a dict")
check("Has accuracy fields", all(
    k in impact for k in ["train_accuracy", "live_accuracy", "accuracy_drop"]
), "missing fields")
check("Train accuracy > 0", impact.get("train_accuracy", 0) > 0, "zero accuracy")
check("Accuracy drop is number", isinstance(impact.get("accuracy_drop"), float), "not a float")

# --- Feature Importance ---
print("\n📊 Feature Importance")
importance = feature_importance_analysis(train, live)

check("Importance returned", isinstance(importance, dict) and len(importance) > 0, "empty dict")
check("Has change field", all(
    "change" in v for v in importance.values()
), "missing 'change' field")

# --- Timeline ---
print("\n📈 Timeline Simulation")
timeline = simulate_drift_over_time(steps=10)

check("Timeline returned", isinstance(timeline, list) and len(timeline) > 0, "empty list")
check("Steps have expected fields", all(
    {"step", "feature", "drift_score"} <= set(t.keys())
    for t in timeline
), "missing fields")
check("Drift increases over time",
      timeline[-1]["drift_score"] > timeline[0]["drift_score"],
      f"first={timeline[0]['drift_score']:.4f}, last={timeline[-1]['drift_score']:.4f}")

# --- Summary ---
print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*40}")

exit(0 if failed == 0 else 1)