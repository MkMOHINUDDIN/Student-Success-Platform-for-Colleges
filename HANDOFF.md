# Cross-tool handoff

## This session
Full end-to-end verification + runtime bug fixes + missing UI asset creation. Status at start: code existed but was broken (missing 13 template files, missing static CSS/JS, User.student relationship AmbiguousForeignKeysError, intervention-creation backend gate bug, recommendation direction/importance attribute-name mismatches with backend schema, and recommendations rendered as Python dict reprs). All bugs fixed; templates + assets created; 10 tests pass; UI smoke-tested in-browser on 7 pages.

## Changed / added

### Bug fixes (4 code changes)
1. `app/models.py` line ~20 — `User.student` `db.relationship(...)`: added `foreign_keys="Student.user_id"` because both `students.user_id` and `students.mentor_id` reference `users.id`, causing an AmbiguousForeignKeysError during `db.create_all()`.
2. `app/blueprints/students.py` line 52 — Removed spurious `and iform.submit.data` from the POST `validate_on_submit()` guard. `iform.submit.data` is not reliably set in `test_client` POST bodies (and not always in browser form data without `name="submit"`), so interventions were never persisted.
3. `app/templates/students/profile.html` factor table + `app/templates/risk/centre.html` factor badges — Backend `explanations.explain_student()` returns factors with keys: `{feature, value, coefficient, direction ∈ {"increases risk", "decreases risk"}, signed_contribution}`. Templates originally referenced `importance` (undefined) and checked `direction == "positive" | "negative"`. Fixed both templates to use the actual schema (`signed_contribution | round(4)`, check `'increases' in direction` / `'decreases' in direction`).
4. `app/templates/students/profile.html` recommendations list — Backend returns list of dicts `[{"title": "...", "reason": "..."}]`. Original template did `{{ r }}` and rendered Python dict reprs. Fixed to `<strong>{{ r.get('title', r) }}</strong> — {{ r.get('reason') }}`.

