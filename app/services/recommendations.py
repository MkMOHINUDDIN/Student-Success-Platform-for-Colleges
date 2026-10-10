def recommend(feats, insufficient):
    if insufficient:
        return [{
            "title": "Collect more records",
            "reason": "Fewer than 5 attendance days or 2 assessment scores; the model should not drive action yet.",
        }]
    recs = []
    if feats["attendance_rate"] < 0.75:
        recs.append({
            "title": "Attendance check-in",
            "reason": f"Attendance rate is {feats['attendance_rate']:.0%}, below the 75% support threshold.",
        })
    if feats["mean_score"] < 50:
        recs.append({
            "title": "Subject tutoring",
            "reason": f"Mean assessment score is {feats['mean_score']:.1f}, below 50.",
        })
    if feats["assignment_completion"] < 0.6:
        recs.append({
            "title": "Assignment catch-up plan",
            "reason": f"Completion rate is {feats['assignment_completion']:.0%}, below 60%.",
        })
    if feats["late_submission_rate"] > 0.3:
        recs.append({
            "title": "Deadline scaffolding",
            "reason": f"Late submissions are {feats['late_submission_rate']:.0%} of assignments.",
        })
    if not recs:
        recs.append({
            "title": "Maintain current supports",
            "reason": "Attendance, scores and completion are above local support thresholds.",
        })
    return recs
