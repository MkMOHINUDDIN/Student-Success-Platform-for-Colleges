from tests.conftest import login
from app.models import Student


def test_login_ok(client):
    r = login(client, "admin@demo.school", "DemoAdmin!23")
    assert r.status_code == 200
    assert b"Dashboard" in r.data


def test_bad_login(client):
    r = login(client, "admin@demo.school", "wrong")
    assert b"Invalid" in r.data


def test_student_cannot_directory(client):
    login(client, "student@demo.school", "DemoStud!23")
    r = client.get("/students/")
    assert r.status_code == 403


def test_student_cannot_other_profile(client, app):
    login(client, "student@demo.school", "DemoStud!23")
    with app.app_context():
        other = Student.query.filter(Student.student_code != "SYN001").first()
        oid = other.id
    r = client.get(f"/students/{oid}")
    assert r.status_code == 403


def test_teacher_blocked_from_admin(client):
    login(client, "teacher@demo.school", "DemoTeach!23")
    assert client.get("/admin/").status_code == 403
