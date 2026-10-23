from fastapi import FastAPI

from tag7.routers import courses, bookings
app = FastAPI(title="Hogwarts-Kursverwaltung", description="Lern-API mit MySQL", version="0.4.0")

app.include_router(courses.router)
app.include_router(bookings.router)

@app.get("/health")
def read_health():
    return {"status": "ok"}
