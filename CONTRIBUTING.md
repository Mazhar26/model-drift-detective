# Contributing to Model Drift Detective

Thanks for your interest in contributing! Here's how to get started.

---

## 🚀 Quick Setup

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/model-drift-detective.git
cd model-drift-detective

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the smoke test
python smoke_test.py

# 4. Start the API + Dashboard
python -m uvicorn api.main:app --port 8000
streamlit run dashboard.py
```

---

## 📁 Project Structure

| Directory | Purpose |
|---|---|
| `src/` | Core ML logic (drift detection, explanation, impact, etc.) |
| `api/` | FastAPI backend |
| `pages/` | Streamlit sidebar pages |
| `data/` | Dataset (Telco Customer Churn) |
| `screenshots/` | Dashboard screenshots for README |

---

## 🔧 How to Contribute

### Reporting Bugs

- Open a [GitHub Issue](https://github.com/Mazhar26/model-drift-detective/issues)
- Include steps to reproduce, expected behavior, and actual behavior
- Attach error logs or screenshots if possible

### Suggesting Features

- Open an issue with the **"enhancement"** label
- Describe the feature and why it would be useful

### Submitting Code

1. **Fork** the repository
2. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feat/your-feature-name
   ```
3. **Make your changes** — follow the existing code style
4. **Run the smoke test** to make sure nothing is broken:
   ```bash
   python smoke_test.py
   ```
5. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add new drift metric"
   ```
6. **Push** and open a Pull Request

---

## 📝 Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Use for |
|---|---|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `docs:` | Documentation changes |
| `test:` | Adding or updating tests |
| `chore:` | Maintenance, dependencies, config |
| `refactor:` | Code restructuring (no behavior change) |

---

## 🧪 Testing

Before submitting a PR, make sure the smoke test passes:

```bash
python smoke_test.py
# Expected: 18 passed, 0 failed
```

Also verify the API endpoints work:

```bash
python -m uvicorn api.main:app --port 8000
# Then in another terminal:
curl http://127.0.0.1:8000/summary
```

---

## 💡 Ideas for Contributions

- [ ] Add more drift detection methods (PSI, Chi-squared, Jensen-Shannon)
- [x] Add database persistence for drift history (Implemented with SQLite)
- [x] Add email alerts for high-severity drift (Implemented with SMTP alerts)
- [x] Dockerize the application (Implemented with multi-container docker-compose)
- [x] Add unit tests with pytest (Implemented with 36 unit tests)
- [ ] Support for custom datasets (CSV upload)
- [ ] Add authentication to the API

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
