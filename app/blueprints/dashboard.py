import json
from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from ..auth import visible_students
from ..services.analytics import kpis, score_trend, risk_by_class
from ..models import ModelVersion

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    students = visible_students().all()
    ids = [s.id for s in students]
    stats = kpis(ids)
    trend = score_trend()
    by_class = risk_by_class(visible_students())
    mv = ModelVersion.query.filter_by(is_active=True).first()
    metrics = json.loads(mv.metrics_json) if mv and mv.metrics_json else None
    return render_template(
        "dashboard/index.html",
        stats=stats,
        trend=trend,
        by_class=by_class,
        metrics=metrics,
        notice=current_app.config["DATA_NOTICE"],
    )
