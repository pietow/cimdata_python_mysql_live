from fastapi import APIRouter
from sqlalchemy import select

from tag7.models import Booking
from tag7.schemas import BookingBatchCreate, BookingRead
from tag9.dependencies import DbSession
from tag9.routers.bookings import create_booking_batch as save_batch
from tag10.models import CourseManager
from tag10.permissions import StaffUser, managed_course

router = APIRouter(tags=["Buchungen"])


@router.get("/bookings", response_model=list[BookingRead])
def read_bookings(db: DbSession, user: StaffUser):
    statement = (
        select(Booking)
        # Zuständigkeit zum Kurs der Buchung hinzunehmen.
        .join(CourseManager, CourseManager.course_id == Booking.course_id)
        # API1: Nur Kurse des bestätigten Kontos auswählen.
        .where(CourseManager.user_id == user.id)
        .order_by(Booking.id)
    )
    return db.scalars(statement).all()


@router.post("/booking-batches", response_model=list[BookingRead],
             status_code=201)
def create_booking_batch(data: BookingBatchCreate,
                         db: DbSession, user: StaffUser):
    # API1: Auch die Kurs-ID aus einem gültigen JSON braucht eine Rechteprüfung.
    managed_course(data.course_id, db, user)
    # Normaler Python-Aufruf: Wir reichen die bereits offene Session weiter.
    # FastAPI führt bei diesem direkten Aufruf keine Dependencies erneut aus.
    # Tag 9 prüft die Fachregeln und committet die ganze Gruppe.
    return save_batch(data=data, db=db)
