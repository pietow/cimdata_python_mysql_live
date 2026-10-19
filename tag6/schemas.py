from pydantic import BaseModel, Field

class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)

class CourseRead(BaseModel):
    id: int
    title: str