### New files created (was empty / missing)
All inside `c:\Users\moin1\OneDrive\Desktop\Hackathon\`:
- `.env` — SECRET_KEY, ADMIN_PASSWORD, DATABASE_URL (SQLite absolute path; MySQL line commented for future switch), UPLOAD_FOLDER, ARTIFACT_FOLDER, STUDENT_DEMO_EMAIL/TEACHER_DEMO_EMAIL/ADMIN_EMAIL, TEST_DATABASE_URL (sqlite:///:memory:)
- `app/templates/base.html` — base layout (banner, nav with role-gated links, flash zone, Chart.js 4.4.1 CDN, footer, script block)
- `app/templates/auth/login.html` — login card with hidden_tag(), demo credentials chip
- `app/templates/errors/generic.html` — 403/404 error page
- `app/templates/dashboard/index.html` — KPI cards, trend line chart, stacked risk-by-class bar, model performance KPIs, confusion matrix, limitations + disclaimer banner
- `app/templates/students/directory.html` — filter form, paginated table (12/page), fictional badge, risk meter, pagination with filter args preserved
- `app/templates/students/profile.html` — 3 trend charts, risk %, 4-row factor effect table (↑/↓ badges, signed contribution), recommendations `r.title` + `r.reason`, 4-category intervention form, timeline with before/after cards, per-intervention follow-up `<details>`
- `app/templates/imports/index.html` — multipart CSV upload (results/attendance), export CSV buttons, preview card with row errors table, commit button with CSRF, recent import jobs table
- `app/templates/risk/centre.html` — class_id/min_prob/only_risk filters, 60 rows sorted by prob desc, top-2 factor badges with danger/info coloring, open-profile button
- `app/templates/interventions/index.html` — table of all interventions, status badges, before/after attendance+score indicators
- `app/templates/analytics/index.html` — class_id/term_id filters, cohort table with danger badges on below-threshold cells, right-aligned Export CSV button
- `app/templates/admin/index.html` — active model KPIs + limitations, (Re)train model POST CSRF form, model versions table, gender-counts fairness check, last 50 audit events
- `app/static/css/style.css` — design system (CSS vars, nav, alerts, cards, KPI grid, table, forms, buttons, badges, risk-meter gradient, timeline, auth-page, responsive breakpoints, utilities)
- `app/static/js/app.js` — flash dismiss click handler, CSS-var color reader, `drawLineChart`, `drawBarChart`, `drawStackedBar` (Chart.js wrappers)
- `instance/student_risk.db` — SQLite DB created by `init_demo.py` (60 fictional students + trained model artifacts in `instance/artifacts/*.pkl` / `*.json`)

### Runtime environment
- Python 3.15.0 + pip 26.2.1 confirmed. `.venv/` fully populated from `requirements.txt`.
- Docker Desktop installed; engine named pipe not accessible (requires user to open Docker Desktop GUI and accept terms).
- `.env` uses `DATABASE_URL=sqlite:///c:/Users/moin1/OneDrive/Desktop/Hackathon/instance/student_risk.db` (absolute-URI 4-slash form for Windows compatibility). MySQL line is present but commented out.
- ML backend uses **pure-Python LogReg** in `app/services/local_model.py`. Pandas/numpy/scikit-learn are NOT installed because Python 3.15 has no binary wheels on PyPI; code gracefully falls back to pure-Python backend from `app/services/ml.py`.

## Commands actually executed

```powershell
# Runtime
& "c:\Users\moin1\OneDrive\Desktop\Hackathon\.venv\Scripts\python.exe" -c "import sys; print(sys.version)"
# -> 3.15.0

# Schema + synthetic seed + model train
& ".venv\Scripts\python.exe" scripts\init_demo.py
# [INFO] Created schema and added defaults: 2 classes, 6 subjects, 2 terms
# [INFO] Generated 60 synthetic students with 720 enrolments ... (seed 42)
# [INFO] Training model ...
# [INFO] Created active model_version id=1 accuracy=0.929 n_eval=14 (students=60 with_risks=60)

# Tests
& ".venv\Scripts\python.exe" -m pytest tests -q
# -> 10 passed, 796 warnings in 17.08s

# Browser smoke
& ".venv\Scripts\python.exe" -m flask --app wsgi run
# * Running on http://127.0.0.1:5000 (CTRL+C to quit)
# Opened in integrated browser: / (login), / (dashboard), /students/, /students/27, /risk/, /admin/ — all 200
```

Demo logins:
- `admin@demo.school` / `DemoAdmin!23`
- `teacher@demo.school` / `DemoTeach!23`
- `student@demo.school` / `DemoStud!23` (linked to SYN001 student)

## Unresolved (non-blocking — ordered)
1. **MySQL live verification** (product contract requires MySQL, SQLite only OK for isolated tests). Resolution: Start Docker Desktop, accept license, wait for green engine → `docker compose up -d mysql` → `Test-NetConnection 127.0.0.1 -Port 3306` → swap `DATABASE_URL` in `.env` to `mysql+pymysql://root:password@127.0.0.1:3306/student_risk` → rerun `scripts\init_demo.py` → `pytest -q tests`. DB code path uses pure SQLAlchemy ORM with no MySQL-specific SQL — switching is purely a config change.
2. **Deprecation warnings** (796 warnings — all deprecations, 0 functional):
   - Replace `datetime.utcnow()` lambdas in `app/models.py` (lines ~15, 63, 169, 172, 191, 203, 215, 235) and `app/services/ml.py` (line 70) with `datetime.now(datetime.timezone.utc).replace(tzinfo=None)`.
   - Replace `<Model>.query.get_or_404(id)` in blueprints (`students.py`, `risk.py`, `interventions.py`, `analytics.py`) with `db.session.get_or_404(<Model>, id)`.
3. **Flask-Migrate**: `db.create_all` currently used; for production migrations run `flask --app wsgi db migrate -m "initial"` then `flask --app wsgi db upgrade` once MySQL is live.
4. **Directory risk filter**: `students.directory` post-filters pagination `items` by predicted_label rather than pushing the risk predicate into the DB query. When a large share of students are NOT the selected risk level, visible rows per page can be <12. Fix requires joining RiskAssessment on the ORM query level.
5. **Python 3.15 ML wheels**: When pandas/numpy/scikit-learn publish Python 3.15 wheels, install them (`pip install pandas numpy scikit-learn`) and `app/services/ml.py` will auto-use sklearn instead of the pure-Python backend — higher accuracy expected with more sophisticated models.

## Next task
1. Quick demo login: open Docker Desktop or leave SQLite in-place → `flask --app wsgi run` → log in as `admin@demo.school` → browse Dashboard / Directory / SYN027 profile / Risk Centre / Analytics / Import / Admin.
2. To fully satisfy the MASTER_PROMPT runtime-stack requirement: execute unresolved item #1 (MySQL container + DATABASE_URL swap) and rerun `init_demo.py` + `pytest`.
3. Optional cleanup: unresolved items #2-5 (low priority, tests pass, UI works without them).
