from datetime import date

from db import SessionLocal
from models import Student, Booking

def register_student(first_name: str, last_name: str, course_id: int, booking_date: date):
    with SessionLocal.begin() as session:
        student = Student(first_name=first_name, last_name=last_name, house=None, school_year=1)
        session.add(student)
        session.flush()
        booking = Booking(student_id=student.id, course_id=course_id, booking_date=booking_date)
        session.add(booking)
        session.flush()
        result = student.id, booking.id
    return result