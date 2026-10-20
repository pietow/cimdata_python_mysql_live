from typing import Annotated

from fastapi import Path, Query

from fastapi import APIRouter, HTTPException

from tag6.data import courses, course_ids
from tag6.schemas import CourseCreate, CourseRead, CourseCount

router = APIRouter(prefix="/courses", tags=["Kurse"])


@router.get("", response_model=list[CourseRead])
def read_courses(q: Annotated[str | None, Query(min_length=2, max_length=100, description="Teil des Titles")]= None):
    rows = [courses[key] for key in courses ]
    if q is not None:
        rows = [row for row in rows if
            q.casefold() in row["title"].casefold()]
    return rows

@router.get("/count", response_model=CourseCount)
def read_course_count():
    # return {"count": -1} # Internal Server Error; 5xx heißt, dass der Server eine falsche Antwort geliefert hat
    return {'count': len(courses)}


@router.get("/{course_id}", response_model=CourseRead)
def read_course(course_id: Annotated[int, Path(ge=1)]):
    course = courses.get(course_id)
    if course is None:
         raise HTTPException(status_code=404, detail="Kurs nicht gefunden.")
    return course


@router.post("", response_model=CourseRead, status_code=201)
def create_course(course: CourseCreate): # Bei Fehler in CourseCreate.model_validate(body.json) wird create_course nicht aufgerufen
    course_id = next(course_ids)
    created = {
            "id": course_id, 
            "title": course.title, 
            "internal_note": "hardcoded",
        }
    courses[course_id] = created
    print('COURSES: ', courses)
    return created
