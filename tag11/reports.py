from sqlalchemy import select
from sqlalchemy.orm import joinedload

from tag7.models import Booking
from tag10.models import CourseManager

from tag11.schemas import BookingReportRead


def booking_statement(user_id, day, limit=20, after_id=0):
    return (
        select(Booking)
            .join(CourseManager, CourseManager.course_id == Booking.course_id)
            .where(
                CourseManager.user_id == user_id,
                Booking.booking_date == day,
                Booking.id > after_id,

            )
            .order_by(Booking.id)
            .limit(limit)
    )


def load_report(db, statement, eager=True):
    if eager:
        statement = statement.options(
            joinedload(Booking.student),
            joinedload(Booking.course),
        )

    rows = []

    for booking in db.scalars(statement):
        student = booking.student
        rows.append(BookingReportRead(
            id = booking.id,
            student_name=f"{student.first_name} {student.last_name}",
            course_title=booking.course.title,
            booking_date=booking.booking_date,
        ))
    return rows