from sqlalchemy import select

from tag7.db import SessionLocal
from tag7.models import Course
from tag9.models import User
from tag10.models import CourseManager


def main():
    course_id = int(input("Kurs-ID: "))
    username = input("Zuständiges staff-Konto: ").strip()


    with SessionLocal.begin() as db:
        course = db.get(Course, course_id) # SELECT * FROM courses;
        user = db.scalar(select(User).where(User.username == username)) # Select * FROM users WHERE username = %s , username;
        if course is None: 
            raise SystemExit("Kurs nicht gefunden")
        if user is None or not user.is_active or user.role != "staff": 
            raise SystemExit("Aktives User/staff-Konto erforderlich.")
        assignment = db.get(CourseManager, course_id)
        if assignment is None:
            db.add(CourseManager(course_id=course_id, user_id=user.id))
        else:
            assignment.user_id = user.id
    print("Zuständigkeit gespeichert")

if __name__ == "__main__":
    main()