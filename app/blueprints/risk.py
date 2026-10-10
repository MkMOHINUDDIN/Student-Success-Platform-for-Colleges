import json
from flask import Blueprint, render_template, request
from flask_login import login_required
from ..auth import visible_students, roles_required
from ..models import Student, ClassGroup
from ..services.ml import latest_risk

bp = Blueprint("risk", __name__, url_prefix="/risk")


@bp.route("/")
@login_required
@roles_required("admin", "teacher")
def centre():
    q = visible_students()
    class_id = request.args.get("class_id")
    if class_id:
        q = q.filter(Student.class_id == int(class_id))
    min_p = request.args.get("min_prob", type=float)
    items = []
    for s in q.order_by(Student.last_name).all():
        ra = latest_risk(s.id)
        if not ra:
            continue
        if request.args.get("only_risk") and not ra.predicted_label:
            continue
        if min_p is not None and ra.probability < min_p:
            continue
        items.append((s, ra, json.loads(ra.explanation_json or "{}")))
    items.sort(key=lambda x: x[1].probability, reverse=True)
    classes = ClassGroup.query.order_by(ClassGroup.name).all()
    return render_template("risk/centre.html", items=items, classes=classes)
