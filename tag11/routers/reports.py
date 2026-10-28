from datetime import date

from fastapi import APIRouter

from tag9.dependencies import DbSession
from tag10.pagination import AfterId, Limit
from tag10.permissions import StaffUser
from tag11.reports import booking_statement, load_report
from tag11.schemas import BookingReportRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/bookings", response_model=list[BookingReportRead])
def read_booking_report(booking_date: date, db: DbSession, user: StaffUser, limit: Limit = 20, after_id: AfterId=0):
    statement = booking_statement(user.id, booking_date, limit, after_id)
    return load_report(db, statement)