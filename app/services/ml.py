import json
import os
from datetime import datetime
from flask import current_app
from ..extensions import db
from ..models import Student, ModelVersion, RiskAssessment
from .features import FEATURE_NAMES, student_term_features, at_risk_label, feature_vector, latest_two_terms
from .explanations import explain_student
from .recommendations import recommend
from .local_model import LogRegModel, stratified_split, metrics_from, dump_model, load_model


def build_dataset():
    earlier, later = latest_two_terms()
    if not earlier or not later:
        return None
    X, y, ids = [], [], []
    for s in Student.query.all():
        feats = student_term_features(s.id, earlier.id)
        later_feats = student_term_features(s.id, later.id)
        if feats["insufficient"]:
            continue
        X.append(feature_vector(feats))
        y.append(at_risk_label(later_feats))
        ids.append(s.id)
    if len(X) < 10:
        return None
    return X, y, ids, earlier, later


def train_and_persist():
    data = build_dataset()
    if data is None:
        raise RuntimeError("Not enough labelled term pairs to train.")
    X, y, ids, earlier, later = data
    X_train, X_test, y_train, y_test = stratified_split(X, y)
    model = LogRegModel()
    model.fit(X_train, y_train)
    y_prob = [model.predict_proba_one(r) for r in X_test]
    y_pred = [int(p >= 0.5) for p in y_prob]
    m = metrics_from(y_test, y_pred, y_prob)
    metrics = {
        "n_samples": len(y),
        "n_train": len(y_train),
        "n_test": len(y_test),
        "target": f"at_risk in {later.name} from features in {earlier.name}",
        "positive_definition": "attendance_rate<0.75 OR mean_score<50 OR assignment_completion<0.6",
        "accuracy": float(m["accuracy"]),
        "precision": float(m["precision"]),
        "recall": float(m["recall"]),
        "f1": float(m["f1"]),
        "roc_auc": m["roc_auc"],
        "confusion_matrix": m["confusion_matrix"],
        "feature_names": FEATURE_NAMES,
        "backend": "pure-python-logreg (Python 3.15 has no pandas/sklearn wheels)",
        "limitations": [
            "Synthetic fictional data only.",
            "Small sample; metrics are indicative, not production-ready.",
            "Target uses academic/attendance rules; model estimates the next term of those rules.",
            "Not a causal model of student outcomes.",
            "Installed without pandas/numpy/scikit-learn because this Python version has no binary wheels.",
        ],
    }
    folder = current_app.config["ARTIFACT_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "model.pkl")
    dump_model(path, {"pipeline": model, "features": FEATURE_NAMES, "metrics": metrics})
    ModelVersion.query.update({ModelVersion.is_active: False})
    mv = ModelVersion(
        name=f"logreg-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
        metrics_json=json.dumps(metrics),
        artifact_path=path,
        notes=metrics["target"],
        is_active=True,
    )
    db.session.add(mv)
    db.session.commit()
    score_all_students(model, mv, earlier)
    return metrics, mv


def load_active_model():
    mv = ModelVersion.query.filter_by(is_active=True).order_by(ModelVersion.id.desc()).first()
    if not mv or not mv.artifact_path or not os.path.exists(mv.artifact_path):
        return None, None
    payload = load_model(mv.artifact_path)
    return payload["pipeline"], mv


def score_all_students(pipe=None, mv=None, feature_term=None):
    if pipe is None or mv is None:
        pipe, mv = load_active_model()
    if pipe is None:
        return 0
    if feature_term is None:
        earlier, _ = latest_two_terms()
        feature_term = earlier
    if feature_term is None:
        return 0
    n = 0
    for s in Student.query.all():
        feats = student_term_features(s.id, feature_term.id)
        if feats["insufficient"]:
            expl = {"insufficient_data": True, "factors": []}
            recs = recommend(feats, True)
            db.session.add(RiskAssessment(
                student_id=s.id, model_version_id=mv.id, term_id=feature_term.id,
                probability=0.5, predicted_label=False,
                explanation_json=json.dumps(expl),
                recommendations_json=json.dumps(recs),
            ))
            continue
        row = feature_vector(feats)
        proba = float(pipe.predict_proba_one(row))
        label = bool(pipe.predict_one(row))
        expl = explain_student(feats, pipe.coef_, FEATURE_NAMES)
        recs = recommend(feats, False)
        db.session.add(RiskAssessment(
            student_id=s.id, model_version_id=mv.id, term_id=feature_term.id,
            probability=proba, predicted_label=label,
            explanation_json=json.dumps(expl),
            recommendations_json=json.dumps(recs),
        ))
        n += 1
    db.session.commit()
    return n


def latest_risk(student_id):
    return (
        RiskAssessment.query.filter_by(student_id=student_id)
        .order_by(RiskAssessment.created_at.desc())
        .first()
    )
