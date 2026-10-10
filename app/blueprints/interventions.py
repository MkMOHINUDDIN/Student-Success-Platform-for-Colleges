from flask import Blueprint, render_template
from flask_login import login_required
from ..auth import visible_students, roles_required
from ..models import Intervention

bp = Blueprint("interventions", __name__, url_prefix="/interventions")


@bp.route("/")
@login_required
@roles_required("admin", "teacher")
def index():
    ids = [s.id for s in visible_students().all()]
    items = (
        Intervention.query.filter(Intervention.student_id.in_(ids or [-1]))
        .order_by(Intervention.created_at.desc())
        .all()
    )
    return render_template("interventions/index.html", items=items)
