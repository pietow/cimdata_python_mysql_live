from fastapi.testclient import TestClient

from tag6.data import courses
from tag6.main import app

client = TestClient(app)

def test_read_course():
    response = client.get("courses/1")  # Es wird eine HTTP Anfrage simuliert
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Arithmantik"}

def test_missing_course():
    response = client.get("courses/999")  # Es wird eine HTTP Anfrage simuliert
    assert response.status_code == 404
    assert response.json() == {"detail":"Kurs nicht gefunden."}


def test_invalid_body():
    before = len(courses)

    response = client.post('courses', json={"title": "   "})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "title"]

    after = len(courses)

    assert before == after

def test_create_and_filter_response():
    before = len(courses)

    response = client.post("courses", json={"title": "  Flugkunde  "})
    assert response.status_code == 201

    created = response.json()

    try:
        assert created["title"] == "Flugkunde"
        #assert list(created.keys()) == ['id', 'title']
        assert set(created) == {"id", 'title'}
        stored = courses[created["id"]]
        # Antwortfilter bzw. Antwortschema wird geprüft
        assert stored['internal_note'] == 'hardcoded'
    finally:
        courses.pop(created["id"], None)

