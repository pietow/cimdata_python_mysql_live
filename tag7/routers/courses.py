from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Response
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from tag7.dependencies import DbSession
from tag7.models import Course
from tag7.schemas import CourseCount, CourseCreate, CourseRead

router = APIRouter(prefix="/courses", tags=["Kurse"])
CourseId = Annotated[int, Path(ge=1)]
Search = Annotated[str | None, Query(min_length=2, max_length=100)]


@router.get("", response_model=list[CourseRead])
def read_courses(db: DbSession, q: Search = None):
    statement = select(Course).order_by(Course.id)
    if q is not None:
        # Werte werden gebunden. % und _ bleiben hier normale Suchzeichen.
        statement = statement.where(Course.title.contains(q, autoescape=True))
    return db.scalars(statement).all()


@router.get("/count", response_model=CourseCount)
def count_courses(db: DbSession):
    return {"count": db.scalar(select(func.count()).select_from(Course))}


@router.get("/{course_id}", response_model=CourseRead)
def read_course(course_id: CourseId, db: DbSession):
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(404, "Kurs nicht gefunden.")
    return course


@router.post("", response_model=CourseRead, status_code=201)
def create_course(data: CourseCreate, db: DbSession):
    with db.begin():
        course = Course(title=data.title)
        db.add(course)
        db.flush()  # INSERT ausführen und die vergebene ID einlesen.
        result = CourseRead.model_validate(course)
    # Erst nach erfolgreichem Commit den Erfolg zurückgeben.
    return result


@router.put("/{course_id}", response_model=CourseRead)
def replace_course(course_id: CourseId, data: CourseCreate, db: DbSession):
    # Auch der SELECT gehört in den Transaktionsblock.
    with db.begin():
        course = db.get(Course, course_id)
        if course is None:
            raise HTTPException(404, "Kurs nicht gefunden.")
        course.title = data.title
        db.flush()
        result = CourseRead.model_validate(course)
    return result


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: CourseId, db: DbSession):
    try:
        with db.begin():
            if db.get(Course, course_id) is None:
                raise HTTPException(404, "Kurs nicht gefunden.")
            # Direktes DELETE lässt MySQL die Fremdschlüssel prüfen.
            db.execute(delete(Course).where(Course.id == course_id))
    except IntegrityError as exc:
        # begin() hat bereits zurückgerollt, bevor dieser Block läuft.
        raise HTTPException(409, "Kurs wird noch verwendet.") from exc
    return Response(status_code=204)
