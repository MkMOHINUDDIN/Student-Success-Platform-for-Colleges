import json
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from ..auth import roles_required, audit
from ..models import ModelVersion, AuditEvent, Student, Attendance, Result
from ..services.ml import train_and_persist
from ..extensions import db
from sqlalchemy import func

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
@roles_required("admin")
def index():
    versions = ModelVersion.query.order_by(ModelVersion.id.desc()).all()
    events = AuditEvent.query.order_by(AuditEvent.id.desc()).limit(50).all()
    active = ModelVersion.query.filter_by(is_active=True).first()
    metrics = json.loads(active.metrics_json) if active and active.metrics_json else None
    gender_counts = dict(
        db.session.query(Student.gender, func.count(Student.id)).group_by(Student.gender).all()
    )
    return render_template(
        "admin/index.html",
        versions=versions, events=events, metrics=metrics, gender_counts=gender_counts,
    )


@bp.route("/train", methods=["POST"])
@login_required
@roles_required("admin")
def train():
    try:
        metrics, mv = train_and_persist()
        audit("model_train", mv.name)
        db.session.commit()
        flash(f"Trained {mv.name}. Accuracy {metrics.get('accuracy', 0):.2f}.", "success")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.index"))
