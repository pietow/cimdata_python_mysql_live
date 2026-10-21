from fastapi import FastAPI

from tag7.routers.courses import router as course_router

app = FastAPI(title="Hogwarts-Kursverwaltung", description="Lern-API mit MySQL", version="0.3.0")

app.include_router(course_router)

@app.get("/health")
def read_health():
    return {"status": "ok"}
