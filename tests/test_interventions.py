from tests.conftest import login
from app.models import Student, Intervention
from app.extensions import db


def test_create_and_export(client, app):
    login(client, "admin@demo.school", "DemoAdmin!23")
    with app.app_context():
        sid = Student.query.first().id
    r = client.post(f"/students/{sid}", data={"category": "attendance", "notes": "Check-in plan"}, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert Intervention.query.filter_by(student_id=sid).count() >= 1
    exp = client.get("/analytics/export")
    assert exp.status_code == 200
    assert exp.mimetype == "text/csv"
    assert b"student_code" in exp.data
