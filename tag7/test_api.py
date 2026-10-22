from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from tag7.db import SessionLocal
from tag7.main import app
from tag7.models import Booking, Course, Student


# Vorgegebene Hilfsfunktionen: vorbereiten, nachlesen, aufräumen.
def prepare_batch_case():
    with SessionLocal.begin() as db:
        students = list(db.scalars(select(Student.id)
                                   .order_by(Student.id).limit(2)))
        assert len(students) == 2, "Zwei vorhandene Schüler benötigt."
        max_id = db.scalar(select(func.max(Student.id)))
        if max_id is None:
            raise TypeError('Keine students gefunden.')
        missing_id = max_id + 1000 
        course = Course(title="Flugkunde")
        db.add(course)
        db.flush()
        course_id = course.id
    return course_id, students, missing_id


def booking_snapshot(course_id):
    # Neue Session: den gespeicherten Stand dieses Testkurses prüfen.
    with SessionLocal() as db:
        statement = select(
            Booking.id, Booking.student_id, Booking.course_id,
            Booking.booking_date,
        ).where(Booking.course_id == course_id).order_by(Booking.id)
        return db.execute(statement).all()


def cleanup_course(course_id):
    # Nur die Datensätze des in diesem Test erzeugten Kurses entfernen.
    with SessionLocal.begin() as db:
        db.execute(delete(Booking).where(Booking.course_id == course_id))
        db.execute(delete(Course).where(Course.id == course_id))


def test_course_roundtrip():
    with TestClient(app) as client:
        response = client.post("/courses", json={"title": " Flugkunde "})
        assert response.status_code == 201
        course = response.json()
        course_id = response.json()["id"]
        try:
            assert course['title'] == "Flugkunde"
            url = f"/courses/{course_id}"
            stored = client.get(url)
            changed = client.put(url, json={"title": "Flugtraining I"})
            removed = client.delete(url)

            assert stored.json()['title'] == "Flugkunde"
            assert changed.json()['title'] == "Flugtraining I"
            assert removed.status_code == 204
            
            stored = client.get(url)
            assert stored.status_code == 404
        finally:
            cleanup_course(course_id)

def test_batch_saves_all_bookings():
    course_id, students, _ = prepare_batch_case()
    try:
        with TestClient(app) as client:
            response = client.post("/booking-batches", json={
                "course_id": course_id,
                "student_ids": students,
                "booking_date": "1993-09-06",
            })
        assert response.status_code == 201
        assert [row['student_id'] for row in response.json()] == students   
           
    finally:
        cleanup_course(course_id)

def test_batch_rolls_back_on_missing_student():
    course_id, students, missing_id = prepare_batch_case()
    try:
        before = booking_snapshot(course_id)
        with TestClient(app) as client:
            response = client.post("/booking-batches", json={
                "course_id": course_id,
                "student_ids": [students[0], missing_id],
                "booking_date": "1993-09-06",
            })
        assert response.status_code == 404
        assert response.json() == {"detail": "Kurs nicht gefunden."}
        assert booking_snapshot(course_id) == before
           
    finally:
        cleanup_course(course_id)
