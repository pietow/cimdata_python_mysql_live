from fastapi.testclient import TestClient

from tag5.main import app

client = TestClient(app)

def test_read_course():
    response = client.get("courses/1")  # Es wird eine HTTP Anfrage simuliert
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Arithmantik"}

def test_missing_course():
    response = client.get("courses/999")  # Es wird eine HTTP Anfrage simuliert
    assert response.status_code == 404
    assert response.json() == {"detail":"Kurs nicht gefunden."}



