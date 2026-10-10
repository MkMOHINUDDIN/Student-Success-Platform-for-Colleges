import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app
from app.services.ml import train_and_persist

app = create_app()
with app.app_context():
    metrics, mv = train_and_persist()
    print(mv.name, metrics)
