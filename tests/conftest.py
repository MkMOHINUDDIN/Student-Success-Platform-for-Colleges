import pytest
from app import create_app
from app.extensions import db
from scripts.generate_synthetic import generate
from app.services.ml import train_and_persist


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test",
        "UPLOAD_FOLDER": "instance/test-uploads",
        "ARTIFACT_FOLDER": "instance/test-artifacts",
    })
    with app.app_context():
        db.create_all()
        generate(n_students=24)
        train_and_persist()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, email, password):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
