# Student Early Support (hackathon)

Local Flask app that flags fictional students who may need academic support. **All records are synthetic.** No paid APIs.

Stack: Python, Flask, SQLAlchemy, MySQL, Jinja, CSS, vanilla JS, Chart.js. Scientific wheels (pandas/sklearn) are skipped on Python 3.15; CSV uses the stdlib and the risk model is a local logistic regression.

## Setup

1. Create a MySQL database named `student_risk`.
2. Copy `.env.example` to `.env` and set `SECRET_KEY` plus `DATABASE_URL`.
3. Create a virtualenv and install dependencies:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_demo.py
flask --app wsgi run
```

Open http://127.0.0.1:5000

### Demo logins

| Role | Email | Password |
| --- | --- | --- |
| Admin | admin@demo.school | DemoAdmin!23 |
| Teacher | teacher@demo.school | DemoTeach!23 |
| Student | student@demo.school | DemoStud!23 |

Walkthrough: `scripts/demo_walkthrough.md`.

## Tests

Tests use in-memory SQLite only (allowed for isolated tests). Runtime is MySQL.

```
pytest -q
```

## Model

The local logistic regression predicts **Term 2 at-risk** from **Term 1** features (attendance rate, scores, assignment completion). At-risk means attendance &lt; 75% **or** mean score &lt; 50 **or** assignment completion &lt; 60%. Metrics, confusion matrix, and limitations are on the Admin page. This is not a causal model.

## Known limitations

- Synthetic data and a small sample.
- Target is a rule on the next term; the model is a correlational early-warning score.
- Before/after intervention numbers are descriptive, not causal effects.
- SQLite is not for runtime data.
