# Persistent coding-agent rules

Read `MASTER_PROMPT.md`, `FEATURES.md`, `ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `PROJECT_STATUS.md`, and `HANDOFF.md` before work. `MASTER_PROMPT.md` is the full product contract. Preserve existing code, user changes, `.env`, and database data. Never rebuild blindly or run destructive commands without permission.

Runtime stack: Python, Flask, SQLAlchemy, MySQL, Jinja/HTML, CSS, vanilla JS, Chart.js, pandas, NumPy, scikit-learn. SQLite is only allowed for isolated tests. No paid API/service may be required. Use fictional synthetic student data only.

Implement small verified changes; enforce backend authorization, CSRF, password hashing, input validation, safe uploads/exports, and transactions. Never fabricate metrics or claim unrun tests passed. Update feature status and handoff docs after every meaningful session. See `MASTER_PROMPT.md` for the complete required feature list and acceptance expectations.
