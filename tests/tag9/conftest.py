import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, delete, text
from sqlalchemy.orm import sessionmaker

from tag7.models import Booking, Course, Student
from tag8.testing_db import make_test_url
from tag9.create_user import add_user
from tag9.dependencies import get_session
from tag9.main import app
from tag9.models import AccessToken, User
from tag9.schemas import LoginInput, UserRead

TEST_PASSWORD = "Nur-fuer-den-lokalen-Test-123!"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(make_test_url(), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            name = connection.scalar(text("SELECT DATABASE()"))
            if name != "hogwarts_test":
                raise RuntimeError("Dies ist nicht die Testdatenbank.")
            revision = connection.scalar(text(
                "SELECT version_num FROM alembic_version"
            ))
            if revision != "0003":
                raise RuntimeError("Zuerst init_test_db ausführen.")
        yield engine
    finally:
        engine.dispose()


def clear_test_rows(factory):
    with factory.begin() as db:
        # Beide Fremdschlüsselketten von den Kindern aus aufräumen.
        for model in (AccessToken, User, Booking, Student, Course):
            db.execute(delete(model))


@pytest.fixture
def db_factory(test_engine):
    factory = sessionmaker(bind=test_engine)
    clear_test_rows(factory)
    try:
        yield factory
    finally:
        clear_test_rows(factory)


@pytest.fixture
def api_client(db_factory):
    def test_session():
        # Derselbe Ablauf wie in get_session, aber auf hogwarts_test.
        # FastAPI verwendet dieses eine Session-Objekt im gesamten Request.
        with db_factory() as db:
            try:
                yield db
            except Exception:
                db.rollback()
                raise

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = test_session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.fixture
def accounts(db_factory):
    result: dict[str, UserRead] = {}
    for name, role in (("babbling", "reader"), ("vector", "staff")):
        with db_factory() as db:
            user = add_user(db, LoginInput(
                username=name, password=SecretStr(TEST_PASSWORD),
            ), role)
            result[role] = user
    return result


@pytest.fixture
def login_as(api_client, accounts):
    # Diese Fixture führt beim Aufbau noch keinen Login aus.
    # Sie baut eine Hilfsfunktion, die später mit einer Rolle aufgerufen wird.
    def login(role):
        # Die innere Funktion kann api_client und accounts aus der äußeren
        # Funktion weiter verwenden. Diese Bindung nennt man Closure.
        response = api_client.post("/auth/login", json={
            "username": accounts[role].username,
            "password": TEST_PASSWORD,
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    # Ohne Klammern: Wir geben die Funktion zurück, nicht ihr Ergebnis.
    return login


@pytest.fixture
def seed(db_factory):
    with db_factory.begin() as db:
        harry = Student(first_name="Harry", last_name="Potter",
                        house="Gryffindor", school_year=3)
        luna = Student(first_name="Luna", last_name="Lovegood",
                       house="Ravenclaw", school_year=2)
        course = Course(title="Alte Runen")
        db.add_all([harry, luna, course])
        db.flush()
        result = {"harry_id": harry.id, "luna_id": luna.id,
                  "course_id": course.id}
    return result
