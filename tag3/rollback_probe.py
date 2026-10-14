from db import SessionLocal, engine
from models import Course


engine.echo = True
try:
    with SessionLocal() as session: # kein autocommit
        course = session.get(Course, 2)

        if not course:
            raise ValueError("Fehlt")
        course.title = "Wahrsagen - Probe"
        session.flush()
        print("In dieser Transaktion: ", course.title)
        session.rollback()
        print("Nach Rollback: ", course.title)



finally:
    engine.echo = False