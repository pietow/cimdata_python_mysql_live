import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from tag7.dependencies import DbSession
from tag7.models import Booking, Course, Student
from tag7.schemas import BookingBatchCreate, BookingRead
from tag8.rules import validate_elective_year

router = APIRouter(tags=["Buchungen"])
logger = logging.getLogger("hogwarts.bookings")

@router.get("/bookings", response_model=list[BookingRead])
def read_bookings(db: DbSession):
    return db.scalars(select(Booking).order_by(Booking.id)).all()


@router.post("/booking-batches", response_model=list[BookingRead], status_code=201)
def create_booking_batch(data: BookingBatchCreate, db: DbSession):
    try:
        with db.begin():
            course = db.get(Course, data.course_id)
            if course is None:
                raise HTTPException(404, "Kurs nicht gefunden.")

            result = []
            for student_id in data.student_ids:
                student = db.get(Student, student_id)
                if student is None:
                    raise HTTPException(404, "Kurs nicht gefunden.")
                # Neue fachliche Regel
                validate_elective_year(student.school_year, course.title)
                booking = Booking(   # ORM Instanz
                    student_id = student_id,
                    course_id = data.course_id,
                    booking_date=data.booking_date
                )
                db.add(booking)
                db.flush()
                result.append(BookingRead.model_validate(booking)) # list aus Pyantic Model Instanzen (nicht mit ORM Model instanzen verwechseln)
        logger.info(f"booking_batch_saved course_id={data.course_id} count={len(result)}")
        return result
    except IntegrityError as exc:
        raise HTTPException(409, "Buchungskonflikt")

