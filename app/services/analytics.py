from sqlalchemy import func
from ..extensions import db
from ..models import Student, Attendance, Result, RiskAssessment, ClassGroup, Term, Assessment
from .features import student_term_features, latest_two_terms


def kpis(student_ids):
    if not student_ids:
        return {
            "n_students": 0, "at_risk": 0, "mean_score": 0, "attendance_rate": 0,
            "data_warnings": ["No students in scope."],
        }
    latest = (
        db.session.query(RiskAssessment.student_id, func.max(RiskAssessment.id).label("rid"))
        .filter(RiskAssessment.student_id.in_(student_ids))
        .group_by(RiskAssessment.student_id)
        .subquery()
    )
    at_risk = (
        db.session.query(func.count(RiskAssessment.id))
        .join(latest, RiskAssessment.id == latest.c.rid)
        .filter(RiskAssessment.predicted_label.is_(True))
        .scalar()
    ) or 0
    scores = db.session.query(func.avg(Result.score)).filter(Result.student_id.in_(student_ids)).scalar()
    att_q = Attendance.query.filter(Attendance.student_id.in_(student_ids)).all()
    n_att = len(att_q)
    att_rate = (sum(1 for a in att_q if a.status == "present") + 0.5 * sum(1 for a in att_q if a.status == "late")) / n_att if n_att else 0
    warnings = []
    if n_att < len(student_ids) * 5:
        warnings.append("Attendance coverage is thin for some students.")
    missing_risk = len(student_ids) - (
        db.session.query(func.count(latest.c.rid)).scalar() or 0
    )
    if missing_risk:
        warnings.append(f"{missing_risk} students have no risk score yet. Train or rescore the model.")
    return {
        "n_students": len(student_ids),
        "at_risk": int(at_risk),
        "mean_score": round(float(scores or 0), 1),
        "attendance_rate": round(att_rate, 3),
        "data_warnings": warnings,
    }


def score_trend():
    rows = (
        db.session.query(Term.name, func.avg(Result.score))
        .join(Assessment, Assessment.id == Result.assessment_id)
        .join(Term, Term.id == Assessment.term_id)
        .group_by(Term.sequence, Term.name)
        .order_by(Term.sequence)
        .all()
    )
    return [{"term": r[0], "mean": round(float(r[1] or 0), 1)} for r in rows]


def risk_by_class(student_query):
    students = student_query.all()
    buckets = {}
    for s in students:
        name = s.class_group.name if s.class_group else "Unknown"
        buckets.setdefault(name, {"n": 0, "risk": 0})
        buckets[name]["n"] += 1
        ra = (
            RiskAssessment.query.filter_by(student_id=s.id)
            .order_by(RiskAssessment.id.desc())
            .first()
        )
        if ra and ra.predicted_label:
            buckets[name]["risk"] += 1
    return [{"class": k, **v} for k, v in buckets.items()]


def cohort_table(class_id=None, subject_id=None, term_id=None, student_ids=None):
    q = Student.query
    if student_ids is not None:
        q = q.filter(Student.id.in_(student_ids or [-1]))
    if class_id:
        q = q.filter(Student.class_id == int(class_id))
    earlier, later = latest_two_terms()
    term = db.session.get(Term, int(term_id)) if term_id else later or earlier
    rows = []
    for s in q.all():
        if not term:
            continue
        feats = student_term_features(s.id, term.id)
        rows.append({
            "student_code": s.student_code,
            "name": f"{s.first_name} {s.last_name}",
            "class": s.class_group.name,
            "attendance_rate": feats["attendance_rate"],
            "mean_score": feats["mean_score"],
            "assignment_completion": feats["assignment_completion"],
        })
    return rows
