from contextlib import asynccontextmanager
from datetime import date

from fastapi import APIRouter

from tag10.pagination import AfterId, Limit
from tag10.permissions import StaffUser
from tag11.reports import booking_statement
from tag11.schemas import BookingReportRead
from tag12.db import AsyncDb, async_engine
from tag12.reports import load_report_async


# Bereitgestellt: macht die Funktion zum asynchronen Kontextmanager.
@asynccontextmanager
async def lifespan(app):
    try:
        yield  # Der Server bedient jetzt Requests.
    finally:
        await async_engine.dispose()  # Pool beim Herunterfahren schließen.


router = APIRouter(prefix="/async/reports", lifespan=lifespan)

@router.get("/bookings", response_model=list[BookingReportRead])
async def read_report(
        booking_date: date,
        db: AsyncDb,
        user: StaffUser,
        limit: Limit = 20,
        after_id: AfterId = 0,
):
    statement = booking_statement(user.id, booking_date, limit, after_id)
    return await load_report_async(db, statement) # Co-Routine
