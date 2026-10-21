from sqlalchemy import func, select

from tag7.db import SessionLocal
from tag7.models import Course


with SessionLocal() as session:
    print(session.in_transaction())
    session.scalar(select(func.count()).select_from(Course))
    print(session.in_transaction())
    session.rollback()
    print(session.in_transaction())