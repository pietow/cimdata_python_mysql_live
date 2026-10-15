from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db import SessionLocal
from models import Student
from register_student import register_student

try:
    register_student("Test", "Rollback", 999, date(1993, 9, 5))
except IntegrityError:
    print("Ungültiger Kurs: Anmeldung volständig zurückgesetzt.")


with SessionLocal() as session:
    existing_id = session.scalar(
        select(Student.id).where(Student.first_name=="Elias", Student.last_name == "Brook")
    )


if existing_id is None:
    ids = register_student("Elias", "Brook", 1, date(1993, 9, 5))
    print("Gespeichert: Schüler-ID, Buchungs-ID ", ids)
else:
    print("Elias bereits vorhanden.")