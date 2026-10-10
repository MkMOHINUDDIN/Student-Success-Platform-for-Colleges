# Product contract — Student Early Support

Build a local web application that helps teachers and mentors identify fictional students who may need academic support, explain the indicators, recommend practical next steps, and record interventions.

## Non-negotiables

- Runtime: Python, Flask, SQLAlchemy, **MySQL**. SQLite only in isolated tests.
- UI: Jinja/HTML, CSS, vanilla JS, Chart.js. No paid API or service required.
- Data: **fictional synthetic students only**, clearly labelled.
- Security: hashed passwords, CSRF, backend role checks (Admin / Teacher / Student), validated uploads/exports, transactions on imports.
- Do not fabricate metrics. Do not claim unrun tests passed. Preserve `.env` and existing data.

## Required product

Normalized academic schema; idempotent synthetic seed; CSV preview/validation/import with row errors and rollback; database-backed dashboard; searchable student directory and profile; local scikit-learn risk model with leakage-resistant evaluation, real metrics, per-student factors and recommendations; risk alert centre; interventions with follow-up and descriptive before/after indicators (no causal claims); cohort analytics and permission-safe CSV export; model version + audit log; tests; README and demo script.

See `FEATURES.md` for the checklist and `ARCHITECTURE.md` for the implemented layout.
