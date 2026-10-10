# Architecture (implemented)

- `app/__init__.py` — Flask factory, CSRF, login, error handlers
- `app/config.py`, `app/extensions.py`, `app/models.py`, `app/auth.py`, `app/forms.py`
- Blueprints: `auth`, `dashboard`, `students`, `imports`, `risk`, `interventions`, `analytics`, `admin`
- Services: CSV (pandas) preview/commit, feature engineering, scikit-learn pipeline, explanations, recommendations, intervention snapshots
- Templates + `static/css/style.css` + `static/js/app.js` (Chart.js CDN)
- `scripts/generate_synthetic.py` (seed 42), `scripts/init_demo.py`, `scripts/train_model.py`
- Tests in `tests/` using in-memory SQLite
- Runtime DB: MySQL via `DATABASE_URL` (`mysql+pymysql://...`)

ML target: Term 2 at-risk rule from Term 1 features (attendance &lt; 75% or mean score &lt; 50 or assignment completion &lt; 60%). Artifact: `instance/artifacts/model.joblib`.
