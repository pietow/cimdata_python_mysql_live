from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from tag7.models import Base
from tag9.models import User  # Registriert users an derselben Base.


class CourseManager(Base):
    __tablename__ = "course_managers"

    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    