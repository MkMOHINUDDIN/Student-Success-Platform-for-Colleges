from functools import wraps
from flask import abort
from flask_login import current_user
from .extensions import login_manager, db
from .models import User, Student, ClassGroup, AuditEvent


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def can_access_student(student: Student) -> bool:
    if not current_user.is_authenticated:
        return False
    if current_user.role == "admin":
        return True
    if current_user.role == "teacher":
        taught_ids = {c.id for c in ClassGroup.query.filter_by(teacher_id=current_user.id).all()}
        return student.mentor_id == current_user.id or student.class_id in taught_ids
    if current_user.role == "student" and current_user.student:
        return student.id == current_user.student.id
    return False


def visible_students():
    q = Student.query
    if current_user.role == "admin":
        return q
    if current_user.role == "teacher":
        taught_ids = [c.id for c in ClassGroup.query.filter_by(teacher_id=current_user.id).all()]
        return q.filter(db.or_(Student.mentor_id == current_user.id, Student.class_id.in_(taught_ids or [-1])))
    if current_user.role == "student" and current_user.student:
        return q.filter(Student.id == current_user.student.id)
    return q.filter(Student.id == -1)


def audit(action, detail=None):
    uid = current_user.id if getattr(current_user, "is_authenticated", False) else None
    db.session.add(AuditEvent(user_id=uid, action=action, detail=detail))
