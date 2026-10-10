from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="user", uselist=False, foreign_keys="Student.user_id")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ClassGroup(db.Model):
    __tablename__ = "classes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    year_level = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    teacher = db.relationship("User", foreign_keys=[teacher_id])


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)


class Term(db.Model):
    __tablename__ = "terms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    sequence = db.Column(db.Integer, nullable=False)


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(32), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    fictional_flag = db.Column(db.Boolean, default=True, nullable=False)
    gender = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class_group = db.relationship("ClassGroup", backref="students")
    mentor = db.relationship("User", foreign_keys=[mentor_id])


class Enrolment(db.Model):
    __tablename__ = "enrolments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"), nullable=False)
    __table_args__ = (db.UniqueConstraint("student_id", "subject_id", "term_id"),)
    student = db.relationship("Student", backref="enrolments")
    subject = db.relationship("Subject")
    term = db.relationship("Term")


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late
    __table_args__ = (db.UniqueConstraint("student_id", "date"),)
    student = db.relationship("Student", backref="attendance")
    term = db.relationship("Term")


class Assessment(db.Model):
    __tablename__ = "assessments"
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    max_score = db.Column(db.Float, default=100.0, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    subject = db.relationship("Subject")
    term = db.relationship("Term")


class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)
    submitted_at = db.Column(db.Date, nullable=True)
    __table_args__ = (db.UniqueConstraint("assessment_id", "student_id"),)
    assessment = db.relationship("Assessment", backref="results")
    student = db.relationship("Student", backref="results")


class Assignment(db.Model):
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    subject = db.relationship("Subject")
    term = db.relationship("Term")


class Submission(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    submitted_at = db.Column(db.Date, nullable=True)
    late = db.Column(db.Boolean, default=False, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    __table_args__ = (db.UniqueConstraint("assignment_id", "student_id"),)
    assignment = db.relationship("Assignment", backref="submissions")
    student = db.relationship("Student", backref="submissions")


class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    target_value = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship("Student", backref="goals")


class ModelVersion(db.Model):
    __tablename__ = "model_versions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)
    metrics_json = db.Column(db.Text, nullable=True)
    artifact_path = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=False, nullable=False)


class RiskAssessment(db.Model):
    __tablename__ = "risk_assessments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    model_version_id = db.Column(db.Integer, db.ForeignKey("model_versions.id"), nullable=True)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"), nullable=True)
    probability = db.Column(db.Float, nullable=False)
    predicted_label = db.Column(db.Boolean, nullable=False)
    explanation_json = db.Column(db.Text, nullable=True)
    recommendations_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship("Student", backref="risk_assessments")
    model_version = db.relationship("ModelVersion")
    term = db.relationship("Term")


class Intervention(db.Model):
    __tablename__ = "interventions"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="open", nullable=False)
    outcome = db.Column(db.String(80), nullable=True)
    before_attendance = db.Column(db.Float, nullable=True)
    before_mean_score = db.Column(db.Float, nullable=True)
    after_attendance = db.Column(db.Float, nullable=True)
    after_mean_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)
    student = db.relationship("Student", backref="interventions")
    created_by = db.relationship("User")


class FollowUp(db.Model):
    __tablename__ = "follow_ups"
    id = db.Column(db.Integer, primary_key=True)
    intervention_id = db.Column(db.Integer, db.ForeignKey("interventions.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    observation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    intervention = db.relationship("Intervention", backref="follow_ups")
    author = db.relationship("User")


class ImportJob(db.Model):
    __tablename__ = "import_jobs"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    kind = db.Column(db.String(40), nullable=False)
    status = db.Column(db.String(30), default="previewed", nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    row_count = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    created_by = db.relationship("User")


class ImportError(db.Model):
    __tablename__ = "import_errors"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("import_jobs.id"), nullable=False)
    row_number = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(500), nullable=False)
    job = db.relationship("ImportJob", backref="errors")


class AuditEvent(db.Model):
    __tablename__ = "audit_events"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(80), nullable=False)
    detail = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User")


def today():
    return date.today()
