from collections import defaultdict
from ..models import Attendance, Result, Submission, Assessment, Assignment, Term


FEATURE_NAMES = [
    "attendance_rate",
    "late_rate",
    "mean_score",
    "min_score",
    "assignment_completion",
    "late_submission_rate",
    "assessment_count",
]


def _term_map():
    return {t.id: t for t in Term.query.order_by(Term.sequence).all()}


def student_term_features(student_id, term_id):
    att = Attendance.query.filter_by(student_id=student_id, term_id=term_id).all()
    n = len(att)
    present = sum(1 for a in att if a.status == "present")
    late = sum(1 for a in att if a.status == "late")
    attendance_rate = (present + 0.5 * late) / n if n else 0.0
    late_rate = late / n if n else 0.0

    assessments = Assessment.query.filter_by(term_id=term_id).all()
    a_ids = [a.id for a in assessments]
    results = Result.query.filter(Result.student_id == student_id, Result.assessment_id.in_(a_ids or [-1])).all()
    scores = [r.score for r in results]
    mean_score = sum(scores) / len(scores) if scores else 0.0
    min_score = min(scores) if scores else 0.0

    assignments = Assignment.query.filter_by(term_id=term_id).all()
    as_ids = [a.id for a in assignments]
    subs = Submission.query.filter(
        Submission.student_id == student_id, Submission.assignment_id.in_(as_ids or [-1])
    ).all()
    completion = sum(1 for s in subs if s.completed) / len(subs) if subs else 0.0
    late_sub = sum(1 for s in subs if s.late) / len(subs) if subs else 0.0

    return {
        "attendance_rate": round(attendance_rate, 4),
        "late_rate": round(late_rate, 4),
        "mean_score": round(mean_score, 2),
        "min_score": round(min_score, 2),
        "assignment_completion": round(completion, 4),
        "late_submission_rate": round(late_sub, 4),
        "assessment_count": float(len(scores)),
        "n_attendance": n,
        "insufficient": n < 5 or len(scores) < 2,
    }


def at_risk_label(feats):
    return int(
        feats["attendance_rate"] < 0.75
        or feats["mean_score"] < 50
        or feats["assignment_completion"] < 0.6
    )


def feature_vector(feats):
    return [feats[n] for n in FEATURE_NAMES]


def latest_two_terms():
    terms = Term.query.order_by(Term.sequence).all()
    if len(terms) < 2:
        return None, None
    return terms[-2], terms[-1]
