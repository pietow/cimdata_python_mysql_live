from sqlalchemy import func, select

from tag7.models import Booking, Course, Student


def count_rows(db, model):
    return db.scalar(select(func.count()).select_from(model))


def test_db_factory_starts_empty(db_factory):
    with db_factory() as db:
        assert count_rows(db, Student) == 0
        assert count_rows(db, Course) == 0
        assert count_rows(db, Booking) == 0


def test_seed_creates_known_rows(db_factory, seed):
    with db_factory() as db:
        assert count_rows(db, Student) == 4
        assert count_rows(db, Course) == 3
        assert count_rows(db, Booking) == 0
        assert db.get(Student, seed["luna_id"]).school_year == 2
