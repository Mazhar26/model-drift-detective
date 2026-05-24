# Changelog

All notable changes to the **Model Drift Detective** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] - 2026

### Added

#### Core Engine
- KS Test based drift detection engine (`scipy.stats.ks_2samp`)
- Severity classification (High / Medium / Low) with configurable thresholds
- Root cause analysis with mean shift detection and segment-level distribution changes
- Model accuracy impact analysis (RandomForest train vs live comparison)
- Feature importance comparison between train and live models
- Drift timeline simulation with progressive noise injection
- Smart recommendation engine combining drift severity and accuracy impact

#### API
- FastAPI REST API with versioned endpoints (`/api/v1/`)
- 9 endpoints: detect, explain, impact, recommend, importance, timeline, summary, history, history/trend
- Pydantic request/response models for all endpoints
- Input validation (threshold 0–1) with proper HTTP status codes (400/422/500)
- Structured error responses (`{"error": "...", "code": 500}`)
- Auto-generated Swagger UI documentation (`/docs`) and ReDoc (`/redoc`)
- Global exception handler for unhandled errors

#### Dashboard
- Streamlit interactive dashboard with 7 sidebar pages
- Main dashboard with overview metrics, drift chart, and top recommendations
- Interactive drift threshold slider
- Feature-level deep dive with severity labels
- Real-time drift history tracking with "Run Drift Check" button

#### Infrastructure
- Docker containerization (FastAPI + Streamlit)
- Docker Compose orchestration with healthchecks, shared network, and volume mounts
- GitHub Actions CI/CD pipeline (pytest + smoke tests + flake8 linting)
- Pre-commit hooks (Black, Flake8, isort)
- Centralized configuration via environment variables (`config.py`)
- Structured logging system with console + file output (`logger.py`)

#### Persistence & Alerts
- SQLite-based drift history tracking (`src/history.py`)
- Daily drift trend aggregation
- Email alert system for high-drift notifications (`src/alerts.py`)
- Configurable alert thresholds and SMTP settings via `.env`

#### Testing
- Smoke test suite with 18 assertions (`smoke_test.py`)
- pytest unit test suite with **28 tests** across 6 modules:
  `test_drift`, `test_recommend`, `test_impact`, `test_config`, `test_alerts`, `test_history`
- Test coverage: drift detection, recommendations, impact analysis, configuration, alerts, history

#### Documentation
- README with badges (CI, Python, MIT, FastAPI, Streamlit, scikit-learn)
- ASCII system architecture diagram
- API endpoint documentation table
- Quick Start guides (Docker + Manual)
- Development setup instructions (pre-commit)
- CONTRIBUTING.md with contribution guidelines

#### Legal
- MIT License

---

## [1.0.1] - 2026-05-24

### Fixed

- **`src/importance.py`** — Added `feature_importance_analysis` as a public alias for `get_feature_importance`.
  `smoke_test.py` and `api/main.py` imported the alias name, causing an `ImportError`.
- **`src/impact.py`** — Added `train_accuracy` as an alias key alongside `validation_accuracy` in the
  return dict. Tests and smoke test expected `train_accuracy`; both keys now coexist for full compatibility.
- **`src/recommend.py`** — Changed recommendation return value from nested dict (`{severity, drift_score,
  recommendation}`) to a flat action string. This matches the FastAPI `RecommendResponse(Dict[str, str])`
  Pydantic model and all test assertions.

### Updated

- **`README.md`** — Corrected pytest test count from 19 to 28, listed all 6 test modules, and added
  full pytest expected output block to the Testing section.
