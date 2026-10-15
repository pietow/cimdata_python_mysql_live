from sqlalchemy import select

from db import SessionLocal
from models import Booking


with SessionLocal() as session:
    statement = (
        select(Booking)
        .where(Booking.student_id == 2) 
        .order_by(Booking.id)
    )

    for booking in session.scalars(statement):
        print(
            booking.student.first_name,
            booking.student.last_name,
            booking.course.title,
            booking.booking_date,
        )

    for booking in session.execute(statement):
        print(booking[0])