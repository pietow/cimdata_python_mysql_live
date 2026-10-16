from itertools import count

from fastapi import FastAPI, HTTPException

from tag5.data import courses
from tag5.schemas import CourseCreate, CourseRead

app = FastAPI(title="Hogwarts-Kursverwaltung")

course_ids = count(6)

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.get("/courses", response_model=list[CourseRead])
def read_courses(q: str | None ):
    rows = [courses[key] for key in courses ]
    if q is not None:
        rows = [row for row in rows if
            q.casefold() in row["title"].casefold()]
    return rows

@app.get("/courses/{course_id}", response_model=CourseRead)
def read_course(course_id: int):
    course = courses.get(course_id)
    if course is None:
         raise HTTPException(status_code=404, detail="Kurs nicht gefunden.")
    return course


@app.post("/courses", response_model=CourseCreate, status_code=201)
def create_course(course: CourseCreate):
    course_id = next(course_ids)
    created = {"id": course_id, "title": course.title}
    courses[course_id] = created
    return created