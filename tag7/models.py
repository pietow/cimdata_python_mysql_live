from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint(
            "school_year BETWEEN 1 AND 7",
            name="ck_students_school_year"
        ),    
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    house: Mapped[str | None] = mapped_column(String(20))
    school_year: Mapped[int] = mapped_column(TINYINT)
    bookings: Mapped[list["Booking"]] = relationship(back_populates="student")
   

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    room: Mapped[str | None] = mapped_column(String(30))  # New
    bookings: Mapped[list["Booking"]] = relationship(back_populates="course")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    booking_date: Mapped[date] = mapped_column(Date)
    student: Mapped[Student] = relationship(back_populates="bookings")
    course: Mapped[Course] = relationship(back_populates="bookings")