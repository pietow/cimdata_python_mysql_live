from pydantic import BaseModel, ConfigDict, Field, field_validator

class CourseCreate(BaseModel):
    # Eingabeschema
    model_config = ConfigDict(extra="forbid") # extra Felder werden abgelehnt z.b. {title: '...', id: 10, internal_notes: '...'} 
    # erzeugt 422
    title: str = Field(min_length=1, max_length=100)

    @field_validator('title', mode="before")
    @classmethod
    def trim_title(cls, value): # value= '   '
        print('DEBUG: ', value)
        if isinstance(value, str):
            return value.strip()     # value = ''
        return value   # später von pydantic course_instanze = CourseCreate(value) 


class CourseRead(BaseModel):
    # Ausgabeschema bzw. Antwortschema
    id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=100)

class CourseCount(BaseModel):
    count: int = Field(ge=0)