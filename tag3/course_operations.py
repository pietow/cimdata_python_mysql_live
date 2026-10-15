from db import SessionLocal
from models import Course

# CRUD

#CREATE
def create_course(title: str) -> int:
    with SessionLocal.begin() as session:  # mit .begin() haben wir autocommit = True
        course = Course(title=title)
        session.add(course) # add merkt sich nur das neue Objekt vor
        session.flush() # erzeugt die Zeile in der DB
        course_id = course.id
    return course_id

#READ

def get_course(course_id: int) -> tuple[int, str] | None:
    with SessionLocal() as session:
        course = session.get(Course, course_id)
        if course is None:
            return None
        return course.id, course.title

# UPDATE

def rename_course(course_id: int, new_title: str) -> bool:
    with SessionLocal.begin() as session:
        course = session.get(Course, course_id)
        if course is None:
            return False
        course.title = new_title
    return True 

# DELETE

def delete_course(course_id: int) -> bool:
    with SessionLocal.begin() as session:
        course = session.get(Course, course_id)
        if course is None:
            return False
        session.delete(course)
    return True



