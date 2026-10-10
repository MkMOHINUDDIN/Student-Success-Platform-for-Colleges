import os
from flask import Flask, render_template
from .config import Config
from .extensions import db, login_manager, csrf, migrate


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["ARTIFACT_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import models  # noqa: F401
    from .auth import load_user  # noqa: F401

    from .blueprints.auth import bp as auth_bp
    from .blueprints.dashboard import bp as dashboard_bp
    from .blueprints.students import bp as students_bp
    from .blueprints.imports import bp as imports_bp
    from .blueprints.risk import bp as risk_bp
    from .blueprints.interventions import bp as interventions_bp
    from .blueprints.analytics import bp as analytics_bp
    from .blueprints.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(imports_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(interventions_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(admin_bp)

    if test_config and test_config.get("TESTING"):
        with app.app_context():
            db.create_all()

    @app.errorhandler(403)
    def forbidden(_e):
        return render_error(403, "You do not have access to this page."), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_error(404, "That page was not found."), 404

    return app


def render_error(code, message):
    from flask import render_template
    return render_template("errors/generic.html", code=code, message=message)
