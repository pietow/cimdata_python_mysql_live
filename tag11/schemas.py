from datetime import date
from pydantic import BaseModel

class BookingReportRead(BaseModel):
    id: int
    student_name: str
    course_title: str
    booking_date: date