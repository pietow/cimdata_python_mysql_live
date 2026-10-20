from fastapi import FastAPI, HTTPException

from tag6.routers.courses import router as course_router

app = FastAPI(title="Hogwarts-Kursverwaltung", description="Lern-API mit vorübergehendem Speicherstand.", version="0.2.0")

app.include_router(course_router)

@app.get("/health")
def read_health():
    return {"status": "ok"}
