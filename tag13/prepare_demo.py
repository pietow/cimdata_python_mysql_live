import os
from datetime import date

from sqlalchemy import select

from tag7.db import SessionLocal
from tag7.models import Booking, Course, Student
from tag9.models import User
from tag9.passwords import hash_password
from tag10.models import CourseManager


def main():
    # Nur für die frische Unterrichtsumgebung; keine vorhandenen Konten ändern.
    with SessionLocal.begin() as db:
        if db.scalar(select(User.id).where(User.username == "vector")):
            print("Demo bereits vorhanden; keine Daten geändert.")
            return

        password = os.environ.get("DEMO_PASSWORD", "")
        if not 16 <= len(password) <= 128 or password.startswith("REPLACE_"):
            raise SystemExit("DEMO_PASSWORD durch ein langes Demo-Passwort ersetzen.")

        users = []
        for name, role in (("vector", "staff"), ("hagrid", "staff"),
                           ("babbling", "reader")):
            user = User(username=name, role=role,
                        password_hash=hash_password(password))
            db.add(user)
            users.append(user)

        own = Course(title="Arithmantik")
        other = Course(title="Pflege magischer Geschöpfe")
        db.add_all([own, other])
        db.flush()  # IDs werden für die folgenden Zuordnungen gebraucht.
        db.add_all([
            CourseManager(course_id=own.id, user_id=users[0].id),
            CourseManager(course_id=other.id, user_id=users[1].id),
        ])

        for first, last, course in (
            ("Hermione", "Granger", own),
            ("Harry", "Potter", own),
            ("Ron", "Weasley", own),
            ("Neville", "Longbottom", other),
        ):
            student = Student(first_name=first, last_name=last,
                              house="Gryffindor", school_year=3)
            db.add(student)
            db.flush()
            db.add(Booking(student_id=student.id, course_id=course.id,
                           booking_date=date(1993, 9, 1)))
    # Kontext verlassen: Alle Beispieldaten werden gemeinsam committed.
    print("Demo eingerichtet: vector, hagrid, babbling; Berichtstag 1993-09-01.")


if __name__ == "__main__":
    main()
