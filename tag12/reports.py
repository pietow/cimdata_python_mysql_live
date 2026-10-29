from sqlalchemy.orm import joinedload, raiseload

from tag7.models import Booking
from tag11.schemas import BookingReportRead


async def load_report_async(db, statement):
    statement = statement.options(
            joinedload(Booking.student),
            joinedload(Booking.course),
            raiseload('*'), 
    )

    result = await db.scalars(statement)
    rows = []

    for booking in result:
        student = booking.student
        booking_report_instanz = BookingReportRead(
            id = booking.id,
            student_name=f"{student.first_name} {student.last_name}",
            course_title=booking.course.title,
            booking_date=booking.booking_date,
        )
        rows.append(booking_report_instanz)
    return rows