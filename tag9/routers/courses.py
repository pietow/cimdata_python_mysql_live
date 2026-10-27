from typing import Annotated


from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError


from tag7.models import Course
from tag7.schemas import CourseCreate, CourseRead, CourseCount
from tag9.dependencies import DbSession, get_current_user, require_staff


router = APIRouter(
        prefix="/courses", 
        tags=["Kurse"], 
        dependencies=[Depends(get_current_user)]
)

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


@router.post("", response_model=CourseRead, status_code=201, dependencies=[Depends(require_staff)])
def create_course(data: CourseCreate, session: DbSession): # Bei Fehler in CourseCreate.model_validate(body.json) wird create_course nicht aufgerufen
    # Kein session.begin(): get_current_user hat die Transaktion schon gestartet (autobegin)
    course = Course(title=data.title) #ORM Instanz
    session.add(course)
    session.flush()
    result = CourseRead.model_validate(course)  # vor commit, danach sind Attribute abgelaufen
    session.commit()
    return result

@router.put("/{course_id}", response_model=CourseRead, dependencies=[Depends(require_staff)])
def replace_course(course_id: CourseId, data: CourseCreate, session: DbSession):
    course = session.get(Course, course_id)   # ORM-Objekt via SQLAlchemy
    if course is None:
        raise HTTPException(404, "Kurs nicht gefunden")
    course.title = data.title
    session.flush()
    result = CourseRead.model_validate(course)
    session.commit()
    return result


@router.delete("/{course_id}", status_code=204, dependencies=[Depends(require_staff)])
def delete_course(course_id: CourseId, session: DbSession):
    if session.get(Course, course_id) is None:
        raise HTTPException(404, "Kurs nicht gefunden")
    try:
        session.execute(delete(Course).where(Course.id == course_id))
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Kurs wird noch verwendet.")
    return Response(status_code=204)