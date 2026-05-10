import numpy as np
from src.data_setup import load_data
from src.drift import detect_drift

def simulate_drift_over_time(steps=10):
    timeline = []

    # ✅ Load data ONCE, not 10 times
    train, base_live = load_data()

    for step in range(steps):
        live = base_live.copy()

        # Increase drift over time
        live['MonthlyCharges'] = live['MonthlyCharges'] + np.random.normal(step * 5, 10, len(live))

        drift = detect_drift(train, live)

        if not drift:
            continue

        # Get top drift score
        top_feature = max(drift.items(), key=lambda x: x[1]["drift_score"])
        
        timeline.append({
            "step": step,
            "feature": top_feature[0],
            "drift_score": top_feature[1]["drift_score"]
        })

    return timeline