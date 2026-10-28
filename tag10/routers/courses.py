from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from tag7.models import Course
from tag7.schemas import CourseCount, CourseCreate, CourseRead
from tag9.dependencies import DbSession, get_current_user
from tag9.routers.courses import CourseId, Search
from tag10.models import CourseManager #Neu
from tag10.pagination import AfterId, Limit  # Neu (OWASP: API4)
from tag10.permissions import StaffUser, managed_course #Neu


router = APIRouter(
        prefix="/courses", 
        tags=["Kurse"], 
        dependencies=[Depends(get_current_user)]
)



@router.get("", response_model=list[CourseRead])
def read_courses(session: DbSession, q:Search = None, limit: Limit = 20, after_id: AfterId = 0):  # Neue Parameter 
    statement = select(Course).where(Course.id > after_id) # Neu
    if q is not None:
        statement = statement.where(Course.title.contains(q, autoescape=True))
    return session.scalars(statement.order_by(Course.id).limit(limit)).all() # Pagination: API4 (OWASP)

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
def create_course(data: CourseCreate, session: DbSession, user: StaffUser): # Bei Fehler in CourseCreate.model_validate(body.json) wird create_course nicht aufgerufen
    # Kein session.begin(): get_current_user hat die Transaktion schon gestartet (autobegin)
    course = Course(title=data.title) #ORM Instanz
    session.add(course)
    session.flush() # führt den INSERT aus, somit vergibt MYSQL die ID, auf die wir dann (über course-Instanz) zugreifen können
    session.add(CourseManager(course_id=course.id, user_id=user.id))
    result = CourseRead.model_validate(course)  # vor commit, danach sind Attribute abgelaufen
    session.commit() # Kurs und Zuordnung werden gemeinsam gespeichert
    return result

@router.put("/{course_id}", response_model=CourseRead)
def replace_course(course_id: CourseId, data: CourseCreate, session: DbSession, user: StaffUser): # Neu
    course = managed_course(course_id, session, user) # Neu
    course.title = data.title
    session.flush()
    result = CourseRead.model_validate(course)
    session.commit()
    return result


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: CourseId, session: DbSession, user: StaffUser):
    managed_course(course_id, session, user) # Neu
    try:
        session.execute(delete(Course).where(Course.id == course_id))
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Kurs wird noch verwendet.")
    return Response(status_code=204)