import logging


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from tag8.logging_setup import configure_logging
from tag8.routers import bookings
from tag8.rules import SchoolYearTooLow

from tag9.routers import auth, courses

configure_logging()
logger = logging.getLogger("hogwarts.api")
app = FastAPI(title="Hogwarts-Kursverwaltung", description="Lern-API mit MySQL", version="0.5.0")
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(bookings.router)

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.exception_handler(SchoolYearTooLow)
def school_year_error(request: Request, exc: SchoolYearTooLow):
    logger.warning("booking_batch_rejected reason=school_year")
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(OperationalError)
def database_error(request: Request, exc: OperationalError):
    logger.error(f"database_unavailable method={request.method} path={request.url.path}")
    return JSONResponse(status_code=503, content={"detail": "Datenbank derzeit nicht erreichbar."})