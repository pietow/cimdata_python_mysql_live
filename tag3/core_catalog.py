from sqlalchemy import text, Column, Integer, MetaData, String, Table
from sqlalchemy import bindparam, select

from db import engine


# statement = text(
#     """
#     SELECT id, title
#     FROM courses
#     WHERE title = :wanted_title
#     ORDER BY id
#     """
# )

metadata = MetaData()

courses = Table(
    "courses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(100), nullable=False)
)

statement = (
    select(courses.c.id, courses.c.title)
    .where(courses.c.title == bindparam("wanted_title"))
    .order_by(courses.c.id)
)

with engine.connect() as connection:
    rows = connection.execute(
        statement, {"wanted_title": "Alte Runen"}
    ).all()
    for course_id, title in rows:
        print(course_id, title)


