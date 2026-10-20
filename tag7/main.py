from fastapi import FastAPI

from tag7.routers import courses, bookings

app = FastAPI(title="Hogwarts-Kursverwaltung", version="0.3.0")
app.include_router(courses.router)
app.include_router(bookings.router)

@app.get("/health")
def read_health():
    # Prozessprüfung; eine funktionierende Datenbank folgt daraus nicht.
    return {"status": "ok"}