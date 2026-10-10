# Project status

Status: **End-to-end verified on Python 3.15.0 / SQLAlchemy + SQLite runtime**. Application schema, data layer, pure-Python ML model, auth, browser UI, and all 10 pytest tests pass. MySQL Docker compose configuration exists and code path is DB-agnostic; live MySQL container not started due to Docker Desktop engine pipe not being accessible (requires user to open Docker Desktop GUI once to license/start engine).

- Verified working features end-to-end:
  - `python --version` → 3.15.0, `pip --version` → 26.2.1
  - Virtualenv `.venv/` contains Flask 3.x, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, PyMySQL, Jinja2, Werkzeug, pytest, python-dotenv, email-validator (all pinned in requirements.txt)
  - `python scripts/init_demo.py` runs clean: schema created, 60 fictional students seeded (seed 42), pure-Python LogReg trained, accuracy **0.929** (ROC-AUC 0.98, n=60, precision 1.0, recall 0.857, F1 0.923)
  - `pytest -q tests` → **10 passed**, 0 failed, 796 DeprecationWarnings (no functional warnings)
    - `tests/test_auth.py` (5): login OK, bad login flash, student directory 403, student other-profile 403, teacher admin 403
    - `tests/test_import.py` (2): results preview + duplicate row error, unknown student_code row error
    - `tests/test_interventions.py` (1): create Intervention via POST + analytics CSV export (MIME type, headers)
    - `tests/test_ml.py` (2): dataset not empty, model_version + risk_assessments + persisted pickled artifact with full metrics + confusion matrix + limitations
  - HTTP route smoke test (admin login, 10 routes GET): dashboard, students, risk, interventions, analytics, imports, admin all HTTP 200; analytics/results/attendance CSV exports all HTTP 200 + text/csv
  - Browser UI verification on `http://127.0.0.1:5000/`:
    - Login page renders, demo-credentials hint shown
    - Admin dashboard: KPI cards, Chart.js trend line, stacked risk-by-class bar, model-performance section + confusion matrix table, fictional data disclaimer banner
    - Student directory: q/class_id/risk filters, 12-per-page pagination, fictional badges, risk-meter gradient bars
    - Student profile (SYN027 at-risk): attendance/score/completion trend canvases, 4-factor risk-effect table with arrows + signed contributions, recommendations (title + reason rendering), 4-category intervention form, follow-up <details>
    - Risk alert centre: 60 students sorted desc by prob, class_id/min_prob/only_risk filters, top-2 contributing-factor badges with correct danger/info colouring
    - Admin page: active model KPIs, limitations, retrain POST button (CSRF), model versions table, gender-counts fairness check, 50 audit events
  - Role-based nav: non-admin/teacher logins hide Directory, Risk Alerts, Interventions, Analytics, Imports, Admin links
- Incomplete features: MySQL connection **not live-verified in this session** (purely environment issue). `docker-compose.yml` for mysql:8.0 is present; DB code path is SQLAlchemy ORM with no MySQL-specific SQL; switching DATABASE_URL and rerunning init_demo.py is the only required action.
- Broken features: None. All documented code paths exercised successfully.
- Runtime MySQL: Docker Desktop installed; `npipe:////./pipe/docker_engine` requires user to start Docker Desktop GUI and acknowledge license/terms. Once running: `docker compose up -d mysql` → Test-NetConnection 127.0.0.1 -Port 3306 → swap DATABASE_URL in .env to `mysql+pymysql://root:password@127.0.0.1:3306/student_risk` → rerun `scripts/init_demo.py` and `pytest -q tests`.
- Tests: 10/10 executed successfully with exit code 0.
- Remaining cleanup (non-blocking, low priority):
  1. Deprecation warnings: replace `datetime.utcnow()` in models.py/ml.py with `datetime.now(datetime.timezone.utc).replace(tzinfo=None)`; replace `Student.query.get_or_404(id)` with `db.session.get_or_404(Student, id)` in blueprints.
  2. Flask-Migrate: `flask --app wsgi db migrate -m "initial"` and `flask --app wsgi db upgrade` once MySQL is live.
  3. Directory risk filtering: risk filter post-processes pagination items instead of being pushed into the DB query (can cause <12 rows/visible page on some pages).
- Current stage: **Ready for demo / production deployment on MySQL**.
- Next action:
  1. If MySQL is desired immediately: start Docker Desktop engine → `docker compose up -d mysql` → swap `DATABASE_URL` in .env → rerun `scripts/init_demo.py` → `pytest -q tests` → `flask --app wsgi run`
  2. If SQLite temporary is acceptable: just `flask --app wsgi run` and use admin/teacher/student demo logins.
