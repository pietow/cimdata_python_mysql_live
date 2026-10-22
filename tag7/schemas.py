from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

class CourseCreate(BaseModel):
    # Eingabeschema
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True) 
    title: str = Field(min_length=1, max_length=100)


class CourseRead(BaseModel):
    # Ausgabeschema bzw. Antwortschema
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=100)
    room: str | None = None

class CourseCount(BaseModel):
    count: int = Field(ge=0)


class BookingBatchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    course_id: int = Field(ge=1)
    student_ids: list[Annotated[int, Field(ge=1)]] = Field(
                                            min_length=1, max_length=20 # bezieht sich auf list
    )  # Gruppenbuchung
    booking_date: date

class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    course_id: int
    booking_date: date