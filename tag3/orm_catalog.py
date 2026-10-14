from sqlalchemy import select

from db import SessionLocal
from models import Course


with SessionLocal() as session:
    statement = select(Course).order_by(Course.id)
    course = session.get(Course, 3)

    print(course.title if course else "Nicht gefunden")
    print(session.get(Course, 999))




