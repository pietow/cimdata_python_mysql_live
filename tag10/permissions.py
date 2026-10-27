from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from tag7.models import Course
from tag9.dependencies import require_staff
from tag9.schemas import UserRead
from tag10.models import CourseManager


# OWASP API5, ist bereits bekannt: FastAPI prüft die Rolle und übergibt das bestätigte Konto
StaffUser = Annotated[UserRead, Depends(require_staff)] # wird später in den Routen verwendet


def managed_course(course_id: int, db: Session, user: UserRead) -> Course:
    if user.role != "staff":
        raise HTTPException(403, "Nicht befugt.")
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(404, "Kurs nicht gefunden.")
    assigment = db.get(CourseManager, course_id) # entspricht eine Zeile

    if assigment is None or assigment.user_id != user.id:
        raise HTTPException(403, "Keine Berechtigung/Zuständigkeit für diesen Kurs.")
    return course

