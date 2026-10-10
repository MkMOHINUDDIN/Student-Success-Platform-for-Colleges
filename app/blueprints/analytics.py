from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from ..auth import visible_students, roles_required, audit
from ..models import ClassGroup, Subject, Term
from ..services.analytics import cohort_table
from ..services.csv_import import export_rows
from ..extensions import db

bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@bp.route("/")
@login_required
@roles_required("admin", "teacher")
def index():
    ids = [s.id for s in visible_students().all()]
    rows = cohort_table(
        class_id=request.args.get("class_id") or None,
        term_id=request.args.get("term_id") or None,
        student_ids=ids,
    )
    return render_template(
        "analytics/index.html",
        rows=rows,
        classes=ClassGroup.query.all(),
        subjects=Subject.query.all(),
        terms=Term.query.order_by(Term.sequence).all(),
    )


@bp.route("/export")
@login_required
@roles_required("admin", "teacher")
def export():
    ids = [s.id for s in visible_students().all()]
    rows = cohort_table(
        class_id=request.args.get("class_id") or None,
        term_id=request.args.get("term_id") or None,
        student_ids=ids,
    )
    # Privacy: round rates; no dates of birth
    for r in rows:
        r["attendance_rate"] = round(r["attendance_rate"], 2)
        r["assignment_completion"] = round(r["assignment_completion"], 2)
    data = export_rows(rows, ["student_code", "name", "class", "attendance_rate", "mean_score", "assignment_completion"])
    audit("analytics_export")
    db.session.commit()
    return Response(data, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=cohort.csv"})
