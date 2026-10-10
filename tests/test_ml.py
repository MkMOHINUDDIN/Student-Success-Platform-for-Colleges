from app.services.ml import build_dataset, load_active_model
from app.models import ModelVersion, RiskAssessment


def test_dataset_no_empty(app):
    with app.app_context():
        data = build_dataset()
        assert data is not None
        X, y, ids, earlier, later = data
        assert len(X) == len(y) == len(ids)
        assert earlier.sequence < later.sequence


def test_model_persisted(app):
    with app.app_context():
        pipe, mv = load_active_model()
        assert pipe is not None
        assert mv is not None
        assert ModelVersion.query.filter_by(is_active=True).count() == 1
        assert RiskAssessment.query.count() > 0
        m = __import__("json").loads(mv.metrics_json)
        assert "accuracy" in m and "confusion_matrix" in m
        assert "limitations" in m
