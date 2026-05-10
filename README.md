# 🧠 Model Drift Detective

An AI-powered model monitoring platform that detects, explains, and recommends actions for **data drift** in machine learning models. Built with **FastAPI** + **Streamlit** on the Telco Customer Churn dataset.

---

## 📸 Screenshots

### Main Dashboard
> Lightweight overview with key metrics, drift chart, and top recommendations at a glance.

![Dashboard](screenshots/dashboard.png)

### System Overview
> Quick health check — drifted feature count, top drifted feature, accuracy drop, and system status.

![Overview](screenshots/overview.png)

### Drift Detection
> Interactive threshold slider to explore which features have drifted, with severity labels and bar chart.

![Drift Detection](screenshots/drift.png)

### Drift Explanation
> Feature-level deep dive — severity, p-value, mean shift, and segment distribution changes.

![Drift Explanation](screenshots/explanation.png)

### Impact Analysis
> Model performance comparison between training and live data with accuracy drop metric.

![Impact Analysis](screenshots/impact.png)

### Drift Timeline
> Simulated drift over 10 steps showing how drift scores increase over time.

![Drift Timeline](screenshots/timeline.png)

### Feature Importance
> Comparison of feature importance between train and live models, highlighting the biggest changes.

![Feature Importance](screenshots/importance.png)

### Recommendations
> Smart, severity-based action items — from "Monitor closely" to "Immediate retraining required."

![Recommendations](screenshots/recommendations.png)

---

## 🏗️ Architecture

```
model-drift-mvp/
├── api/
│   └── main.py              # FastAPI backend (8 endpoints)
├── src/
│   ├── data_setup.py         # Data loading + drift simulation
│   ├── drift.py              # KS-test based drift detection
│   ├── explain.py            # Drift explanation with segment analysis
│   ├── impact.py             # Model accuracy impact analysis
│   ├── importance.py         # Feature importance comparison
│   ├── recommend.py          # Smart action recommendations
│   └── timeline.py           # Drift simulation over time
├── pages/                    # Streamlit sidebar pages
│   ├── 1_Overview.py
│   ├── 2_Drift.py
│   ├── 3_Explanation.py
│   ├── 4_Impact.py
│   ├── 5_Timeline.py
│   ├── 6_Importance.py
│   └── 7_Recommendations.py
├── data/
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
├── dashboard.py              # Streamlit main dashboard
├── utils.py                  # Shared utilities (API client)
├── smoke_test.py             # Automated smoke test (18 checks)
└── requirements.txt
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python -m uvicorn api.main:app --port 8000
```

### 3. Start the Dashboard

```bash
streamlit run dashboard.py
```

### 4. Open in Browser

Navigate to **http://localhost:8501**

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/detect?threshold=0.3` | GET | Detect drift above threshold |
| `/explain` | GET | Explain drifted features |
| `/impact` | GET | Model accuracy impact analysis |
| `/recommend` | GET | Smart action recommendations |
| `/importance` | GET | Feature importance comparison |
| `/timeline` | GET | Drift simulation over time |
| `/summary` | GET | Overall system summary |

---

## 🔍 How It Works

1. **Data Loading** — Telco Churn dataset is split into train/live. The live set gets simulated drift (scale, shift, and noise) on key features.

2. **Drift Detection** — Uses the **Kolmogorov-Smirnov test** (`scipy.stats.ks_2samp`) to compare distributions between train and live data. Features are scored and classified by severity (high/medium/low).

3. **Explanation** — Computes mean shifts and segment-level distribution changes for each drifted feature.

4. **Impact Analysis** — Trains a **Random Forest** on the training data and evaluates it on both datasets to quantify the accuracy drop caused by drift.

5. **Feature Importance** — Compares feature importance rankings between models trained on train vs live data to identify which features changed the most.

6. **Recommendations** — Combines drift severity and accuracy impact to generate prioritized action items (immediate retrain, monitor, etc.).

---

## 🧪 Testing

Run the smoke test to verify all modules:

```bash
python smoke_test.py
```

Expected output:
```
📦 Data Loading
  ✅ Train set loaded
  ✅ Live set loaded
  ✅ Churn column exists
  ✅ No NaN in train
  ✅ Churn is integer

🔍 Drift Detection
  ✅ Drift results returned
  ✅ Results have expected keys

📝 Drift Explanation
  ✅ Explanation returned
  ✅ Contains mean values

📉 Impact Analysis
  ✅ Impact returned
  ✅ Has accuracy fields
  ✅ Train accuracy > 0
  ✅ Accuracy drop is number

📊 Feature Importance
  ✅ Importance returned
  ✅ Has change field

📈 Timeline Simulation
  ✅ Timeline returned
  ✅ Steps have expected fields
  ✅ Drift increases over time

========================================
Results: 18 passed, 0 failed
========================================
```

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Uvicorn
- **Frontend:** Streamlit
- **ML:** scikit-learn (Random Forest), SciPy (KS-test)
- **Data:** Pandas, NumPy
- **Dataset:** [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)

---

## 📄 License

This project is for educational and demonstration purposes.
