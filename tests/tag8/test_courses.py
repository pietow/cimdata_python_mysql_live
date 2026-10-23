from tag7.models import Course

def test_course_roundtrip(api_client, db_factory):
    # Arrange and Act
    response = api_client.post("/courses", json={"title": " Flugkunde "})
    assert response.status_code == 201
    created = response.json()
    course_id = created["id"]
    assert created == {"id": course_id, "title": "Flugkunde", "room": None} 
    # Ein neuer DB-Zugriff prüft den commit der Route
    with db_factory() as db:
        assert db.get(Course, course_id).title == "Flugkunde"

    url = f"/courses/{course_id}"
    stored = api_client.get(url)
    assert stored.status_code == 200

    changed = api_client.put(url, json={"title": "Flugtraining I"})
    with db_factory() as db:
        assert db.get(Course, course_id).title == "Flugtraining I"


    removed = api_client.delete(url)
    assert removed.status_code == 204
    with db_factory() as db:
        assert db.get(Course, course_id) is None

    