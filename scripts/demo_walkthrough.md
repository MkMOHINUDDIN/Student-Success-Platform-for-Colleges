# End-to-end demo

1. Copy `.env.example` to `.env` and set MySQL `DATABASE_URL`.
2. `python -m venv .venv` then install `requirements.txt`.
3. Create database `student_risk`.
4. `python scripts/init_demo.py`
5. `flask --app wsgi run`
6. Sign in as `admin@demo.school` / `DemoAdmin!23`.
7. Open Dashboard (KPIs + charts), Students, a profile, Risk alerts, Interventions, Analytics export, Imports, Admin metrics.
8. Sign in as teacher, confirm only assigned classes.
9. Sign in as student, confirm only own profile.

All names and scores are fictional.
