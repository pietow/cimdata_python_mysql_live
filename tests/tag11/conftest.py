import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, text
from sqlalchemy.orm import sessionmaker

from tag7.models import Booking, Course, Student
from tag8.testing_db import make_test_url
from tag9.create_user import add_user
from tag9.dependencies import get_session
from tag9.models import AccessToken, User
from tag9.schemas import LoginInput
from tag10.models import CourseManager
from tag11.main import create_app # neues main


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(make_test_url(), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            if connection.scalar(text("SELECT DATABASE()")) != "hogwarts_test":
                raise RuntimeError("Dies ist nicht die Testdatenbank.")
            revision = connection.scalar(text(
                "SELECT version_num FROM alembic_version"
            ))
            if revision != "0004":
                raise RuntimeError("Zuerst init_test_db ausführen.")
        yield engine
    finally:
        engine.dispose()


def clear_rows(factory):
    with factory.begin() as db:
        # Abhängige Zeilen zuerst löschen, damit Fremdschlüssel gültig bleiben.
        for model in (CourseManager, AccessToken, User,
                      Booking, Student, Course):
            db.execute(delete(model))


@pytest.fixture
def db_factory(test_engine):
    factory = sessionmaker(bind=test_engine)
    clear_rows(factory)
    try:
        yield factory
    finally:
        clear_rows(factory)


@pytest.fixture
def api_app(db_factory):
    app = create_app(show_docs=True)

    def test_session():
        with db_factory() as db:
            try:
                yield db
            except Exception:
                db.rollback()
                raise

    # Nur DB-Zugang ersetzen. Anmeldung und Rechteprüfung laufen weiterhin echt.
    app.dependency_overrides[get_session] = test_session
    return app


@pytest.fixture
def api_client(api_app):
    # localhost gehört zu den erlaubten Hostnamen der App.
    with TestClient(api_app, base_url="http://localhost") as client:
        yield client


@pytest.fixture
def accounts(db_factory):
    result = {"password": "Nur-fuer-den-lokalen-Test-123!"}
    for name, role in (("vector", "staff"), ("hagrid", "staff"),
                       ("babbling", "reader")):
        with db_factory() as db:
            result[name] = add_user(db, LoginInput(
                username=name, password=result["password"],
            ), role)
    return result


@pytest.fixture
def login_as(api_client, accounts):
    def login(name):
        response = api_client.post("/auth/login", json={
            "username": name, "password": accounts["password"],
        })
        assert response.status_code == 200
        return {"Authorization": "Bearer " + response.json()["access_token"]}
    return login


@pytest.fixture
def seed(db_factory, accounts):
    with db_factory.begin() as db:
        harry = Student(first_name="Harry", last_name="Potter",
                        house="Gryffindor", school_year=3)
        luna = Student(first_name="Luna", last_name="Lovegood",
                       house="Ravenclaw", school_year=2)
        own = Course(title="Arithmantik")
        other = Course(title="Pflege magischer Geschöpfe")
        unassigned = Course(title="Astronomie")
        db.add_all([harry, luna, own, other, unassigned])
        db.flush()
        db.add_all([
            CourseManager(course_id=own.id, user_id=accounts["vector"].id),
            CourseManager(course_id=other.id, user_id=accounts["hagrid"].id),
        ])
        result = {"own_id": own.id, "other_id": other.id,
                  "unassigned_id": unassigned.id,
                  "harry_id": harry.id, "luna_id": luna.id}
    return result

@pytest.fixture # neuer fixture
def report_seed(db_factory, seed):
    from datetime import date

    day = date(1993, 9, 1)
    with db_factory.begin() as db:
        nora = Student(first_name="Nora", last_name="Winter",
                       house="Ravenclaw", school_year=3)
        elias = Student(first_name="Elias", last_name="Brook",
                        house="Hufflepuff", school_year=3)
        db.add_all([nora, elias])
        db.flush()
        # Eigene IDs sind durch eine fremde Buchung unterbrochen.
        bookings = [
            Booking(student_id=seed["harry_id"],
                    course_id=seed["own_id"], booking_date=day),
            Booking(student_id=seed["harry_id"],
                    course_id=seed["other_id"], booking_date=day),
            Booking(student_id=nora.id, course_id=seed["own_id"],
                    booking_date=day),
            Booking(student_id=elias.id, course_id=seed["own_id"],
                    booking_date=day),
            Booking(student_id=seed["harry_id"],
                    course_id=seed["own_id"], booking_date=date(1993, 9, 2)),
        ]
        db.add_all(bookings)
        db.flush()
        return {
            "day": day,
            "own_ids": [bookings[i].id for i in (0, 2, 3)],
            "foreign_id": bookings[1].id,
        }
