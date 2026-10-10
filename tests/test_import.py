from io import BytesIO
from tests.conftest import login
from app.models import Result, Student, Assessment
from app.extensions import db


def test_results_preview_and_duplicate(client, app):
    login(client, "admin@demo.school", "DemoAdmin!23")
    with app.app_context():
        s = Student.query.first()
        a = Assessment.query.first()
        Result.query.filter_by(student_id=s.id, assessment_id=a.id).delete()
        db.session.commit()
        code, aname, term = s.student_code, a.name, a.term.name
    csv = f"student_code,assessment_name,term,score\n{code},{aname},{term},88\n{code},{aname},{term},88\n".encode()
    r = client.post("/imports/", data={"kind": "results", "file": (BytesIO(csv), "t.csv")}, content_type="multipart/form-data")
    assert r.status_code == 200
    assert b"Duplicate" in r.data or b"error" in r.data.lower()


def test_unknown_student_row_error(client):
    login(client, "admin@demo.school", "DemoAdmin!23")
    csv = b"student_code,assessment_name,term,score\nNOPE,X,Term 1,10\n"
    r = client.post("/imports/", data={"kind": "results", "file": (BytesIO(csv), "t.csv")}, content_type="multipart/form-data")
    assert b"Unknown student_code" in r.data
