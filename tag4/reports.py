from sqlalchemy import func, select

from tag3.db import SessionLocal
from tag3.models import Booking, Course, Student


def course_register(course_id: int) -> list[dict]:
    statement = (
        select(Student.id.label("student_id"),
               Student.first_name,
               Student.last_name,
               Booking.booking_date
               )
            .select_from(Booking)
            .join(Booking.student)
            .where(Booking.course_id == course_id)       
    )
    with SessionLocal() as session:
        rows = session.execute(statement).mappings()
        return [dict(row) for row in rows]



def course_summary() -> list[dict]:
    statement = (
        select(
            Course.id.label("course_id"),
            Course.title,
            func.count(Booking.id).label("booking_count")
        )
        .outerjoin(Course.bookings)
        .group_by(Course.id, Course.title)
    )
    with SessionLocal() as session:
        return [dict(row) for row in session.execute(statement).mappings()]

def students_without_bookings() -> list[dict]:
    statement = (
        select(Student.id, Student.last_name, Student.first_name)
        .where(~Student.bookings.any())
        .order_by(Student.id)
    )
    with SessionLocal() as session:
        return [dict(row) for row in session.execute(statement).mappings()]