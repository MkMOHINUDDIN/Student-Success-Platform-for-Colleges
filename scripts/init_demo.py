"""Create schema, seed fictional data, train local model."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app
from app.extensions import db
from scripts.generate_synthetic import generate
from app.services.ml import train_and_persist

app = create_app()
with app.app_context():
    db.create_all()
    print("schema:", "ok")
    print("seed:", generate())
    metrics, mv = train_and_persist()
    print("model:", mv.name, "accuracy", round(metrics["accuracy"], 3), "n", metrics["n_samples"])
    print("Demo logins: admin@demo.school / DemoAdmin!23 | teacher@demo.school / DemoTeach!23 | student@demo.school / DemoStud!23")
