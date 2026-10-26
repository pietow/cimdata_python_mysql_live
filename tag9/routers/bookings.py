import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from tag7.models import Booking, Course, Student
from tag7.schemas import BookingBatchCreate, BookingRead
from tag8.rules import validate_elective_year
from tag9.dependencies import DbSession

router = APIRouter(tags=["Buchungen"])
logger = logging.getLogger("hogwarts.bookings")


@router.get("/bookings", response_model=list[BookingRead])
def read_bookings(db: DbSession):
    return db.scalars(select(Booking).order_by(Booking.id)).all()


@router.post("/booking-batches", response_model=list[BookingRead],
             status_code=201)
def create_booking_batch(data: BookingBatchCreate, db: DbSession):
    try:
        course = db.get(Course, data.course_id)
        if course is None:
            raise HTTPException(404, "Kurs nicht gefunden.")
        result = []
        for student_id in data.student_ids:
            student = db.get(Student, student_id)
            if student is None:
                raise HTTPException(404, "Schüler nicht gefunden.")
            validate_elective_year(student.school_year, course.title)
            booking = Booking(
                student_id=student_id,
                course_id=data.course_id,
                booking_date=data.booking_date,
            )
            db.add(booking)
            db.flush()  # INSERT ausführen, aber noch nicht dauerhaft speichern.
            result.append(BookingRead.model_validate(booking))
        # Ein gemeinsamer Commit für die ganze Gruppe, erst nach allen Prüfungen.
        db.commit()
    except IntegrityError as exc:
        raise HTTPException(409, "Buchungskonflikt.") from exc
    # Auch 404 und SchoolYearTooLow verlassen die Route als Ausnahme.
    # get_session rollt dann alle INSERTs dieses Requests zurück.
    logger.info("booking_batch_saved course_id=%s count=%s",
                data.course_id, len(result))
    return result
