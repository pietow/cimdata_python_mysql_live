from db import SessionLocal, engine
from models import Course


engine.echo = True
try:
    with SessionLocal() as session:
        course = session.get(Course, 3)
        if course is None:
            print('Nicht gefunden')
        else:
            print(course.id, course.title)
finally:
    engine.echo = False