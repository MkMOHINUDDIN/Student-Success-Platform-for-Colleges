import json
import os
from flask import current_app


def _path(job_id):
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"preview_{job_id}.json")


def save_preview(job_id, kind, valid):
    serial = []
    for item in valid:
        if kind == "results":
            serial.append({
                "student_id": item["student"].id,
                "assessment_id": item["assessment"].id,
                "score": item["score"],
            })
        else:
            serial.append({
                "student_id": item["student"].id,
                "term_id": item["term"].id,
                "date": item["date"].isoformat(),
                "status": item["status"],
            })
    with open(_path(job_id), "w", encoding="utf-8") as f:
        json.dump(serial, f)


def load_preview(job_id):
    p = _path(job_id)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)
