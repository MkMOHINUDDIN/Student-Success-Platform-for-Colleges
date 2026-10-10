from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from io import BytesIO
from ..auth import roles_required, audit
from ..forms import ImportForm, ConfirmImportForm
from ..models import ImportJob, Result, Attendance, Student, Assessment
from ..extensions import db
from ..services.csv_import import parse_csv, preview_results, preview_attendance, export_rows
from ..services.preview_store import save_preview, load_preview
from ..models import Term

bp = Blueprint("imports", __name__, url_prefix="/imports")


@bp.route("/", methods=["GET", "POST"])
@login_required
@roles_required("admin", "teacher")
def index():
    form = ImportForm()
    confirm = ConfirmImportForm()
    jobs = ImportJob.query.order_by(ImportJob.id.desc()).limit(20).all()
    if form.validate_on_submit():
        rows, fields = parse_csv(form.file.data.stream)
        filename = form.file.data.filename
        if form.kind.data == "results":
            job, valid, errors = preview_results(rows, filename, current_user.id)
        else:
            job, valid, errors = preview_attendance(rows, filename, current_user.id)
        save_preview(job.id, form.kind.data, valid)
        audit("import_preview", f"job {job.id}")
        db.session.commit()
        flash(f"Previewed {len(valid)} valid rows, {len(errors)} errors.", "info")
        return render_template("imports/index.html", form=form, confirm=confirm, job=job, errors=errors, jobs=jobs)
    return render_template("imports/index.html", form=form, confirm=confirm, job=None, errors=[], jobs=jobs)


@bp.route("/commit", methods=["POST"])
@login_required
@roles_required("admin", "teacher")
def commit():
    form = ConfirmImportForm()
    if not form.validate_on_submit():
        abort(400)
    job = ImportJob.query.get_or_404(int(form.job_id.data))
    payload = load_preview(job.id)
    if payload is None:
        flash("Preview expired. Upload again.", "danger")
        return redirect(url_for("imports.index"))
    try:
        if job.kind == "results":
            for item in payload:
                db.session.add(Result(
                    student_id=item["student_id"],
                    assessment_id=item["assessment_id"],
                    score=item["score"],
                ))
        else:
            for item in payload:
                db.session.add(Attendance(
                    student_id=item["student_id"],
                    term_id=item["term_id"],
                    date=date.fromisoformat(item["date"]),
                    status=item["status"],
                ))
        job.status = "committed"
        audit("import_commit", f"job {job.id}")
        db.session.commit()
        flash("Import committed.", "success")
    except Exception:
        db.session.rollback()
        job.status = "rolled_back"
        db.session.add(job)
        db.session.commit()
        flash("Import rolled back due to an error.", "danger")
    return redirect(url_for("imports.index"))


@bp.route("/export/<kind>")
@login_required
@roles_required("admin", "teacher")
def export(kind):
    if kind == "results":
        rows = []
        for r in Result.query.limit(5000).all():
            rows.append({
                "student_code": r.student.student_code,
                "assessment_name": r.assessment.name,
                "term": r.assessment.term.name,
                "score": r.score,
            })
        data = export_rows(rows, ["student_code", "assessment_name", "term", "score"])
    elif kind == "attendance":
        rows = []
        for a in Attendance.query.limit(8000).all():
            rows.append({
                "student_code": a.student.student_code,
                "date": a.date.isoformat(),
                "status": a.status,
                "term": a.term.name,
            })
        data = export_rows(rows, ["student_code", "date", "status", "term"])
    else:
        abort(404)
    audit("export", kind)
    db.session.commit()
    bio = BytesIO(data.encode("utf-8"))
    return send_file(bio, mimetype="text/csv", as_attachment=True, download_name=f"{kind}_export.csv")
