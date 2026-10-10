from datetime import datetime
from ..extensions import db
from ..models import Intervention, FollowUp
from .features import student_term_features, latest_two_terms


def snapshot(student_id, which="before"):
    earlier, later = latest_two_terms()
    term = earlier if which == "before" else later
    if not term:
        return None, None
    f = student_term_features(student_id, term.id)
    return f["attendance_rate"], f["mean_score"]


def create_intervention(student_id, user_id, category, notes):
    att, score = snapshot(student_id, "before")
    item = Intervention(
        student_id=student_id,
        created_by_id=user_id,
        category=category,
        notes=notes,
        status="open",
        before_attendance=att,
        before_mean_score=score,
    )
    db.session.add(item)
    db.session.commit()
    return item


def add_follow_up(intervention, user_id, observation, status, outcome):
    db.session.add(FollowUp(
        intervention_id=intervention.id,
        author_id=user_id,
        observation=observation,
    ))
    intervention.status = status
    if outcome:
        intervention.outcome = outcome
    if status == "completed":
        att, score = snapshot(intervention.student_id, "after")
        intervention.after_attendance = att
        intervention.after_mean_score = score
        intervention.closed_at = datetime.utcnow()
    db.session.commit()
