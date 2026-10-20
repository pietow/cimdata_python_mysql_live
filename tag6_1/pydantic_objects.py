import json

from pydantic import ValidationError

from schemas import CourseCreate, CourseRead


if __name__ == "__main__":
    # first = CourseCreate(title="Alte Runen")
    # second = CourseCreate(title="Flugkunde")


    body = json.loads('{"title": "Alte Runen"}')
    course = CourseCreate.model_validate(body) # Validierung
    print(course.title)

    try:
        CourseCreate.model_validate({"title": ""}) # Validierung
    except ValidationError as e:
        print(e.json()) 

    stored = {"id": 1, "title": "Alte Runen", "internal_note": "Nur für interne Zwecke."}

    public = CourseRead.model_validate(stored) # Validierung
    print(public.model_dump()) # {"id": 1, "title": "Alte Runen"}