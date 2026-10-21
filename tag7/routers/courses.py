from typing import Annotated


from fastapi import APIRouter, HTTPException, Path, Query, Response
from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError

from tag7.dependencies import DbSession
from tag7.models import Course
from tag7.schemas import CourseCreate, CourseRead, CourseCount


router = APIRouter(prefix="/courses", tags=["Kurse"])
CourseId = Annotated[int, Path(ge=1)]
Search = Annotated[str | None, Query(min_length=2, max_length=100, description="Teil des Titles")]


@router.get("", response_model=list[CourseRead])
def read_courses(session: DbSession, q:Search = None):
    statement = select(Course).order_by(Course.id)
    if q is not None:
        statement = statement.where(Course.title.contains(q, autoescape=True))
    return session.scalars(statement).all()

@router.get("/count", response_model=CourseCount)
def read_course_count(session: DbSession):
    return {"count": session.scalar(select(func.count()).select_from(Course))}

@router.get("/{course_id}", response_model=CourseRead)
def read_course(course_id: CourseId, session: DbSession):
    course = session.get(Course, course_id)
    if course is None:
         raise HTTPException(status_code=404, detail="Kurs nicht gefunden.")
    return course


@router.post("", response_model=CourseRead, status_code=201)
def create_course(data: CourseCreate, session: DbSession): # Bei Fehler in CourseCreate.model_validate(body.json) wird create_course nicht aufgerufen
    with session.begin():  # autocommit
        course = Course(title=data.title) #ORM Instanz
        session.add(course)
        session.flush()
        result = CourseRead.model_validate(course)
    return result

@router.put("/{course_id}", response_model=CourseRead)
def replace_course(course_id: CourseId, data: CourseCreate, session: DbSession):
    with session.begin():  # autocommit
        course = session.get(Course, course_id)   # ORM-Objekt via SQLAlchemy
        if course is None:
            raise HTTPException(404, "Kurs nicht gefunden")
        course.title = data.title
        session.flush()
        result = CourseRead.model_validate(course)
    return result


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: CourseId, session: DbSession):
    try:
        with session.begin():  # autocommit
            if session.get(Course, course_id) is None:   
                raise HTTPException(404, "Kurs nicht gefunden")
            session.execute(delete(Course).where(Course.id == course_id))
    except IntegrityError as exc:
        raise HTTPException(409, "Kurs wird noch verwendet.")
    return Response(status_code=204)