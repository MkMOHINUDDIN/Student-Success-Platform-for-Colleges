"""Idempotent fictional student dataset. Seed=42. Not real people."""
from datetime import date, timedelta
import random
from app.extensions import db
from app.models import (
    User, ClassGroup, Subject, Term, Student, Enrolment, Attendance,
    Assessment, Result, Assignment, Submission, Goal,
)

RNG = random.Random(42)
FIRST = ["Asha", "Ben", "Cara", "Dev", "Elena", "Farid", "Gita", "Hugo", "Imani", "Jules",
         "Kai", "Lina", "Mateo", "Noor", "Owen", "Priya", "Quinn", "Ravi", "Sofia", "Tariq"]
LAST = ["Ng", "Patel", "Silva", "Okafor", "Berg", "Chen", "Ali", "Rossi", "Khan", "Meyer"]


def generate(n_students=60):
    if User.query.filter_by(email="admin@demo.school").first():
        return "already_seeded"

    admin = User(email="admin@demo.school", name="Demo Admin", role="admin")
    admin.set_password("DemoAdmin!23")
    t1 = User(email="teacher@demo.school", name="Demo Teacher", role="teacher")
    t1.set_password("DemoTeach!23")
    t2 = User(email="teacher2@demo.school", name="Demo Teacher Two", role="teacher")
    t2.set_password("DemoTeach!23")
    db.session.add_all([admin, t1, t2])
    db.session.flush()

    classes = [
        ClassGroup(name="Year 10 A", year_level=10, teacher_id=t1.id),
        ClassGroup(name="Year 10 B", year_level=10, teacher_id=t1.id),
        ClassGroup(name="Year 11 A", year_level=11, teacher_id=t2.id),
    ]
    db.session.add_all(classes)
    db.session.flush()

    subjects = [
        Subject(code="MATH", name="Mathematics"),
        Subject(code="ENG", name="English"),
        Subject(code="SCI", name="Science"),
        Subject(code="HIS", name="History"),
    ]
    db.session.add_all(subjects)
    terms = [
        Term(name="Term 1", start_date=date(2025, 1, 13), end_date=date(2025, 4, 4), sequence=1),
        Term(name="Term 2", start_date=date(2025, 4, 21), end_date=date(2025, 7, 4), sequence=2),
    ]
    db.session.add_all(terms)
    db.session.flush()

    students = []
    latent = {}
    for i in range(n_students):
        cls = classes[i % 3]
        mentor = t1 if cls.teacher_id == t1.id else t2
        s = Student(
            student_code=f"SYN{i+1:03d}",
            first_name=FIRST[i % len(FIRST)],
            last_name=LAST[i % len(LAST)],
            fictional_flag=True,
            gender=RNG.choice(["female", "male", "non-binary", None]),
            date_of_birth=date(2009, 1, 1) + timedelta(days=i * 7),
            class_id=cls.id,
            mentor_id=mentor.id,
        )
        db.session.add(s)
        db.session.flush()
        if i == 0:
            su = User(email="student@demo.school", name=f"{s.first_name} {s.last_name}", role="student")
            su.set_password("DemoStud!23")
            db.session.add(su)
            db.session.flush()
            s.user_id = su.id
        students.append(s)
        latent[s.id] = RNG.uniform(0.15, 0.95)
        db.session.add(Goal(student_id=s.id, title="Improve term average", target_value="60+"))

    for s in students:
        for term in terms:
            for sub in subjects:
                db.session.add(Enrolment(student_id=s.id, subject_id=sub.id, term_id=term.id))

    for term in terms:
        for d_off in range(12):
            day = term.start_date + timedelta(days=d_off * 2)
            for s in students:
                p_abs = 0.05 + (1 - latent[s.id]) * 0.35
                roll = RNG.random()
                status = "absent" if roll < p_abs else ("late" if roll < p_abs + 0.1 else "present")
                db.session.add(Attendance(student_id=s.id, term_id=term.id, date=day, status=status))
        for sub in subjects:
            for n in (1, 2):
                a = Assessment(
                    subject_id=sub.id, term_id=term.id,
                    name=f"{sub.code} T{term.sequence} A{n}",
                    max_score=100, due_date=term.start_date + timedelta(days=20 * n),
                )
                db.session.add(a)
                db.session.flush()
                for s in students:
                    base = 40 + latent[s.id] * 50 + RNG.uniform(-8, 8)
                    score = max(5, min(100, base))
                    db.session.add(Result(assessment_id=a.id, student_id=s.id, score=round(score, 1)))
            asn = Assignment(
                subject_id=sub.id, term_id=term.id,
                title=f"{sub.code} assignment T{term.sequence}",
                due_date=term.end_date - timedelta(days=7),
            )
            db.session.add(asn)
            db.session.flush()
            for s in students:
                completed = RNG.random() < (0.45 + latent[s.id] * 0.5)
                late = completed and RNG.random() < (0.4 * (1 - latent[s.id]))
                submitted = asn.due_date + timedelta(days=2) if late else (asn.due_date if completed else None)
                db.session.add(Submission(
                    assignment_id=asn.id, student_id=s.id,
                    submitted_at=submitted, late=late, completed=completed,
                ))
    db.session.commit()
    return "seeded"
