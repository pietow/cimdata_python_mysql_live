import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, text
from sqlalchemy.orm import sessionmaker

from tag7.models import Booking, Course, Student
from tag7.dependencies import get_session
from tag8.testing_db import make_test_url
from tag8.main import  app

@pytest.fixture(scope="session")# session ist hier nicht MYSQL SESSION, sondern test session
def test_engine():  
    engine = create_engine(make_test_url(), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            name = connection.scalar(text("SELECT DATABASE()"))
            if name != "hogwarts_test":
                raise RuntimeError("Das ist die falsche DB")
            revision = connection.scalar(text("SELECT version_num FROM alembic_version "))
            if revision != "0002":
                raise RuntimeError("Zuerst init_test_db ausführen.")
        yield engine
    finally:
        engine.dispose()
 

def clear_test_rows(factory):
    with factory.begin() as db:
        db.execute(delete(Booking))
        db.execute(delete(Student))
        db.execute(delete(Course))

@pytest.fixture
def db_factory(test_engine):
    factory = sessionmaker(bind=test_engine)
    clear_test_rows(factory)
    try:
        yield factory
    finally:
        clear_test_rows(factory)


@pytest.fixture
def seed(db_factory):
    with db_factory.begin() as db:
        harry = Student(first_name="Harry", last_name="Potter",
                        house="Gryffindor", school_year=3)
        hermione = Student(first_name="Hermione", last_name="Granger",
                           house="Gryffindor", school_year=3)
        luna = Student(first_name="Luna", last_name="Lovegood",
                       house="Ravenclaw", school_year=2)
        ginny = Student(first_name="Ginny", last_name="Weasley",
                        house="Gryffindor", school_year=2)
        elective = Course(title="Alte Runen")
        other = Course(title="Flugkunde")
        empty = Course(title="Astronomie")
        db.add_all([harry, hermione, luna, ginny, elective, other, empty])
        db.flush()
        # IDs als Werte merken, bevor die Session geschlossen wird.
        result = {
            "harry_id": harry.id, "hermione_id": hermione.id,
            "luna_id": luna.id, "ginny_id": ginny.id,
            "course_id": elective.id, "other_course_id": other.id,
            "empty_course_id": empty.id,
        }
    return result


@pytest.fixture
def api_client(db_factory):
    def override_session():
        with db_factory() as db:
            yield db


    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = override_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)