import json
from flask import Blueprint, render_template, request, abort, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_
from ..auth import visible_students, can_access_student, roles_required
from ..models import Student, ClassGroup, Intervention
from ..services.ml import latest_risk
from ..services.features import student_term_features, latest_two_terms
from ..forms import InterventionForm, FollowUpForm, StudentSearchForm
from ..services.interventions import create_intervention, add_follow_up

bp = Blueprint("students", __name__, url_prefix="/students")


@bp.route("/")
@login_required
@roles_required("admin", "teacher")
def directory():
    form = StudentSearchForm(request.args)
    classes = ClassGroup.query.order_by(ClassGroup.name).all()
    form.class_id.choices = [("", "All classes")] + [(str(c.id), c.name) for c in classes]
    q = visible_students()
    search = request.args.get("q", "").strip()
    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            Student.first_name.ilike(like),
            Student.last_name.ilike(like),
            Student.student_code.ilike(like),
        ))
    class_id = request.args.get("class_id")
    if class_id:
        q = q.filter(Student.class_id == int(class_id))
    page = request.args.get("page", 1, type=int)
    pagination = q.order_by(Student.last_name).paginate(page=page, per_page=12, error_out=False)
    risks = {s.id: latest_risk(s.id) for s in pagination.items}
    if request.args.get("risk") == "high":
        pagination.items = [s for s in pagination.items if risks.get(s.id) and risks[s.id].predicted_label]
    elif request.args.get("risk") == "low":
        pagination.items = [s for s in pagination.items if risks.get(s.id) and not risks[s.id].predicted_label]
    return render_template("students/directory.html", pagination=pagination, form=form, risks=risks)


@bp.route("/<int:student_id>", methods=["GET", "POST"])
@login_required
def profile(student_id):
    student = Student.query.get_or_404(student_id)
    if not can_access_student(student):
        abort(403)
    iform = InterventionForm()
    fform = FollowUpForm()
    if current_user.role in ("admin", "teacher") and iform.validate_on_submit():
        create_intervention(student.id, current_user.id, iform.category.data, iform.notes.data)
        return redirect(url_for("students.profile", student_id=student.id))
    earlier, later = latest_two_terms()
    terms = [t for t in (earlier, later) if t]
    series = [{"term": t.name, **student_term_features(student.id, t.id)} for t in terms]
    risk = latest_risk(student.id)
    expl = json.loads(risk.explanation_json) if risk and risk.explanation_json else {"factors": []}
    recs = json.loads(risk.recommendations_json) if risk and risk.recommendations_json else []
    return render_template(
        "students/profile.html",
        student=student, series=series, risk=risk, expl=expl, recs=recs,
        iform=iform, fform=fform, interventions=student.interventions,
    )


@bp.route("/<int:student_id>/interventions/<int:iid>/followup", methods=["POST"])
@login_required
@roles_required("admin", "teacher")
def followup(student_id, iid):
    student = Student.query.get_or_404(student_id)
    if not can_access_student(student):
        abort(403)
    item = Intervention.query.filter_by(id=iid, student_id=student_id).first_or_404()
    form = FollowUpForm()
    if form.validate_on_submit():
        add_follow_up(item, current_user.id, form.observation.data, form.status.data, form.outcome.data)
    return redirect(url_for("students.profile", student_id=student.id))
