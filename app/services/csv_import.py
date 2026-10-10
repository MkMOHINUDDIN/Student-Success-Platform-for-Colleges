import csv
import io
from datetime import datetime
from ..extensions import db
from ..models import Student, Assessment, Result, Attendance, Term, ImportJob, ImportError


RESULT_FIELDS = ["student_code", "assessment_name", "term", "score"]
ATT_FIELDS = ["student_code", "date", "status", "term"]


def parse_csv(stream):
    text = stream.read()
    if isinstance(text, bytes):
        text = text.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for raw in reader:
        rows.append({k.strip(): ("" if v is None else str(v).strip()) for k, v in raw.items()})
    return rows, [c.strip() for c in (reader.fieldnames or [])]


def _student_by_code():
    return {s.student_code: s for s in Student.query.all()}


def preview_results(rows, filename, user_id):
    errors = []
    valid = []
    students = _student_by_code()
    assessments = {(a.name, a.term.name): a for a in Assessment.query.join(Term).all()}
    seen = set()
    for i, row in enumerate(rows, start=2):
        missing = [f for f in RESULT_FIELDS if not str(row.get(f, "")).strip()]
        if missing:
            errors.append((i, f"Missing fields: {', '.join(missing)}"))
            continue
        code = row["student_code"].strip()
        if code not in students:
            errors.append((i, f"Unknown student_code {code}"))
            continue
        key = (row["assessment_name"].strip(), row["term"].strip())
        if key not in assessments:
            errors.append((i, f"Unknown assessment/term {key}"))
            continue
        try:
            score = float(row["score"])
        except ValueError:
            errors.append((i, "Score is not numeric"))
            continue
        if score < 0 or score > assessments[key].max_score:
            errors.append((i, f"Score {score} outside 0–{assessments[key].max_score}"))
            continue
        dup_key = (code, key)
        if dup_key in seen:
            errors.append((i, "Duplicate row in file"))
            continue
        seen.add(dup_key)
        existing = Result.query.filter_by(
            student_id=students[code].id, assessment_id=assessments[key].id
        ).first()
        if existing:
            errors.append((i, "Duplicate of existing result"))
            continue
        valid.append({"student": students[code], "assessment": assessments[key], "score": score})
    job = ImportJob(
        filename=filename, kind="results", status="previewed",
        created_by_id=user_id, row_count=len(valid), error_count=len(errors),
    )
    db.session.add(job)
    db.session.flush()
    for num, msg in errors:
        db.session.add(ImportError(job_id=job.id, row_number=num, message=msg))
    db.session.commit()
    return job, valid, errors


def commit_results(job, valid):
    try:
        for item in valid:
            db.session.add(Result(
                student_id=item["student"].id,
                assessment_id=item["assessment"].id,
                score=item["score"],
            ))
        job.status = "committed"
        db.session.commit()
    except Exception:
        db.session.rollback()
        job.status = "rolled_back"
        db.session.add(job)
        db.session.commit()
        raise


def preview_attendance(rows, filename, user_id):
    errors = []
    valid = []
    students = _student_by_code()
    terms = {t.name: t for t in Term.query.all()}
    seen = set()
    for i, row in enumerate(rows, start=2):
        missing = [f for f in ATT_FIELDS if not str(row.get(f, "")).strip()]
        if missing:
            errors.append((i, f"Missing fields: {', '.join(missing)}"))
            continue
        code = row["student_code"].strip()
        if code not in students:
            errors.append((i, f"Unknown student_code {code}"))
            continue
        term = terms.get(row["term"].strip())
        if not term:
            errors.append((i, "Unknown term"))
            continue
        status = row["status"].strip().lower()
        if status not in ("present", "absent", "late"):
            errors.append((i, "Status must be present, absent, or late"))
            continue
        try:
            d = datetime.strptime(row["date"].strip(), "%Y-%m-%d").date()
        except ValueError:
            errors.append((i, "Date must be YYYY-MM-DD"))
            continue
        key = (code, d)
        if key in seen:
            errors.append((i, "Duplicate row in file"))
            continue
        seen.add(key)
        if Attendance.query.filter_by(student_id=students[code].id, date=d).first():
            errors.append((i, "Duplicate of existing attendance"))
            continue
        valid.append({"student": students[code], "term": term, "date": d, "status": status})
    job = ImportJob(
        filename=filename, kind="attendance", status="previewed",
        created_by_id=user_id, row_count=len(valid), error_count=len(errors),
    )
    db.session.add(job)
    db.session.flush()
    for num, msg in errors:
        db.session.add(ImportError(job_id=job.id, row_number=num, message=msg))
    db.session.commit()
    return job, valid, errors


def commit_attendance(job, valid):
    try:
        for item in valid:
            db.session.add(Attendance(
                student_id=item["student"].id,
                term_id=item["term"].id,
                date=item["date"],
                status=item["status"],
            ))
        job.status = "committed"
        db.session.commit()
    except Exception:
        db.session.rollback()
        job.status = "rolled_back"
        raise


def export_rows(rows, fieldnames):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()
