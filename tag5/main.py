from fastapi import FastAPI, HTTPException

from tag5.data import courses

app = FastAPI(title="Hogwarts-Kursverwaltung")

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.get("/courses")
def read_courses():
       return [courses[key] for key in courses ]

@app.get("/courses/{course_id}")
def read_course(course_id: int):
    course = courses.get(course_id)
    if course is None:
         raise HTTPException(status_code=404, detail="Kurs nicht gefunden.")
    return course