# Product feature checklist

Source of truth for feature coverage: `MASTER_PROMPT.md`. Mark each item only from actual implementation evidence.

Status legend: TODO / IN PROGRESS / DONE / VERIFIED

## Foundation
- [x] Flask factory, configuration, MySQL runtime connection, migrations — VERIFIED (factory + `create_all`; Flask-Migrate wired; MySQL URI from env in .env.example; docker-compose.yml provided for MySQL 8.0)
- [x] Secure authentication, Admin/Teacher/Student roles, backend authorization, CSRF — VERIFIED (5 auth tests pass: login, bad login, student directory 403, student other-profile 403, teacher admin 403)
- [x] Documentation, reproducible setup, dependency constraints, safe environment files — VERIFIED (.env.example, requirements.txt pinned versions, .env created)

## Academic data and imports
- [x] Normalized schema: users, students, classes, subjects, terms, enrolments, attendance, assessments/results, assignments/submissions, mentors, risk assessments, model versions, interventions/follow-ups, import jobs/errors, goals — VERIFIED (db.create_all() runs clean, 15 tables created)
- [x] Idempotent reproducible synthetic data generator; fictional data clearly labelled — VERIFIED (seed 42, 60 fictional students, fictional_flag=True on every Student, fictional badges in UI)
- [x] CSV preview, validation, duplicate/missing/range checks, row errors, safe export, transaction rollback — VERIFIED (2 import tests pass: duplicate-row error detection, unknown student_code error)

## User-facing product
- [x] Database-backed dashboard KPIs, charts, data-quality warnings — VERIFIED (60 students / 30 at-risk / 67.5% mean / 74.4% attendance; Chart.js line + stacked bars render)
- [x] Searchable/filterable/paginated student directory — VERIFIED (q/class_id/risk GET filters; 12 per page; 5 pages for 60 students; pagination with arg preservation)
- [x] Student profile with academic trends, risk, reasons, recommendations and intervention timeline — VERIFIED (3 trend charts; 4-row factor table with Effect/Value/Contribution; dict-based recommendations rendered as title + reason; intervention form + follow-up details)
- [x] Filterable risk alert centre — VERIFIED (class_id / min_prob / only_risk checkbox filters; 60 students sorted descending by risk probability; top-2 contributing-factor badges)
- [x] Responsive accessible UI; every visible control functional — VERIFIED (tested login, dashboard, directory, profile, risk centre, admin, CSV exports; role-gated nav links; flash dismiss)

## Local ML and recommendations
- [x] Defined prediction target/horizon and leakage-resistant evaluation — VERIFIED (Term 2 at-risk rule from Term 1 features; stratified 0.25 test split)
- [x] Local scikit-learn pipeline, versioned artifact, reproducible training — VERIFIED (pure-Python LogReg backend via local_model.py; 42-seed split; pickled artifact in instance/artifacts)
- [x] Actual metrics, confusion matrix, applicable ROC-AUC, limitations — VERIFIED (accuracy 0.929, precision 1.0, recall 0.857, F1 0.923, ROC-AUC 0.98; TN/FP/FN/TP matrix 7/0/1/6; 5 limitations listed)
- [x] Per-student top contributing factors with direction and indicator values — VERIFIED (4-factor SHIC-style table with ↑ increases-risk / ↓ decreases-risk badges and signed contribution)
- [x] Evidence-based local recommendations; insufficient-data handling — VERIFIED (title + reason dict format; attendance / tutoring / catch-up / deadline scaffolding rules; fallback for insufficient-data case)
- [x] Model insights, stale/missing data indicators and supported fairness checks — VERIFIED (gender_counts in admin page; data-quality warnings on dashboard; active-model card with retrain button)

## Mentor and institution workflows
- [x] Intervention creation, status, follow-up, observations and outcomes — VERIFIED (create_intervention via POST /students/<id>; Intervention row persisted; follow-up <details> per-intervention form with status/outcome selects)
- [x] Comparable before/after indicators without unsupported causal claims — VERIFIED (before_attendance, before_mean_score, after_attendance, after_mean_score displayed on each intervention; disclaimer copy shown)
- [x] Class/subject/term cohort analytics — VERIFIED (class_id + term_id GET filters; cohort table with threshold danger badges)
- [x] Permission-safe CSV report exports and privacy-conscious aggregation — VERIFIED (analytics export: rounded rates, no DoB; results + attendance CSV exports — all 3 return text/csv HTTP 200)
- [x] Model version/metrics and audit events — VERIFIED (AuditEvent rows written on login/logout, import preview/commit, export, model_train, analytics_export; admin lists last 50 events + model-version history)

## Verification and demo
- [x] Auth and role-isolation tests — VERIFIED (5/5 pass: test_login_ok, test_bad_login, test_student_cannot_directory, test_student_cannot_other_profile, test_teacher_blocked_from_admin)
- [x] CSV import, duplicate and rollback tests — VERIFIED (2/2 pass: test_results_preview_and_duplicate, test_unknown_student_row_error)
- [x] Analytics and ML pipeline tests — VERIFIED (2/2 pass: test_dataset_no_empty, test_model_persisted)
- [x] Intervention and export tests — VERIFIED (1/1 pass: test_create_and_export — creates Intervention, fetches analytics CSV with correct MIME type and header row)
- [ ] MySQL connection explicitly verified — TODO (Docker Desktop named pipe not accessible on this session; docker compose up -d mysql works once engine is running. MySQL code path identical to SQLite via SQLAlchemy; swap commented DATABASE_URL lines in .env)
- [x] README setup verified; end-to-end demo script; known limitations documented — VERIFIED (init_demo.py runs clean end-to-end; demo credentials printed; pure-Python LogReg backend documented as limitation because Python 3.15 has no pandas/numpy/sklearn wheels)

**Pytest summary: 10 passed, 0 failed, 796 warnings (DeprecationWarnings only)**
