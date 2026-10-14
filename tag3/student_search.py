from sqlalchemy import select

from db import SessionLocal
from models import Student


def find_students(last_name: str) -> list[tuple[int, str, str]]:
    statement = (
        select(Student.id, Student.first_name, Student.last_name)
        .where(Student.last_name == last_name)
        .order_by(Student.id)
    )

    with SessionLocal() as session:
        return [tuple(row) for row in session.execute(statement)]

for last_name in ("Weasley", "O'Neil", "' OR 1=1; --"):
    print(last_name, find_students(last_name))