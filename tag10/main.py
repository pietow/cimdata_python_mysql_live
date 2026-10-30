import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from tag8.logging_setup import configure_logging
from tag8.rules import SchoolYearTooLow
from tag10.routers import bookings, courses
from tag9.routers import auth

configure_logging()
logger = logging.getLogger("hogwarts.api")



def school_year_error(request: Request, exc: Exception):
    # Starlette erwartet (Request, Exception); FastAPI ruft ihn nur für SchoolYearTooLow auf.
    return JSONResponse(status_code=409, content={"detail": str(exc)})


def unexpected_error(request: Request, exc: Exception):
    # Der rohe Fehlertext könnte SQL-Parameter oder Zugangsdaten enthalten.
    logger.error("unhandled_request_error")
    return JSONResponse(status_code=500, content={
        "detail": "Interner Fehler.",
    })


def create_app(show_docs=False):
    # API8: Zentrale Sicherheitskonfiguration in tag10/main.py.
    # Jede Ausführung erzeugt eine neue, gleich konfigurierte FastAPI-Instanz.
    app = FastAPI(
        title="Hogwarts-Kursverwaltung", version="0.6.0",
        debug=False,  # API8: Keine Debug-Fehlerseiten mit internen Details.
        # API8: Dokumentation bewusst je Betriebsmodus freigeben.
        # Das Abschalten ersetzt keine Rechteprüfung.
        docs_url="/docs" if show_docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if show_docs else None,
    )
    app.include_router(auth.router)
    app.include_router(courses.router)
    app.include_router(bookings.router)

    # Fehlerklasse und Funktion ohne Klammern registrieren.
    # FastAPI ruft den passenden Handler erst beim Auftreten des Fehlers auf.
    # API8: Unsere Handler vermeiden interne SQL-Details in Fehlerantworten.
    app.add_exception_handler(SchoolYearTooLow, school_year_error)
    app.add_exception_handler(Exception, unexpected_error)

    @app.get("/health")
    def read_health():
        return {"status": "ok"}

    # API8 in main.py: Host-Prüfung für die gesamte App registrieren.
    # Die Middleware prüft vor der Route: unbekannter Zielname -> 400.
    # Beim Deployment den tatsächlichen API-Domainnamen ergänzen.
    allowed_hosts = [host.strip() for host in os.environ['ALLOWED_HOSTS'].split(',') if host.strip()]
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=allowed_hosts
    )
    return app


app = create_app(show_docs=os.environ.get("API_DOCS", "0") == "1")
